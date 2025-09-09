"""
通用角色扮演Agent构建器
基于 riddle_complete.py 规范格式

功能：
- 动态生成基于用户输入主题的AI助手和参赛者角色
- 支持任意知识领域：历史、科学、哲学、数学、文化等
- 标准化的游戏流程和结果验证
- 完全匹配答案判定和实时结果存储

使用方法：
python examples/universal_roleplay_agent.py
然后输入主题如：三国历史、量子力学、杭州历史文化等
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

class UniversalRoleplayGame:
    """通用角色扮演游戏类"""
    
    def __init__(self, topic: str):
        self.topic = topic
        self.rounds = []
        self.total_rounds = 0
        self.correct_answers = 0
        
        # 设置模型
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=800).as_dict()
        )
        
        # 动态生成角色定义
        self.assistant = ChatAgent(
            model=model,
            system_message=self.generate_assistant_prompt(topic)
        )
        
        self.contestant = ChatAgent(
            model=model,
            system_message=self.generate_contestant_prompt(topic)
        )
    
    def generate_assistant_prompt(self, topic: str) -> str:
        """根据主题生成AI助手的系统消息"""
        return f"""你是{topic}领域的专业出题助手。

职责：
1. 必须主动出题，基于{topic}相关知识
2. 输出格式：{{"question": "题目", "answer": "答案"}}
3. 题目要有教育意义，答案要准确简洁
4. 禁止其他格式或解释

示例格式：
{{"question": "关于{topic}的基础知识问题", "answer": "准确答案"}}
{{"question": "{topic}中的重要概念是什么？", "answer": "核心概念名称"}}
{{"question": "在{topic}中，什么是关键要素？", "answer": "关键要素描述"}}"""

    def generate_contestant_prompt(self, topic: str) -> str:
        """根据主题生成参赛者的系统消息"""
        return f"""你是{topic}领域的知识答题者。

职责：
1. 必须基于{topic}知识直接回答问题
2. 答案要简洁准确，不要反问，不要解释推理过程
3. 禁止要求出题或提出其他要求
4. 只给出你认为的正确答案"""

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
        print(f"\n🎯 第{round_num}轮 - {self.topic}")
        
        # AI助手出题
        print(f"🤖 AI助手({self.topic}专家)正在出题...")
        question_msg = BaseMessage.make_user_message("系统", f"请出第{round_num}个关于{self.topic}的题目，必须输出JSON格式")
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
        print(f"🧑‍🎓 参赛者({self.topic}答题者)正在答题...")
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
        
        # 显示结果
        print(f"💡 标准答案: {correct_answer}")
        print(f"🎯 用户回答: {user_answer} ({'✅正确' if is_correct else '❌错误'})")
        
        return result
    
    def play_game(self, max_rounds: int = 12, min_rounds: int = 6, threshold: float = 0.4) -> Dict[str, Any]:
        """运行完整游戏"""
        print("=" * 70)
        print(f"🎯 {self.topic}知识问答游戏开始！")
        print(f"🤖 AI{self.topic}专家 vs 🧑‍🎓 {self.topic}答题者")
        print("=" * 70)
        
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
        print(f"\n{'='*60}")
        print("🏆 游戏结束")
        print("="*60)
        
        rate = self.correct_answers / self.total_rounds if self.total_rounds > 0 else 0
        
        # 成绩评级 - 根据主题调整评级标准
        if rate >= 0.8:
            grade, comment = "优秀", f"{self.topic}知识大师！"
        elif rate >= 0.6:
            grade, comment = "良好", f"{self.topic}知识不错！"
        elif rate >= 0.4:
            grade, comment = "及格", f"继续学习{self.topic}！"
        else:
            grade, comment = "需要努力", f"多学习{self.topic}知识！"
        
        print(f"主题: {self.topic}")
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
                print(f"  第{r['round']:2d}轮: {r['question'][:40]}... → {r['user_answer'][:20]} {status}")
        
        return {
            'topic': self.topic,
            'total_rounds': self.total_rounds,
            'correct_answers': self.correct_answers,
            'correct_rate': rate,
            'grade': grade,
            'comment': comment,
            'rounds': self.rounds
        }

def get_topic_from_user() -> str:
    """从用户获取主题输入"""
    print("\n" + "="*60)
    print("🎯 通用角色扮演Agent构建器")
    print("="*60)
    print("支持的主题示例：")
    print("• 三国历史 • 量子力学 • 杭州历史文化")
    print("• 食物链 • 空气动力学 • 知识图谱")
    print("• 时间 • 鸡兔同笼 • 相遇问题")
    print("• 瞬时速度 • 哲学家尼采 • 抗日战争")
    print("• 台湾 • 浙江历史博物馆 • 任何你感兴趣的主题")
    print("="*60)
    
    while True:
        topic = input("请输入主题：").strip()
        if topic:
            return topic
        print("❌ 主题不能为空，请重新输入！")

def main():
    """主程序入口"""
    try:
        # 获取用户输入的主题
        topic = get_topic_from_user()
        
        print(f"\n✅ 正在启动 {topic} 知识问答游戏...")
        print("请稍等，正在初始化角色...")
        
        # 创建游戏实例
        game = UniversalRoleplayGame(topic)
        
        # 运行游戏
        result = game.play_game()
        
        print(f"\n✅ {topic} 知识问答游戏完成！")
        
        # 询问是否继续其他主题
        while True:
            continue_choice = input("\n是否继续其他主题？(y/n): ").strip().lower()
            if continue_choice in ['y', 'yes', '是']:
                main()  # 递归调用继续游戏
                break
            elif continue_choice in ['n', 'no', '否']:
                print("👋 感谢使用通用角色扮演Agent构建器！")
                break
            else:
                print("请输入 y 或 n")
                
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {str(e)}")

if __name__ == "__main__":
    main()