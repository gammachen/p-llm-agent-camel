"""
脑筋急转弯游戏示例
Riddle game example using CAMEL-AI framework

本脚本将旅行规划功能改造为脑筋急转弯游戏，包含两个AI角色：
- AI助手：负责出题和核对答案
- 参赛者：负责回答问题

游戏规则：
1. 最多30轮出题+答复
2. 20轮以上且正确率低于50%时结束
3. 最终给出成绩等级和评价

This script transforms travel planning into a riddle game with two AI roles:
- AI Assistant: Responsible for creating riddles and checking answers
- Contestant: Responsible for answering questions

Game Rules:
1. Maximum 30 rounds of questions and answers
2. End when >20 rounds and accuracy < 50%
3. Final grade and evaluation provided
"""
import os
import time
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage
from camel.societies import RolePlaying

# Load environment variables
# 加载环境变量
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 游戏配置常量
MAX_ROUNDS = 10  # 最大游戏轮次
MIN_ROUNDS = 5  # 最小游戏轮次
CORRECT_RATE_THRESHOLD = 0.5  # 正确率阈值

def create_riddle_game(model) -> Dict[str, Any]:
    """
    创建脑筋急转弯游戏会话
    
    Args:
        model: 用于游戏的模型
        
    Returns:
        包含游戏会话和统计信息的字典
    """
    print("🎮 正在创建脑筋急转弯游戏...")
    
    # 创建角色扮演会话（使用CAMEL框架的标准方式）
    task_prompt = """进行脑筋急转弯问答游戏。

AI助手（出题者）的明确指令：
- 你是出题者，必须主动提出脑筋急转弯题目与答案
- 每轮只提出一个具体的问题，不要要求对方出题
- 出题后直接等待对方回答
- 输出问题和答案的格式必须是Json格式，key为"question"和"answer"
- 示例格式：{"question": "什么东西越洗越脏？", "answer": "水"}
- 必须严格按照Json格式输出，不能有任何额外的文本

参赛者（答题者）的明确指令：
- 你是答题者，必须直接回答问题
- 不要提出任何要求或询问，只回答问题
- 答案要简洁直接，不要反问
- 示例回答："水"

游戏规则：
1. AI助手必须主动出题
2. 参赛者必须直接回答题目
3. 禁止角色互换或混淆
4. 每轮必须完成：出题→回答"""
    
    role_play_session = RolePlaying(
        assistant_role_name="AI出题助手",
        user_role_name="参赛者",
        assistant_agent_kwargs=dict(model=model),
        user_agent_kwargs=dict(model=model),
        task_prompt=task_prompt,
        with_task_specify=False,
        output_language='中文'
    )
    
    print("✅ 脑筋急转弯游戏创建成功！")
    return {
        "session": role_play_session,
        "stats": {
            "total_rounds": 0,
            "correct_answers": 0,
            "current_round": 0
        }
    }

def play_riddle_game() -> Dict[str, Any]:
    """
    脑筋急转弯游戏主逻辑
    游戏规则：
    1. 最多30轮出题+答复
    2. 当轮次达到20轮以上且正确率低于50%时结束
    3. AI助手负责出题和评分，参赛者负责回答
    
    Returns:
        包含游戏结果和统计信息的字典
    """
    print("🎯 开始脑筋急转弯游戏！")
    
    # 设置模型
    model_platform = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    print(f"使用模型平台: {model_platform}")
    
    if model_platform.lower() == "ollama":
        print("初始化Ollama模型")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type=os.getenv("OLLAMA_MODEL_NAME", "qwen2"),
            model_config_dict={}
        )
    else:
        print("初始化OpenAI模型")
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.8, max_tokens=2000).as_dict()
        )
    
    # 创建游戏会话
    game_data = create_riddle_game(model)
    game_session = game_data["session"]
    game_stats = game_data["stats"]
    
    # 游戏变量初始化
    game_rounds = []
    current_round = 0
    
    # 初始化对话
    print("🎮 正在启动游戏对话...")
    input_msg = game_session.init_chat()
    
    # 确保AI助手首先出题
    if input_msg and hasattr(input_msg, 'content'):
        print(f"🎯 游戏初始化完成，AI助手准备出题...")
    
    # 游戏主循环
    while current_round < MAX_ROUNDS:
        current_round += 1
        print(f"\n🎯 第 {current_round} 轮开始")
        
        # AI助手出题
        print("🤖 AI助手正在出题...")
        ai_response, user_response = game_session.step(input_msg)
        
        # 验证响应格式
        if not ai_response or not user_response:
            print("❌ 获取响应失败")
            break
        
        # 检查游戏状态
        if ai_response.terminated or user_response.terminated:
            print("❌ 游戏意外终止")
            break
            
        # 获取对话内容
        ai_message = ai_response.msgs[0] if hasattr(ai_response, 'msgs') and ai_response.msgs else None
        user_message = user_response.msgs[0] if hasattr(user_response, 'msgs') and user_response.msgs else None
        
        if not ai_message or not user_message:
            print("❌ 无法获取对话内容")
            break
            
        # 清理和验证内容
        ai_content = str(ai_message.content).strip()
        user_content = str(user_message.content).strip()
        
        # 检查角色行为
        if "请提供" in user_content or "请出题" in user_content or "我需要" in user_content:
            print("⚠️ 检测到参赛者角色混淆，尝试纠正...")
            user_content = "让我重新回答：" + user_content.replace("请提供", "").replace("请出题", "").replace("我需要", "")
        
        # 打印题目和答案
        print(f"\n📝 第 {current_round} 轮题目：")
        print(f"{ai_content}")
        print(f"\n💡 参赛者回答：")
        print(f"{user_content}")
        
        # 更新消息内容
        ai_message.content = ai_content
        user_message.content = user_content
        
        # 解析这轮的结果
        round_result = {
            "round": current_round,
            "question": ai_message.content,
            "answer": user_message.content,
            "is_correct": "正确" in ai_message.content or "答对了" in ai_message.content or "正确" in user_message.content,
            "timestamp": time.time()
        }
        
        # 更新统计信息
        game_stats["current_round"] = current_round
        game_stats["total_rounds"] = current_round
        if round_result["is_correct"]:
            game_stats["correct_answers"] += 1
            
        game_rounds.append(round_result)
        
        # 显示当前轮次结果
        correct_rate = game_stats["correct_answers"] / game_stats["total_rounds"]
        print(f"📊 当前正确率: {correct_rate:.1%} ({game_stats['correct_answers']}/{game_stats['total_rounds']})")
        
        # 检查游戏结束条件
        if current_round >= MAX_ROUNDS:
            print(f"🎉 游戏完成！共进行了 {current_round} 轮")
            break
            
        if current_round >= MIN_ROUNDS and correct_rate < CORRECT_RATE_THRESHOLD:
            print(f"⏰ 游戏结束！已进行 {current_round} 轮，正确率 {correct_rate:.1%} 低于 {CORRECT_RATE_THRESHOLD:.0%}")
            break
            
        # 准备下一轮
        input_msg = user_message
        
        # 短暂停顿，让对话更自然
        time.sleep(1)
    
    # 计算最终成绩
    final_correct_rate = game_stats["correct_answers"] / game_stats["total_rounds"] if game_stats["total_rounds"] > 0 else 0
    
    print("\n" + "="*50)
    print("🏆 游戏结束！")
    print("="*50)
    print(f"总轮次: {game_stats['total_rounds']}")
    print(f"正确答题: {game_stats['correct_answers']}")
    print(f"最终正确率: {final_correct_rate:.1%}")
    
    # 根据成绩给出评价
    if final_correct_rate >= 0.8:
        grade = "优秀"
        comment = "太厉害了！你是脑筋急转弯大师！"
    elif final_correct_rate >= 0.6:
        grade = "良好"
        comment = "表现不错，继续保持！"
    elif final_correct_rate >= 0.4:
        grade = "及格"
        comment = "还有提升空间，再接再厉！"
    else:
        grade = "需要努力"
        comment = "别灰心，多练习会更棒！"
    
    print(f"成绩等级: {grade}")
    print(f"评语: {comment}")
    
    return {
        "game_summary": {
            "total_rounds": game_stats["total_rounds"],
            "correct_answers": game_stats["correct_answers"],
            "correct_rate": final_correct_rate,
            "grade": grade,
            "comment": comment
        },
        "game_rounds": game_rounds,
        "status": "completed"
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

if __name__ == "__main__":
    """
    脑筋急转弯游戏主程序入口
    """
    print("=" * 60)
    print("🎯 脑筋急转弯游戏 - CAMEL AI 双角色对话")
    print("🤖 AI助手 vs 🧑‍🎓 参赛者")
    print("=" * 60)
    
    print("\n游戏规则：")
    print("1️⃣ AI助手负责出题和评分")
    print("2️⃣ 参赛者负责回答问题")
    print("3️⃣ 最多30轮出题+答复")
    print("4️⃣ 20轮以上且正确率低于50%时结束")
    print("5️⃣ 最终给出成绩等级和评价")
    
    try:
        print("\n🚀 正在启动游戏...")
        result = play_riddle_game()
        
        if result["status"] == "completed":
            print("\n✅ 游戏成功完成！")
            
            # 显示详细的游戏结果
            summary = result["game_summary"]
            print(f"\n📊 游戏统计：")
            print(f"总轮次: {summary['total_rounds']}")
            print(f"正确答题: {summary['correct_answers']}")
            print(f"最终正确率: {summary['correct_rate']:.1%}")
            print(f"成绩等级: {summary['grade']}")
            print(f"评语: {summary['comment']}")
            
            # 显示部分游戏回合（如果轮次较多，只显示前后几轮）
            rounds = result["game_rounds"]
            if rounds:
                print(f"\n🎮 游戏回合预览：")
                
                # 显示前3轮和最后2轮
                display_rounds = []
                if len(rounds) <= 5:
                    display_rounds = rounds
                else:
                    display_rounds = rounds[:3] + rounds[-2:]
                
                for i, round_data in enumerate(display_rounds, 1):
                    print(f"\n回合 {round_data['round']}:")
                    print(f"题目: {round_data['question'][:100]}...")
                    print(f"答案: {round_data['answer'][:50]}...")
                    print(f"结果: {'✅ 正确' if round_data['is_correct'] else '❌ 错误'}")
                    
                    # 添加分隔线（除了最后一轮）
                    if i < len(display_rounds):
                        print("-" * 40)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  游戏被用户中断")
    except Exception as e:
        print(f"\n❌ 游戏运行错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("🎮 脑筋急转弯游戏结束！")
    print("="*60)