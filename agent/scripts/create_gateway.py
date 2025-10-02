#!/usr/bin/env python3
"""
Customer Retention Agent - Create AgentCore Gateway

This script creates the AgentCore Gateway with Cognito authentication
and stores the configuration in SSM Parameter Store.
"""

import boto3
import os
import logging
import json
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
SSM_CLIENT = boto3.client('ssm', region_name=REGION)
IAM_CLIENT = boto3.client('iam', region_name=REGION)
GATEWAY_CLIENT = boto3.client('bedrock-agentcore-control', region_name=REGION)

# Parameter Store Paths
COGNITO_USER_POOL_ID_PATH = "/customer-retention-agent/cognito/user-pool-id"
COGNITO_M2M_CLIENT_ID_PATH = "/customer-retention-agent/cognito/m2m-client-id"
COGNITO_M2M_CLIENT_SECRET_PATH = "/customer-retention-agent/cognito/m2m-client-secret"
COGNITO_DISCOVERY_URL_PATH = "/customer-retention-agent/cognito/discovery-url"
COGNITO_AUTH_SCOPE_PATH = "/customer-retention-agent/cognito/auth-scope"

GATEWAY_ID_PATH = "/customer-retention-agent/gateway/id"
GATEWAY_URL_PATH = "/customer-retention-agent/gateway/url"

# Gateway Configuration
GATEWAY_NAME = "customer-retention-gateway"
GATEWAY_IAM_ROLE_NAME = "CustomerRetentionGatewayRole"

def get_ssm_parameter(name: str) -> str:
    """Retrieve a parameter from SSM Parameter Store."""
    try:
        response = SSM_CLIENT.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            logger.error(f"SSM parameter '{name}' not found. Please create it.")
        else:
            logger.error(f"Error retrieving SSM parameter '{name}': {e}")
        raise

def put_ssm_parameter(name: str, value: str, description: str, overwrite: bool = True):
    """Store a parameter in SSM Parameter Store."""
    try:
        SSM_CLIENT.put_parameter(
            Name=name,
            Value=value,
            Type='String',
            Overwrite=overwrite,
            Description=description,
            Tags=[{'Key': 'project', 'Value': 'customer-retention-agent'}, {'Key': 'component', 'Value': 'gateway'}]
        )
        logger.info(f"✅ Stored SSM parameter: {name}")
    except ClientError as e:
        logger.error(f"Error storing SSM parameter '{name}': {e}")
        raise

def create_gateway_iam_role() -> str:
    """Create or get the IAM role for the AgentCore Gateway."""
    try:
        # Check if role already exists
        try:
            role = IAM_CLIENT.get_role(RoleName=GATEWAY_IAM_ROLE_NAME)
            logger.info(f"✅ IAM role '{GATEWAY_IAM_ROLE_NAME}' already exists: {role['Role']['Arn']}")
            return role['Role']['Arn']
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchEntity':
                raise # Re-raise if it's not a "not found" error

        logger.info(f"Creating IAM role: {GATEWAY_IAM_ROLE_NAME}")

        # Trust policy for Bedrock AgentCore
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        create_role_response = IAM_CLIENT.create_role(
            RoleName=GATEWAY_IAM_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Customer Retention AgentCore Gateway to invoke Lambda functions",
            Tags=[{'Key': 'project', 'Value': 'customer-retention-agent'}, {'Key': 'component', 'Value': 'gateway'}]
        )
        role_arn = create_role_response['Role']['Arn']
        logger.info(f"✅ IAM role '{GATEWAY_IAM_ROLE_NAME}' created with ARN: {role_arn}")

        # Attach policy for Lambda invocation
        # This policy grants permission to invoke *all* Lambda functions.
        # In a production environment, you would restrict this to specific Lambda ARNs.
        invoke_lambda_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "lambda:InvokeFunction"
                    ],
                    "Resource": [
                        f"arn:aws:lambda:{REGION}:{boto3.client('sts').get_caller_identity()['Account']}:function:dev-customer-retention-web-search",
                        f"arn:aws:lambda:{REGION}:{boto3.client('sts').get_caller_identity()['Account']}:function:dev-customer-retention-churn-data-query",
                        f"arn:aws:lambda:{REGION}:{boto3.client('sts').get_caller_identity()['Account']}:function:dev-customer-retention-retention-offer"
                    ]
                }
            ]
        }
        IAM_CLIENT.put_role_policy(
            RoleName=GATEWAY_IAM_ROLE_NAME,
            PolicyName="CustomerRetentionGatewayLambdaInvokePolicy",
            PolicyDocument=json.dumps(invoke_lambda_policy)
        )
        logger.info(f"✅ Attached Lambda invocation policy to '{GATEWAY_IAM_ROLE_NAME}'")

        return role_arn

    except Exception as e:
        logger.error(f"Error creating/getting Gateway IAM role: {e}")
        raise

def create_agentcore_gateway(gateway_iam_role_arn: str) -> tuple[str, str]:
    """Create or get the AgentCore Gateway."""
    try:
        # Check if gateway already exists
        try:
            response = GATEWAY_CLIENT.list_gateways(nameContains=GATEWAY_NAME)
            for gw in response.get('gateways', []):
                if gw['name'] == GATEWAY_NAME:
                    logger.info(f"✅ AgentCore Gateway '{GATEWAY_NAME}' already exists: {gw['gatewayId']}")
                    return gw['gatewayId'], gw['gatewayUrl']
            
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise # Re-raise if it's not a "not found" error

        logger.info(f"Creating AgentCore Gateway: {GATEWAY_NAME}")

        # Retrieve Cognito parameters
        user_pool_id = get_ssm_parameter(COGNITO_USER_POOL_ID_PATH)
        m2m_client_id = get_ssm_parameter(COGNITO_M2M_CLIENT_ID_PATH)
        discovery_url = get_ssm_parameter(COGNITO_DISCOVERY_URL_PATH)

        auth_config = {
            "customJWTAuthorizer": {
                "allowedClients": [m2m_client_id],
                "discoveryUrl": discovery_url
            }
        }

        create_response = GATEWAY_CLIENT.create_gateway(
            name=GATEWAY_NAME,
            roleArn=gateway_iam_role_arn,
            protocolType="MCP",
            authorizerType="CUSTOM_JWT",
            authorizerConfiguration=auth_config,
            description="AgentCore Gateway for Customer Retention Agent's external tools",
            tags={'project': 'customer-retention-agent', 'component': 'gateway'}
        )

        gateway_id = create_response['gatewayId']
        gateway_url = create_response['gatewayUrl']
        logger.info(f"✅ AgentCore Gateway '{GATEWAY_NAME}' created with ID: {gateway_id}, URL: {gateway_url}")

        # Store in SSM
        put_ssm_parameter(GATEWAY_ID_PATH, gateway_id, "AgentCore Gateway ID for Customer Retention Agent")
        put_ssm_parameter(GATEWAY_URL_PATH, gateway_url, "AgentCore Gateway URL for Customer Retention Agent")

        return gateway_id, gateway_url

    except Exception as e:
        logger.error(f"Error creating/getting AgentCore Gateway: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("🚀 Starting AgentCore Gateway setup...")
        
        # 1. Create or get Gateway IAM Role
        gateway_iam_role_arn = create_gateway_iam_role()
        
        # 2. Create or get AgentCore Gateway
        gateway_id, gateway_url = create_agentcore_gateway(gateway_iam_role_arn)
        
        logger.info("🎉 AgentCore Gateway setup complete!")
        logger.info(f"Gateway ID: {gateway_id}")
        logger.info(f"Gateway URL: {gateway_url}")

    except Exception as e:
        logger.error(f"❌ AgentCore Gateway setup failed: {e}")
