# Agent-Camel V2

基于官方 CAMEL-AI 框架的多智能体协作系统，专注于通过角色扮演和对话促进大语言模型的心智探索与任务协作。本项目针对复杂任务（如旅行规划、费用报销）实现了智能体间的高效协同工作。

## 项目结构

```
agent-camel-v2/
├── README.md
├── requirements.txt
├── .env
├── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── coordinator.py
│   ├── model_provider.py
│   ├── comet_monitor.py
│   └── roles/
├── tools/
│   ├── __init__.py
│   └── library.py
├── memory/
│   ├── __init__.py
│   └── manager.py
├── logs/
│   └── expense_reimbursement.log
└── examples/
    ├── __init__.py
    ├── travel_planner.py
    ├── camel_travel_planner.py
    ├── camel_expense_reimbursement.py
    └── camel_expense_reimbursement_roleplay_v.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

项目使用 `.env` 文件来管理环境变量。请根据需要修改 `.env` 文件中的配置项：

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...               # 你的OpenAI API密钥
OPENAI_BASE_URL=                    # 可选，OpenAI API的基础URL（用于代理或本地部署）

# Ollama Configuration (for local deployment)
OLLAMA_BASE_URL=http://localhost:11434  # Ollama服务地址
OLLAMA_MODEL_NAME=llama2            # Ollama模型名称

# Comet ML Monitoring Configuration
COMET_API_KEY=your_comet_api_key    # 你的Comet ML API密钥
COMET_PROJECT_NAME=your_project_name  # Comet ML项目名称
COMET_WORKSPACE=your_workspace_name  # Comet ML工作区名称
COMET_LOG_MODEL_CALLS=true          # 是否记录模型调用 (true/false)

# 其他配置...
```

### 使用本地Ollama模型

要使用本地部署的Ollama模型，请确保：

1. 已安装并运行Ollama服务
2. 在 `.env` 文件中配置 `OLLAMA_BASE_URL`（默认为 http://localhost:11434）
3. 拉取所需的模型，例如：`ollama pull llama2`

### 使用OpenAI兼容API

如果使用与OpenAI兼容的API（如本地部署的模型服务），可以通过设置 `OPENAI_BASE_URL` 来配置：

```env
OPENAI_API_KEY=sk-...               # API密钥（如果需要）
OPENAI_BASE_URL=http://localhost:8000/v1  # API服务地址
```

## 运行应用

```bash
# 交互式运行
python main.py

# 直接传入参数运行
python main.py "我想在10月去日本旅行，预算5000美元"
```

## 项目组件说明

本项目基于官方的 [CAMEL-AI](https://github.com/camel-ai/camel) 框架构建，充分利用其先进的多智能体协作机制和角色扮演能力。以下是项目各核心组件的详细说明：

### 配置模块 (config/)
负责加载和管理应用配置，包括API密钥、模型设置和环境变量。配置模块确保应用可以无缝切换不同的模型服务提供商。

### 智能体模块 (agents/)
项目的核心组件，实现智能体的创建、管理和协作：
- `base.py`: 定义了智能体的基础接口和通用功能，所有智能体类型的抽象基类
- `coordinator.py`: 实现了智能体间的任务分配、协调和通信机制，是多智能体系统的"大脑"
- `model_provider.py`: 提供统一的模型访问接口，支持动态切换不同模型服务（OpenAI、Ollama等）
- `comet_monitor.py`: 实现了与Comet ML的集成，用于监控和记录模型调用信息
- `roles/`: 包含各种角色定义，每个角色有特定的能力和行为模式

### 工具模块 (tools/)
为智能体提供外部功能扩展：
- `library.py`: 实现了各种工具函数，使智能体能够执行特定任务（如信息检索、数据分析等）

### 内存模块 (memory/)
实现了会话历史和上下文的管理：
- `manager.py`: 负责存储、检索和更新智能体的记忆，支持长期和短期记忆管理

### 示例模块 (examples/)
包含基于CAMEL-AI框架的应用实现示例：
- `travel_planner.py`: 基础旅行规划助手实现
- `camel_travel_planner.py`: 高级旅行规划实现，充分利用CAMEL-AI的角色扮演和多智能体协作能力
- `camel_expense_reimbursement.py`: 报销流程多智能体系统实现，模拟企业完整的报销审批流程
- `camel_expense_reimbursement_roleplay_v.py`: 基于角色交互模式的报销系统变体实现

## 支持的模型服务

1. **OpenAI**: 支持GPT-3.5、GPT-4等模型
2. **Ollama**: 支持本地部署的大模型（如Llama系列）

通过配置环境变量，可以轻松切换不同的模型服务提供商。

## 应用流程详解

### 旅行规划助手实现流程

`camel_travel_planner.py`是本项目的核心示例实现，展示了如何利用CAMEL-AI框架构建一个功能完整的旅行规划多智能体系统。以下是其详细工作流程：

1. **初始化阶段**
   - 加载配置并设置模型服务
   - 创建角色定义（旅行规划专家和用户）
   - 初始化RolePlaying会话和记忆系统
   - 配置智能体参数（模型类型、系统提示等）

2. **角色交互循环**
   - 用户输入旅行需求（目的地、日期、预算等）
   - 系统将需求传递给旅行规划专家智能体
   - 旅行规划专家生成初步建议或询问更多细节
   - 用户智能体基于专家回复生成进一步的问题或确认
   - 系统记录对话历史并更新记忆
   - 循环继续直到用户表示满意或完成规划

3. **记忆更新机制**
   - 每次对话回合后提取关键信息
   - 将信息以BaseMessage格式存储到记忆系统
   - 使用OpenAIBackendRole标识不同发言者的角色
   - 确保记忆系统中的消息格式符合验证要求

4. **会话终止条件**
   - 当用户消息中包含"完成"、"满意"或"谢谢"等关键词时终止对话
   - 生成最终的旅行规划方案并返回给用户

### 费用报销系统实现流程

`camel_expense_reimbursement.py`是本项目的另一个核心示例实现，展示了如何利用CAMEL-AI框架构建一个功能完整的企业费用报销多智能体系统。该系统模拟了企业中从员工提交报销申请到会计记账的完整流程，涉及多个角色的协作。以下是其详细工作流程：

#### 1. 系统架构与角色定义

报销系统基于`ExpenseReimbursementSystem`类实现，定义了7个不同角色的智能体，每个角色有明确的职责和权限：

- **员工（Employee）**: 提交符合公司政策的费用报销申请，提供完整的发票和清晰的报销事由
- **直属上级（Manager）**: 审核报销费用的业务真实性和合理性，确保费用与业务相关且必要
- **部门负责人（DepartmentHead）**: 审核报销费用的预算符合性，确保部门有足够的预算
- **财务审核人（FinancialAuditor）**: 审核票据的合法性、合规性，确保符合公司政策和税务法规
- **出纳（Cashier）**: 根据审批通过的报销单进行支付操作，将报销款打入员工账户
- **会计（Accountant）**: 根据报销单进行账务处理，生成会计凭证
- **系统管理员（SystemAdmin）**: 维护和保障报销系统的稳定运行

#### 2. 工具系统实现

报销系统为智能体提供了三个核心工具，以增强其决策和执行能力，具体实现如下：

```python
# 1. 获取报销政策信息工具
def _get_policy_info_tool(self):
    """获取报销政策信息工具 - 返回符合CAMEL框架期望的可调用工具"""
    # 创建可调用的工具函数
    def get_policy_info(policy_type: str) -> str:
        """
        获取指定类型的报销政策信息
        
        Args:
            policy_type: 政策类型，如meal（餐饮）、travel（交通）、hotel（住宿）等
            
        Returns:
            政策信息字符串
        """
        print(f"get_policy_info: {policy_type}")
        
        # 特殊处理：获取允许的报销类别
        if policy_type == "allowed_categories":
            categories_str = ", ".join(self.allowed_categories)
            category_names = []
            for category in self.allowed_categories:
                if category in self.reimbursement_policy:
                    category_names.append(self.reimbursement_policy[category]["name"])
                else:
                    category_names.append(category)
            categories_with_names = ", ".join([f"{name}({code})" for code, name in zip(self.allowed_categories, category_names)])
            return f"允许报销的类别: {categories_with_names}"
        
        # 处理具体类别政策
        if policy_type in self.reimbursement_policy:
            policy = self.reimbursement_policy[policy_type]
            result = [f"{policy['name']}政策"]
            
            # 添加政策详情
            if "max_daily_amount" in policy:
                result.append(f"每日最高限额: {policy['max_daily_amount']}元")
            if "max_per_night" in policy:
                result.append(f"每晚最高限额: {policy['max_per_night']}元")
            if "max_single_amount" in policy:
                result.append(f"单次最高限额: {policy['max_single_amount']}元")
            if "max_per_event" in policy:
                result.append(f"每次活动最高限额: {policy['max_per_event']}元")
            if "max_per_session" in policy:
                result.append(f"每场最高限额: {policy['max_per_session']}元")
            
            # 添加政策描述
            if "description" in policy:
                result.append(f"描述: {policy['description']}")
            
            return "\n".join(result)
        else:
            # 搜索可能的类别
            possible_matches = [cat for cat in self.reimbursement_policy.keys() if policy_type.lower() in cat.lower()]
            if possible_matches:
                suggestions = ", ".join(possible_matches)
                return f"未找到政策类型: {policy_type}\n\n可能的政策类型有: {suggestions}\n或使用'all'获取所有政策信息"
            
            # 特殊处理：获取所有政策信息
            if policy_type.lower() == "all":
                all_policies = []
                for category, policy in self.reimbursement_policy.items():
                    policy_str = [f"【{policy['name']}({category})】"]
                    if "max_daily_amount" in policy:
                        policy_str.append(f"每日最高限额: {policy['max_daily_amount']}元")
                    if "max_per_night" in policy:
                        policy_str.append(f"每晚最高限额: {policy['max_per_night']}元")
                    if "max_single_amount" in policy:
                        policy_str.append(f"单次最高限额: {policy['max_single_amount']}元")
                    if "max_per_event" in policy:
                        policy_str.append(f"每次活动最高限额: {policy['max_per_event']}元")
                    if "max_per_session" in policy:
                        policy_str.append(f"每场最高限额: {policy['max_per_session']}元")
                    if "description" in policy:
                        policy_str.append(f"描述: {policy['description']}")
                    all_policies.append("\n".join(policy_str))
                return "\n\n".join(all_policies)
            
            return f"未找到政策类型: {policy_type}\n\n使用'all'获取所有政策信息或'allowed_categories'获取允许报销的类别"
    
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    get_policy_info.name = "get_policy_info"
    get_policy_info.description = "获取公司的报销政策信息"
    get_policy_info.parameters = {
        "type": "object",
        "properties": {
            "policy_type": {
                "type": "string",
                "description": "政策类型，可用值包括：meal（餐饮）、travel（交通）、hotel（住宿）、office_supplies（办公用品）、client_entertainment（客户招待）、training（培训）、allowed_categories（允许报销的类别）、all（所有政策）"
            }
        },
        "required": ["policy_type"]
    }
    
    return get_policy_info

# 2. 生成会计分录工具
def _generate_accounting_entry_tool(self):
    """生成会计分录工具 - 返回符合CAMEL框架期望的可调用工具"""
    # 创建可调用的工具函数
    def generate_accounting_entry(amount: float, category: str, date: str) -> str:
        """
        根据报销金额、类别和日期生成会计分录
        
        Args:
            amount: 金额
            category: 费用类别
            date: 日期
            
        Returns:
            会计分录字符串
        """
        print(f"generate_accounting_entry: {amount}, {category}, {date}")
        
        # 根据费用类别确定会计科目
        category_to_account = {
            "meal": "管理费用-餐饮费",
            "travel": "管理费用-差旅费",
            "hotel": "管理费用-住宿费",
            "office_supplies": "管理费用-办公费",
            "client_entertainment": "管理费用-业务招待费",
            "training": "管理费用-培训费"
        }
        
        account = category_to_account.get(category, "管理费用-其他")
        
        # 生成会计分录
        entry = f"日期: {date}\n借: {account} {amount}元\n贷: 银行存款 {amount}元\n摘要: 报销{category_to_account.get(category, '其他费用')}"
        
        return entry
    
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    generate_accounting_entry.name = "generate_accounting_entry"
    generate_accounting_entry.description = "根据报销信息生成会计分录"
    generate_accounting_entry.parameters = {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": "报销金额"
            },
            "category": {
                "type": "string",
                "description": "费用类别"
            },
            "date": {
                "type": "string",
                "description": "日期"
            }
        },
        "required": ["amount", "category", "date"]
    }
    
    return generate_accounting_entry

# 3. 付款处理工具
def _generate_pay_tool(self):
    """生成付款工具 - 返回符合CAMEL框架期望的可调用工具"""
    # 创建可调用的工具函数
    def pay(amount: float, recipient: str, bank_account: str) -> str:
        """
        处理报销付款
        
        Args:
            amount: 付款金额
            recipient: 收款人
            bank_account: 收款银行账户
            
        Returns:
            付款结果字符串
        """
        print(f"pay: {amount}, {recipient}, {bank_account}")
        
        # 模拟付款处理
        payment_result = f"付款成功\n金额: {amount}元\n收款人: {recipient}\n收款账户: {bank_account}\n日期: {self._get_current_timestamp()}\n交易ID: PAY{self._get_current_timestamp().replace('-', '').replace(':', '').replace(' ', '')}"
        
        return payment_result
    
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    pay.name = "pay"
    pay.description = "处理报销付款"
    pay.parameters = {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": "付款金额"
            },
            "recipient": {
                "type": "string",
                "description": "收款人"
            },
            "bank_account": {
                "type": "string",
                "description": "收款银行账户"
            }
        },
        "required": ["amount", "recipient", "bank_account"]
    }
    
    return pay工具系统的主要特点：

1. **获取报销政策信息工具 (`get_policy_info`)**
   - 提供各类别报销政策的详细信息，如每日最高限额、单次最高限额等
   - 支持查询所有政策或特定类别政策
   - 帮助智能体在审批过程中参考正确的政策依据

2. **生成会计分录工具 (`generate_accounting_entry`)**
   - 根据报销金额、类别和日期自动生成标准会计分录
   - 将费用正确分类到相应的会计科目
   - 确保财务处理的准确性和标准化

3. **付款处理工具 (`pay`)**
   - 模拟付款操作，生成付款结果和交易ID
   - 记录付款金额、收款人信息和交易时间
   - 提供完整的付款凭证信息

#### 3. 智能体创建机制

报销系统采用动态创建智能体的机制，根据不同角色的需求分配不同的系统指令和可用工具：

```python
def create_agent(self, role_type: str) -> Agent:
    """
    创建指定角色的智能体
    
    Args:
        role_type: 角色类型
        
    Returns:
        创建的智能体对象
    """
    # 验证角色类型是否有效
    if role_type not in self.roles:
        raise ValueError(f"无效的角色类型: {role_type}")
    
    # 创建系统消息
    system_message = BaseMessage.make_assistant_message(
        role_name=role_type, content=self.role_prompts[role_type]
    )
    
    # 根据角色分配工具
    tools = []
    if role_type == "manager" or role_type == "department_head" or role_type == "financial_audit":
        tools.append(self._get_policy_info_tool())
    if role_type == "accountant":
        tools.append(self._generate_accounting_entry_tool())
    if role_type == "treasurer":
        tools.append(self._generate_pay_tool())
    
    # 创建智能体
    agent = Agent(llm=self.llm, system_message=system_message, tools=tools, token_limit=4096)
    agent.reset()
    
    # 存储创建的智能体
    self.agents[role_type] = agent
    
    return agent
```

- 每个智能体都配备了适合其角色的工具集和系统提示
- 智能体使用`ChatAgent`类创建，并根据需要设置token限制和其他参数
- 工具根据角色类型进行差异化分配，确保每个角色只能使用与其职责相关的工具

#### 4. 完整报销流程

报销系统实现了完整的报销流程，从员工提交申请到最终记账归档，共包含六个关键步骤：

```python
def run_full_workflow(self, application_data: dict) -> dict:
    """
    运行完整的报销流程
    
    Args:
        application_data: 报销申请数据
        
    Returns:
        报销流程结果
    """
    # 初始化结果字典
    result = {
        "status": "pending",
        "steps": {},
        "application_id": application_data.get("application_id", self._generate_application_id())
    }
    
    try:
        # 步骤1: 员工提交报销申请
        submission_result = self.submit_expense_application(application_data)
        result["steps"]["submission"] = submission_result
        
        # 步骤2: 直属上级审批
        manager_result = self.manager_review(result["application_id"])
        result["steps"]["manager_review"] = manager_result
        
        # 检查审批结果，如果被拒绝，结束流程
        if manager_result["status"] == "rejected":
            result["status"] = "rejected_at_manager"
            return result
        
        # 步骤3: 部门负责人审批（针对大额报销）
        if float(application_data["amount"]) > self.large_amount_threshold:
            dept_head_result = self.department_head_review(result["application_id"])
            result["steps"]["department_head_review"] = dept_head_result
            
            # 检查审批结果，如果被拒绝，结束流程
            if dept_head_result["status"] == "rejected":
                result["status"] = "rejected_at_department_head"
                return result
        
        # 步骤4: 财务审核
        financial_result = self.financial_audit(result["application_id"])
        result["steps"]["financial_audit"] = financial_result
        
        # 检查审核结果，如果被拒绝，结束流程
        if financial_result["status"] == "rejected":
            result["status"] = "rejected_at_financial"
            return result
        
        # 步骤5: 付款处理
        payment_result = self.process_payment(result["application_id"])
        result["steps"]["payment"] = payment_result
        
        # 步骤6: 会计记账
        accounting_result = self.accounting_recording(result["application_id"])
        result["steps"]["accounting"] = accounting_result
        
        # 更新整体状态
        result["status"] = "completed"
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result
```

完整的报销流程包括以下关键步骤：

1. **员工提交报销申请**
   - 员工智能体创建并提交报销申请，包含金额、事由、类别、日期和部门等信息
   - 系统记录申请信息，状态更新为"submitted"
   - 函数调用：`submit_expense_application(amount, purpose, category, date, department)`

2. **直属上级审批**
   - 经理智能体审核报销申请的业务真实性
   - 系统引导经理使用`get_policy_info`工具获取相关报销政策信息
   - 经理根据申请内容和政策做出审批决定
   - 系统记录审批结果，状态更新为"manager_approved"或"manager_rejected"
   - 函数调用：`manager_review()`

3. **部门负责人/预算负责人审批**
   - 仅对金额大于等于5000元的报销申请进行此步骤
   - 部门负责人智能体审核预算符合性，检查部门预算是否充足
   - 如审批通过，系统自动扣减相应部门的预算额度
   - 系统记录审批结果，状态更新为"department_head_approved"或"department_head_rejected"
   - 函数调用：`department_head_review()`

4. **财务审核**
   - 财务审核人智能体审核申请的合规性，检查费用类别是否符合规定
   - 确认报销金额是否在政策允许的范围内
   - 系统记录审核结果，状态更新为"financial_approved"或"financial_rejected"
   - 函数调用：`financial_audit()`

5. **出纳付款**
   - 出纳智能体根据审批通过的报销单执行付款操作
   - 使用`pay`工具生成付款结果，包含交易ID和付款详情
   - 系统记录付款结果，状态更新为"paid"
   - 付款完成后自动触发会计记账流程
   - 函数调用：`process_payment()`

6. **会计记账**
   - 会计智能体根据已付款的报销单进行账务处理
   - 使用`generate_accounting_entry`工具生成相应的会计分录
   - 系统记录所有账务信息，完成报销全流程
   - 函数调用：`accounting_recording()`

#### 5. 智能体交互机制

系统中智能体之间的交互采用了层次化的决策流程，主要特点包括：

- **顺序决策流**: 严格按照员工→经理→部门负责人→财务→出纳→会计的顺序进行审批流转
- **条件分支**: 根据报销金额自动决定是否需要部门负责人审批（金额 >= 5000元时）
- **状态驱动**: 每个流程节点的执行依赖于当前的报销状态（如submitted、manager_approved等）
- **工具增强**: 智能体可以使用专用工具获取外部信息或执行特定操作
  - 所有角色都可以使用`get_policy_info`工具获取报销政策信息
  - 会计角色可以使用`generate_accounting_entry`工具生成会计分录
  - 出纳角色可以使用`pay`工具处理付款操作
- **结果记录**: 所有智能体的决策和操作都会被记录到流程历史中，包含时间戳、执行角色和操作详情
- **自动流转**: 审批通过后系统自动流转到下一环节，无需人工干预

系统核心交互流程如下：
1. 每个智能体根据其角色和当前流程状态接收特定的系统提示
2. 智能体使用工具获取必要信息（如报销政策）
3. 智能体根据输入和获取的信息做出决策
4. 系统记录智能体的决策和响应
5. 根据决策结果更新报销状态并决定下一步操作

以下是智能体交互的关键实现代码：

```python
def manager_review(self, application_id: str) -> dict:
    """
    经理审批报销申请
    
    Args:
        application_id: 报销申请ID
        
    Returns:
        审批结果
    """
    # 获取申请信息
    application = self.applications[application_id]
    
    # 创建智能体
    manager_agent = self.create_agent("manager")
    
    # 准备提示消息
    prompt = f"请审批以下报销申请：\n员工姓名: {application['employee_name']}\n部门: {application['department']}\n金额: {application['amount']}元\n类别: {application['category']}\n事由: {application['purpose']}\n日期: {application['date']}\n\n请给出审批意见和最终决定（批准或拒绝）。你可以使用get_policy_info工具获取相关报销政策信息。"
    
    # 执行智能体交互
    response = manager_agent.step(prompt)
    
    # 提取审批结果
    result = {
        "status": "approved" if "批准" in response.content.lower() else "rejected",
        "comment": response.content,
        "timestamp": self._get_current_timestamp()
    }
    
    # 更新申请状态
    application["status"] = "manager_reviewed"
    application["manager_comment"] = response.content
    
    # 记录交互日志
    self._log_agent_interaction("manager", "review", prompt, response.content, result["status"])
    
    return result

#### 6. 监控与日志系统

系统集成了Comet ML监控功能，实现了全面的智能体交互监控：

- **智能体交互日志**: 记录所有智能体之间的交互过程，包括：
  - 智能体角色和输入提示
  - 智能体的响应结果
  - 流程步骤和状态变化
  - 工具使用情况
  - 关键决策点
- **控制台日志**: 实时输出关键操作和状态变更到控制台，便于调试和监控
- **文件日志**: 支持将日志信息输出到文件，用于长期存储和分析
- **流程历史**: 完整记录报销流程的每一步操作和状态变更
- **结果查询**: 提供`get_process_status`方法查询当前流程状态和历史记录

Comet ML集成的关键功能实现如下：

```python
def _log_agent_interaction(self, agent_role: str, action: str, prompt: str, response: str, result: str):
    """
    记录智能体交互日志
    
    Args:
        agent_role: 智能体角色
        action: 执行的操作
        prompt: 输入提示
        response: 智能体响应
        result: 操作结果
    """
    # 格式化日志
    log_entry = {
        "timestamp": self._get_current_timestamp(),
        "agent_role": agent_role,
        "action": action,
        "prompt": prompt,
        "response": response,
        "result": result
    }
    
    # 添加到日志列表
    self.interaction_logs.append(log_entry)
    
    # 打印日志
    print(f"[{log_entry['timestamp']}] {log_entry['agent_role']} - {log_entry['action']}: {log_entry['result']}")
    
    # 如果有Comet监控器，记录到Comet
    if self.comet_monitor:
        self.comet_monitor.log_agent_interaction(
            agent_role=agent_role,
            action=action,
            prompt=prompt,
            response=response,
            result=result
        )

#### 7. 运行与测试模式

系统提供了交互式测试模式，支持多种测试场景：
- **小额报销测试**（1200.50元，销售部客户午餐）
- **大额报销测试**（6500.00元，工程部差旅费）
- **自定义报销测试**（用户输入报销详情）

测试完成后，系统会展示完整的流程结果，包括各步骤的审批状态和详细评论。

主函数实现了完整的测试交互逻辑：

```python
def main():
    """运行CAMEL-AI报销流程多智能体系统的主函数"""
    print("Starting CAMEL-AI Multi-Agent Expense Reimbursement System")
    print("CAMEL-AI Multi-Agent Expense Reimbursement System")
    print("=" * 60)
    
    # 创建报销系统实例
    reimbursement_system = ExpenseReimbursementSystem()
    
    # 示例报销数据
    example_expenses = [
        {
            "amount": 1200.50,
            "purpose": "客户项目沟通午餐",
            "category": "meal",
            "date": "2023-11-15",
            "department": "Sales"
        },
        {
            "amount": 6500.00,
            "purpose": "技术研讨会差旅费（机票+酒店）",
            "category": "travel",
            "date": "2023-11-10",
            "department": "Engineering"
        }
    ]
    
    while True:
        print("\n请选择测试场景：")
        print("1. 小额报销（1200.50元，销售部客户午餐）
2. 大额报销（6500.00元，工程部差旅费）
3. 自定义报销
4. 退出")
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == "4":
            print("感谢使用CAMEL-AI报销流程多智能体系统！")
            break
        
        if choice == "1":
            expense_data = example_expenses[0]
        elif choice == "2":
            expense_data = example_expenses[1]
        elif choice == "3":
            try:
                amount = float(input("请输入报销金额: ").strip())
                purpose = input("请输入报销事由: ").strip()
                category = input("请输入费用类别 (meal/travel/office_supplies/client_entertainment/training): ").strip()
                date = input("请输入发生日期 (YYYY-MM-DD): ").strip()
                department = input("请输入所属部门 (Engineering/Marketing/Sales/HR): ").strip()
                
                expense_data = {
                    "amount": amount,
                    "purpose": purpose,
                    "category": category,
                    "date": date,
                    "department": department
                }
            except ValueError:
                print("输入无效，请重新选择。")
                continue
        else:
            print("无效选择，请重新输入。")
            continue
        
        print(f"\n正在处理报销请求：")
        print(f"金额：{expense_data['amount']}元")
        print(f"事由：{expense_data['purpose']}")
        print(f"类别：{expense_data['category']}")
        print(f"日期：{expense_data['date']}")
        print(f"部门：{expense_data['department']}")
        print("请稍候...")
        
        # 运行完整报销流程
        result = reimbursement_system.run_full_workflow(expense_data)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("报销流程结果总结:")
        print("=" * 60)
        print(f"最终状态: {result['status']}")
        
        # 显示各步骤详情
        print("\n流程详情:")
        if 'submission' in result['steps']:
            print(f"1. 提交申请: 成功")
        
        if 'manager_review' in result['steps']:
            manager_result = result['steps']['manager_review']
            approval_status = "通过" if manager_result['status'] == 'approved' else "拒绝"
            print(f"2. 直属上级审批: {approval_status} - {manager_result['comment']}")
        
        if 'department_head_review' in result['steps']:
            dept_head_result = result['steps']['department_head_review']
            approval_status = "通过" if dept_head_result['status'] == 'approved' else "拒绝"
            print(f"3. 部门负责人审批: {approval_status} - {dept_head_result['comment']}")
        
        if 'financial_audit' in result['steps']:
            financial_result = result['steps']['financial_audit']
            approval_status = "通过" if financial_result['status'] == 'approved' else "拒绝"
            print(f"4. 财务审核: {approval_status} - {financial_result['comment']}")
        
        if 'payment' in result['steps']:
            payment_result = result['steps']['payment']
            print(f"5. 付款处理: 成功 - {payment_result['result']}")
        
        if 'accounting' in result['steps']:
            accounting_result = result['steps']['accounting']
            print(f"6. 会计记账: 成功 - {accounting_result['result']}")
        
        # 询问是否继续
        if input("\n是否继续测试？(y/n): ").strip().lower() != 'y':
            print("感谢使用CAMEL-AI报销流程多智能体系统！")
            break

if __name__ == "__main__":
    main()

以下是系统的一些关键辅助函数实现：

```python
#### 8. 关键辅助函数实现

系统实现了多个关键辅助函数，用于支持报销流程中的各项业务逻辑：

```python
def check_receipt_validity(receipt_data: dict) -> dict:
    """
    检查报销收据的有效性
    
    参数:
        receipt_data: 包含收据信息的字典
    
    返回:
        包含验证结果的字典
    """
    # 模拟收据验证逻辑
    validity = {
        "is_valid": True,
        "issues": []
    }
    
    # 检查必填字段
    required_fields = ["amount", "date", "category", "department", "purpose"]
    for field in required_fields:
        if field not in receipt_data or not receipt_data[field]:
            validity["is_valid"] = False
            validity["issues"].append(f"缺少必填字段: {field}")
    
    # 检查金额是否为正数
    if "amount" in receipt_data and receipt_data["amount"] <= 0:
        validity["is_valid"] = False
        validity["issues"].append("报销金额必须大于0")
    
    # 检查类别是否有效
    valid_categories = ["meal", "travel", "office_supplies", "client_entertainment", "training"]
    if "category" in receipt_data and receipt_data["category"] not in valid_categories:
        validity["is_valid"] = False
        validity["issues"].append(f"无效的费用类别: {receipt_data['category']}")
    
    # 检查部门是否有效
    valid_departments = ["Engineering", "Marketing", "Sales", "HR"]
    if "department" in receipt_data and receipt_data["department"] not in valid_departments:
        validity["is_valid"] = False
        validity["issues"].append(f"无效的部门: {receipt_data['department']}")
    
    # 模拟一些额外的验证逻辑
    if "amount" in receipt_data and receipt_data["amount"] > 5000:
        validity["requires_additional_review"] = True
        validity["issues"].append("金额超过5000元，需要额外审批")
    
    return validity


def check_department_budget(department: str, amount: float) -> dict:
    """
    检查部门预算是否充足
    
    参数:
        department: 部门名称
        amount: 申请金额
    
    返回:
        包含预算检查结果的字典
    """
    # 模拟部门预算数据
    department_budgets = {
        "Engineering": {"total": 200000, "used": 150000},
        "Marketing": {"total": 150000, "used": 120000},
        "Sales": {"total": 300000, "used": 180000},
        "HR": {"total": 80000, "used": 60000}
    }
    
    # 检查部门是否存在于预算数据中
    if department not in department_budgets:
        return {
            "is_available": False,
            "message": f"部门 '{department}' 的预算数据不存在",
            "remaining_budget": 0
        }
    
    # 获取部门预算信息
    budget_info = department_budgets[department]
    remaining_budget = budget_info["total"] - budget_info["used"]
    
    # 检查剩余预算是否足够
    if remaining_budget >= amount:
        return {
            "is_available": True,
            "message": f"预算充足，剩余预算: {remaining_budget}元",
            "remaining_budget": remaining_budget
        }
    else:
        return {
            "is_available": False,
            "message": f"预算不足，剩余预算: {remaining_budget}元，申请金额: {amount}元",
            "remaining_budget": remaining_budget
        }


def make_payment(employee_id: str, amount: float, payment_method: str = "bank_transfer") -> dict:
    """
    执行报销付款操作
    
    参数:
        employee_id: 员工ID
        amount: 付款金额
        payment_method: 付款方式
    
    返回:
        包含付款结果的字典
    """
    # 模拟付款处理逻辑
    try:
        # 模拟付款处理
        # 在实际系统中，这里会调用银行API或支付网关
        transaction_id = f"TXN-{int(time.time())}-{random.randint(1000, 9999)}"
        
        # 付款成功
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount,
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat(),
            "message": f"付款 {amount} 元已成功处理"
        }
    except Exception as e:
        # 付款失败
        return {
            "status": "failed",
            "amount": amount,
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": f"付款处理失败: {str(e)}"
        }
```
```

## CAMEL-AI 框架能力与应用

本项目充分利用了CAMEL-AI框架的核心能力，实现了高效的智能体协作系统。以下是框架关键能力及其在项目中的应用：

### 1. 多智能体协作机制

CAMEL-AI框架实现了先进的智能体间通信和协作机制，项目通过以下方式利用这一能力：
- **智能体角色分配**: 根据任务需求为智能体分配特定角色（如旅行顾问、行程规划师等）
- **回合制对话系统**: 实现智能体间有序的信息交换和决策过程
- **任务导向协作**: 确保所有智能体围绕共同目标协同工作

### 2. 角色扮演实现

角色扮演是CAMEL-AI框架的核心特性，项目通过以下方式实现：
- **角色定义**: 为每个智能体设定详细的角色描述、能力边界和行为准则
- **系统提示优化**: 精心设计系统提示以引导智能体表现出符合角色的行为
- **角色互动约束**: 确保智能体在对话中保持角色一致性

### 3. 任务分解与分配

针对复杂任务（如旅行规划），项目实现了以下策略：
- **分层任务分解**: 将复杂任务拆分为多个子任务（如目的地选择、行程安排、预算规划等）
- **能力匹配**: 根据智能体的特长分配合适的子任务
- **进度协调**: 监控各子任务进展并协调整体任务完成

### 4. 记忆管理系统

项目实现了高效的记忆管理机制，支持智能体在长期对话中保持上下文一致性：
- **会话历史存储**: 记录智能体间的完整对话历史
- **关键信息提取**: 从对话中提取重要实体和决策信息
- **上下文维护**: 在对话过程中动态更新和维护上下文信息

## 技术实现与修复的问题

系统实现了以下关键技术特性，并解决了多个技术挑战：

### 技术实现亮点

1. **动态工具调用机制**：实现了基于JSON Schema的工具定义与动态调用，使智能体能够根据需求自动选择和使用合适的工具。

2. **统一的智能体创建与管理**：通过create_agent方法统一智能体创建流程，支持动态调整系统消息、工具分配和模型参数。

3. **结构化工作流处理**：通过run_full_workflow方法实现了结构化的报销流程控制，支持条件分支、失败处理和状态追踪。

4. **多级审批策略**：实现了基于金额阈值的多级审批策略，小额报销走简化流程，大额报销需经过完整审批链。

5. **实时监控与记录**：集成Comet ML实现智能体交互的实时监控与记录，支持后续分析和问题排查。

6. **模块化设计**：系统采用高度模块化的设计，各功能组件（工具、智能体、流程）独立封装，便于扩展和维护。

### 关键修复问题

在系统开发过程中，我们成功解决了以下关键问题：

1. **参数冲突问题**
   - **问题**：在RolePlaying初始化过程中系统消息参数重复传递
   - **解决方案**：移除了agent_kwargs中显式声明的system_message参数，避免与RolePlaying内部处理冲突
   - **实现**：在智能体创建时统一由RolePlaying处理系统消息

2. **消息处理机制**
   - **问题**：ChatAgentResponse对象属性访问错误
   - **解决方案**：正确使用.msgs[0].content访问消息内容，并添加了空值检查
   - **实现**：统一对话循环中的消息提取逻辑

3. **记忆记录验证**
   - **问题**：MemoryRecord验证错误
   - **解决方案**：确保向记忆系统传递正确类型的消息对象（BaseMessage实例）
   - **实现**：通过提取ChatAgentResponse中的msgs[0]属性获取有效消息

4. **类型导入完善**
   - **问题**：缺失必要的类型导入
   - **解决方案**：添加了缺失的OpenAIBackendRole导入，确保类型引用的完整性
   - **实现**：完善了模块导入结构

5. **代码一致性优化**
   - **问题**：对话循环中的消息处理逻辑不一致
   - **解决方案**：统一了消息处理逻辑，确保各部分代码使用相同的消息提取方式
   - **实现**：重构了消息处理相关函数，提高了代码的可维护性

## CAMEL-AI框架高级特性

### 模型适配性

CAMEL-AI框架设计具有高度的模型适配性：
- 支持多种大语言模型平台（OpenAI、Ollama等）
- 提供统一的接口抽象，使切换模型变得简单
- 自适应不同模型的特性和限制

### 扩展性设计

框架具有良好的扩展性，支持：
- 自定义智能体角色和行为
- 集成外部工具和API
- 扩展记忆管理机制
- 实现自定义的会话流程控制

### 性能优化

框架内置了多种性能优化机制：
- 对话上下文压缩
- 记忆选择性存储
- 智能缓存机制
- 资源使用监控

## 最佳实践与开发建议

1. **角色设计建议**
   - 为智能体提供清晰、具体的角色定义
   - 明确每个角色的职责和能力边界
   - 设计互补的角色组合以提高任务完成效率

2. **系统提示优化**
   - 精心设计系统提示以引导智能体行为
   - 使用结构化的提示模板提高一致性
   - 避免模糊表述，确保指令明确

3. **错误处理策略**
   - 实现健壮的错误捕获和恢复机制
   - 为关键操作添加重试逻辑
   - 设计优雅的失败处理流程

## 总结

本项目成功实现了基于CAMEL-AI框架的多智能体协作系统，特别针对旅行规划场景进行了优化。通过解决关键技术问题，完善了智能体交互机制，实现了高效的角色扮演和任务协作。项目充分展示了CAMEL-AI框架在构建复杂多智能体应用方面的强大能力，为进一步开发更高级的智能体系统奠定了基础。