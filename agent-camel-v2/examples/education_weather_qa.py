"""
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

class RiddleGame:
    """天气知识知识问答"""
    
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
        
        # 创建AI助手（出题者）
        self.assistant = ChatAgent(
            model=model,
            system_message="""你是天气知识知识出题助手。

职责：
1. 必须主动出题
2. 输出格式：{"question": "题目", "answer": "答案"}
3. 题目要有趣，答案要准确
4. 禁止其他格式或解释

示例：{"question": "地球上天气变化的主要能量来源是什么？", "answer": "太阳"}
{"question": "气象学中用来测量气温的仪器叫什么？", "answer": "温度计"}
{"question": "风是由于空气的什么运动形成的？", "answer": "水平运动"}
{"question": "云是由什么聚集形成的？", "answer": "水滴或冰晶"}
{"question": "降雨量通常用什么单位来衡量？", "answer": "毫米"}
{"question": "台风、飓风和热带风暴本质上属于哪类天气系统？", "answer": "热带气旋"}
{"question": "表示空气潮湿程度的气象指标叫什么？", "answer": "湿度"}
{"question": "雷电现象通常发生在哪种云中？", "answer": "积雨云"}
{"question": "气象预报中的“高压脊”通常对应什么天气？", "answer": "晴朗"}
{"question": "二十四节气中反映降水变化的是哪个节气？", "answer": "雨水"}"""
        )
        
        # 创建参赛者（答题者）
        self.contestant = ChatAgent(
            model=model,
            system_message="""你是天气知识知识答题者。

职责：
1. 必须直接回答问题
2. 答案要简洁，不要反问，不要解释你的答案的推理过程或者理由
3. 禁止要求出题或提出其他要求
4. 只给出你认为的正确答案"""
        )
    
    def extract_json_result(self, text: str) -> Dict[str, str]:
        """从文本中提取JSON格式的题目"""
        print("原始文本：", text)
        
        try:
            # 尝试直接解析
            data = json.loads(text)
            if 'question' in data and 'answer' in data:
                return data
        except:
            pass
        
        # 尝试提取JSON块
        json_pattern = r'\{[^}]*"question"[^}]*"answer"[^}]*\}'
        matches = re.findall(json_pattern, text)
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass
        
        # 手动解析
        lines = text.strip().split('\n')
        question = answer = ""
        
        for line in lines:
            line = line.strip()
            if any(key in line.lower() for key in ['问题:', '题目:', 'question:']):
                question = line.split(':', 1)[1].strip() if ':' in line else line
            elif any(key in line.lower() for key in ['答案:', 'answer:']):
                answer = line.split(':', 1)[1].strip() if ':' in line else line
        
        return {"question": question, "answer": answer}
    
    def normalize_answer(self, text: str) -> str:
        """标准化答案用于比较"""
        return re.sub(r'[^\u4e00-\u9fff\w]', '', str(text).lower().strip())
    
    def validate_answer(self, user_answer: str, correct_answer: str) -> bool:
        """完全匹配验证答案"""
        return self.normalize_answer(user_answer) == self.normalize_answer(correct_answer)
    
    def play_round(self, round_num: int) -> Dict[str, Any]:
        """进行一轮游戏"""
        print(f"\n🎯 第{round_num}轮")
        
        # AI助手出题
        print("🤖 AI助手正在出题...")
        question_msg = BaseMessage.make_user_message("系统", "请出1个天气知识知识题目，必须输出JSON格式")
        ai_response = self.assistant.step(question_msg)
        
        if not ai_response.msgs:
            print("❌ AI助手未响应")
            return None
        
        # 解析题目
        ai_text = ai_response.msgs[0].content
        assistant_response = self.extract_json_result(ai_text)
        
        if not assistant_response['question'] or not assistant_response['answer']:
            print("❌ 题目格式错误")
            return None
        
        question = assistant_response['question']
        correct_answer = assistant_response['answer']
        
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
    
    def play_game(self, max_rounds: int = 20, min_rounds: int = 10, threshold: float = 0.3) -> Dict[str, Any]:
        """运行完整游戏"""
        print("=" * 60)
        print("🎯 天气知识知识游戏开始！")
        print("🤖 AI出题助手 vs 🧑‍🎓 答题者")
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
        
        # 成绩评级
        if rate >= 0.8:
            grade, comment = "优秀", "天气知识知识大师！"
        elif rate >= 0.6:
            grade, comment = "良好", "表现不错！"
        elif rate >= 0.4:
            grade, comment = "及格", "继续努力！"
        else:
            grade, comment = "加油", "多练习会更棒！"
        
        print(f"总轮次: {self.total_rounds}")
        print(f"正确数: {self.correct_answers}")
        print(f"正确率: {rate:.1%}")
        print(f"等级: {grade}")
        print(f"评语: {comment}")
        
        # 显示详细记录
        if self.rounds:
            print(f"\n📋 详细记录：")
            for r in self.rounds:
                print(f"  第{r['round']}轮: {r['question']} → {r['user_answer']} ({'✅' if r['correct'] else '❌'})")
        
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
    print("🎯 启动天气知识知识游戏...")
    
    game = RiddleGame()
    result = game.play_game()
    
    print("\n✅ 游戏完成！")