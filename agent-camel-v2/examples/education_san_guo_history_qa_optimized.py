"""
三国历史知识问答游戏 - 优化版
基于 riddle_complete.py 规范格式重构

✅ 1. 首轮AI助手主动出题触发
✅ 2. 严格JSON格式输出（问题+答案）
✅ 3. 问题正确传递给参赛者
✅ 4. 实时存储答题结果
✅ 5. 完全匹配答案判定

使用简化的角色创建方式，确保游戏流畅运行
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

class SanGuoHistoryGame:
    """三国历史知识问答游戏类"""
    
    def __init__(self):
        self.rounds = []
        self.total_rounds = 0
        self.correct_answers = 0
        
        # 设置模型
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=800).as_dict()
        )
        
        # 创建AI助手（出题者）- 使用更简洁的系统消息
        self.assistant = ChatAgent(
            model=model,
            system_message="""你是三国历史知识出题助手。

职责：
1. 必须主动出题
2. 输出格式：{"question": "题目", "answer": "答案"}
3. 题目要有趣，答案要准确
4. 禁止其他格式或解释

示例：
{"question": "三国时期指的是哪三个国家？", "answer": "魏、蜀、吴"}
{"question": "三国时期开始的标志性事件是什么？", "answer": "曹丕称帝"}
{"question": "被称为“奸雄”的是哪位三国人物？", "answer": "曹操"}
{"question": "“三顾茅庐”的故事中，刘备请的是谁出山？", "answer": "诸葛亮"}
{"question": "赤壁之战发生在哪一年？其主要参战方是谁？", "answer": "208年，曹操 vs 孙刘联军"}"""
        )
        
        # 创建参赛者（答题者）- 使用更简洁的系统消息
        self.contestant = ChatAgent(
            model=model,
            system_message="""你是三国历史知识答题者。

职责：
1. 必须直接回答问题
2. 答案要简洁，不要反问，不要解释推理过程
3. 禁止要求出题或提出其他要求
4. 只给出你认为的正确答案"""
        )
    
    def extract_json_riddle(self, text: str) -> Dict[str, str]:
        """从文本中提取JSON格式的题目和答案"""
        print("📝 原始文本：", text)
        
        try:
            # 尝试直接解析完整JSON
            data = json.loads(text.strip())
            if 'question' in data and 'answer' in data:
                return data
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON块
        json_pattern = r'\{[^}]*"question"[^}]*"answer"[^}]*\}'
        matches = re.findall(json_pattern, text, re.IGNORECASE)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # 手动解析 - 更健壮的解析
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        question = answer = ""
        
        for line in lines:
            line_lower = line.lower()
            if any(key in line_lower for key in ['问题:', '题目:', 'question:']):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    question = parts[1].strip()
                else:
                    question = line
            elif any(key in line_lower for key in ['答案:', 'answer:']):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    answer = parts[1].strip()
                else:
                    answer = line
        
        # 如果没有找到明确的问题，使用第一行
        if not question and lines:
            question = lines[0]
            if len(lines) > 1:
                answer = lines[1]
        
        return {"question": question, "answer": answer}
    
    def normalize_answer(self, text: str) -> str:
        """标准化答案用于比较"""
        return re.sub(r'[^\u4e00-\u9fff\w]', '', str(text).lower().strip())
    
    def validate_answer(self, user_answer: str, correct_answer: str) -> bool:
        """完全匹配验证答案"""
        return self.normalize_answer(user_answer) == self.normalize_answer(correct_answer)
    
    def play_round(self, round_num: int) -> Dict[str, Any]:
        """进行一轮游戏"""
        print(f"\n🎯 第{round_num}轮 - 三国历史知识")
        
        # AI助手出题
        print("🤖 AI助手正在出题...")
        question_msg = BaseMessage.make_user_message("系统", f"请出第{round_num}个三国历史知识题目，必须输出JSON格式")
        ai_response = self.assistant.step(question_msg)
        
        if not ai_response.msgs:
            print("❌ AI助手未响应")
            return None
        
        # 解析题目
        ai_text = ai_response.msgs[0].content
        riddle = self.extract_json_riddle(ai_text)
        
        if not riddle['question'] or not riddle['answer']:
            print("❌ 题目格式错误")
            return None
        
        question = riddle['question']
        correct_answer = riddle['answer']
        
        print(f"📝 问题: {question}")
        
        # 参赛者答题
        print("🧑‍🎓 参赛者正在答题...")
        answer_msg = BaseMessage.make_user_message("出题者", question)
        user_response = self.contestant.step(answer_msg)
        
        if not user_response.msgs:
            print("❌ 参赛者未响应")
            return None
        
        user_answer = user_response.msgs[0].content.strip()
        
        # 验证答案
        is_correct = self.validate_answer(user_answer, correct_answer)
        
        # 存储结果
        result = {
            'round': round_num,
            'question': question,
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'correct': is_correct
        }
        
        self.rounds.append(result)
        self.total_rounds += 1
        if is_correct:
            self.correct_answers += 1
        
        # 显示结果
        print(f"💡 标准答案: {correct_answer}")
        print(f"🎯 用户回答: {user_answer} ({'✅正确' if is_correct else '❌错误'})")
        
        return result
    
    def play_game(self, max_rounds: int = 15, min_rounds: int = 8, threshold: float = 0.35) -> Dict[str, Any]:
        """运行完整游戏"""
        print("=" * 60)
        print("🎯 三国历史知识游戏开始！")
        print("🤖 AI出题助手 vs 🧑‍🎓 历史答题者")
        print("=" * 60)
        
        for round_num in range(1, max_rounds + 1):
            result = self.play_round(round_num)
            if not result:
                continue
            
            # 显示当前统计
            rate = self.correct_answers / self.total_rounds
            print(f"📊 当前正确率: {rate:.1%} ({self.correct_answers}/{self.total_rounds})")
            
            # 检查结束条件
            if round_num >= min_rounds and rate < threshold:
                print(f"\n⏰ 游戏结束！正确率 {rate:.1%} 低于 {threshold:.0%}")
                break
                
            time.sleep(1)
        
        # 最终结果
        print(f"\n{'='*50}")
        print("🏆 游戏结束")
        print("="*50)
        
        rate = self.correct_answers / self.total_rounds if self.total_rounds > 0 else 0
        
        # 成绩评级 - 更合理的评级标准
        if rate >= 0.75:
            grade, comment = "优秀", "三国历史知识大师！"
        elif rate >= 0.55:
            grade, comment = "良好", "历史功底不错！"
        elif rate >= 0.35:
            grade, comment = "及格", "继续加油！"
        else:
            grade, comment = "需要努力", "多学习三国历史！"
        
        print(f"总轮次: {self.total_rounds}")
        print(f"正确数: {self.correct_answers}")
        print(f"正确率: {rate:.1%}")
        print(f"等级: {grade}")
        print(f"评语: {comment}")
        
        # 显示详细记录（只显示最近5轮）
        if self.rounds:
            print(f"\n📋 详细记录（最近5轮）：")
            recent_rounds = self.rounds[-5:] if len(self.rounds) > 5 else self.rounds
            for r in recent_rounds:
                status = "✅" if r['correct'] else "❌"
                print(f"  第{r['round']:2d}轮: {r['question'][:30]}... → {r['user_answer'][:20]} {status}")
        
        return {
            'total_rounds': self.total_rounds,
            'correct_answers': self.correct_answers,
            'correct_rate': rate,
            'grade': grade,
            'comment': comment,
            'rounds': self.rounds
        }

if __name__ == "__main__":
    """主程序入口"""
    print("🎯 启动三国历史知识游戏...")
    
    game = SanGuoHistoryGame()
    result = game.play_game()
    
    print("\n✅ 三国历史知识游戏完成！")