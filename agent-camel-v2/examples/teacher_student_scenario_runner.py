# 导入必要的库和模块
from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from dotenv import load_dotenv
import os
import time
import sys

# 导入Comet监控器
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.comet_monitor import comet_monitor

# 加载环境变量
load_dotenv(dotenv_path='.env')
api_key = os.getenv('OPENAI_API_KEY', "ollama")  # 假设使用Ollama模型的API密钥

# 创建模型实例
def create_model():
    try:
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            url='http://localhost:11434/v1/',  # Ollama 的本地 API 地址
            model_type="qwen2",  # 使用Qwen模型
            api_key=api_key
        )
        return model
    except Exception as e:
        print(Fore.RED + f"创建模型实例失败: {e}")
        return None

# 定义教学任务场景
task_scenarios = [
    {
        "id": 1,
        "title": "分数入门",
        "task_prompt": "理解分数与除法的基本概念和简单运算",
        "assistant_role_name": "有趣的数学老师",
        "user_role_name": "四年级小学生",
        "learning_goal": "掌握分数的基本概念和简单加减法"
    },
    {
        "id": 2,
        "title": "自然探索",
        "task_prompt": "了解水循环的过程和重要性",
        "assistant_role_name": "自然探险家老师",
        "user_role_name": "好奇的小学生",
        "learning_goal": "理解水循环的基本过程及其在自然界中的作用"
    },
    {
        "id": 3,
        "title": "作文写作",
        "task_prompt": "学习如何写一篇关于'敦煌的认识'的作文",
        "assistant_role_name": "高级语文老师",
        "user_role_name": "需要帮助的小作家，小学四年级的学生",
        "learning_goal": "掌握记叙文的基本结构和写作技巧"
    },
    {
        "id": 4,
        "title": "英语学习",
        "task_prompt": "学习用英语描述日常活动和爱好",
        "assistant_role_name": "友好的英语外教",
        "user_role_name": "想学英语的小学生",
        "learning_goal": "掌握日常活动和爱好的英语表达方式"
    },
    {
        "id": 5,
        "title": "科学实验",
        "task_prompt": "通过简单实验了解物体的浮沉原理",
        "assistant_role_name": "科学实验老师",
        "user_role_name": "小小科学家",
        "learning_goal": "理解密度和浮力的基本概念"
    },
    {
        "id": 6,
        "title": "历史故事",
        "task_prompt": "了解中国古代四大发明的历史和影响",
        "assistant_role_name": "故事讲述者老师",
        "user_role_name": "爱听历史的小学生",
        "learning_goal": "了解四大发明及其对世界的贡献"
    },
    {
        "id": 7,
        "title": "艺术创作",
        "task_prompt": "学习用水彩画表现四季的变化",
        "assistant_role_name": "艺术老师",
        "user_role_name": "小画家",
        "learning_goal": "掌握基本的水彩技巧和色彩运用"
    },
    {
        "id": 8,
        "title": "健康生活",
        "task_prompt": "了解健康饮食的重要性并设计一份营养餐单",
        "assistant_role_name": "营养师老师",
        "user_role_name": "关心健康的小学生",
        "learning_goal": "认识食物金字塔和均衡饮食的重要性"
    },
    {
        "id": 9,
        "title": "环境保护",
        "task_prompt": "学习垃圾分类的方法和重要性",
        "assistant_role_name": "环保卫士老师",
        "user_role_name": "地球小卫士",
        "learning_goal": "掌握垃圾分类的基本知识和环保意识"
    },
    {
        "id": 10,
        "title": "数学应用",
        "task_prompt": "解决生活中的简单数学问题：购物找零",
        "assistant_role_name": "生活数学老师",
        "user_role_name": "会算账的小学生",
        "learning_goal": "应用加减乘除解决实际生活中的问题"
    },
    {
        "id": 11,
        "title": "儿童教育",
        "task_prompt": "关于孩子内驱力的课题研究",
        "assistant_role_name": "教育专家",
        "user_role_name": "普通的家长",
        "learning_goal": "概念与教育指导方案"
    }
]

# 运行单个任务场景
def run_single_scenario(scenario, model, chat_turn_limit=10):
    try:
        # 打印任务信息
        print(Fore.YELLOW + f"\n========== 任务 {scenario['id']}: {scenario['title']} ==========")
        print(Fore.CYAN + f"学习目标: {scenario['learning_goal']}")
        print(Fore.GREEN + f"教师角色: {scenario['assistant_role_name']}")
        print(Fore.BLUE + f"学生角色: {scenario['user_role_name']}")
        
        # 初始化角色扮演会话
        role_play_session = RolePlaying(
            assistant_role_name=scenario['assistant_role_name'],
            assistant_agent_kwargs=dict(model=model),
            user_role_name=scenario['user_role_name'],
            user_agent_kwargs=dict(model=model),
            task_prompt=scenario['task_prompt'],
            with_task_specify=True,  # 启用任务细化
            task_specify_agent_kwargs=dict(model=model),
            output_language='中文'  # 设置输出语言为中文
        )
        
        # 打印系统消息和任务信息
        print(Fore.YELLOW + f"原始任务:\n{scenario['task_prompt']}")
        print(Fore.CYAN + f"细化后的任务:\n{role_play_session.specified_task_prompt}")
        
        # 开始对话循环
        n = 0
        input_msg = role_play_session.init_chat()
        while n < chat_turn_limit:
            n += 1
            # 执行一步对话
            assistant_response, user_response = role_play_session.step(input_msg)
            
            # 检查终止条件
            if assistant_response.terminated or user_response.terminated:
                print(Fore.RED + "\n对话已终止。")
                break
                
            # 打印当前对话内容
            print_text_animated(Fore.BLUE + f"\n学生:\n\n{user_response.msg.content}\n")
            print_text_animated(Fore.GREEN + f"{scenario['assistant_role_name']}:\n\n{assistant_response.msg.content}\n")
            
            # 使用Comet记录对话内容
            comet_monitor.log_model_call(
                provider_name="qwen2",
                prompt=user_response.msg.content,
                response=assistant_response.msg.content,
                model="qwen2",
                scenario_id=scenario['id'],
                scenario_title=scenario['title'],
                assistant_role=scenario['assistant_role_name'],
                user_role=scenario['user_role_name']
            )
            
            # 检查任务是否完成
            if "明白了" in user_response.msg.content and ("谢谢" in user_response.msg.content or "感谢" in user_response.msg.content):
                print(Fore.YELLOW + f"\n学生表示理解了概念，任务完成!")
                break
                
            # 将老师的响应作为下一轮的学生输入
            input_msg = assistant_response.msg
            
        # 对话结束后稍作停顿
        time.sleep(2)
        
    except Exception as e:
        print(Fore.RED + f"运行任务 {scenario['id']} 时出错: {e}")

# 运行所有任务场景
def run_all_scenarios(model, chat_turn_limit=10, scenario_ids=None):
    # 如果指定了场景ID，则只运行这些场景
    if scenario_ids:
        scenarios_to_run = [scenario for scenario in task_scenarios if scenario['id'] in scenario_ids]
    else:
        scenarios_to_run = task_scenarios
        
    # 遍历并运行选定的场景
    for i, scenario in enumerate(scenarios_to_run):
        print(Fore.MAGENTA + f"\n开始运行场景 {i+1}/{len(scenarios_to_run)}")
        run_single_scenario(scenario, model, chat_turn_limit)
        print(Fore.MAGENTA + f"场景 {i+1}/{len(scenarios_to_run)} 运行完毕\n")
        
        # 如果不是最后一个场景，询问是否继续
        if i < len(scenarios_to_run) - 1:
            continue_choice = input(Fore.WHITE + "按Enter键继续下一个场景，或输入'q'退出: ")
            if continue_choice.lower() == 'q':
                print(Fore.YELLOW + "已停止运行剩余场景。")
                break

# 选择并运行指定的任务场景
def select_and_run_scenarios(model, chat_turn_limit=10):
    print(Fore.YELLOW + "\n===== 小学四年级教学场景列表 =====")
    for scenario in task_scenarios:
        print(Fore.WHITE + f"{scenario['id']}. {scenario['title']}")
    
    # 获取用户选择
    choice = input(Fore.WHITE + "\n请输入要运行的场景ID（多个ID用逗号分隔，或输入'all'运行所有场景）: ")
    
    if choice.lower() == 'all':
        run_all_scenarios(model, chat_turn_limit)
    else:
        try:
            scenario_ids = [int(id.strip()) for id in choice.split(',')]
            # 验证ID是否有效
            valid_ids = [scenario['id'] for scenario in task_scenarios]
            invalid_ids = [id for id in scenario_ids if id not in valid_ids]
            
            if invalid_ids:
                print(Fore.RED + f"无效的场景ID: {', '.join(map(str, invalid_ids))}")
                valid_ids_input = [id for id in scenario_ids if id in valid_ids]
                if valid_ids_input:
                    print(Fore.YELLOW + f"将运行有效的场景ID: {', '.join(map(str, valid_ids_input))}")
                    run_all_scenarios(model, chat_turn_limit, valid_ids_input)
            else:
                run_all_scenarios(model, chat_turn_limit, scenario_ids)
        except ValueError:
            print(Fore.RED + "输入无效，请输入数字ID或'all'。")

if __name__ == "__main__":
    # 创建模型实例
    model = create_model()
    if model is None:
        print(Fore.RED + "无法创建模型实例，程序退出。")
        sys.exit(1)
        
    # 获取聊天轮次限制（可选参数）
    try:
        chat_turn_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    except ValueError:
        chat_turn_limit = 10
        print(Fore.YELLOW + "无效的聊天轮次限制，使用默认值: 10")
    
    # 选择并运行场景
    select_and_run_scenarios(model, chat_turn_limit)
    
    # 结束Comet实验
    comet_monitor.end_experiment()
    print(Fore.GREEN + "\n教学场景运行完毕！")