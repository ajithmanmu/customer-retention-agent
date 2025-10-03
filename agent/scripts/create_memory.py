#!/usr/bin/env python3
"""
Customer Retention Agent - Create and Attach Memory

This script creates AgentCore Memory for conversation persistence
and stores the configuration in SSM Parameter Store.
"""

import boto3
import os
import logging
import json
from botocore.exceptions import ClientError
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
SSM_CLIENT = boto3.client('ssm', region_name=REGION)
MEMORY_CLIENT = MemoryClient(region_name=REGION)

# Parameter Store Paths
MEMORY_ID_PATH = "/customer-retention-agent/memory/id"
MEMORY_ARN_PATH = "/customer-retention-agent/memory/arn"

# Memory Configuration
MEMORY_NAME = "customer_retention_memory"

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
        # Check if parameter already exists
        try:
            SSM_CLIENT.get_parameter(Name=name)
            parameter_exists = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                parameter_exists = False
            else:
                raise
        
        if parameter_exists and overwrite:
            # Update existing parameter without tags
            SSM_CLIENT.put_parameter(
                Name=name,
                Value=value,
                Type='String',
                Overwrite=True,
                Description=description
            )
            logger.info(f"✅ Updated SSM parameter: {name}")
        else:
            # Create new parameter with tags
            SSM_CLIENT.put_parameter(
                Name=name,
                Value=value,
                Type='String',
                Overwrite=False,
                Description=description,
                Tags=[{'Key': 'project', 'Value': 'customer-retention-agent'}, {'Key': 'component', 'Value': 'memory'}]
            )
            logger.info(f"✅ Created SSM parameter: {name}")
            
    except ClientError as e:
        logger.error(f"Error storing SSM parameter '{name}': {e}")
        raise

def create_agentcore_memory() -> tuple[str, str]:
    """Create or get the AgentCore Memory with strategies."""
    try:
        # First, check if memory already exists in SSM
        try:
            memory_id = get_ssm_parameter(MEMORY_ID_PATH)
            # Verify memory exists by getting it
            memory_info = MEMORY_CLIENT.get_memory(memoryId=memory_id)
            logger.info(f"✅ AgentCore Memory '{MEMORY_NAME}' already exists: {memory_id}")
            return memory_id, memory_info['memoryArn']
        except:
            # SSM parameter doesn't exist, check if memory exists in AWS
            pass

        # Check if memory exists in AWS by listing memories
        try:
            logger.info("Checking for existing memories in AWS...")
            memories = MEMORY_CLIENT.list_memories()
            logger.info(f"Found {len(memories)} existing memories")
            
            for memory in memories:
                memory_id = memory.get('id')
                memory_name = memory.get('name')
                logger.info(f"Checking memory: {memory_name} (ID: {memory_id})")
                
                # Check by name or by ID pattern (since we know our memory ID pattern)
                if (memory_name == MEMORY_NAME or 
                    (memory_id and memory_id.startswith('customer_retention_memory-'))):
                    memory_arn = memory.get('arn')
                    logger.info(f"✅ Found existing AgentCore Memory: {memory_id}")
                    
                    # Store in SSM for future use
                    put_ssm_parameter(MEMORY_ID_PATH, memory_id, "AgentCore Memory ID for Customer Retention Agent")
                    put_ssm_parameter(MEMORY_ARN_PATH, memory_arn, "AgentCore Memory ARN for Customer Retention Agent")
                    
                    return memory_id, memory_arn
            
            logger.info(f"No existing memory found with name '{MEMORY_NAME}'")
        except Exception as e:
            logger.error(f"Could not list existing memories: {e}")
            # If we can't list memories, we'll try to create and let AWS handle the duplicate error

        # If we get here, try to create the memory
        # But first, let's try to find the existing memory by the known ID from previous run
        known_memory_id = "customer_retention_memory-3rXoaL9CjX"
        try:
            logger.info(f"Trying to find existing memory by known ID: {known_memory_id}")
            memory_info = MEMORY_CLIENT.get_memory(memoryId=known_memory_id)
            memory_id = memory_info['id']
            memory_arn = memory_info['arn']
            logger.info(f"✅ Found existing AgentCore Memory by ID: {memory_id}")
            
            # Store in SSM for future use
            put_ssm_parameter(MEMORY_ID_PATH, memory_id, "AgentCore Memory ID for Customer Retention Agent")
            put_ssm_parameter(MEMORY_ARN_PATH, memory_arn, "AgentCore Memory ARN for Customer Retention Agent")
            
            return memory_id, memory_arn
        except Exception as e:
            logger.info(f"Could not find memory by known ID: {e}")

        # If we get here, memory doesn't exist, create it
        logger.info(f"Creating AgentCore Memory: {MEMORY_NAME}")
        logger.info("This will take 2-3 minutes as AWS sets up managed services...")
        logger.info("Setting up:")
        logger.info("• Managed vector databases for semantic search")
        logger.info("• Memory extraction pipelines")
        logger.info("• Secure, multi-tenant storage")
        logger.info("• Namespace isolation for customer data")

        # Define memory strategies for customer retention
        strategies = [
            {
                StrategyType.USER_PREFERENCE.value: {
                    "name": "CustomerRetentionPreferences",
                    "description": "Captures customer preferences, churn risk patterns, and retention behaviors",
                    "namespaces": ["retention/customer/{actorId}/preferences"],
                }
            },
            {
                StrategyType.SEMANTIC.value: {
                    "name": "CustomerRetentionSemantic",
                    "description": "Stores factual information about customer interactions, issues, and retention strategies",
                    "namespaces": ["retention/customer/{actorId}/semantic"],
                }
            },
        ]

        # Create memory with strategies using create_memory_and_wait
        response = MEMORY_CLIENT.create_memory_and_wait(
            name=MEMORY_NAME,
            description="Memory for Customer Retention Agent to persist conversation context and customer interactions",
            strategies=strategies,
            event_expiry_days=90,  # Memories expire after 90 days
        )

        memory_id = response["id"]
        memory_arn = response["arn"]
        logger.info(f"✅ AgentCore Memory '{MEMORY_NAME}' created with ID: {memory_id}, ARN: {memory_arn}")

        # Store in SSM
        put_ssm_parameter(MEMORY_ID_PATH, memory_id, "AgentCore Memory ID for Customer Retention Agent")
        put_ssm_parameter(MEMORY_ARN_PATH, memory_arn, "AgentCore Memory ARN for Customer Retention Agent")

        return memory_id, memory_arn

    except Exception as e:
        logger.error(f"Error creating/getting AgentCore Memory: {e}")
        raise

def test_memory_connection(memory_id: str) -> bool:
    """Test the memory connection by creating a test event."""
    try:
        logger.info(f"Testing memory connection with ID: {memory_id}")
        
        # Test memory operations using the proper MemoryClient methods
        try:
            # Test creating an event (this is the proper way to test memory)
            test_customer_id = "test-customer-001"
            test_session_id = "test-session-001"
            
            # Create a test event with sample customer retention conversation
            test_messages = [
                ("I'm considering switching to a competitor because of high prices", "USER"),
                ("I understand your concern about pricing. Let me check your current plan and see what options we have to help reduce your costs.", "ASSISTANT"),
                ("I prefer premium plans with international calling", "USER"),
                ("Based on your preference for premium plans with international calling, I can offer you a retention discount of 20% for 6 months.", "ASSISTANT")
            ]
            
            MEMORY_CLIENT.create_event(
                memory_id=memory_id,
                actor_id=test_customer_id,
                session_id=test_session_id,
                messages=test_messages
            )
            logger.info("✅ Memory event creation test passed")
            
            # Test retrieving memories (wait a bit for processing)
            import time
            time.sleep(5)  # Give memory time to process
            
            # Test retrieving preferences
            preferences = MEMORY_CLIENT.retrieve_memories(
                memory_id=memory_id,
                namespace=f"retention/customer/{test_customer_id}/preferences",
                query="customer preferences and retention needs",
                top_k=3
            )
            logger.info(f"✅ Memory preferences retrieval test passed - found {len(preferences)} preference memories")
            
            # Test retrieving semantic memories
            semantic = MEMORY_CLIENT.retrieve_memories(
                memory_id=memory_id,
                namespace=f"retention/customer/{test_customer_id}/semantic",
                query="customer interaction and retention conversation",
                top_k=3
            )
            logger.info(f"✅ Memory semantic retrieval test passed - found {len(semantic)} semantic memories")
            
            return True
            
        except Exception as test_error:
            logger.error(f"Memory test failed: {test_error}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing memory connection: {e}")
        return False

if __name__ == "__main__":
    try:
        logger.info("🚀 Starting AgentCore Memory setup...")
        
        # 1. Create or get AgentCore Memory
        memory_id, memory_arn = create_agentcore_memory()
        
        # 2. Test memory connection
        if test_memory_connection(memory_id):
            logger.info("🎉 AgentCore Memory setup complete and tested!")
            logger.info(f"Memory ID: {memory_id}")
            logger.info(f"Memory ARN: {memory_arn}")
            logger.info("\nNext steps:")
            logger.info("1. Update agent to use this memory for conversation persistence")
            logger.info("2. Test the agent with memory integration")
        else:
            logger.error("❌ Memory setup completed but tests failed")
            logger.info("Memory ID and ARN are available, but functionality may be limited")
            logger.info(f"Memory ID: {memory_id}")
            logger.info(f"Memory ARN: {memory_arn}")

    except Exception as e:
        logger.error(f"❌ AgentCore Memory setup failed: {e}")
