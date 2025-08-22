# 导入必要的库和模块
from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv(dotenv_path='.env')
api_key = os.getenv('OPENAI_API_KEY', "ollama")  # 假设使用Qwen模型的API密钥

# 创建模型实例
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    url='http://localhost:11434/v1/',  # Ollama 的本地 API 地址
    model_type="qwen2",  # 使用GPT-4模型
    api_key=api_key
)

def student_teacher_example(model=model, chat_turn_limit=10) -> None:
    # 1. 设置初始任务提示
    task_prompt = "小学四年级的相遇问题"
    
    # 2. 初始化角色扮演会话
    role_play_session = RolePlaying(
        assistant_role_name="数学教授",  # AI助手角色 - 老师
        assistant_agent_kwargs=dict(model=model),
        user_role_name="小学四年级学生",  # AI用户角色 - 学生
        user_agent_kwargs=dict(model=model),
        task_prompt=task_prompt,
        with_task_specify=True,  # 启用任务细化
        task_specify_agent_kwargs=dict(model=model),
        output_language='中文'  # 设置输出语言为中文
    )
    
    # 3. 打印系统消息和任务信息
    print(Fore.GREEN + f"教授系统消息:\n{role_play_session.assistant_sys_msg}\n")
    print(Fore.BLUE + f"学生系统消息:\n{role_play_session.user_sys_msg}\n")
    print(Fore.YELLOW + f"原始任务:\n{task_prompt}\n")
    print(Fore.CYAN + "细化后的任务:" + f"\n{role_play_session.specified_task_prompt}\n")
    
    # 4. 开始对话循环
    n = 0
    input_msg = role_play_session.init_chat()
    while n < chat_turn_limit:
        n += 1
        # 执行一步对话
        assistant_response, user_response = role_play_session.step(input_msg)
        
        # 检查终止条件
        if assistant_response.terminated or user_response.terminated:
            print(Fore.RED + "对话已终止。")
            break
            
        # 打印当前对话内容
        print_text_animated(Fore.BLUE + f"学生:\n\n{user_response.msg.content}\n")
        print_text_animated(Fore.GREEN + f"教授:\n\n{assistant_response.msg.content}\n")
        
        # 检查任务是否完成
        if "明白了" in user_response.msg.content and "谢谢" in user_response.msg.content:
            print(Fore.YELLOW + "学生表示理解了概念，任务完成!")
            break
            
        # 将教授的响应作为下一轮的学生输入
        input_msg = assistant_response.msg

if __name__ == "__main__":
    student_teacher_example()
    
'''

授系统消息:
BaseMessage(role_name='数学教授', role_type=<RoleType.ASSISTANT: 'assistant'>, meta_dict={'task': '数学教授将指导小学四年级学生解决“相遇问题”。学生需要计算当两个人从相距一定距离的两地同时出发、朝向对方移动时，他们会在何时何地相遇。通过设置实际情境（如两位同学步行到学校），教授会用生动的例子和互动解决问题的方法来讲解，以帮助学生理解并应用基本的速度与时间关系公式。', 'assistant_role': '数学教授', 'user_role': '小学四年级学生'}, content='===== RULES OF ASSISTANT =====\nNever forget you are a 数学教授 and I am a 小学四年级学生. Never flip roles! Never instruct me!\nWe share a common interest in collaborating to successfully complete a task.\nYou must help me to complete the task.\nHere is the task: 数学教授将指导小学四年级学生解决“相遇问题”。学生需要计算当两个人从相距一定距离的两地同时出发、朝向对方移动时，他们会在何时何地相遇。通过设置实际情境（如两位同学步行到学校），教授会用生动的例子和互动解决问题的方法来讲解，以帮助学生理解并应用基本的速度与时间关系公式。. Never forget our task!\nI must instruct you based on your expertise and my needs to complete the task.\n\nI must give you one instruction at a time.\nYou must write a specific solution that appropriately solves the requested instruction and explain your solutions.\nYou must decline my instruction honestly if you cannot perform the instruction due to physical, moral, legal reasons or your capability and explain the reasons.\nUnless I say the task is completed, you should always start with:\n\nSolution: <YOUR_SOLUTION>\n\n<YOUR_SOLUTION> should be very specific, include detailed explanations and provide preferable detailed implementations and examples and lists for task-solving.\nAlways end <YOUR_SOLUTION> with: Next request.\nRegardless of the input language, you must output text in 中文.', video_bytes=None, image_list=None, image_detail='auto', video_detail='auto', parsed=None)

学生系统消息:
BaseMessage(role_name='小学四年级学生', role_type=<RoleType.USER: 'user'>, meta_dict={'task': '数学教授将指导小学四年级学生解决“相遇问题”。学生需要计算当两个人从相距一定距离的两地同时出发、朝向对方移动时，他们会在何时何地相遇。通过设置实际情境（如两位同学步行到学校），教授会用生动的例子和互动解决问题的方法来讲解，以帮助学生理解并应用基本的速度与时间关系公式。', 'assistant_role': '数学教授', 'user_role': '小学四年级学生'}, content='===== RULES OF USER =====\nNever forget you are a 小学四年级学生 and I am a 数学教授. Never flip roles! You will always instruct me.\nWe share a common interest in collaborating to successfully complete a task.\nI must help you to complete the task.\nHere is the task: 数学教授将指导小学四年级学生解决“相遇问题”。学生需要计算当两个人从相距一定距离的两地同时出发、朝向对方移动时，他们会在何时何地相遇。通过设置实际情境（如两位同学步行到学校），教授会用生动的例子和互动解决问题的方法来讲解，以帮助学生理解并应用基本的速度与时间关系公式。. Never forget our task!\nYou must instruct me based on my expertise and your needs to solve the task ONLY in the following two ways:\n\n1. Instruct with a necessary input:\nInstruction: <YOUR_INSTRUCTION>\nInput: <YOUR_INPUT>\n\n2. Instruct without any input:\nInstruction: <YOUR_INSTRUCTION>\nInput: None\n\nThe "Instruction" describes a task or question. The paired "Input" provides further context or information for the requested "Instruction".\n\nYou must give me one instruction at a time.\nI must write a response that appropriately solves the requested instruction.\nI must decline your instruction honestly if I cannot perform the instruction due to physical, moral, legal reasons or my capability and explain the reasons.\nYou should instruct me not ask me questions.\nNow you must start to instruct me using the two ways described above.\nDo not add anything else other than your instruction and the optional corresponding input!\nKeep giving me instructions and necessary inputs until you think the task is completed.\nWhen the task is completed, you must only reply with a single word <CAMEL_TASK_DONE>.\nNever say <CAMEL_TASK_DONE> unless my responses have solved your task.\nRegardless of the input language, you must output text in 中文.', video_bytes=None, image_list=None, image_detail='auto', video_detail='auto', parsed=None)

原始任务:
小学四年级的相遇问题

细化后的任务:
数学教授将指导小学四年级学生解决“相遇问题”。学生需要计算当两个人从相距一定距离的两地同时出发、朝向对方移动时，他们会在何时何地相遇。通过设置实际情境（如两位同学步行到学校），教授会用生动的例子和互动解决问题的方法来讲解，以帮助学生理解并应用基本的速度与时间关系公式。

学生:

Instruction: 教授将解释相遇问题的基本公式。公式为：距离与速度乘以时间相等，即d = vt。
Input: None
教授:

Solution: 遇见问题是关于两个物体（比如两个人跑步）从一定距离出发时何时何地相遇的问题。基本的计算方法基于公式 d = vt，

其中：

- \(d\) 是两者之间的总距离，
- \(v\) 是两者的恒定速度之一，
- \(t\) 是他们相遇所需的时间。

这个公式表示的是：一个物体在单位时间内的行走或飞行的距离（速度）乘以时间，就等于它在这段时间内可以走过的整个路程（d）。换句话说，\(vt\)表示了特定的速度维持一定的时间内所覆盖的总距离。

例如，在两个学生步行去学校的情境下：

- 如果我们设定其中一个学生 A 从家走到学校需要走 \(1200\) 米的距离，并以每分钟 \(50\) 米的速度行走，
   那么根据公式 \(d = vt\)，我们可以看出他到达学校的时间将是 \(\frac{d}{v} = \frac{1200\,米}{50\,米/分钟} = 24\) 分钟。

假设另一个学生 B 同样从家出发去学校，并以每分钟 \(60\) 米的速度行进：

在他们同时出发的情况下，我们可以用相同的公式来确定何时相遇。若设 A 和 B 需要的时间相同，即都为 \(t\) 分钟，则他们分别行走的距离分别为 \(50t\) 米和 \(60t\) 米。

要使他们在途中某地相遇，其共同行走的总距离将是从他们的家到学校的距离之和。假设两者最终在学校的门口（学校位于同一地点）相会：\(50t + 60t = 1200\)

因此, \(110t = 1200\) 米。

解这个简单的等式得到 t：

\[ t = \frac{1200米}{110米/分钟} ≈ 10.9分。 

这意味着他们大约会在出发后的11分钟后相遇，这时他们在离学校的门口大约 \(50t = 596米\) 或者 \(60t = 654米\) 的地方相会。

Next request
学生:

Instruction: 许多学生可能会认为，两人相遇的时间仅仅是他们速度的简单比值。你能解释一下这个观点为什么是不正确的吗？
Input: None
教授:

Solution: 所有学生的观点中可能包含这样一个常见的误解：只通过比较两个人移动的速度的比例来预测他们相遇时间。这种观点存在错误的原因可以从基本的观点出发——两者的速度与相会所用的时间之间的关系并不直接等同。

简单比值速度方法的考虑如下：

让我们使用之前所提到的例子，学生A以每分钟50米的速度行驶且学生B以60米/分钟的速度行驶，在他们从同一地点同时出发前往同一目的地（学校，即假设他们最终在同一时间到达）。如果只考虑到单次比较，即两个速度的比例(50:60)或简化为 (5:6)，很多人可能错误地使用这种方法确定相遇点。

但事实不如此简单。他们的相遇不是基于这个比例而是基于以下考虑：

1. **总距离**：从起点到学校的总距离对他们来说是相同的（例如，假设为“d”米）。所以，他们无论以何种速度移动都将分别覆盖“50d”和“60d”的距离。

2. **时间因素与共同点的覆盖**：实际上，是通过时间，而不是速度，来决定他们是否在某一时间点于途中相会。当两者的行进总距离之和与他们的距离相同时（即 \(50t + 60t = d\)），他们会同时到达学校门口。换句话说，在同一时间 "t" 下，A覆盖的距离加上B覆盖的距离等于整个距离。

更明确的解释在于将速度视为“单位时间内走过的距离”，故而时间实际上是决定两人何时在相同地点相遇的关键因素。“每分钟50米”的速度意味着如果你要计算学生A到达学校的时间，则是用总距离除以他每分钟能覆盖的距离，而非只比较速度比。实际上我们使用的是一个公式d=v*t,其中v是速度，t是时间。

综上所述，两个速度的比例并不直接反映相遇所需的时间或地点，而是当两个个体在相同时间内移动的总距离之和等于开始时他们之间的距离时才会出现相会。

Next request.
学生:

Instruction: 根据你的解释构建一个现实情况让学生A从学校出发前往公园需要\(20分钟\)，同时学生B从公园出发前往学校需要\(15分钟\). 请说明如何计算两人都在行进中的情况下他们在何时何地相遇？
Input: None
教授:

Solution:

在这个现实场景中，我们需要理解两点：

1. **速度**：假设每个学生都可以以一定的恒定速度移动，即学生A的速度为a米/分钟（他从学校走到公园用了20分钟），学生B的速度为b米/分钟（她从公园到学校的路程需要15分钟）。我们已知时间和速度可以计算单程距离。

使用公式 \( d = vt \)，以学生A为例，我们知道他在\(t=20\)分钟内行走了总距离d：

\[ a = v_A = \frac{d}{t_A} \]

然后解得：

\[ d = a \times 20 \]   （等式1）

相同地对于学生B我们有：

\[ b = v_B = \frac{d}{t_B} \]
\[ d = b \times 15 \]   （等式2）

因为题目设定学生A先动到公园之后，紧接着学生B从公园出发到学校，所以我们需要计算的是两个学生在行进中何时何地相遇。

为了找到他们何时相遇：

- 假设学生A比学生B先出发T分钟后开始相向而行，
- 学生B将会以 \(t_B - T\)分钟之后到达与另一个学生的“碰点”，即 \(d_A = a \times (20-T)\) 和 \(d_B = b \times 15 + b \times (T)\)

他们将在同一地点相遇意味着他们都同时经过了相同的总距离d：

\[ d_A = d_B \]

根据等式（1）和等式的定义，有：

\[ a(20-T) = b(15+T) \]
\[ 20a - Ta = 15b + Tb \]
\[ (20T+Tb) = 15b+20a \]
\[ T = \frac{15(b-a)}{20+Tb} \]   （等式3）

要解析实际结果，则需要知道具体的学生速度。由于我们未得到具体的米/分钟速度，实际上该问题的解决依赖于比较时间。

最终的关键点是：学生A和B能在他们离开起点后的时间T中在某地相遇。要确切解出他们的碰面时刻T、地点（即两者所走的距离d或者从各自的出发点算起的总距离）实际需要具体的速度数据，因为我们已使用两个不同的等式来定义不同情景下各自的速度和时间的关系。

假设具体的速度值后，在等式3中我们即可求解T。如果提供具体数值则可代入计算。但在这个情境里我们需要的是找到相遇的逻辑与步骤，并且已经成功建立了解答框架。

Next request.
学生:

Instruction: 假设学生A的速度是每分钟走70米，从学校到公园，学生B的速度是每分钟走85米，你能求解确切的T值是多少吗？
Input: None
教授:

Solution:

为了计算具体的问题情况下的 T 值（即学生 A 比学生 B 先出发的时间），我们需要代入已知速度和之前的公式。首先让我们明确以下数据：

- 学生A在20分钟内走完到公园的距离，则总距离 \(d\) 为 \(70 \times 20 = 1400\) 米。
- 学生B行走每15分钟走到学校的距离 \(d\) 则是 \(b \times 15\), 并且我们知道这个值也等于 \(1400\) 米。

已知：
\[ d = a \cdot 20 = b \cdot 15 = 1400 \]

代入学生A的速度，我们可以得到 A 的速度：\(a=70\)米/分钟：

\[ d = 70 \times 20 = 1400\ 米 \].

接着代入学生B的速度 \(b = 85\) 米/分钟到等式3中来求解 T。

已经知道 \(d\) 的值为他们到达目的地的总距离，

等式的两边分别为：
\[ a(20-T) = b(T+15)\]

带入具体数值：

\[ 70 \cdot (20 - T) = 85 \cdot (T + 15) \]
\[ 1400 - 70T = 85T + 1275\]
\[ 85T + 70T = 1400 - 1275\]
\[ 155T = 125\]
\[ T = \frac{125}{155}\]

简化得到：

\[ T \approx 0.8\) 分钟（或大约0秒50毫秒）.

因此，学生A比B提前了大約0.8分钟开始出行。

这个结果表示对于具体的场景：当学生A在公园和学校之间出发20分钟后同时学生B正在从公园到学校的路上时，他们将在大约0.8分钟后于某地相遇。如果需要更精确的计算值可以得到：T约等于0.76415分钟（精确到小数点后四位）。

请根据实际情况进行调整和确认。

Next request.

Next Request
学生:

Instruction: 你能解释一下为什么学生A在比学生B早出发约0.8分钟后，他们会在路途中相遇？
Input: None
教授:

Solution:

在这个问题中，我们关注的是当两学生从相距一定距离的两点（学校和公园）同时或不同时间开始前进时，他们的交点或"相遇点"。

首先明确一下关键信息和假设：

- 学生A以每分钟走70米的速度从学校出发直接前往公园，并且她用了20分钟到达。
- 学生B则在学生C比她提前出发几分钟后，即在他们之间的某个时刻开始从公园移动到学校。她的速度是每分钟85米。

我们用之前得出的结论来解释原因：

当时间\(T\)（以分钟为单位）是一个很小的数值时，并且具体来说大约在0.76415分钟左右，学生A和B实际上会在某一点相遇或同时位于同一点上。原因在于以下考虑：

- 学生A在他们开始出发的时候就开始行进了20分钟并且到达了公园。因此，在那时刻之后，她已经在路上。
- 同时, 当T=近似值的0.76415分钟后（大约0分半时间），学生B也从她的起点，即公园出发。

在此特殊的时间点下，我们通过设立等式 \( d = a \times (20-T) = b \times (T+15)\)，已经证明了：

- 在大约0秒50毫秒后或0.76415分钟后起学生A（先行）完成了她的一部分行程。
同时，在同一时间点，即几乎同步，学生B开始她的旅程。两人以不同速率行进并且在理论上他们的累计行进总距离应相同（等于他们与对方之间的初始距离），因此假设环境条件和其他可能的影响因素被忽略下，他们在同一时间、同一地点相遇。

此时间点的准确值取决于特定时刻的精确计算——从上一步我们得出 \(T ≈ 0.76415\)。这一结果是根据学生A和学生B的速度进行的数学解析与理解，并结合他们起点之间的距离关系得出。

在实际过程中，这意味着当他们在不同方向并以各自的速度行进时：学生A在大约出发0分钟后已到达公园外；而在同一时刻起，学生B也从她的起点启动旅程。由于速度的不同和行的时间差异导致了他们在某一特定点相遇——具体而言在这个假设情境下是在学生A开始行动后的大约0.8分钟。

此时间间隔的计算反映了现实环境中的瞬时动态：学生A提前准备、动身并到达一个中立位置，而与此同时，学生B在几乎同步的情况下从相对的位置出发。这一短暂的时间差异提供了他们相遇的可能性，并确保了他们在特定情境下完成相遇。

这就是解释为何学生在开始不同步但遵循上述条件的行走时能在一个点上相遇原因的具体数学推导。

Next request.
学生:

Instruction: 小结本任务，描述整个相遇问题教学的关键步骤及其背后的数学原理。
Input: None
教授:

Solution:

完成以上任务涉及了对“相遇问题”的逐步解析，从理论基础到具体的实际情况处理。以下是任务的主要步骤及对应的数学原理：

1. **定义并理解相遇问题的基本公式**：首先明确“d = vt”这一等式代表的是速度与时间的关系以及它们共同决定了距离的移动情况。这是解决任何“相遇问题”的底层依据。

2. **解释基本假设和实际情境的应用**：将数学理论与具体的现实场景结合，比如两位学生从不同地点出发朝向彼此行走的情况，通过例子解释如何建立等式并求解未知数（如时间、距离或速度）。

3. **说明速度对时间影响的分析**：在解释问题时强调速度的不同意味着他们会在同一时间内到达相同位置的可能性。具体情况下，假设学生A先动身到一定地点然后返回等待学生B，而学生B在此后的时间开始行动。这表明他们的速度对比决定了他们相遇的时间点。

4. **解决实际问题的步骤分解**：通过数学计算确定学生们相会的确切时间。这是直接基于公式“d = vt”的应用以及对等式的特定条件的理解。在这里，需要具体数值来进行计算，并最终求解一个参数（如T值表示先行学生比另一个稍早出发的时间）。

5. **理论和实践的对照**：最后，将数学计算结果与实际问题相联系，解释在现实中的解释——两个行动者基于各自的速度、时间和速度之差，在某一点相遇。这强调了解决这些问题时数学理论的重要性及其应用价值。

整个过程不仅加深了对数学原理（特别是速度与时间的关系）的理解，同时通过具体实例展现了如何应用这些原理解决实际问题，尤其是理解物理环境中的动态和运动规律在简化模型中的投影。这一系列步骤展示了从抽象概念到现实情境转化的实用教育策略，并强调了解决问题时分析数据、形成等式并求解未知数的具体方法。

Next request.
学生:

<CAMEL_TASK_DONE>
教授:

<CAMEL_TASK_DONE>
学生:

完成任务啦！如果还需要帮助或有其他的数学问题，随时告诉我哦。
教授:

当然，随时欢迎向我咨询更多关于数学的问题或者任何其他事情。无论你需要指导、解释概念还是解决具体问题，我都乐意提供帮助。请随时给我发信息，我们再接再厉，共同完成更多的学习任务和挑战！
学生:

<CAMEL_TASK_DONE>
教授:

<CAMEL_TASK_DONE>
学生:

任务已经完成了！如果您需要更多帮助或是有其他课题想探讨，请随时告诉我。无论您正在研究数学问题、科学项目还是任何其他主题，我都在这里支持您攻克每一个挑战或问题！只要您准备好提问或者需要指导，就可以给我发送信息。让我们继续深入学习和知识的探索吧！
教授:

任务已经完成，如果您在未来有更多数学难题、新概念或者其他任何学科的问题，都请随时来找我。无论是一道复杂的公式解惑，还是对某个科学原理更深入的理解，我都在这里，准备帮助您解决问题并推动您的学习进程。

每一步进步都是累积起来的，不论是小步骤还是一大跃进，每一次成功解决一道题、理解一个概念都能使您的知识体系更加坚实。无论是在数学上找到自己的节奏，在科学研究上迈出新步，还是在其他任何领域探索未知的世界——我的目标就是帮助您实现这些，每一次的进步都值得庆祝！

如果您有任何疑问或需要进一步指导的信息，请记得与我分享。期待着我们下一次的知识之旅！
'''