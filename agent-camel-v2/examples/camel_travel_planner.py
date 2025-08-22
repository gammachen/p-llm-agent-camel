"""
Travel Planner Example using official CAMEL-AI framework.
使用官方CAMEL-AI框架的旅行规划示例
"""
import os
import logging
from typing import Dict, Any, List
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType, RoleType, OpenAIBackendRole
from camel.configs import ChatGPTConfig
from camel.agents import TaskSpecifyAgent, TaskPlannerAgent
from camel.societies import RolePlaying
from dotenv import load_dotenv

# Load environment variables
# 加载环境变量
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define travel roles
# 定义旅行角色
travel_roles = {
    "travel_planner": {
        "role_name": "TravelPlanner",
        "role_description": "资深旅行规划师，你是一位有20年经验的旅行规划专家，擅长根据用户偏好制定个性化旅行方案"
    },
    "local_guide": {
        "role_name": "LocalGuide", 
        "role_description": "当地向导，你是目的地的本地居民，对当地文化、美食和景点了如指掌"
    },
    "budget_advisor": {
        "role_name": "BudgetAdvisor",
        "role_description": "预算顾问，你是财务规划专家，擅长在保证体验的前提下优化旅行开支"
    }
}

def create_agent(role_type: str, model) -> ChatAgent:
    """
    Create an agent with specified role.
    创建具有指定角色的Agent
    
    Args:
        role_type: Type of role (travel_planner, local_guide, budget_advisor)
               角色类型
        model: Model to use for the agent
           用于Agent的模型
        
    Returns:
        ChatAgent instance
        ChatAgent实例
    """
    print(f"Creating agent with role: {role_type}")
    
    if role_type not in travel_roles:
        logger.warning(f"Unknown role type: {role_type}, defaulting to travel_planner")
        role_type = "travel_planner"
    
    role_info = travel_roles[role_type]
    
    # Create system message (assistant role)
    # 创建系统消息（助手角色）
    assistant_sys_msg = BaseMessage.make_assistant_message(
        role_name=role_info["role_name"],
        content=role_info["role_description"]
    )
    
    # Create the agent
    # 创建Agent
    agent = ChatAgent(
        system_message=assistant_sys_msg,
        model=model,
        token_limit=4096
    )
    
    # Reset the agent
    # 重置Agent
    agent.reset()
    
    print(f"Agent {role_info['role_name']} created successfully")
    return agent

def camel_travel_planning_conversation(user_request: str) -> Dict[str, Any]:
    """
    Travel planning conversation flow using CAMEL-AI framework with RolePlaying society.
    使用CAMEL-AI框架的RolePlaying社会进行旅行规划对话流程
    
    Args:
        user_request: User's travel request
                  用户的旅行请求
        
    Returns:
        Final travel plan response
        最终旅行计划响应
    """
    print(f"Starting CAMEL RolePlaying travel planning conversation for request: {user_request}")
    
    # Setup model
    # 设置模型
    model_platform = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    print(f"Using model platform: {model_platform}")
    
    if model_platform.lower() == "ollama":
        print("Initializing Ollama model")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type=os.getenv("OLLAMA_MODEL_NAME", "llama2"),
            model_config_dict={}
        )
    else:
        # Default to OpenAI
        # 默认使用OpenAI
        print("Initializing OpenAI model")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=2000).as_dict()
        )
    
    # 1. Use TaskSpecifyAgent to clarify the task
    # 1. 使用TaskSpecifyAgent明确任务
    print("Creating task specify agent")
    task_specify_agent = TaskSpecifyAgent(model)
    specified_task = task_specify_agent.run(user_request, meta_dict={"domain": "travel planning"})
    print(f"Specified task: {specified_task}")
    
    # 2. Create RolePlaying society for multi-agent collaboration
    # 2. 创建RolePlaying社会进行多智能体协作
    print("Creating RolePlaying society")
    
    # Define assistant and user roles for the conversation
    # 定义对话中的助手和用户角色
    assistant_role_name = "TravelPlanningExpert"
    user_role_name = "TravelClient"
    
    # Create system messages for both roles
    # 为两个角色创建系统消息
    assistant_sys_msg = BaseMessage.make_assistant_message(
        role_name=assistant_role_name,
        content=(
            "你是一个专业的旅行规划专家团队，包含以下三个专家：\n"
            "1. 旅行规划师：负责制定详细的行程安排和目的地推荐\n"
            "2. 当地向导：提供目的地的文化、美食和景点信息\n"
            "3. 预算顾问：制定合理的旅行预算和费用优化建议\n"
            "请以团队协作的方式，为客户提供全面的旅行规划服务。"
        )
    )
    
    user_sys_msg = BaseMessage.make_user_message(
        role_name=user_role_name,
        content=(
            "你是一位寻求专业旅行规划服务的客户。你会提出具体的旅行需求，"
            "并与旅行专家团队进行互动，以获得最佳的旅行方案。"
        )
    )
    
    # Create the RolePlaying society
    # 创建RolePlaying社会
    role_play_session = RolePlaying(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        assistant_agent_kwargs=dict(
            model=model
        ),
        user_agent_kwargs=dict(
            model=model
        ),
        task_prompt=specified_task,
        with_task_specify=False,  # We already specified the task
        with_task_planner=False,  # We'll handle planning within the conversation
    )
    
    print("Starting RolePlaying conversation")
    
    # Initialize the conversation
    # 初始化对话
    input_msg = role_play_session.init_chat()
    
    # Run the conversation for several turns to get comprehensive planning
    # 运行多轮对话以获得全面的规划
    conversation_history = []
    max_turns = 6  # Limit conversation turns
    
    for turn in range(max_turns):
        print(f"Conversation turn {turn + 1}")
        
        # Get assistant response
        # 获取助手响应
        # Extract messages from ChatAgentResponse objects
        raw_response = role_play_session.step(input_msg)
        assistant_response = raw_response[0]
        user_msg = raw_response[1]

        # Extract the actual message content
        assistant_msg = assistant_response.msgs[0] if hasattr(assistant_response, 'msgs') and assistant_response.msgs else None
        user_message = user_msg.msgs[0] if hasattr(user_msg, 'msgs') and user_msg.msgs else None

        # Update memory with extracted messages
        if hasattr(role_play_session.assistant_agent, 'update_memory') and assistant_msg:
            role_play_session.assistant_agent.update_memory(assistant_msg, OpenAIBackendRole.ASSISTANT)
        if hasattr(role_play_session.user_agent, 'update_memory') and user_message:
            role_play_session.user_agent.update_memory(user_message, OpenAIBackendRole.USER)
        
        if assistant_response.terminated:
            print("Conversation terminated by assistant")
            break
            
        conversation_history.append({
            "turn": turn + 1,
            "assistant": assistant_msg.content if assistant_msg else "",
            "user": user_message.content if user_message else ""
        })
        
        # Use the extracted user message as input for next turn
        # 使用提取的用户消息作为下一轮的输入
        input_msg = user_message
        
        # Break if user message indicates completion
        # 如果用户消息表示完成则中断
        if user_message and ("完成" in user_message.content or "满意" in user_message.content or "谢谢" in user_message.content):
            print("Conversation completed by user satisfaction")
            break
    
    # Extract the final comprehensive response
    # 提取最终的综合响应
    if conversation_history:
        final_response = conversation_history[-1]["assistant"]
    else:
        final_response = "抱歉，无法生成旅行规划。请稍后重试。"
    
    print("CAMEL RolePlaying travel planning conversation completed")
    return {
        "response": final_response,
        "conversation_history": conversation_history,
        "status": "success"
    }

def synthesize_results(results: Dict[str, str], user_request: str) -> str:
    """
    Synthesize results from multiple agents into a final response.
    将多个Agents的结果综合成最终响应
    
    Args:
        results: Results from different agents
             来自不同Agents的结果
        user_request: Original user request
                  原始用户请求
        
    Returns:
        Final synthesized response
        最终综合响应
    """
    print("Synthesizing results from multiple agents")
    
    # Create a summary of all agent responses
    # 创建所有Agent响应的摘要
    response_text = f"根据您的请求 '{user_request}'，我们为您提供以下旅行建议：\n\n"
    
    response_text += "🌍 目的地规划：\n"
    response_text += f"{results.get('destination_planning', '正在为您规划最佳目的地...')}\n\n"
    
    response_text += "📍 当地指南：\n"
    response_text += f"{results.get('local_guidance', '正在为您收集当地信息...')}\n\n"
    
    response_text += "💰 预算规划：\n"
    response_text += f"{results.get('budget_planning', '正在为您制定预算计划...')}\n\n"
    
    print("Results synthesized successfully")
    return response_text

def execute_agent_task(agent: ChatAgent, task_description: str) -> str:
    """
    Execute a task with the given agent.
    使用给定Agent执行任务
    
    Args:
        agent: ChatAgent to execute the task
           执行任务的ChatAgent
        task_description: Description of the task
                    任务描述
        
    Returns:
        Task execution result
        任务执行结果
    """
    print(f"Executing task with agent {agent.role_name}")
    
    # Create user message
    # 创建用户消息
    user_msg = BaseMessage.make_user_message(
        role_name="User",
        content=task_description
    )
    
    # Get response from agent
    # 从Agent获取响应
    print(f"Sending task to agent {agent.role_name}: {task_description}")
    response = agent.step(user_msg)
    print(f"Received response from agent {agent.role_name}")
    
    if response.msgs:
        result_content = response.msgs[0].content
        print(f"Task executed successfully by agent {agent.role_name} with result: {result_content}")
        return result_content
    else:
        logger.warning(f"Failed to execute task with agent {agent.role_name}")
        return f"抱歉，{agent.role_name}无法生成响应，请稍后重试。"

def main():
    """Main function to run the CAMEL-AI travel planner.
    运行CAMEL-AI旅行规划器的主函数"""
    print("Starting CAMEL-AI Multi-Role Travel Planner")
    print("CAMEL-AI Multi-Role Travel Planner")
    print("=" * 40)
    
    # Get user input
    # 获取用户输入
    user_request = input("请输入您的旅行需求: ")
    print(f"User input received: {user_request}")
    
    if not user_request.strip():
        logger.warning("No valid travel request provided")
        print("未提供有效的旅行需求。")
        return
    
    print(f"\n正在处理您的请求: {user_request}")
    print("请稍候...")
    print(f"Processing user request: {user_request}")
    
    # Process the travel request
    # 处理旅行请求
    result = camel_travel_planning_conversation(user_request)
    print("Travel request processing completed")
    
    # Display the result
    # 显示结果
    print("\n" + "=" * 50)
    print("旅行计划结果:")
    print("=" * 50)
    print(result["response"])
    
    # Display detailed results if in debug mode
    # 如果处于调试模式则显示详细结果
    if logger.isEnabledFor(logging.DEBUG):
        print("\n详细信息:")
        for key, value in result["details"].items():
            print(f"- {key}: {value}")
    
    print("Displayed travel plan result to user")


if __name__ == "__main__":
    main()