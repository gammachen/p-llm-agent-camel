"""
通用角色扮演Agent构建器 - 简化版
减少上下文长度和令牌使用
"""
import os
import json
import re
import time
from typing import Dict, List, Any
from dotenv import load_dotenv

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage

load_dotenv()

class SimpleRoleplayGame:
    """简化版通用角色扮演游戏"""
    
    def __init__(self, topic: str):
        self.topic = topic
        self.rounds = []
        self.total_rounds = 0
        self.correct_answers = 0
        
        # 使用更少的令牌
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=400).as_dict()
        )
        
        # 超简洁的系统消息
        self.assistant = ChatAgent(
            model=model,
            system_message=f"你是{topic}出题者，输出格式：{{\"question\":\"题\",\"answer\":\"答\"}}"
        )
        
        self.contestant = ChatAgent(
            model=model,
            system_message=f"你是{topic}答题者，直接回答，不要解释"
        )
    
    def extract_json_riddle(self, text: str) -> Dict[str, str]:
        """提取JSON格式的题目"""
        try:
            # 简单提取
            data = json.loads(text.strip())
            if 'question' in data and 'answer' in data:
                return data
        except:
            pass
        
        # 手动解析
        question = answer = ""
        lines = text.strip().split('\n')
        for line in lines:
            if 'question' in line.lower() and ':' in line:
                question = line.split(':', 1)[1].strip('" }')
            elif 'answer' in line.lower() and ':' in line:
                answer = line.split(':', 1)[1].strip('" }')
        
        if not question and lines:
            question = lines[0]
        if not answer and len(lines) > 1:
            answer = lines[1]
        
        return {"question": question, "answer": answer}
    
    def normalize_answer(self, text: str) -> str:
        """标准化答案"""
        return re.sub(r'[^\u4e00-\u9fff\w]', '', str(text).lower().strip())
    
    def validate_answer(self, user_answer: str, correct_answer: str) -> bool:
        """验证答案"""
        return self.normalize_answer(user_answer) == self.normalize_answer(correct_answer)
    
    def play_round(self, round_num: int) -> Dict[str, Any]:
        """进行一轮游戏"""
        print(f"\n🎯 第{round_num}轮 - {self.topic}")
        
        # AI出题
        question_msg = BaseMessage.make_user_message("系统", f"出题{round_num}")
        ai_response = self.assistant.step(question_msg)
        
        if not ai_response.msgs:
            return None
        
        riddle = self.extract_json_riddle(ai_response.msgs[0].content)
        if not riddle['question'] or not riddle['answer']:
            return None
        
        question = riddle['question']
        correct_answer = riddle['answer']
        
        print(f"📝 {question}")
        
        # 参赛者答题
        answer_msg = BaseMessage.make_user_message("出题者", question)
        user_response = self.contestant.step(answer_msg)
        
        if not user_response.msgs:
            return None
        
        user_answer = user_response.msgs[0].content.strip()
        
        # 验证
        is_correct = self.validate_answer(user_answer, correct_answer)
        
        result = {
            'round': round_num,
            'topic': self.topic,
            'question': question,
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'correct': is_correct
        }
        
        self.rounds.append(result)
        self.total_rounds += 1
        if is_correct:
            self.correct_answers += 1
        
        print(f"💡 {correct_answer}")
        print(f"🎯 {user_answer} ({'✅' if is_correct else '❌'})")
        
        return result
    
    def play_game(self, max_rounds: int = 8, min_rounds: int = 4, threshold: float = 0.3) -> Dict[str, Any]:
        """运行游戏"""
        print(f"\n🎯 {self.topic}问答开始")
        
        for round_num in range(1, max_rounds + 1):
            result = self.play_round(round_num)
            if not result:
                continue
            
            rate = self.correct_answers / self.total_rounds
            print(f"📊 {rate:.1%} ({self.correct_answers}/{self.total_rounds})")
            
            if round_num >= min_rounds and rate < threshold:
                print(f"\n⏰ 结束！正确率 {rate:.1%}")
                break
                
            time.sleep(1)
        
        rate = self.correct_answers / self.total_rounds if self.total_rounds > 0 else 0
        
        print(f"\n🏆 {self.topic}结果:")
        print(f"轮次: {self.total_rounds}")
        print(f"正确: {self.correct_answers}")
        print(f"正确率: {rate:.1%}")
        
        return {
            'topic': self.topic,
            'total_rounds': self.total_rounds,
            'correct_answers': self.correct_answers,
            'correct_rate': rate
        }

def get_topic():
    """获取主题"""
    print("\n🎯 通用知识问答")
    print("主题示例：三国历史、量子力学、杭州文化、鸡兔同笼")
    
    topics = [
        "三国历史", "量子力学", "杭州历史文化", "食物链", 
        "空气动力学", "知识图谱", "时间", "鸡兔同笼", 
        "相遇问题", "瞬时速度", "哲学家尼采", "抗日战争"
    ]
    
    print("可选：", " | ".join(topics))
    topic = input("输入主题：").strip()
    return topic if topic else "杭州历史文化"

if __name__ == "__main__":
    try:
        topic = get_topic()
        game = SimpleRoleplayGame(topic)
        game.play_game()
        print("✅ 完成")
    except KeyboardInterrupt:
        print("\n👋 退出")
    except Exception as e:
        print(f"❌ 错误: {e}")