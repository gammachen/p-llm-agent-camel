"""
Task Coordinator for Agent-Camel V2.
Agent-Camel V2的任务协调器
"""
from typing import Dict, Any, List, Optional
import uuid
import logging
from agents.base import BaseAgent

# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TravelPlannerAgent(BaseAgent):
    """Travel planner agent implementation.
    旅行规划Agent实现"""
    
    def __init__(self, agent_id: str, model_provider: str = "openai"):
        super().__init__(
            agent_id=agent_id,
            role="资深旅行规划师，你是一位有20年经验的旅行规划专家，擅长根据用户偏好制定个性化旅行方案",
            model_provider=model_provider
        )
    
    def process_message(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Process an incoming message.
        处理传入的消息"""
        print(f"TravelPlannerAgent {self.agent_id} processing message in session {session_id}")
        # 1. Update context
        # 1. 更新上下文
        print(f"Updating context for session {session_id}")
        self.memory.update_context(session_id, message)
        
        # 2. Plan next action
        # 2. 规划下一个动作
        print(f"Planning next action for session {session_id}")
        plan = self.plan_next_action(message, session_id)
        print(f"Planned action for session {session_id}: {plan.get('action', 'unknown')}")
        
        # 3. Execute plan
        # 3. 执行计划
        print(f"Executing plan for session {session_id}")
        response = self.execute_plan(plan, session_id)
        print(f"Executed plan for session {session_id}")
        
        # 4. Store interaction
        # 4. 存储交互记录
        print(f"Storing interaction for session {session_id}")
        self.memory.store_interaction(session_id, message, response, plan)
        print(f"Stored interaction for session {session_id}")
        
        return response
    
    def plan_next_action(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Plan the next action.
        规划下一个动作"""
        print(f"TravelPlannerAgent {self.agent_id} planning next action for session {session_id}")
        context = self.memory.get_context(session_id)
        tools = self.tools.get_available_tools()
        print(f"TravelPlannerAgent Retrieved context with {len(context)} messages and {len(tools)} tools for session {session_id}")
        
        prompt = self._create_planning_prompt(message, context, tools)
        print(f"TravelPlannerAgent Generated planning prompt for session {session_id}")
        plan_text = self.model.generate(prompt, max_tokens=300)
        print(f"TravelPlannerAgent Generated plan text for session {session_id}")
        
        # Try to parse the plan to determine if tools should be used
        # 尝试解析计划以确定是否应使用工具
        if "search" in plan_text.lower() or "search" in message.get("content", "").lower():
            return {
                "action": "use_tool",
                "tool_name": "search",
                "parameters": {
                    "query": message.get("content", "")
                }
            }
        elif "calculate" in plan_text.lower() or "budget" in plan_text.lower():
            return {
                "action": "use_tool",
                "tool_name": "calculator",
                "parameters": {
                    "expression": "placeholder calculation"
                }
            }
        else:
            return {
                "action": "respond",
                "content": plan_text
            }
    
    def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute the plan.
        执行计划"""
        print(f"TravelPlannerAgent {self.agent_id} executing plan for session {session_id}")
        if plan['action'] == 'respond':
            print(f"TravelPlannerAgent Responding with content for session {session_id}")
            response = self._generate_response(plan['content'])
            print(f"Generated response for session {session_id}")
            return response
        elif plan['action'] == 'use_tool':
            print(f"TravelPlannerAgent Using tool {plan['tool_name']} for session {session_id}")
            tool_result = self._use_tool(plan['tool_name'], plan.get('parameters', {}))
            # Generate a response based on tool result
            # 根据工具结果生成响应
            response_content = f"工具执行结果: {tool_result.get('result', '执行完成')}"
            response = self._generate_response(response_content)
            print(f"TravelPlannerAgent Generated response based on tool result for session {session_id}")
            return response
        else:
            logger.warning(f"Unknown action {plan['action']} for session {session_id}")
            return self._generate_response("抱歉，我无法执行该操作。")


class LocalGuideAgent(BaseAgent):
    """Local guide agent implementation.
    当地向导Agent实现"""
    
    def __init__(self, agent_id: str, model_provider: str = "openai"):
        super().__init__(
            agent_id=agent_id,
            role="当地向导，你是目的地的本地居民，对当地文化、美食和景点了如指掌",
            model_provider=model_provider
        )
    
    def process_message(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Process an incoming message.
        处理传入的消息"""
        print(f"LocalGuideAgent {self.agent_id} processing message in session {session_id}")
        # 1. Update context
        # 1. 更新上下文
        print(f"LocalGuideAgent Updating context for session {session_id}")
        self.memory.update_context(session_id, message)
        
        # 2. Plan next action
        # 2. 规划下一个动作
        print(f"LocalGuideAgent Planning next action for session {session_id}")
        plan = self.plan_next_action(message, session_id)
        print(f"LocalGuideAgent Planned action for session {session_id}: {plan.get('action', 'unknown')}")
        
        # 3. Execute plan
        # 3. 执行计划
        print(f"LocalGuideAgent Executing plan for session {session_id}")
        response = self.execute_plan(plan, session_id)
        print(f"LocalGuideAgent Executed plan for session {session_id}")
        
        # 4. Store interaction
        # 4. 存储交互记录
        print(f"LocalGuideAgent Storing interaction for session {session_id}")
        self.memory.store_interaction(session_id, message, response, plan)
        print(f"LocalGuideAgent Stored interaction for session {session_id}")
        
        return response
    
    def plan_next_action(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Plan the next action.
        规划下一个动作"""
        print(f"LocalGuideAgent {self.agent_id} planning next action for session {session_id}")
        context = self.memory.get_context(session_id)
        tools = self.tools.get_available_tools()
        print(f"LocalGuideAgent Retrieved context with {len(context)} messages and {len(tools)} tools for session {session_id}")
        
        prompt = self._create_planning_prompt(message, context, tools)
        print(f"LocalGuideAgent Generated planning prompt for session {session_id}")
        plan_text = self.model.generate(prompt, max_tokens=300)
        print(f"LocalGuideAgent Generated plan text for session {session_id}")
        
        # Try to parse the plan to determine if tools should be used
        # 尝试解析计划以确定是否应使用工具
        if "search" in plan_text.lower() or "search" in message.get("content", "").lower():
            return {
                "action": "use_tool",
                "tool_name": "search",
                "parameters": {
                    "query": message.get("content", "")
                }
            }
        else:
            return {
                "action": "respond",
                "content": plan_text
            }
    
    def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute the plan.
        执行计划"""
        print(f"LocalGuideAgent {self.agent_id} executing plan for session {session_id}")
        if plan['action'] == 'respond':
            print(f"Responding with content for session {session_id}")
            response = self._generate_response(plan['content'])
            print(f"Generated response for session {session_id}")
            return response
        elif plan['action'] == 'use_tool':
            print(f"Using tool {plan['tool_name']} for session {session_id}")
            tool_result = self._use_tool(plan['tool_name'], plan.get('parameters', {}))
            # Generate a response based on tool result
            # 根据工具结果生成响应
            response_content = f"工具执行结果: {tool_result.get('result', '执行完成')}"
            response = self._generate_response(response_content)
            print(f"Generated response based on tool result for session {session_id}")
            return response
        else:
            logger.warning(f"Unknown action {plan['action']} for session {session_id}")
            return self._generate_response("抱歉，我无法执行该操作.")


class BudgetAdvisorAgent(BaseAgent):
    """Budget advisor agent implementation.
    预算顾问Agent实现"""
    
    def __init__(self, agent_id: str, model_provider: str = "openai"):
        super().__init__(
            agent_id=agent_id,
            role="预算顾问，你是财务规划专家，擅长在保证体验的前提下优化旅行开支",
            model_provider=model_provider
        )
    
    def process_message(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Process an incoming message.
        处理传入的消息"""
        print(f"BudgetAdvisorAgent {self.agent_id} processing message in session {session_id}")
        # 1. Update context
        # 1. 更新上下文
        print(f"BudgetAdvisorAgent Updating context for session {session_id}")
        self.memory.update_context(session_id, message)
        
        # 2. Plan next action
        # 2. 规划下一个动作
        print(f"BudgetAdvisorAgent 规划 next action for session {session_id}")
        plan = self.plan_next_action(message, session_id)
        print(f"BudgetAdvisorAgent Planned action for session {session_id}: {plan.get('action', 'unknown')}")
        
        # 3. Execute plan
        # 3. 执行计划
        print(f"BudgetAdvisorAgent Executing plan for session {session_id}")
        response = self.execute_plan(plan, session_id)
        print(f"BudgetAdvisorAgent Executed plan for session {session_id}")
        
        # 4. Store interaction
        # 4. 存储交互记录
        print(f"BudgetAdvisorAgent Storing interaction for session {session_id}")
        self.memory.store_interaction(session_id, message, response, plan)
        print(f"BudgetAdvisorAgent Stored interaction for session {session_id}")
        
        return response
    
    def plan_next_action(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Plan the next action.
        规划下一个动作"""
        print(f"BudgetAdvisorAgent {self.agent_id} planning next action for session {session_id}")
        context = self.memory.get_context(session_id)
        tools = self.tools.get_available_tools()
        print(f"BudgetAdvisorAgent Retrieved context with {len(context)} messages and {len(tools)} tools for session {session_id}")
        
        prompt = self._create_planning_prompt(message, context, tools)
        print(f"BudgetAdvisorAgent Generated planning prompt for session {session_id}")
        plan_text = self.model.generate(prompt, max_tokens=300)
        print(f"BudgetAdvisorAgent Generated plan text for session {session_id}")
        
        # Try to parse the plan to determine if tools should be used
        # 尝试解析计划以确定是否应使用工具
        if "calculate" in plan_text.lower() or "budget" in message.get("content", "").lower():
            return {
                "action": "use_tool",
                "tool_name": "calculator",
                "parameters": {
                    "expression": "placeholder calculation for " + message.get("content", "")
                }
            }
        elif "search" in plan_text.lower():
            return {
                "action": "use_tool",
                "tool_name": "search",
                "parameters": {
                    "query": "budget information for " + message.get("content", "")
                }
            }
        else:
            return {
                "action": "respond",
                "content": plan_text
            }
    
    def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute the plan.
        执行计划"""
        print(f"BudgetAdvisorAgent {self.agent_id} executing plan for session {session_id}")
        if plan['action'] == 'respond':
            print(f"Responding with content for session {session_id}")
            response = self._generate_response(plan['content'])
            print(f"Generated response for session {session_id}")
            return response
        elif plan['action'] == 'use_tool':
            print(f"Using tool {plan['tool_name']} for session {session_id}")
            tool_result = self._use_tool(plan['tool_name'], plan.get('parameters', {}))
            # Generate a response based on tool result
            # 根据工具结果生成响应
            response_content = f"工具执行结果: {tool_result.get('result', '执行完成')}"
            response = self._generate_response(response_content)
            print(f"Generated response based on tool result for session {session_id}")
            return response
        else:
            logger.warning(f"Unknown action {plan['action']} for session {session_id}")
            return self._generate_response("抱歉，我无法执行该操作.")


class TaskCoordinator:
    """
    Task coordinator responsible for assigning tasks and managing agent collaboration.
    任务协调器，负责分配任务和管理Agent协作
    """
    
    def __init__(self):
        """Initialize the task coordinator.
        初始化任务协调器"""
        self.agents: Dict[str, BaseAgent] = {}  # Registered agents
                                    # 已注册的Agents
        self.task_queue: List[Dict[str, Any]] = []   # Task queue
                                         # 任务队列
        self.sessions: Dict[str, Dict[str, Any]] = {}  # Session management
                                           # 会话管理
        print("Initialized TaskCoordinator")
    
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str], 
                      model_provider: str = "openai") -> None:
        """
        Register an agent with the coordinator.
        向协调器注册一个Agent
        
        Args:
            agent_id: Unique identifier for the agent
                  Agent的唯一标识符
            agent_type: Type of the agent
                    Agent的类型
            capabilities: List of agent capabilities
                      Agent的能力列表
            model_provider: Model provider for the agent
                        Agent的模型提供商
        """
        print(f"Registering agent {agent_id} of type {agent_type}")
        # Create agent instance based on type
        # 根据类型创建Agent实例
        if agent_type == "travel_planner":
            agent = TravelPlannerAgent(agent_id, model_provider)
            print(f"Created TravelPlannerAgent {agent_id}")
        elif agent_type == "local_guide":
            agent = LocalGuideAgent(agent_id, model_provider)
            print(f"Created LocalGuideAgent {agent_id}")
        elif agent_type == "budget_advisor":
            agent = BudgetAdvisorAgent(agent_id, model_provider)
            print(f"Created BudgetAdvisorAgent {agent_id}")
        else:
            # Default to travel planner
            # 默认使用旅行规划师
            agent = TravelPlannerAgent(agent_id, model_provider)
            logger.warning(f"Unknown agent type {agent_type}, defaulting to TravelPlannerAgent")
        
        self.agents[agent_id] = agent
        print(f"Registered agent {agent_id} of type {agent_type}")
    
    def assign_task(self, task: Dict[str, Any], requirements: Dict[str, Any]) -> Optional[str]:
        """
        Assign a task to a suitable agent.
        将任务分配给合适的Agent
        
        Args:
            task: Task to be assigned
              要分配的任务
            requirements: Task requirements
                      任务需求
            
        Returns:
            Agent ID if successfully assigned, None otherwise
            如果成功分配则返回Agent ID，否则返回None
        """
        print(f"Assigning task of type {task.get('type', 'unknown')}")
        suitable_agents = self._find_suitable_agents(requirements)
        print(f"Found {len(suitable_agents)} suitable agents")
        if not suitable_agents:
            # If no suitable agents found, we might need to create a new one
            # 如果没有找到合适的Agent，我们可能需要创建一个新的
            # For now, we'll return None
            # 目前，我们将返回None
            logger.warning("No suitable agents found for task")
            return None
        
        # Select the best agent for the task
        # 为任务选择最佳的Agent
        selected_agent = self._select_best_agent(suitable_agents, task)
        print(f"Selected agent {selected_agent} for task")
        return self._dispatch_task(selected_agent, task)
    
    def _find_suitable_agents(self, requirements: Dict[str, Any]) -> List[str]:
        """
        Find agents that match the given requirements.
        查找符合给定需求的Agents
        
        Args:
            requirements: Task requirements
                      任务需求
            
        Returns:
            List of suitable agent IDs
            合适的Agent ID列表
        """
        print(f"Finding suitable agents for requirements: {requirements}")
        suitable_agents = []
        for agent_id, agent in self.agents.items():
            # For simplicity, we're just checking if the agent exists
            # 为简单起见，我们只是检查Agent是否存在
            # In a more complex implementation, we would check capabilities
            # 在更复杂的实现中，我们会检查能力
            suitable_agents.append(agent_id)
        print(f"Found suitable agents: {suitable_agents}")
        return suitable_agents
    
    def _matches_requirements(self, capabilities: List[str], requirements: Dict[str, Any]) -> bool:
        """
        Check if agent capabilities match the requirements.
        检查Agent能力是否符合需求
        
        Args:
            capabilities: Agent capabilities
                      Agent能力
            requirements: Task requirements
                      任务需求
            
        Returns:
            True if capabilities match requirements, False otherwise
            如果能力符合需求则返回True，否则返回False
        """
        print(f"Checking if capabilities {capabilities} match requirements {requirements}")
        # Simple implementation - check if any required capability is in agent capabilities
        # 简单实现 - 检查是否有任何所需能力在Agent能力中
        required_capabilities = requirements.get('capabilities', [])
        if not required_capabilities:
            print("No specific capabilities required")
            return True
            
        match = any(cap in capabilities for cap in required_capabilities)
        print(f"Capabilities match: {match}")
        return match
    
    def _select_best_agent(self, suitable_agents: List[str], task: Dict[str, Any]) -> str:
        """
        Select the best agent from suitable agents.
        从合适的Agents中选择最佳的Agent
        
        Args:
            suitable_agents: List of suitable agent IDs
                         合适的Agent ID列表
            task: Task to be assigned
              要分配的任务
            
        Returns:
            Selected agent ID
            选定的Agent ID
        """
        print(f"Selecting best agent from {suitable_agents} for task")
        # Simple implementation - select the first suitable agent
        # 简单实现 - 选择第一个合适的Agent
        # In a more complex system, this could consider agent workload, expertise, etc.
        # 在更复杂的系统中，这可以考虑Agent的工作负载、专业等
        selected = suitable_agents[0] if suitable_agents else None
        print(f"Selected agent: {selected}")
        return selected
    
    def _dispatch_task(self, agent_id: str, task: Dict[str, Any]) -> str:
        """
        Dispatch a task to an agent.
        向Agent分发任务
        
        Args:
            agent_id: Agent ID to dispatch task to
                  要分发任务的Agent ID
            task: Task to dispatch
              要分发的任务
            
        Returns:
            Agent ID
            Agent ID
        """
        print(f"Dispatching task to agent {agent_id}")
        # Add task to queue
        # 将任务添加到队列
        task_entry = {
            'id': str(uuid.uuid4()),
            'agent_id': agent_id,
            'task': task,
            'status': 'assigned'
        }
        self.task_queue.append(task_entry)
        print(f"Task added to queue with ID {task_entry['id']}")
        
        return agent_id
    
    def execute_task(self, agent_id: str, task: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Execute a task with a specific agent.
        使用特定Agent执行任务
        
        Args:
            agent_id: ID of the agent to execute the task
                  执行任务的Agent ID
            task: Task to execute
              要执行的任务
            session_id: Session identifier
                    会话标识符
            
        Returns:
            Task execution result
            任务执行结果
        """
        print(f"Executing task with agent {agent_id} in session {session_id}")
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return {
                "error": f"Agent {agent_id} not found"
            }
        
        agent = self.agents[agent_id]
        print(f"Found agent {agent_id} for task execution")
        
        # Create a message from the task
        # 从任务创建消息
        message = {
            "role": "user",
            "content": task.get("description", "Please help with this task")
        }
        print(f"Created message from task: {message['content']}")
        
        # Process the message with the agent
        # 使用Agent处理消息
        print(f"Processing message with agent {agent_id}")
        result = agent.process_message(message, session_id)
        print(f"Task execution completed with agent {agent_id} in session {session_id}")
        
        return {
            "agent_id": agent_id,
            "task_type": task.get("type"),
            "result": result.get("content", ""),
            "details": result
        }
    
    def analyze_request(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze user request and break it down into tasks.
        分析用户请求并将其分解为任务
        
        Args:
            user_request: User's request
                      用户的请求
            
        Returns:
            Task analysis results
            任务分析结果
        """
        print(f"Analyzing user request: {user_request}")
        # For now, we'll create a simple task structure
        # 目前，我们将创建一个简单的任务结构
        # In a real implementation, we would use an LLM to analyze the request
        # 在实际实现中，我们会使用LLM来分析请求
        result = {
            "tasks": [
                {
                    "type": "destination_planning",
                    "description": f"Plan travel destinations for: {user_request}",
                    "requirements": {
                        "capabilities": ["destination_recommendation"]
                    }
                },
                {
                    "type": "local_guidance",
                    "description": f"Provide local guidance for: {user_request}",
                    "requirements": {
                        "capabilities": ["local_knowledge"]
                    }
                },
                {
                    "type": "budget_planning",
                    "description": f"Create a budget plan for: {user_request}",
                    "requirements": {
                        "capabilities": ["cost_estimation"]
                    }
                }
            ]
        }
        print(f"Analysis result: {result}")
        return result