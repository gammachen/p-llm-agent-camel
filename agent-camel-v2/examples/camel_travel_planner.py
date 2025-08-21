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
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig
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
    logger.info(f"Creating agent with role: {role_type}")
    
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
        assistant_sys_msg,
        model=model,
        token_limit=4096
    )
    
    # Reset the agent
    # 重置Agent
    agent.reset()
    
    logger.debug(f"Agent {role_info['role_name']} created successfully")
    return agent

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
    logger.info(f"Executing task with agent {agent.role_name}")
    
    # Create user message
    # 创建用户消息
    user_msg = BaseMessage.make_user_message(
        role_name="User",
        content=task_description
    )
    
    # Get response from agent
    # 从Agent获取响应
    logger.debug(f"Sending task to agent {agent.role_name}: {task_description}")
    response = agent.step(user_msg)
    logger.debug(f"Received response from agent {agent.role_name}")
    
    if response.msgs:
        result_content = response.msgs[0].content
        logger.info(f"Task executed successfully by agent {agent.role_name} with result: {result_content}")
        return result_content
    else:
        logger.warning(f"Failed to execute task with agent {agent.role_name}")
        return f"抱歉，{agent.role_name}无法生成响应，请稍后重试。"

def camel_travel_planning_conversation(user_request: str) -> Dict[str, Any]:
    """
    Travel planning conversation flow using CAMEL-AI framework with multiple roles.
    使用CAMEL-AI框架的多角色旅行规划对话流程
    
    Args:
        user_request: User's travel request
                  用户的旅行请求
        
    Returns:
        Final travel plan response
        最终旅行计划响应
    """
    logger.info(f"Starting multi-role travel planning conversation for request: {user_request}")
    
    # Setup model
    # 设置模型
    model_platform = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    logger.debug(f"Using model platform: {model_platform}")
    
    if model_platform.lower() == "ollama":
        logger.debug("Initializing Ollama model")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type=os.getenv("OLLAMA_MODEL_NAME", "llama2"),
            model_config_dict={}
        )
    else:
        # Default to OpenAI
        # 默认使用OpenAI
        logger.debug("Initializing OpenAI model")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=2000).as_dict()
        )
    
    # Create agents for different roles
    # 为不同角色创建Agent
    logger.debug("Creating agents for different roles")
    travel_planner_agent = create_agent("travel_planner", model)
    local_guide_agent = create_agent("local_guide", model)
    budget_advisor_agent = create_agent("budget_advisor", model)
    
    # Break down the user request into subtasks
    # 将用户请求分解为子任务
    logger.info("Breaking down user request into subtasks")
    subtasks = {
        "destination_planning": f"请根据用户需求'{user_request}'规划旅行目的地，包括推荐地点和行程安排。",
        "local_guidance": f"针对用户需求'{user_request}'，提供目的地的当地文化和美食建议。",
        "budget_planning": f"根据用户需求'{user_request}'，制定旅行预算计划，包括各项费用估算。"
    }
    
    # Execute tasks with respective agents
    # 使用相应的Agent执行任务
    logger.info("Executing subtasks with respective agents")
    results = {}
    
    results["destination_planning"] = execute_agent_task(
        travel_planner_agent, 
        subtasks["destination_planning"]
    )
    
    results["local_guidance"] = execute_agent_task(
        local_guide_agent, 
        subtasks["local_guidance"]
    )
    
    results["budget_planning"] = execute_agent_task(
        budget_advisor_agent, 
        subtasks["budget_planning"]
    )
    
    # Synthesize results from all agents
    # 综合所有Agent的结果
    logger.info("Synthesizing results from all agents")
    final_response = synthesize_results(results, user_request)
    
    logger.info("Multi-role travel planning conversation completed")
    return {
        "response": final_response,
        "details": results,
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
    logger.debug("Synthesizing results from multiple agents")
    
    # Create a summary of all agent responses
    # 创建所有Agent响应的摘要
    response_text = f"根据您的请求 '{user_request}'，我们为您提供以下旅行建议：\n\n"
    
    response_text += "🌍 目的地规划：\n"
    response_text += f"{results.get('destination_planning', '正在为您规划最佳目的地...')}\n\n"
    
    response_text += "📍 当地指南：\n"
    response_text += f"{results.get('local_guidance', '正在为您收集当地信息...')}\n\n"
    
    response_text += "💰 预算规划：\n"
    response_text += f"{results.get('budget_planning', '正在为您制定预算计划...')}\n\n"
    
    logger.debug("Results synthesized successfully")
    return response_text

def main():
    """Main function to run the CAMEL-AI travel planner.
    运行CAMEL-AI旅行规划器的主函数"""
    logger.info("Starting CAMEL-AI Multi-Role Travel Planner")
    print("CAMEL-AI Multi-Role Travel Planner")
    print("=" * 40)
    
    # Get user input
    # 获取用户输入
    user_request = input("请输入您的旅行需求: ")
    logger.debug(f"User input received: {user_request}")
    
    if not user_request.strip():
        logger.warning("No valid travel request provided")
        print("未提供有效的旅行需求。")
        return
    
    print(f"\n正在处理您的请求: {user_request}")
    print("请稍候...")
    logger.info(f"Processing user request: {user_request}")
    
    # Process the travel request
    # 处理旅行请求
    result = camel_travel_planning_conversation(user_request)
    logger.debug("Travel request processing completed")
    
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
    
    logger.info("Displayed travel plan result to user")


if __name__ == "__main__":
    main()