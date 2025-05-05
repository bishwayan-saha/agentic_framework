# =============================================================================
# This file defines the agent-related data models used throughout the Agent2Agent (A2A) system.
# It helps desciribing the agent's identity, its features, and how it interacts with other agents
# or clients in a structured and consistent way.
# - Capabilities that an agent supports (e.g., streaming, push notifications)
# - Metadata about the agent itself (AgentCard)
# - Metadata for each skill the agent can perform (AgentSkill)
# =============================================================================

from typing import List

from pydantic import BaseModel


# This class defines what features or protocols the agent support which can be used by A2A clients
#  to understand how to interact with the agent.
class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False
    stateTransitionHistory: bool = False


# This class defines metadata about a single skill that the agent offers.
class AgentSkill(BaseModel):
    id: str
    name: str
    description: str | None = None
    examples: List[str] | None = None
    inputModes: List[str] | None = None
    outputModes: List[str] | None = None


# This class provides core metadata about an agent which can be shared to other agents to describe
# what the agent does, where to reach it, and what capabilities it supports.
class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
    defaultInputModes: List[str] = ["text"]
    defaultOutputModes: List[str] = ["text"]
