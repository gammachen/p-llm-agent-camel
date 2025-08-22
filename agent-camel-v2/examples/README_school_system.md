# 学校智能系统 (School Intelligent System)

## 系统概述

学校智能系统是基于CAMEL-AI框架构建的一个多Agent协同系统，旨在模拟并优化现实校园的运作，实现教育领域的数字孪生或"全息智慧校园大脑"。系统由多个专业化、人格化的AI Agent组成，这些Agent通过角色扮演的方式进行智能调度与交互，共同完成校园内的各种任务。

## 技术架构

- 基于CAMEL-AI框架实现
- 多Agent交互采用角色扮演模式
- 使用模拟数据支持系统构建
- 模块化设计，易于扩展

## 核心功能

1. **学生服务**：学习伴侣、任务代办、统一接口、数据看板
2. **教师服务**：教学助理、学情分析、日程管理、沟通中枢
3. **阅卷服务**：多模态批改、学情洞察、数据分发
4. **班级管理**：班级总控、预警干预、家校桥梁
5. **家长服务**：透明校园、授权沟通、成长档案
6. **行政服务**：资源调度、活动管理、档案管理
7. **健康服务**：健康监测、应急响应、咨询顾问
8. **餐饮服务**：食谱优化、安全溯源、个性化服务
9. **安保服务**：智能巡检、应急广播、访客管理
10. **决策支持**：决策驾驶舱、趋势洞察、资源规划

## 代理角色设计

系统设计了10个核心Agent角色，每个角色都有特定的职责和能力：

| 角色 | 职责描述 | 核心能力 |
|------|---------|---------|
| **学生代理** | 为每位学生提供个性化服务 | 学习伴侣、任务代办、统一接口、数据看板 |
| **学科教师代理** | 为每位学科教师提供教学助理服务 | 教学助理、学情分析、日程管理、沟通中枢 |
| **阅卷代理** | 为学校/年级组提供自动阅卷服务 | 多模态批改、学情洞察、数据分发 |
| **班主任代理** | 为每位班主任提供班级管理服务 | 班级总控、预警干预、家校桥梁 |
| **家长代理** | 为每位家长提供校园信息服务 | 透明校园、授权沟通、成长档案 |
| **教务行政代理** | 为教务处提供资源调度服务 | 资源调度、活动管理、档案管理 |
| **医务代理** | 为校医室提供健康监测服务 | 健康监测、应急响应、咨询顾问 |
| **营养膳食代理** | 为食堂提供食谱优化服务 | 食谱优化、安全溯源、个性化服务 |
| **安保代理** | 为保卫处提供智能巡检服务 | 智能巡检、应急广播、访客管理 |
| **校长/教导主任代理** | 为校领导提供决策支持服务 | 决策驾驶舱、趋势洞察、资源规划 |

## 系统架构

### 1. 基础Agent类

`SchoolAgent` 类是系统中所有代理的基类，扩展自CAMEL的`BaseAgent`类。它提供了代理间通信、消息处理、计划生成和执行等基础功能。每个具体代理角色都继承自`SchoolAgent`并实现其特定的功能。

### 2. 工具系统

系统为每个代理角色提供了一系列特定的工具，用于执行各种任务。工具采用`Tool`基类实现，每个工具都有唯一的标识符、描述和执行逻辑。

### 3. 会话管理

系统支持代理之间创建会话并进行消息传递，实现多Agent之间的交互。会话管理功能允许代理在特定上下文中进行沟通，并保持对话的连贯性。

### 4. 模拟数据

为支持系统构建，提供了学生、教师、家长和班级的模拟数据。这些数据存储在系统实例中，供各个代理访问和使用。

## 使用方法

### 1. 初始化系统

```python
from examples.camel_school_system import SchoolIntelligentSystem

# 创建学校智能系统实例
school_system = SchoolIntelligentSystem()
```

### 2. 创建代理

```python
# 创建学生代理
student_agent = school_system.create_student_agent("S001")

# 创建教师代理
teacher_agent = school_system.create_teacher_agent("T001")

# 创建班主任代理
head_teacher_agent = school_system.create_head_teacher_agent("T001")

# 创建家长代理
parent_agent = school_system.create_parent_agent("P001")
```

### 3. 代理间通信

```python
# 创建会话
session_id = school_system.create_session("student_S001", "teacher_T001")

# 发送消息
message = {
    "role": "student",
    "content": "赵老师，我想请教一下数学作业中的第5题怎么做？",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

# 获取响应
response = school_system.send_message(session_id, message)
```

## 模拟数据

系统内置了以下模拟数据：

### 学生数据

- S001: 张三，高一(1)班
- S002: 李四，高一(1)班
- S003: 王五，高二(2)班

### 教师数据

- T001: 赵老师，数学，高一(1)班
- T002: 钱老师，英语，高一(1)班、高二(2)班
- T003: 孙老师，物理，高二(2)班

### 家长数据

- P001: 张父，孩子S001
- P002: 李母，孩子S002
- P003: 王父，孩子S003

### 班级数据

- C001: 高一(1)班，班主任T001
- C002: 高二(2)班，班主任T003

## 关键辅助函数

### 1. 消息处理

```python
def process_message(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """
    处理传入的消息
    
    Args:
        message: 传入的消息
        session_id: 会话标识符
        
    Returns:
        响应消息
    """
```

### 2. 计划生成与执行

```python
def plan_next_action(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """
    根据消息和上下文规划下一个动作
    
    Args:
        message: 传入的消息
        session_id: 会话标识符
        
    Returns:
        动作计划
    """


def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """
    执行给定的计划
    
    Args:
        plan: 要执行的动作计划
        session_id: 会话标识符
        
    Returns:
        执行结果
    """
```

### 3. 会话管理

```python
def create_session(self, from_agent_id: str, to_agent_id: str) -> str:
    """
    创建Agent之间的会话
    
    Args:
        from_agent_id: 发送方Agent ID
        to_agent_id: 接收方Agent ID
        
    Returns:
        会话ID
    """


def send_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """
    在会话中发送消息
    
    Args:
        session_id: 会话ID
        message: 消息内容
        
    Returns:
        响应消息
    """
```

## 运行与测试

系统提供了一个简单的测试示例，可以通过运行以下命令进行测试：

```bash
python -m examples.camel_school_system
```

测试将创建几个示例代理，并演示它们之间的交互过程。

## 技术亮点

1. **模块化设计**：基于CAMEL框架的模块化设计，使系统易于扩展和维护。
2. **角色扮演交互**：多Agent之间采用角色扮演模式进行智能调度与交互，提高了系统的智能性和灵活性。
3. **工具化实现**：每个代理角色都配备了一系列特定的工具，用于执行各种任务。
4. **会话管理**：支持代理之间创建会话并进行消息传递，实现多Agent之间的交互。
5. **模拟数据支持**：提供了学生、教师、家长和班级的模拟数据，方便系统测试和演示。

## 注意事项

1. 本系统是一个模拟实现，实际应用中需要根据具体需求进行扩展和优化。
2. 系统使用了模拟数据，实际部署时需要接入真实的数据库或API。
3. 代理的行为和响应依赖于底层的语言模型，不同的模型可能会产生不同的结果。
4. 系统目前仅实现了基本功能，更多高级功能和优化可以根据需求进行开发。