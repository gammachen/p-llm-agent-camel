"""
Travel Planner Example for Agent-Camel V2.
Agent-Camel V2的旅行规划示例
"""
import uuid
from typing import Dict, Any, List
from agents.coordinator import TaskCoordinator
from config.settings import settings


# Define travel roles
# 定义旅行角色
travel_roles = {
    "travel_planner": {
        "role": "资深旅行规划师",
        "goal": "为用户制定完美的旅行计划",
        "backstory": "你是一位有20年经验的旅行规划专家，擅长根据用户偏好制定个性化旅行方案"
    },
    "local_guide": {
        "role": "当地向导",
        "goal": "提供目的地详细信息和建议",
        "backstory": "你是目的地的本地居民，对当地文化、美食和景点了如指掌"
    },
    "budget_advisor": {
        "role": "预算顾问",
        "goal": "帮助用户优化旅行预算",
        "backstory": "你是财务规划专家，擅长在保证体验的前提下优化旅行开支"
    }
}


def travel_planning_conversation(user_request: str) -> Dict[str, Any]:
    """
    Travel planning conversation flow.
    旅行规划对话流程
    
    Args:
        user_request: User's travel request
                  用户的旅行请求
        
    Returns:
        Final travel plan response
        最终旅行计划响应
    """
    # 1. Initialize session and coordinator
    # 1. 初始化会话和协调器
    session_id = str(uuid.uuid4())
    coordinator = TaskCoordinator()
    
    # 2. Register relevant agents
    # 2. 注册相关Agents
    # Determine model provider based on settings
    # 根据设置确定模型提供商
    model_provider = settings.DEFAULT_MODEL_PROVIDER
    
    coordinator.register_agent("planner_1", "travel_planner", 
                              ["destination_recommendation", "itinerary_planning"],
                              model_provider)
    coordinator.register_agent("guide_1", "local_guide", 
                              ["local_knowledge", "attraction_recommendation"],
                              model_provider)
    coordinator.register_agent("budget_1", "budget_advisor", 
                              ["cost_estimation", "budget_optimization"],
                              model_provider)
    
    # 3. Analyze user request and assign tasks
    # 3. 分析用户请求并分配任务
    task_analysis = coordinator.analyze_request(user_request)
    
    print(f"Task analysis: {task_analysis}")
    
    # 4. Execute multi-agent collaboration
    # 4. 执行多Agent协作
    results = {}
    for task in task_analysis.get('tasks', []):
        agent_id = coordinator.assign_task(task, task.get('requirements', {}))
        if agent_id:
            result = coordinator.execute_task(agent_id, task, session_id)
            results[task['type']] = result
    
    # 5. Synthesize results and generate final response
    # 5. 综合结果并生成最终响应
    final_response = synthesize_results(results, user_request)
    
    return final_response


# No changes needed in analyze_request function for now
# 目前不需要更改analyze_request函数
# As we're keeping the simple placeholder for request analysis
# 因为我们保持请求分析的简单占位符


# No changes needed in execute_task function for now
# 目前不需要更改execute_task函数
# As we're keeping the simple placeholder for task execution
# 因为我们保持任务执行的简单占位符


def synthesize_results(results: Dict[str, Any], user_request: str) -> Dict[str, Any]:
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
    # Create a summary of all agent responses
    # 创建所有Agent响应的摘要
    response_text = f"根据您的请求 '{user_request}'，我们为您提供以下旅行建议：\n\n"
    
    for task_type, result in results.items():
        if task_type == "destination_planning":
            response_text += "🌍 目的地规划：\n"
            response_text += f"{result.get('result', '正在为您规划最佳目的地...')}\n\n"
        elif task_type == "local_guidance":  # Changed from local_guide to local_guidance
            response_text += "📍 当地指南：\n"
            response_text += f"{result.get('result', '正在为您收集当地信息...')}\n\n"
        elif task_type == "budget_planning":
            response_text += "💰 预算规划：\n"
            response_text += f"{result.get('result', '正在为您制定预算计划...')}\n\n"
    
    return {
        "response": response_text,
        "details": results,
        "status": "success"
    }