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
    task_prompt = '''**背景：**
公司决定开发一款名为“每日清单”（DailyList）的新习惯追踪类App。核心功能包括：自定义习惯、每日打卡、数据统计和成就系统。公司要求该项目在4个月内完成并上线，初始研发团队有5人（1名后端、2名前端、1名UI/UX设计师、1名测试）。预算为50万元。

**你的任务是：**
为我编写一份初始的项目计划书草案。

**产出要求：**
- 使用专业项目文档的格式。
- 必须包含以下部分：
    1.  项目愿景与目标
    2.  主要功能范围界定（MoSCoW法则：Must-have, Should-have, Could-have）
    3.  里程碑计划（以月为单位，列出关键交付物）
    4.  资源分配与团队角色
    5.  主要风险及应对策略（至少列出3条）
- 语言简洁、逻辑清晰，便于向管理层汇报。'''
    model = ModelFactory.create(
        model_platform=ModelPlatformType.DEFAULT,
        model_type=ModelType.DEFAULT,
        model_config_dict=ChatGPTConfig(temperature=1.4, n=3).as_dict(),
    )
    assistant_agent_kwargs = dict(model=model)
    user_agent_kwargs = dict(model=model)
    role_play_session = RolePlaying(
        "经验丰富的IT项目经理",
        "企业CTO",
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
