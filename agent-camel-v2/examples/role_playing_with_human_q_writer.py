# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
from colorama import Fore

from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.societies import RolePlaying
from camel.types import ModelPlatformType, ModelType
from camel.utils import print_text_animated

from dotenv import load_dotenv

# Load environment variables
# 加载环境变量
load_dotenv()
def main() -> None:
    task_prompt = '''### **Task Prompt**

**【角色设定】**
你是一名经验丰富、深受学生喜爱的小学五年级语文教师。你擅长用生动、具体、易于理解的方式指导学生写作，尤其精通记叙文的写作技巧。你的教学风格亲切、鼓励性强，善于通过范文引路和步骤拆解来化解学生的畏难情绪。

**【核心任务】**
你的任务是：**为一节小学五年级语文课《如何写好一篇参观场馆的游记》设计一份完整的教学档案**。

**【背景与目标学生】**
本节课的教学对象是小学五年级学生，他们有一定的写作基础，但往往在游记写作中陷入“流水账”的困境，抓不住重点，缺乏真情实感和细节描写。本次教学旨在引导学生掌握“有重点、有顺序、有感受”地记录一次参观经历。

**【输出内容要求】**
请生成的教学档案需包含以下四个核心部分，内容需专业、具体、可操作性强：

**1. 教学目标**
*   清晰列出本节课在“知识与技能”、“过程与方法”、“情感态度与价值观”三个维度的具体目标。
    *   例如：学会抓住一两个展品进行详写，做到点面结合；学会按照一定的空间顺序进行叙述；能写出自己参观时的真实感受和想法。

**2. 教学重难点**
*   **教学重点**：指出本节课最核心要传授的知识点（如：如何筛选素材，抓住重点展品进行详写）。
*   **教学难点**：指出学生最可能遇到困难的地方（如：如何将看到的展品与自己的联想、感受结合起来，避免枯燥的说明）。

**3. 教学过程**
*   这是核心部分，请详细设计45分钟课堂的完整流程，建议分为以下几个环节：
    *   **导入（约5分钟）**：用一个有趣的问题或故事激发学生兴趣，引出课题。
    *   **范文引路，技法点拨（约15分钟）**：
        *   提供一篇简短优秀的范文（例如：《参观科技馆的奇妙之旅》片段）。
        *   **必须对范文进行精要的点评**，用划线、批注等方式，**高亮指出**范文哪里写得好（例如：这里用了比喻的修辞手法让展品很生动；这里通过心理描写写出了自己的惊讶之感；这里用“首先……接着……然后……”的词语清晰地交代了参观顺序）。
        *   基于范文，总结出“写作小妙招”或“神奇口诀”（如：1. 路线顺序要清晰；2. 重点展品细描摹；3. 感受想法不能少）。
    *   **写作构思指导（约10分钟）**：引导学生如何选择要写的场馆、如何列提纲。可以提供一个简单的思维框架图或提问清单（如：你最想介绍哪个场馆？哪个展品让你印象最深？它是什么样子？看到它你想到了什么？）。
    *   **课堂小结与布置作业（约5分钟）**：总结本节课要点，并布置完整的游记写作任务。

**4. 范文示例**
*   提供一篇**完整、高质量**的学生范文，字数在400字左右。
*   **范文要求**：
    *   标题明确，如《参观自然博物馆记》。
    *   结构清晰：开头（时间地点人物）、中间（详写一两个展品，略写其他）、结尾（感受总结）。
    *   语言生动：适当运用比喻、拟人等修辞手法，有真实的心理活动描写。
    *   在范文末尾，附上【教师评语】，再次点出这篇范文值得学习借鉴的2-3个优点，与前面的“技法点拨”相呼应。

**【输出风格】**
语言口语化，亲切自然，充满教学热情，符合小学教师的课堂用语习惯。提供的范文和点评要贴近小学五年级学生的认知水平和写作能力，具有极强的模仿和参考价值。
'''
    model = ModelFactory.create(
        model_platform=ModelPlatformType.DEFAULT,
        model_type=ModelType.DEFAULT,
        model_config_dict=ChatGPTConfig(temperature=1.4, n=3).as_dict(),
    )
    assistant_agent_kwargs = dict(model=model)
    user_agent_kwargs = dict(model=model)
    role_play_session = RolePlaying(
        "优秀著名教师",
        "行知小学5年级语文老师",
        critic_role_name="human",
        task_prompt=task_prompt,
        with_task_specify=True,
        with_critic_in_the_loop=True,
        assistant_agent_kwargs=assistant_agent_kwargs,
        user_agent_kwargs=user_agent_kwargs,
        output_language='中文',
    )

    print(
        Fore.GREEN
        + f"AI Assistant sys message:\n{role_play_session.assistant_sys_msg}\n"
    )
    print(
        Fore.BLUE + f"AI User sys message:\n{role_play_session.user_sys_msg}\n"
    )

    print(Fore.YELLOW + f"Original task prompt:\n{task_prompt}\n")
    print(
        Fore.CYAN
        + "Specified task prompt:"
        + f"\n{role_play_session.specified_task_prompt}\n"
    )
    print(Fore.RED + f"Final task prompt:\n{role_play_session.task_prompt}\n")

    chat_turn_limit, n = 50, 0
    input_msg = role_play_session.init_chat()
    while n < chat_turn_limit:
        n += 1
        assistant_response, user_response = role_play_session.step(input_msg)

        if assistant_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI Assistant terminated. Reason: "
                    f"{assistant_response.info['termination_reasons']}."
                )
            )
            break
        if user_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI User terminated. "
                    f"Reason: {user_response.info['termination_reasons']}."
                )
            )
            break

        print_text_animated(
            Fore.BLUE + f"AI User:\n\n{user_response.msg.content}\n"
        )
        print_text_animated(
            Fore.GREEN + f"AI Assistant:\n\n{assistant_response.msg.content}\n"
        )

        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

        input_msg = assistant_response.msg


if __name__ == "__main__":
    main()
