#!/usr/bin/env python3
"""
Customer Retention Agent - Attach Lambda Functions to Gateway

This script attaches our 3 Lambda functions as Gateway targets
with proper tool schemas for MCP integration.
"""

import os
import sys
import boto3
import json
from botocore.exceptions import ClientError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
ACCOUNT_ID = boto3.client('sts').get_caller_identity()['Account']

def get_ssm_parameter(parameter_name: str) -> str:
    """Get parameter value from SSM Parameter Store"""
    try:
        ssm_client = boto3.client('ssm', region_name=REGION)
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Error getting SSM parameter {parameter_name}: {str(e)}")
        raise

def get_lambda_tool_schemas():
    """Define tool schemas for our Lambda functions"""
    return [
        {
            "name": "web_search",
            "description": "Search the web for updated information using DuckDuckGo",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "The search query keywords"
                    },
                    "region": {
                        "type": "string",
                        "description": "The search region (e.g., us-en, uk-en, ru-ru)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "The maximum number of results to return"
                    }
                },
                "required": ["keywords"]
            }
        },
        {
            "name": "churn_data_query",
            "description": "Query customer churn data and risk analysis from Athena",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer ID to query churn data for"
                    }
                },
                "required": ["customer_id"]
            }
        },
        {
            "name": "retention_offer",
            "description": "Generate personalized retention offers based on customer risk",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer ID to generate offers for"
                    },
                    "churn_risk": {
                        "type": "string",
                        "description": "Customer churn risk level (LOW, MEDIUM, HIGH)"
                    },
                    "risk_score": {
                        "type": "number",
                        "description": "Numeric churn risk score"
                    }
                },
                "required": ["customer_id", "churn_risk"]
            }
        }
    ]

def create_gateway_target(gateway_id: str, target_name: str, lambda_arn: str, tool_schemas: list):
    """Create a Gateway target for a Lambda function"""
    try:
        gateway_client = boto3.client('bedrock-agentcore-control', region_name=REGION)
        
        # Check if target already exists
        try:
            response = gateway_client.list_gateway_targets(gatewayIdentifier=gateway_id)
            for target in response.get('gatewayTargets', []):
                if target['name'] == target_name:
                    logger.info(f"✅ Gateway target already exists: {target['targetId']}")
                    return target['targetId']
        except Exception as e:
            logger.info(f"Could not check existing targets: {str(e)}")
            # Continue to create new target
        
        # Lambda target configuration
        lambda_target_config = {
            "mcp": {
                "lambda": {
                    "lambdaArn": lambda_arn,
                    "toolSchema": {
                        "inlinePayload": tool_schemas
                    }
                }
            }
        }
        
        # Credential configuration (use Gateway IAM role)
        credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]
        
        logger.info(f"Creating Gateway target: {target_name}")
        
        # Create the target
        try:
            create_response = gateway_client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name=target_name,
                description=f"Lambda target for {target_name} function",
                targetConfiguration=lambda_target_config,
                credentialProviderConfigurations=credential_config
            )
            
            target_id = create_response['targetId']
            logger.info(f"✅ Gateway target created: {target_id}")
            
            return target_id
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                # Target already exists, get its ID
                logger.info(f"Target {target_name} already exists, getting existing target ID...")
                try:
                    response = gateway_client.list_gateway_targets(gatewayIdentifier=gateway_id)
                    logger.info(f"Found {len(response.get('gatewayTargets', []))} existing targets")
                    for target in response.get('gatewayTargets', []):
                        logger.info(f"Checking target: {target.get('name', 'NO_NAME')}")
                        if target.get('name') == target_name:
                            logger.info(f"✅ Using existing Gateway target: {target['targetId']}")
                            return target['targetId']
                    
                    # If we still can't find it, let's try a different approach
                    logger.warning(f"Could not find target {target_name} in list, but it exists. This might be a timing issue.")
                    logger.info("Skipping this target and continuing with others...")
                    return None
                    
                except Exception as list_error:
                    logger.error(f"Error listing targets: {str(list_error)}")
                    logger.info("Skipping this target and continuing with others...")
                    return None
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error creating Gateway target {target_name}: {str(e)}")
        raise

def attach_all_lambda_targets():
    """Attach all 3 Lambda functions as Gateway targets"""
    try:
        # Get Gateway configuration
        gateway_id = get_ssm_parameter('/customer-retention-agent/gateway/id')
        logger.info(f"Using Gateway ID: {gateway_id}")
        
        # Get tool schemas
        tool_schemas = get_lambda_tool_schemas()
        
        # Lambda function ARNs
        lambda_functions = {
            'WebSearchTarget': {
                'arn': f'arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:dev-customer-retention-web-search',
                'tools': [tool_schemas[0]]  # web_search
            },
            'ChurnDataQueryTarget': {
                'arn': f'arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:dev-customer-retention-churn-data-query',
                'tools': [tool_schemas[1]]  # churn_data_query
            },
            'RetentionOfferTarget': {
                'arn': f'arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:dev-customer-retention-retention-offer',
                'tools': [tool_schemas[2]]  # retention_offer
            }
        }
        
        target_ids = {}
        
        # Create targets for each Lambda function
        for target_name, config in lambda_functions.items():
            target_id = create_gateway_target(
                gateway_id=gateway_id,
                target_name=target_name,
                lambda_arn=config['arn'],
                tool_schemas=config['tools']
            )
            if target_id:  # Only store if we got a valid target ID
                target_ids[target_name] = target_id
            else:
                logger.warning(f"Skipping {target_name} due to existing target issues")
        
        logger.info("🎉 All Lambda targets attached successfully!")
        logger.info(f"Target IDs: {target_ids}")
        
        return target_ids
        
    except Exception as e:
        logger.error(f"Error attaching Lambda targets: {str(e)}")
        raise

def store_target_config(target_ids: dict):
    """Store target configuration in SSM Parameter Store"""
    try:
        ssm_client = boto3.client('ssm', region_name=REGION)
        
        for target_name, target_id in target_ids.items():
            parameter_name = f'/customer-retention-agent/gateway/targets/{target_name.lower()}'
            ssm_client.put_parameter(
                Name=parameter_name,
                Value=target_id,
                Type='String',
                Description=f'Customer Retention Gateway Target ID for {target_name}',
                Tags=[
                    {'Key': 'project', 'Value': 'customer-retention-agent'},
                    {'Key': 'component', 'Value': 'gateway-target'}
                ]
            )
        
        logger.info("✅ Target configuration stored in SSM Parameter Store")
        
    except Exception as e:
        logger.error(f"Error storing target configuration: {str(e)}")
        raise

def main():
    """Main function to attach Lambda targets to Gateway"""
    try:
        logger.info("🚀 Starting Lambda target attachment to Gateway...")
        
        # Attach all Lambda targets
        target_ids = attach_all_lambda_targets()
        
        # Store target configuration
        store_target_config(target_ids)
        
        logger.info("🎉 Lambda target attachment completed successfully!")
        logger.info("Available tools in Gateway:")
        logger.info("  - web_search: Search the web for updated information")
        logger.info("  - churn_data_query: Query customer churn data and risk analysis")
        logger.info("  - retention_offer: Generate personalized retention offers")
        
        return target_ids
        
    except Exception as e:
        logger.error(f"❌ Lambda target attachment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
