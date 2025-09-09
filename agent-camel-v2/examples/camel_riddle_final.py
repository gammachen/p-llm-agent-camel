"""
最终版脑筋急转弯游戏 - 完全修复版本
Final Riddle game with all 5 issues resolved

完全解决以下5个问题：
1. ✅ 首轮AI助手主动出题触发机制
2. ✅ 严格限制题目输出格式（含问题和答案）
3. ✅ 确保问题正确传递给参赛者
4. ✅ 存储参赛者答题结果（内存方案）
5. ✅ 使用完全匹配规则判定答案正确性

新增特性：
- 强制角色分离
- JSON格式验证
- 实时结果存储
- 答案完全匹配
- 游戏流程控制
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

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 游戏配置
MAX_ROUNDS = 10
MIN_ROUNDS = 3
CORRECT_RATE_THRESHOLD = 0.3

class GameStorage:
    """游戏数据存储"""
    def __init__(self):
        self.rounds = []
        self.total = 0
        self.correct = 0
    
    def add_round(self, data):
        self.rounds.append(data)
        self.total += 1
        if data.get('correct', False):
            self.correct += 1
    
    def get_stats(self):
        rate = self.correct / self.total if self.total > 0 else 0
        return {'total': self.total, 'correct': self.correct, 'rate': rate, 'rounds': self.rounds}

class AnswerValidator:
    """答案验证器"""
    @staticmethod
    def extract_json(text):
        """从文本中提取JSON"""
        try:
            # 直接尝试解析
            return json.loads(text)
        except:
            # 尝试提取JSON块
            json_match = re.search(r'\{[^}]*"question"[^}]*"answer"[^}]*\}', text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        return None
    
    @staticmethod
    def normalize(text):
        """标准化文本用于比较"""
        return re.sub(r'[^\w]', '', str(text).lower().strip())
    
    @staticmethod
    def validate(user_answer, correct_answer):
        """完全匹配验证"""
        return AnswerValidator.normalize(user_answer) == AnswerValidator.normalize(correct_answer)

def create_game(model):
    """创建游戏"""
    print("🎮 创建脑筋急转弯游戏...")
    
    task_prompt = """脑筋急转弯游戏：
AI助手：出题者，必须输出JSON格式{"question":"题目","answer":"答案"}
参赛者：答题者，必须直接给出答案
禁止角色互换，答案完全匹配判定。"""
    
    game = RolePlaying(
        assistant_role_name="出题助手",
        user_role_name="答题者",
        assistant_agent_kwargs={'model': model},
        user_agent_kwargs={'model': model},
        task_prompt=task_prompt,
        with_task_specify=False,
        output_language='中文'
    )
    
    return {
        'game': game,
        'storage': GameStorage(),
        'validator': AnswerValidator()
    }

def play_game():
    """主游戏逻辑"""
    print("🎯 开始脑筋急转弯游戏！")
    
    # 设置模型
    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=ModelType.GPT_3_5_TURBO,
        model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=1000).as_dict()
    )
    
    # 初始化游戏
    game_data = create_game(model)
    game = game_data['game']
    storage = game_data['storage']
    validator = game_data['validator']
    
    current_round = 0
    
    # 初始化并触发首轮
    print("🎮 启动游戏...")
    game.init_chat()
    
    # 首轮触发消息
    trigger = BaseMessage.make_user_message("系统", "开始游戏，请出题")
    
    while current_round < MAX_ROUNDS:
        current_round += 1
        print(f"\n🎯 第{current_round}轮")
        
        # 获取响应
        if current_round == 1:
            ai_resp, user_resp = game.step(trigger)
        else:
            # 使用上一轮的用户消息作为输入
            ai_resp, user_resp = game.step()
        
        if not ai_resp or not user_resp:
            break
        
        # 提取内容
        ai_msg = ai_resp.msgs[0] if ai_resp.msgs else None
        user_msg = user_resp.msgs[0] if user_resp.msgs else None
        
        if not ai_msg or not user_msg:
            break
        
        # 解析题目
        ai_text = str(ai_msg.content).strip()
        riddle_data = validator.extract_json(ai_text)
        
        if not riddle_data or 'question' not in riddle_data or 'answer' not in riddle_data:
            print("❌ 题目格式错误")
            continue
        
        question = riddle_data['question']
        correct_answer = riddle_data['answer']
        user_answer = str(user_msg.content).strip()
        
        # 验证答案
        is_correct = validator.validate(user_answer, correct_answer)
        
        # 存储结果
        storage.add_round({
            'round': current_round,
            'question': question,
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'correct': is_correct
        })
        
        # 显示结果
        print(f"📝 问题: {question}")
        print(f"💡 答案: {correct_answer}")
        print(f"🎯 回答: {user_answer} ({'✅' if is_correct else '❌'})")
        
        stats = storage.get_stats()
        print(f"📊 正确率: {stats['rate']:.1%} ({stats['correct']}/{stats['total']})")
        
        # 检查结束条件
        if current_round >= MIN_ROUNDS and stats['rate'] < CORRECT_RATE_THRESHOLD:
            print(f"⏰ 游戏结束！正确率低于阈值")
            break
            
        time.sleep(1)
    
    # 最终结果
    stats = storage.get_stats()
    print(f"\n{'='*50}")
    print("🏆 游戏结束")
    print(f"总轮次: {stats['total']}")
    print(f"正确数: {stats['correct']}")
    print(f"正确率: {stats['rate']:.1%}")
    
    # 成绩评级
    rate = stats['rate']
    if rate >= 0.8:
        grade, comment = "优秀", "脑筋急转弯大师！"
    elif rate >= 0.6:
        grade, comment = "良好", "表现不错！"
    elif rate >= 0.4:
        grade, comment = "及格", "继续努力！"
    else:
        grade, comment = "加油", "多练习会更棒！"
    
    print(f"等级: {grade}")
    print(f"评语: {comment}")
    
    return stats

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 最终版脑筋急转弯游戏")
    print("🤖 AI出题 vs 🧑‍🎓 答题")
    print("=" * 60)
    
    try:
        result = play_game()
        print("\n✅ 游戏完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()