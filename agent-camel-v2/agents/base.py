"""
Base Agent class for Agent-Camel V2.
Agent-Camel V2的基础Agent类
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
from agents.model_provider import ModelProviderFactory
from memory.manager import MemoryManager
from tools.library import ToolLibrary

# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    系统中所有Agent的基类
    """
    
    def __init__(self, agent_id: str, role: str, model_provider: str = "openai"):
        """
        Initialize the base agent.
        初始化基础Agent
        
        Args:
            agent_id: Unique identifier for the agent
                  Agent的唯一标识符
            role: Role of the agent
                  Agent的角色
            model_provider: Provider of the language model (default: "openai")
                        语言模型提供商（默认："openai"）
        """
        self.agent_id = agent_id
        self.role = role
        self.model_provider = model_provider
        self.memory = MemoryManager(agent_id)
        self.tools = ToolLibrary()
        self.model = ModelProviderFactory.get_provider(model_provider)
        logger.info(f"Initialized agent {agent_id} with role: {role} using {model_provider} model provider")
    
    @abstractmethod
    def process_message(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Process an incoming message.
        处理传入的消息
        
        Args:
            message: Incoming message
                  传入的消息
            session_id: Session identifier
                    会话标识符
            
        Returns:
            Response message
            响应消息
        """
        pass
    
    @abstractmethod
    def plan_next_action(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Plan the next action based on the message and context.
        根据消息和上下文规划下一个动作
        
        Args:
            message: Incoming message
                  传入的消息
            session_id: Session identifier
                    会话标识符
            
        Returns:
            Action plan
            动作计划
        """
        pass
    
    @abstractmethod
    def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Execute the given plan.
        执行给定的计划
        
        Args:
            plan: Action plan to execute
              要执行的动作计划
            session_id: Session identifier
                    会话标识符
            
        Returns:
            Execution result
            执行结果
        """
        pass
    
    def _create_planning_prompt(self, message: Dict[str, Any], context: List[Dict[str, Any]], 
                               tools: List[Dict[str, str]]) -> str:
        """
        Create a prompt for planning the next action.
        创建用于规划下一个动作的提示
        
        Args:
            message: Incoming message
                  传入的消息
            context: Conversation context
                 对话上下文
            tools: Available tools
               可用工具
            
        Returns:
            Planning prompt
            规划提示
        """
        logger.debug(f"Creating planning prompt for agent {self.agent_id}")
        prompt = f"You are {self.role}. "
        prompt += f"Your goal is to help the user with their request.\n\n"
        
        prompt += "Conversation context:\n"
        for i, ctx in enumerate(context[-5:], 1):  # Last 5 messages
            prompt += f"{i}. {ctx.get('content', '')}\n"
        
        prompt += f"\nUser message: {message.get('content', '')}\n\n"
        
        prompt += "Available tools:\n"
        for tool in tools:
            prompt += f"- {tool['name']}: {tool['description']}\n"
        
        prompt += "\nPlease provide your plan in a structured format. You can use available tools if needed."
        logger.debug(f"Planning prompt created for agent {self.agent_id}")
        return prompt
    
    def _generate_response(self, content: str) -> Dict[str, Any]:
        """
        Generate a standardized response.
        生成标准化响应
        
        Args:
            content: Response content
                 响应内容
            
        Returns:
            Standardized response dictionary
            标准化响应字典
        """
        logger.debug(f"Generating response for agent {self.agent_id}")
        response = {
            "role": "assistant",
            "content": content,
            "agent_id": self.agent_id
        }
        logger.debug(f"Response generated for agent {self.agent_id}")
        return response
    
    def _use_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use a tool with given parameters.
        使用给定参数的工具
        
        Args:
            tool_name: Name of the tool to use
                   要使用的工具名称
            parameters: Parameters for the tool
                    工具参数
            
        Returns:
            Tool execution result
            工具执行结果
        """
        logger.info(f"Agent {self.agent_id} using tool: {tool_name}")
        try:
            result = self.tools.execute(tool_name, parameters)
            logger.debug(f"Tool {tool_name} executed successfully by agent {self.agent_id}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name} by agent {self.agent_id}: {str(e)}")
            return {
                "error": f"Error executing tool {tool_name}: {str(e)}"
            }