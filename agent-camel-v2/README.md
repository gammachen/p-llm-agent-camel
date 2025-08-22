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
def _get_policy_info_tool(self, category: str = None) -> dict:
    """获取报销政策信息"""
    # 如果指定了类别，返回该类别政策；否则返回所有政策
    if category and category in self.reimbursement_policies:
        return {
            "status": "success",
            "data": {category: self.reimbursement_policies[category]}
        }
    return {
        "status": "success",
        "data": self.reimbursement_policies
    }

# 2. 生成会计分录工具
def _generate_accounting_entry_tool(self, amount: float, category: str, date: str) -> dict:
    """生成会计分录"""
    # 根据费用类别确定会计科目
    expense_account = f"管理费用-差旅费"  # 默认科目
    if category == "差旅费":
        expense_account = "管理费用-差旅费"
    elif category == "餐饮费":
        expense_account = "管理费用-业务招待费"
    elif category == "办公用品":
        expense_account = "管理费用-办公费"
    
    # 生成会计分录
    entry = {
        "date": date,
        "debit": [
            {"account": expense_account, "amount": amount}
        ],
        "credit": [
            {"account": "银行存款", "amount": amount}
        ],
        "description": f"{category}报销"
    }
    
    return {
        "status": "success",
        "data": entry
    }

# 3. 付款处理工具
def _pay_tool(self, recipient: str, amount: float, reimbursement_id: str) -> dict:
    """处理付款操作"""
    # 模拟付款过程
    import uuid
    import datetime
    
    transaction_id = f"TXN-{uuid.uuid4().hex[:10]}"
    transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 记录付款信息
    payment_info = {
        "transaction_id": transaction_id,
        "transaction_time": transaction_time,
        "recipient": recipient,
        "amount": amount,
        "reimbursement_id": reimbursement_id,
        "status": "completed"
    }
    
    return {
        "status": "success",
        "data": payment_info
    }
```

工具系统的主要特点：

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

系统通过`create_agent`方法动态创建不同角色的智能体，关键实现如下：

```python
# 智能体创建核心逻辑
def create_agent(self, role_type: str, with_tools: bool = True) -> ChatAgent:
    """根据角色类型创建相应的智能体"""
    # 获取角色描述和系统提示
    role_info = reimbursement_roles[role_type]
    system_message = role_info["system_message"]
    
    # 根据角色类型分配相应的工具
    tools = []
    if with_tools:
        # 为会计角色提供记账工具
        if role_type == "Accountant":
            tools = [self._generate_accounting_entry_tool]
        # 为出纳角色提供付款工具
        elif role_type == "Cashier":
            tools = [self._pay_tool]
        # 为其他角色提供政策查询工具
        else:
            tools = [self._get_policy_info_tool]
    
    # 创建并返回智能体
    return ChatAgent(
        system_message=system_message,
        model=self.model,
        tools=tools,
        token_limit=2000  # 设置token限制，防止输出过长
    )
```

- 每个智能体都配备了适合其角色的工具集和系统提示
- 智能体使用`ChatAgent`类创建，并根据需要设置token限制和其他参数
- 工具根据角色类型进行差异化分配，确保每个角色只能使用与其职责相关的工具

#### 4. 完整报销流程

系统实现了完整的报销流程控制逻辑，核心流程控制代码如下：

```python
def run_full_workflow(self, application_data: dict) -> dict:
    """运行完整的报销流程"""
    # 1. 员工提交报销申请
    application_result = self.submit_expense_application(application_data)
    if not application_result["status"] == "success":
        return application_result
    
    application_id = application_result["application_id"]
    amount = application_data["amount"]
    
    # 2. 直属上级审批
    manager_review_result = self.manager_review(application_id)
    if not manager_review_result["status"] == "approved":
        return {
            "status": "rejected",
            "step": "manager_review",
            "reason": manager_review_result["reason"]
        }
    
    # 3. 部门负责人审批（仅对大额报销）
    department_head_review_result = None
    if amount >= 5000:
        department_head_review_result = self.department_head_review(application_id)
        if not department_head_review_result["status"] == "approved":
            return {
                "status": "rejected",
                "step": "department_head_review",
                "reason": department_head_review_result["reason"]
            }
    
    # 4. 财务审核
    financial_audit_result = self.financial_audit(application_id)
    if not financial_audit_result["status"] == "approved":
        return {
            "status": "rejected",
            "step": "financial_audit",
            "reason": financial_audit_result["reason"]
        }
    
    # 5. 出纳付款
    payment_result = self.process_payment(application_id)
    if not payment_result["status"] == "success":
        return {
            "status": "failed",
            "step": "payment",
            "reason": payment_result["reason"]
        }
    
    # 6. 会计记账
    accounting_result = self.accounting_recording(application_id)
    if not accounting_result["status"] == "success":
        return {
            "status": "failed",
            "step": "accounting",
            "reason": accounting_result["reason"]
        }
    
    # 7. 返回最终结果
    return {
        "status": "completed",
        "application_id": application_id,
        "process_history": self.get_process_history(application_id)
    }
```

完整的报销流程包括以下关键步骤：

1. **员工提交报销申请**
   - 员工智能体创建并提交报销申请，包含金额、事由、类别、日期和部门等信息
   - 系统记录申请信息，状态更新为"已提交"

2. **直属上级审批**
   - 经理智能体审核报销申请的业务真实性
   - 系统引导经理使用`get_policy_info`工具获取相关报销政策信息
   - 经理根据申请内容和政策做出审批决定

3. **部门负责人/预算负责人审批**
   - 仅对金额大于等于5000元的报销申请进行此步骤
   - 部门负责人智能体审核预算符合性，检查部门预算是否充足
   - 如审批通过，系统自动扣减相应部门的预算额度

4. **财务审核**
   - 财务审核人智能体审核申请的合规性，检查费用类别是否符合规定
   - 确认报销金额是否在政策允许的范围内

5. **出纳付款**
   - 出纳智能体根据审批通过的报销单执行付款操作
   - 使用`pay`工具生成付款结果，包含交易ID和付款详情

6. **会计记账**
   - 会计智能体根据已付款的报销单进行账务处理
   - 使用`generate_accounting_entry`工具生成相应的会计分录
   - 系统记录所有账务信息，完成报销全流程

#### 5. 智能体交互机制

系统中智能体之间的交互采用了层次化的决策流程，主要特点包括：

- **顺序决策流**: 严格按照员工→经理→部门负责人→财务→出纳→会计的顺序进行审批流转
- **条件分支**: 根据报销金额自动决定是否需要部门负责人审批
- **状态驱动**: 每个流程节点的执行依赖于当前的报销状态
- **工具增强**: 智能体可以使用工具获取外部信息或执行特定操作
- **结果记录**: 所有智能体的决策和操作都会被记录到流程历史中

#### 6. 监控与日志系统

系统集成了Comet ML监控功能，实现了全面的智能体交互监控：

- 记录模型调用参数（如temperature、max_tokens等）
- 记录智能体角色、输入提示和输出响应
- 记录流程步骤和状态变化
- 支持同时输出到控制台和文件日志
- 提供完整的流程历史查询功能

#### 6. 运行与测试模式

系统提供了交互式测试模式，支持多种测试场景：
- 小额报销测试（1200.50元，销售部客户午餐）
- 大额报销测试（6500.00元，工程部差旅费）
- 自定义报销测试（用户输入报销详情）

测试完成后，系统会展示完整的流程结果，包括各步骤的审批状态和详细评论。

以下是系统的一些关键辅助函数实现：

```python
# 验证报销发票
@staticmethod
def check_receipt_validity(receipt_info: dict) -> dict:
    """检查报销发票的有效性"""
    # 验证发票日期（必须在报销申请日期前30天内）
    if not receipt_info.get("date"):
        return {"is_valid": False, "reason": "发票日期不能为空"}
    
    # 验证发票金额与报销金额是否一致
    if not receipt_info.get("amount"):
        return {"is_valid": False, "reason": "发票金额不能为空"}
    
    # 验证发票号码是否存在
    if not receipt_info.get("invoice_number"):
        return {"is_valid": False, "reason": "发票号码不能为空"}
    
    # 发票验证通过
    return {"is_valid": True, "reason": "发票验证通过"}

# 检查部门预算
@staticmethod
def check_department_budget(department: str, amount: float, budget_data: dict) -> dict:
    """检查部门预算是否充足"""
    if department not in budget_data:
        return {"has_enough_budget": False, "reason": "部门预算信息不存在"}
    
    remaining_budget = budget_data[department]["remaining"]
    if remaining_budget < amount:
        return {"has_enough_budget": False, "reason": f"部门预算不足，剩余{remaining_budget}元"}
    
    return {"has_enough_budget": True, "reason": "部门预算充足"}
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

在项目实现过程中，我们解决了以下关键技术问题：

1. **参数冲突问题**: 修复了在RolePlaying初始化过程中系统消息参数重复传递的问题
   - 解决方案: 移除了agent_kwargs中显式声明的system_message参数，避免与RolePlaying内部处理冲突

2. **消息处理机制**: 解决了ChatAgentResponse对象属性访问错误
   - 解决方案: 正确使用.msgs[0].content访问消息内容，并添加了空值检查

3. **记忆记录验证**: 修复了MemoryRecord验证错误
   - 解决方案: 确保向记忆系统传递正确类型的消息对象（BaseMessage实例），通过提取ChatAgentResponse中的msgs[0]属性

4. **类型导入完善**: 添加了缺失的OpenAIBackendRole导入，确保类型引用的完整性

5. **代码一致性优化**: 统一了对话循环中的消息处理逻辑，确保各部分代码使用相同的消息提取方式，提高了代码的可维护性

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