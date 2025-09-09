"""
优化版脑筋急转弯游戏 - 减少上下文警告
Optimized Riddle Game with reduced context warnings

解决令牌限制和上下文截断问题
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

class OptimizedRiddleGame:
    """优化版脑筋急转弯游戏"""
    
    def __init__(self):
        self.rounds = []
        self.total_rounds = 0
        self.correct_answers = 0
        
        # 设置模型 - 优化令牌限制
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(
                temperature=0.7,
                max_tokens=400  # 减少令牌使用
            ).as_dict()
        )
        
        # 简化的系统消息 - 减少令牌使用
        self.assistant = ChatAgent(
            model=model,
            system_message='出题：输出JSON格式{"q":"题目","a":"答案"}'
        )
        
        self.contestant = ChatAgent(
            model=model,
            system_message="答题：直接回答问题，简短"
        )
    
    def extract_riddle(self, text: str) -> Dict[str, str]:
        """提取题目和答案"""
        text = text.strip()
        
        # 尝试JSON解析
        try:
            data = json.loads(text)
            if 'q' in data and 'a' in data:
                return {"question": data['q'], "answer": data['a']}
            if 'question' in data and 'answer' in data:
                return data
        except:
            pass
        
        # 简化提取
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        question = answer = ""
        
        for line in lines:
            if any(k in line.lower() for k in ['q:', '问题:', 'question:']):
                question = line.split(':', 1)[1].strip() if ':' in line else line
            elif any(k in line.lower() for k in ['a:', '答案:', 'answer:']):
                answer = line.split(':', 1)[1].strip() if ':' in line else line
        
        # 如果没有找到，尝试整个文本作为问题
        if not question and lines:
            question = lines[0]
            if len(lines) > 1:
                answer = lines[1]
        
        return {"question": question, "answer": answer}
    
    def normalize(self, text: str) -> str:
        """标准化答案"""
        return re.sub(r'[^\u4e00-\u9fff\w]', '', str(text).lower().strip())
    
    def play_round(self, round_num: int) -> Dict[str, Any]:
        """进行一轮游戏"""
        print(f"\n🎯 第{round_num}轮")
        
        # 简化的出题指令
        question_prompt = f"出第{round_num}个脑筋急转弯，格式：{{\"q\":\"题目\",\"a\":\"答案\"}}"
        ai_msg = BaseMessage.make_user_message("系统", question_prompt)
        
        try:
            ai_response = self.assistant.step(ai_msg)
            if not ai_response.msgs:
                return None
                
            riddle_data = self.extract_riddle(ai_response.msgs[0].content)
            if not riddle_data['question'] or not riddle_data['answer']:
                return None
                
            question = riddle_data['question']
            correct_answer = riddle_data['answer']
            
            print(f"📝 问题: {question}")
            
            # 简化的答题指令
            answer_prompt = f"问题：{question}\n直接回答："
            user_msg = BaseMessage.make_user_message("出题者", answer_prompt)
            
            user_response = self.contestant.step(user_msg)
            if not user_response.msgs:
                return None
                
            user_answer = user_response.msgs[0].content.strip()
            
            # 验证答案
            is_correct = self.normalize(user_answer) == self.normalize(correct_answer)
            
            result = {
                'round': round_num,
                'question': question,
                'correct': correct_answer,
                'answer': user_answer,
                'correct': is_correct
            }
            
            self.rounds.append(result)
            self.total_rounds += 1
            if is_correct:
                self.correct_answers += 1
            
            print(f"💡 答案: {correct_answer}")
            print(f"🎯 回答: {user_answer} ({'✅' if is_correct else '❌'})")
            
            return result
            
        except Exception as e:
            print(f"❌ 本轮出错: {str(e)}")
            return None
    
    def play_game(self, max_rounds: int = 8, min_rounds: int = 3, threshold: float = 0.25):
        """运行游戏"""
        print("=" * 50)
        print("🎯 优化版脑筋急转弯游戏")
        print("=" * 50)
        
        for i in range(1, max_rounds + 1):
            result = self.play_round(i)
            if result:
                rate = self.correct_answers / self.total_rounds
                print(f"📊 正确率: {rate:.1%} ({self.correct_answers}/{self.total_rounds})")
                
                if i >= min_rounds and rate < threshold:
                    print(f"\n⏰ 游戏结束！正确率 {rate:.1%} 低于 {threshold:.0%}")
                    break
            
            time.sleep(0.5)
        
        # 结果总结
        rate = self.correct_answers / self.total_rounds if self.total_rounds > 0 else 0
        
        print(f"\n{'='*50}")
        print("🏆 游戏结束")
        print(f"总轮次: {self.total_rounds}")
        print(f"正确数: {self.correct_answers}")
        print(f"正确率: {rate:.1%}")
        
        # 简单评级
        if rate >= 0.6:
            grade = "优秀"
        elif rate >= 0.4:
            grade = "良好"
        elif rate >= 0.2:
            grade = "及格"
        else:
            grade = "加油"
        
        print(f"等级: {grade}")
        
        if self.rounds:
            print(f"\n📋 记录：")
            for r in self.rounds[-5:]:
                print(f"  {r['round']}: {r['question'][:20]}... → {r['answer']} ({'✅' if r['correct'] else '❌'})")

if __name__ == "__main__":
    game = OptimizedRiddleGame()
    game.play_game()