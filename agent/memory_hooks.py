#!/usr/bin/env python3
"""
Customer Retention Agent - Memory Hooks

This module provides memory hooks for conversation persistence and customer context awareness.
"""

import uuid
import logging
from bedrock_agentcore.memory import MemoryClient
from strands.hooks import AfterInvocationEvent, MessageAddedEvent, HookProvider, HookRegistry

logger = logging.getLogger(__name__)

class CustomerRetentionMemoryHooks(HookProvider):
    """Memory hooks for Customer Retention Agent"""
    
    def __init__(self, memory_id: str, customer_id: str = None, session_id: str = None, region: str = "us-east-1"):
        self.memory_id = memory_id
        self.customer_id = customer_id or "default-customer"
        self.session_id = session_id or str(uuid.uuid4())
        self.memory_client = MemoryClient(region_name=region)
        
        # Get memory strategies and namespaces
        try:
            strategies = self.memory_client.get_memory_strategies(self.memory_id)
            self.namespaces = {
                strategy["type"]: strategy["namespaces"][0]
                for strategy in strategies
            }
            logger.info(f"✅ Memory namespaces loaded: {list(self.namespaces.keys())}")
        except Exception as e:
            logger.error(f"Error loading memory strategies: {e}")
            self.namespaces = {
                "USER_PREFERENCE": "retention/customer/{actorId}/preferences",
                "SEMANTIC": "retention/customer/{actorId}/semantic"
            }
    
    def retrieve_customer_context(self, event: MessageAddedEvent):
        """Retrieve customer context before processing retention query"""
        messages = event.agent.messages
        if (
            messages[-1]["role"] == "user"
            and "toolResult" not in messages[-1]["content"][0]
        ):
            user_query = messages[-1]["content"][0]["text"]

            try:
                all_context = []

                for context_type, namespace in self.namespaces.items():
                    # Retrieve customer context from each namespace
                    memories = self.memory_client.retrieve_memories(
                        memory_id=self.memory_id,
                        namespace=namespace.format(actorId=self.customer_id),
                        query=user_query,
                        top_k=3,
                    )
                    # Format memories into context strings
                    for memory in memories:
                        if isinstance(memory, dict):
                            content = memory.get("content", {})
                            if isinstance(content, dict):
                                text = content.get("text", "").strip()
                                if text:
                                    all_context.append(
                                        f"[{context_type.upper()}] {text}"
                                    )

                # Inject customer context into the query
                if all_context:
                    context_text = "\n".join(all_context)
                    original_text = messages[-1]["content"][0]["text"]
                    messages[-1]["content"][0][
                        "text"
                    ] = f"Customer Context:\n{context_text}\n\n{original_text}"
                    logger.info(f"Retrieved {len(all_context)} customer context items")

            except Exception as e:
                logger.error(f"Failed to retrieve customer context: {e}")

    def save_retention_interaction(self, event: AfterInvocationEvent):
        """Save customer retention interaction after agent response"""
        try:
            messages = event.agent.messages
            if len(messages) >= 2 and messages[-1]["role"] == "assistant":
                # Get last customer query and agent response
                customer_query = None
                agent_response = None

                for msg in reversed(messages):
                    if msg["role"] == "assistant" and not agent_response:
                        agent_response = msg["content"][0]["text"]
                    elif (
                        msg["role"] == "user"
                        and not customer_query
                        and "toolResult" not in msg["content"][0]
                    ):
                        customer_query = msg["content"][0]["text"]
                        break

                if customer_query and agent_response:
                    # Save the retention interaction
                    self.memory_client.create_event(
                        memory_id=self.memory_id,
                        actor_id=self.customer_id,
                        session_id=self.session_id,
                        messages=[
                            (customer_query, "USER"),
                            (agent_response, "ASSISTANT"),
                        ],
                    )
                    logger.info("Saved retention interaction to memory")

        except Exception as e:
            logger.error(f"Failed to save retention interaction: {e}")

    def register_hooks(self, registry: HookRegistry) -> None:
        """Register customer retention memory hooks"""
        registry.add_callback(MessageAddedEvent, self.retrieve_customer_context)
        registry.add_callback(AfterInvocationEvent, self.save_retention_interaction)
        logger.info("Customer retention memory hooks registered")
    
    def get_customer_context(self):
        """Get customer-specific context from memory"""
        try:
            all_context = []
            
            for context_type, namespace in self.namespaces.items():
                memories = self.memory_client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=namespace.format(actorId=self.customer_id),
                    query="customer preferences and retention history",
                    top_k=5
                )
                
                for memory in memories:
                    if isinstance(memory, dict):
                        content = memory.get("content", {})
                        if isinstance(content, dict):
                            text = content.get("text", "").strip()
                            if text:
                                all_context.append(f"[{context_type.upper()}] {text}")
            
            return all_context
        except Exception as e:
            logger.error(f"Error getting customer context: {e}")
            return []
