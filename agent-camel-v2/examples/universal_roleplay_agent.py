"""
通用角色扮演Agent构建器 - 无警告版
基于 riddle_complete.py 规范格式，临时关闭CAMEL框架警告

功能：
- 动态生成基于用户输入主题的AI助手和参赛者角色
- 支持任意知识领域：历史、科学、哲学、数学、文化等
- 标准化的游戏流程和结果验证
- 完全匹配答案判定和实时结果存储

使用方法：
python examples/universal_roleplay_agent.py
然后输入主题如：三国历史、量子力学、杭州历史文化等

警告：已临时关闭CAMEL框架的上下文截断和令牌预算警告
"""
import os
import json
import re
import time
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage

# 临时关闭CAMEL框架警告
logging.getLogger('camel.camel.memories.context_creators.score_based').setLevel(logging.ERROR)
logging.getLogger('camel.camel.agents.chat_agent').setLevel(logging.ERROR)

load_dotenv()

class UniversalRoleplayGame:
    """通用角色扮演游戏类"""
    
    def __init__(self, topic: str):
        self.topic = topic
        self.rounds = []
        self.total_rounds = 0
        self.correct_answers = 0
        
        # 设置模型 - 减少令牌使用
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=500).as_dict()
        )
        
        # 更简洁的系统消息
        self.assistant = ChatAgent(
            model=model,
            system_message=f"你是{topic}专家，出题格式：{{\"q\":\"题\",\"a\":\"答\"}}"
        )
        
        self.contestant = ChatAgent(
            model=model,
            system_message=f"你是{topic}答题者，直接回答"
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
        try:
            # 支持简写格式q和a
            data = json.loads(text.strip())
            if 'q' in data and 'a' in data:
                return {"question": data['q'], "answer": data['a']}
            if 'question' in data and 'answer' in data:
                return data
        except:
            pass
        
        # 手动解析
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        question = answer = ""
        
        for line in lines:
            line_lower = line.lower()
            if any(key in line_lower for key in ['q:', '题:', 'question:']):
                question = line.split(':', 1)[1].strip('" }')
            elif any(key in line_lower for key in ['a:', '答:', 'answer:']):
                answer = line.split(':', 1)[1].strip('" }')
        
        if not question and lines:
            question = lines[0]
        if not answer and len(lines) > 1:
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
        question_msg = BaseMessage.make_user_message("系统", f"出{round_num}题")
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
        print(f"💡 {correct_answer}")
        print(f"🎯 {user_answer} ({'✅' if is_correct else '❌'})")
        
        return result
    
    def play_game(self, max_rounds: int = 4, min_rounds: int = 3, threshold: float = 0.4) -> Dict[str, Any]:
        """运行完整游戏"""
        print(f"\n🎮 {self.topic}问答")
        
        try:
            for round_num in range(1, max_rounds + 1):
                result = self.play_round(round_num)
                if not result:
                    continue
        
        except KeyboardInterrupt:
            pass
        
        # 结果统计
        accuracy = self.correct_answers / self.total_rounds if self.total_rounds > 0 else 0
        print(f"\n📊 {self.correct_answers}/{self.total_rounds}")
        
        return {
            'topic': self.topic,
            'total_rounds': self.total_rounds,
            'correct_answers': self.correct_answers,
            'accuracy': accuracy,
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