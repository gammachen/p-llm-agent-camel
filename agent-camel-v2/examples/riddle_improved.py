"""
改进版脑筋急转弯游戏示例
Enhanced Riddle game example using CAMEL-AI framework

本脚本解决以下5个关键问题：
1. 首轮AI助手主动出题触发机制
2. 严格限制题目输出格式（含问题和答案）
3. 确保问题正确传递给参赛者
4. 存储参赛者答题结果（内存方案）
5. 使用完全匹配规则判定答案正确性

改进内容：
- AI助手必须主动出题并输出标准JSON格式
- 参赛者只能回答问题，不能要求出题
- 实时存储答题结果和评分
- 完全匹配答案判定
- 清晰的角色职责分离
"""
import os
import time
import logging
import json
import re
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage
from camel.societies import RolePlaying

# Load environment variables
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 游戏配置常量
MAX_ROUNDS = 20  # 最大游戏轮次
MIN_ROUNDS = 5   # 最小游戏轮次
CORRECT_RATE_THRESHOLD = 0.5  # 正确率阈值

class RiddleGameStorage:
    """存储游戏数据的内存存储类"""
    
    def __init__(self):
        self.game_rounds = []
        self.total_rounds = 0
        self.correct_answers = 0
        
    def add_round(self, round_data: Dict[str, Any]):
        """添加一轮游戏数据"""
        self.game_rounds.append(round_data)
        self.total_rounds += 1
        if round_data.get('is_correct', False):
            self.correct_answers += 1
    
    def get_correct_rate(self) -> float:
        """获取正确率"""
        if self.total_rounds == 0:
            return 0.0
        return self.correct_answers / self.total_rounds
    
    def get_summary(self) -> Dict[str, Any]:
        """获取游戏摘要"""
        return {
            'total_rounds': self.total_rounds,
            'correct_answers': self.correct_answers,
            'correct_rate': self.get_correct_rate(),
            'rounds': self.game_rounds
        }

class RiddleValidator:
    """脑筋急转弯验证器"""
    
    @staticmethod
    def parse_riddle_response(content: str) -> Dict[str, str]:
        """解析AI助手的题目响应，提取JSON格式的问题和答案"""
        try:
            # 尝试直接解析JSON
            data = json.loads(content)
            if 'question' in data and 'answer' in data:
                return data
        except json.JSONDecodeError:
            pass
        
        # 尝试从文本中提取JSON
        json_pattern = r'\{[^}]*"question"[^}]*"answer"[^}]*\}'
        matches = re.findall(json_pattern, content)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # 尝试手动解析
        lines = content.strip().split('\n')
        question = ""
        answer = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('问题：') or line.startswith('题目：'):
                question = line[3:].strip()
            elif line.startswith('答案：'):
                answer = line[3:].strip()
        
        return {"question": question, "answer": answer}
    
    @staticmethod
    def validate_answer(user_answer: str, correct_answer: str) -> bool:
        """使用完全匹配规则验证答案"""
        if not user_answer or not correct_answer:
            return False
        
        # 清理答案
        user_clean = user_answer.strip().lower().replace(' ', '')
        correct_clean = correct_answer.strip().lower().replace(' ', '')
        
        # 完全匹配
        return user_clean == correct_clean
    
    @staticmethod
    def clean_user_response(content: str) -> str:
        """清理用户响应，移除角色混淆内容"""
        # 移除常见的角色混淆关键词
        clean_content = content.strip()
        
        # 移除要求出题的内容
        patterns = [
            r'请.*出题.*',
            r'我.*需要.*题目.*',
            r'让.*我.*出题.*',
            r'你.*回答.*',
            r'请.*提供.*问题.*',
            r'我.*来.*出题.*'
        ]
        
        for pattern in patterns:
            clean_content = re.sub(pattern, '', clean_content, flags=re.IGNORECASE)
        
        return clean_content.strip()

def create_enhanced_riddle_game(model) -> Dict[str, Any]:
    """创建增强版脑筋急转弯游戏会话"""
    print("🎮 正在创建增强版脑筋急转弯游戏...")
    
    # 创建简化的任务提示
    task_prompt = """脑筋急转弯游戏：AI助手出题，参赛者答题。

AI助手规则：主动出题，输出JSON格式{"question":"题目","answer":"答案"}，如{"question":"什么东西越洗越脏？","answer":"水"}
参赛者规则：直接回答问题，如"水"
禁止角色互换，完全匹配答案判定。"""
    
    role_play_session = RolePlaying(
        assistant_role_name="AI出题助手",
        user_role_name="参赛者",
        assistant_agent_kwargs=dict(model=model),
        user_agent_kwargs=dict(model=model),
        task_prompt=task_prompt,
        with_task_specify=False,
        output_language='中文'
    )
    
    # 创建存储和验证器
    storage = RiddleGameStorage()
    validator = RiddleValidator()
    
    print("✅ 增强版脑筋急转弯游戏创建成功！")
    return {
        "session": role_play_session,
        "storage": storage,
        "validator": validator,
        "stats": {
            "total_rounds": 0,
            "correct_answers": 0
        }
    }

def trigger_first_riddle(game_session) -> str:
    """触发首轮AI助手出题"""
    print("🎯 触发首轮AI助手出题...")
    
    # 创建一个明确的触发消息
    trigger_msg = BaseMessage.make_user_message(
        role_name="系统",
        content="开始游戏，请AI助手立即出题，必须输出标准JSON格式的问题和答案。"
    )
    
    return trigger_msg

def play_enhanced_riddle_game() -> Dict[str, Any]:
    """增强版脑筋急转弯游戏主逻辑"""
    print("🎯 开始增强版脑筋急转弯游戏！")
    
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
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=2000).as_dict()
        )
    
    # 创建游戏会话
    game_data = create_enhanced_riddle_game(model)
    game_session = game_data["session"]
    storage = game_data["storage"]
    validator = game_data["validator"]
    
    # 游戏变量初始化
    current_round = 0
    
    # 初始化对话并触发首轮出题
    print("🎮 正在启动游戏对话...")
    input_msg = game_session.init_chat()
    
    # 触发首轮AI助手出题
    trigger_msg = trigger_first_riddle(game_session)
    
    # 游戏主循环
    while current_round < MAX_ROUNDS:
        current_round += 1
        print(f"\n🎯 第 {current_round} 轮开始")
        
        # 如果是第一轮，使用触发消息
        if current_round == 1:
            current_input = trigger_msg
        else:
            current_input = input_msg
        
        # AI助手出题
        print("🤖 AI助手正在出题...")
        ai_response, user_response = game_session.step(current_input)
        
        # 验证响应
        if not ai_response or not user_response:
            print("❌ 获取响应失败")
            break
        
        if ai_response.terminated or user_response.terminated:
            print("❌ 游戏意外终止")
            break
        
        # 获取对话内容
        ai_message = ai_response.msgs[0] if hasattr(ai_response, 'msgs') and ai_response.msgs else None
        user_message = user_response.msgs[0] if hasattr(user_response, 'msgs') and user_response.msgs else None
        
        if not ai_message or not user_message:
            print("❌ 无法获取对话内容")
            break
        
        # 解析题目和答案
        ai_content = str(ai_message.content).strip()
        riddle_data = validator.parse_riddle_response(ai_content)
        
        if not riddle_data['question'] or not riddle_data['answer']:
            print("❌ AI助手输出格式错误，跳过本轮")
            continue
        
        # 清理用户回答
        user_content = validator.clean_user_response(str(user_message.content))
        
        # 验证答案
        is_correct = validator.validate_answer(user_content, riddle_data['answer'])
        
        # 存储本轮结果
        round_result = {
            'round': current_round,
            'question': riddle_data['question'],
            'correct_answer': riddle_data['answer'],
            'user_answer': user_content,
            'is_correct': is_correct,
            'timestamp': time.time()
        }
        
        storage.add_round(round_result)
        
        # 显示本轮结果
        print(f"\n📝 第 {current_round} 轮题目：")
        print(f"问题：{riddle_data['question']}")
        print(f"标准答案：{riddle_data['answer']}")
        print(f"\n💡 参赛者回答：{user_content}")
        print(f"🎯 判定结果：{'✅ 正确' if is_correct else '❌ 错误'}")
        
        # 显示当前统计
        correct_rate = storage.get_correct_rate()
        print(f"📊 当前正确率: {correct_rate:.1%} ({storage.correct_answers}/{storage.total_rounds})")
        
        # 检查游戏结束条件
        if current_round >= MIN_ROUNDS and correct_rate < CORRECT_RATE_THRESHOLD:
            print(f"⏰ 游戏结束！已进行 {current_round} 轮，正确率 {correct_rate:.1%} 低于 {CORRECT_RATE_THRESHOLD:.0%}")
            break
            
        if current_round >= MAX_ROUNDS:
            print(f"🎉 游戏完成！共进行了 {current_round} 轮")
            break
        
        # 准备下一轮 - 使用上一轮的用户消息作为输入
        input_msg = user_message
        
        # 短暂停顿
        time.sleep(1)
    
    # 获取最终游戏摘要
    game_summary = storage.get_summary()
    
    # 计算最终成绩
    final_correct_rate = game_summary['correct_rate']
    
    print("\n" + "="*60)
    print("🏆 游戏结束！")
    print("="*60)
    print(f"总轮次: {game_summary['total_rounds']}")
    print(f"正确答题: {game_summary['correct_answers']}")
    print(f"最终正确率: {final_correct_rate:.1%}")
    
    # 成绩评级
    if final_correct_rate >= 0.8:
        grade = "优秀"
        comment = "脑筋急转弯大师！反应敏捷，思维活跃！"
    elif final_correct_rate >= 0.6:
        grade = "良好"
        comment = "表现不错，继续保持思维训练！"
    elif final_correct_rate >= 0.4:
        grade = "及格"
        comment = "还有提升空间，多练习会更棒！"
    else:
        grade = "需要努力"
        comment = "别灰心，脑筋急转弯需要多练习和积累！"
    
    print(f"成绩等级: {grade}")
    print(f"评语: {comment}")
    
    # 显示部分游戏回合详情
    rounds = game_summary['rounds']
    if len(rounds) > 5:
        print(f"\n📋 游戏详情摘要：")
        for i, round_data in enumerate(rounds[:3]):
            print(f"  第{round_data['round']}轮: {round_data['question']} → {round_data['user_answer']} ({'✅' if round_data['is_correct'] else '❌'})")
        print("  ...")
        for round_data in rounds[-2:]:
            print(f"  第{round_data['round']}轮: {round_data['question']} → {round_data['user_answer']} ({'✅' if round_data['is_correct'] else '❌'})")
    else:
        print(f"\n📋 详细游戏记录：")
        for round_data in rounds:
            print(f"  第{round_data['round']}轮: {round_data['question']} → {round_data['user_answer']} ({'✅' if round_data['is_correct'] else '❌'})")
    
    return {
        'game_summary': {
            'total_rounds': game_summary['total_rounds'],
            'correct_answers': game_summary['correct_answers'],
            'correct_rate': final_correct_rate,
            'grade': grade,
            'comment': comment
        },
        'game_rounds': rounds,
        'status': 'completed',
        'storage': storage
    }

if __name__ == "__main__":
    """
    增强版脑筋急转弯游戏主程序入口
    """
    print("=" * 80)
    print("🎯 增强版脑筋急转弯游戏 - CAMEL AI 双角色对话")
    print("🤖 AI出题助手 vs 🧑‍🎓 参赛者")
    print("=" * 80)
    
    print("\n✨ 改进特性：")
    print("1️⃣ AI助手强制主动出题")
    print("2️⃣ 标准JSON格式输出（问题+答案）")
    print("3️⃣ 实时答题结果存储")
    print("4️⃣ 完全匹配答案判定")
    print("5️⃣ 清晰的角色职责分离")
    
    try:
        print("\n🚀 正在启动增强版游戏...")
        result = play_enhanced_riddle_game()
        
        if result['status'] == 'completed':
            print("\n✅ 增强版游戏成功完成！")
            
    except Exception as e:
        print(f"\n❌ 游戏执行出错: {str(e)}")
        import traceback
        traceback.print_exc()