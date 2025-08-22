# 导入必要的库和模块
from colorama import Fore  # 用于终端彩色输出
from camel.societies import RolePlaying  # RolePlaying 核心类
from camel.utils import print_text_animated  # 动画效果打印文本
from camel.models import ModelFactory  # 模型工厂
from camel.types import ModelPlatformType  # 模型平台类型
from dotenv import load_dotenv  # 加载环境变量
import os

# 加载环境变量（例如API密钥）
load_dotenv(dotenv_path='.env')
api_key = os.getenv('OPENAI_API_KEY')  # 假设使用Qwen模型的API密钥

# 创建模型实例
# model = ModelFactory.create(
#     model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,  # 平台类型
#     model_type="Qwen/Qwen2.5-72B-Instruct",  # 指定模型名称
#     url='https://api-inference.modelscope.cn/v1/',  # API地址
#     api_key=api_key  # API密钥
# )

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,  # 平台类型
    model_type="qwen2",  # 指定 Ollama 中的模型名称
    url='http://localhost:11434/v1/',  # Ollama 的本地 API 地址
    api_key="ollama"  # Ollama 不需要 API 密钥，但需要提供一个值
)

def main(model=model, chat_turn_limit=50) -> None:
    # 1. 设置初始任务提示
    task_prompt = "为股票市场开发一个交易机器人"

    # 2. 初始化角色扮演会话
    role_play_session = RolePlaying(
        assistant_role_name="Python 程序员",  # AI助手角色
        assistant_agent_kwargs=dict(model=model),  # 助手模型配置
        user_role_name="股票交易员",  # AI用户角色
        user_agent_kwargs=dict(model=model),  # 用户模型配置
        task_prompt=task_prompt,  # 初始任务提示
        with_task_specify=True,  # 启用任务细化Agent
        task_specify_agent_kwargs=dict(model=model),  # 任务细化模型配置
        output_language='中文'  # 设置输出语言
    )

    # 3. 打印系统消息和任务信息（可选，便于调试和观察）
    print(Fore.GREEN + f"AI 助手系统消息:\n{role_play_session.assistant_sys_msg}\n")
    print(Fore.BLUE + f"AI 用户系统消息:\n{role_play_session.user_sys_msg}\n")
    print(Fore.YELLOW + f"原始任务提示:\n{task_prompt}\n")
    print(Fore.CYAN + "指定的任务提示:" + f"\n{role_play_session.specified_task_prompt}\n")
    print(Fore.RED + f"最终任务提示:\n{role_play_session.task_prompt}\n")

    # 4. 开始对话循环
    n = 0
    input_msg = role_play_session.init_chat()  # 初始化对话，获取第一条消息
    while n < chat_turn_limit:  # 限制最大对话轮数，避免无限循环
        n += 1
        # 4.1 执行一步对话
        assistant_response, user_response = role_play_session.step(input_msg)

        # 4.2 检查终止条件
        if assistant_response.terminated:
            print(Fore.GREEN + ("AI 助手已终止。原因: " f"{assistant_response.info['termination_reasons']}."))
            break
        if user_response.terminated:
            print(Fore.GREEN + ("AI 用户已终止。" f"原因: {user_response.info['termination_reasons']}."))
            break

        # 4.3 打印当前对话内容
        print_text_animated(Fore.BLUE + f"AI 用户:\n\n{user_response.msg.content}\n")
        print_text_animated(Fore.GREEN + "AI 助手:\n\n" f"{assistant_response.msg.content}\n")

        # 4.4 检查任务是否完成（例如，用户消息中包含特定完成标记）
        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

        # 4.5 将助手的响应作为下一轮的输入
        input_msg = assistant_response.msg

if __name__ == "__main__":
    main()