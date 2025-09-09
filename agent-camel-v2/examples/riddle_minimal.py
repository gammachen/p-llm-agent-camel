"""
极简版脑筋急转弯游戏 - 最小化令牌使用
Minimal Riddle Game with ultra-low token usage
"""
import json
import re
from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage
from dotenv import load_dotenv

load_dotenv()

class MinimalRiddleGame:
    """极简版脑筋急转弯游戏"""
    
    def __init__(self):
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict=ChatGPTConfig(
                temperature=0.7,
                max_tokens=1500  # 极低令牌限制
            ).as_dict()
        )
        
        # 超简洁系统消息
        self.assistant = ChatAgent(
            model=model,
            system_message="出题:JSON格式{'q':'题目','a':'答案'}"
        )
        
        self.contestant = ChatAgent(
            model=model,
            system_message="答题:直接回答"
        )
    
    def extract_riddle(self, text: str) -> dict:
        """快速提取题目答案"""
        try:
            # 找JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {"q": data.get("q", ""), "a": data.get("a", "")}
        except:
            pass
        
        # 快速提取
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 2:
            return {"q": lines[0], "a": lines[1]}
        return {"q": text, "a": ""}
    
    def normalize(self, text: str) -> str:
        """标准化"""
        return re.sub(r'[^\u4e00-\u9fff\w]', '', str(text).lower().strip())
    
    def play_round(self, round_num: int) -> bool:
        """玩一轮"""
        try:
            # 出题
            q_msg = BaseMessage.make_user_message("系统", f"出脑筋急转弯{round_num}")
            ai_resp = self.assistant.step(q_msg)
            
            riddle = self.extract_riddle(ai_resp.msgs[0].content)
            if not riddle["q"] or not riddle["a"]:
                return False
            
            print(f"\n🎯 {riddle['q']}")
            
            # 答题
            a_msg = BaseMessage.make_user_message("出题者", f"答：{riddle['q']}")
            user_resp = self.contestant.step(a_msg)
            
            user_answer = user_resp.msgs[0].content.strip()
            is_correct = self.normalize(user_answer) == self.normalize(riddle["a"])
            
            print(f"💡 答案: {riddle['a']}")
            print(f"🎯 回答: {user_answer} {'✅' if is_correct else '❌'}")
            
            return is_correct
            
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def play(self, rounds: int = 5):
        """运行游戏"""
        print("🎯 极简脑筋急转弯")
        correct = 0
        
        for i in range(1, rounds + 1):
            if self.play_round(i):
                correct += 1
        
        rate = correct / rounds
        print(f"\n🏆 {rounds}轮 正确{correct} 正确率{rate:.0%}")

if __name__ == "__main__":
    game = MinimalRiddleGame()
    game.play(3)  # 玩3轮