#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Expense Reimbursement System using CAMEL-AI RolePlaying Framework.
使用官方CAMEL-AI框架的RolePlaying模式实现的报销流程示例
"""
import os
import sys

# 调整Python搜索路径，添加项目根目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from typing import Dict, Any, List
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType, RoleType, OpenAIBackendRole
from camel.configs import ChatGPTConfig
from camel.agents import TaskSpecifyAgent
from camel.societies import RolePlaying
from dotenv import load_dotenv

# 导入comet监控器
from agents.comet_monitor import comet_monitor

# Load environment variables
# 加载环境变量
load_dotenv()

# 设置日志记录
import os
# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(log_dir, exist_ok=True)
# 配置日志同时输出到控制台和文件
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'expense_reimbursement.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 定义报销流程中的角色
reimbursement_roles = {
    "employee": {
        "role_name": "Employee",
        "role_description": "报销申请人，你是公司的一名员工，负责提交符合公司政策的费用报销申请。你需要提供完整的发票和清晰的报销事由。"
    },
    "manager": {
        "role_name": "Manager",
        "role_description": "直属上级，你是员工的直接经理，负责审核报销费用的业务真实性和合理性。确保费用与业务相关且必要。"
    },
    "department_head": {
        "role_name": "DepartmentHead",
        "role_description": "部门负责人，你负责审核报销费用的预算符合性，确保部门有足够的预算来覆盖这些支出，并且符合部门的业务规划。"
    },
    "financial_auditor": {
        "role_name": "FinancialAuditor",
        "role_description": "财务审核人，你是公司的财务专员，负责审核票据的合法性、合规性，确保符合公司的费用报销政策和税务法规。如果发现问题，你会驳回申请并说明原因。"
    },
    "cashier": {
        "role_name": "Cashier",
        "role_description": "出纳，你负责根据审批通过的报销单进行支付操作，将报销款打入员工账户。确保支付准确、及时。"
    },
    "accountant": {
        "role_name": "Accountant",
        "role_description": "会计，你负责根据报销单进行账务处理，生成会计凭证，将费用计入正确的会计科目，并归档保存所有凭证。"
    },
    "system_admin": {
        "role_name": "SystemAdmin",
        "role_description": "系统管理员，你负责维护和保障报销系统的稳定运行，管理流程节点和权限设置，解决员工在系统使用中遇到的技术问题。"
    }
}

class ExpenseReimbursementSystem:
    """
    报销流程多智能体系统 - 支持传统Workflow和RolePlaying两种模式
    """
    def __init__(self, model=None):
        """
        初始化报销系统
        
        Args:
            model: 模型实例，如果为None则自动创建
        """
        # 先初始化监控器
        self.monitor = comet_monitor
        
        # 再初始化模型
        self.model = self._setup_model() if model is None else model
        
        # 其他初始化
        self.roles = reimbursement_roles
        self.agents = {}
        self.current_status = "initialized"
        self.process_history = []
        self.expense_application = {
            "amount": 0,
            "purpose": "",
            "category": "",
            "date": "",
            "receipts": [],
            "status": "draft"
        }
        print(f"Comet monitoring status: {'active' if self.monitor.is_active else 'inactive'}")
        
        # 简单的部门预算数据（模拟）
        self.department_budgets = {
            "Engineering": 100000,
            "Marketing": 80000,
            "Sales": 120000,
            "HR": 50000
        }
        
        # 允许的报销类别
        self.allowed_categories = ["meal", "travel", "office_supplies", "client_entertainment", "training"]
        
        # 公司报销政策（按类别定义）
        self.reimbursement_policy = {
            "meal": {
                "name": "餐饮费",
                "max_daily_amount": 200,
                "description": "员工因公外出的餐饮费用"
            },
            "travel": {
                "name": "交通费",
                "max_daily_amount": 500,
                "description": "员工因公外出的交通费用，包括机票、火车票、出租车费等"
            },
            "hotel": {
                "name": "住宿费",
                "max_per_night": 1000,
                "description": "员工因公出差的住宿费用"
            },
            "office_supplies": {
                "name": "办公用品费",
                "max_single_amount": 1000,
                "description": "办公所需的文具、设备等用品费用"
            },
            "client_entertainment": {
                "name": "客户招待费",
                "max_per_event": 2000,
                "description": "因业务需要招待客户产生的费用"
            },
            "training": {
                "name": "培训费",
                "max_per_session": 5000,
                "description": "员工参加培训课程的费用"
            }
        }
        
        # 初始化RolePlaying会话
        self.role_play_sessions = {}
    
    def _setup_model(self):
        """
        设置模型实例
        """
        print(os.getenv("DEFAULT_MODEL_PROVIDER"))
        print(os.getenv("OPENAI_API_KEY"))
        print(os.getenv("OPENAI_BASE_URL"))
        
        model_platform = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
        print(f"Using model platform: {model_platform}")
        
        if model_platform.lower() == "ollama":
            model = ModelFactory.create(
                model_platform=ModelPlatformType.OLLAMA,
                model_type=os.getenv("OLLAMA_MODEL_NAME", "llama2"),
                model_config_dict={}
            )
        else:
            # 默认使用OpenAI
            model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=ModelType.GPT_3_5_TURBO,
                model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=2000).as_dict()
            )
        
        # 记录模型设置到comet
        if self.monitor.is_active:
            self.monitor.log_parameter("model_platform", model_platform)
            self.monitor.log_parameter("model_type", model_type if model_platform.lower() == "ollama" else "GPT_3_5_TURBO")
            self.monitor.log_parameter("temperature", 0.7)
            self.monitor.log_parameter("max_tokens", 2000)
        
        return model
    
    def _log_agent_interaction(self, agent_role: str, prompt: str, response: str, **kwargs):
        """
        记录智能体交互到Comet监控
        
        Args:
            agent_role: 智能体角色
            prompt: 输入提示
            response: 模型响应
            **kwargs: 其他参数
        """
        
        print(f"self.monitor: {self.monitor.is_active}")
        
        if self.monitor.is_active:
            provider_name = os.getenv("DEFAULT_MODEL_PROVIDER", "openai").upper()
            try:
                # 获取模型配置信息
                model_config = {}
                if hasattr(self.model, '_config'):
                    model_config = self.model._config
                
                # 提取相关配置
                temperature = getattr(model_config, 'temperature', 0.7)
                max_tokens = getattr(model_config, 'max_tokens', 2000)
                
                # 记录交互
                self.monitor.log_model_call(
                    provider_name=provider_name,
                    prompt=prompt,
                    response=response,
                    model=os.getenv("DEFAULT_MODEL_NAME", "gpt-3.5-turbo"),
                    temperature=temperature,
                    max_tokens=max_tokens,
                    agent_role=agent_role,
                    **kwargs
                )
            except Exception as e:
                logger.error(f"Failed to log agent interaction to Comet: {str(e)}")
    
    def _get_policy_info_tool(self):
        """
        获取报销政策信息工具 - 返回符合CAMEL框架期望的可调用工具
        """
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
    
    def _generate_accounting_entry_tool(self):
        """
        生成会计分录工具 - 返回符合CAMEL框架期望的可调用工具
        """
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
        
    def _generate_pay_tool(self):
        """
        生成付款工具 - 返回符合CAMEL框架期望的可调用工具
        """
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
        
        return pay
        
    def create_agent(self, role_type: str) -> ChatAgent:
        """
        创建具有指定角色的智能体
        
        Args:
            role_type: 角色类型
        
        Returns:
            ChatAgent实例
        """
        print(f"Creating agent with role: {role_type}")
        
        if role_type not in self.roles:
            logger.warning(f"Unknown role type: {role_type}")
            return None
        
        role_info = self.roles[role_type]
        
        # 创建系统消息
        system_msg = BaseMessage.make_assistant_message(
            role_name=role_info["role_name"],
            content=role_info["role_description"]
        )
        
        # 根据角色类型选择工具
        tools = [self._get_policy_info_tool()]
        
        # 为会计角色添加记账工具
        if role_type == "accountant":
            tools.append(self._generate_accounting_entry_tool())
        
        # 为出纳角色添加付款工具
        if role_type == "cashier":
            tools.append(self._generate_pay_tool())
        
        # 创建智能体
        agent = ChatAgent(
            system_message=system_msg,
            model=self.model,
            token_limit=4096,
            tools=tools
        )
        
        # 重置智能体
        agent.reset()
        
        # 存储智能体
        self.agents[role_type] = agent
        
        print(f"Agent {role_info['role_name']} created successfully")
        return agent
        
    def submit_expense_application(self, amount: float, purpose: str, category: str, date: str, department: str):
        """
        提交报销申请
        
        Args:
            amount: 报销金额
            purpose: 报销事由
            category: 费用类别
            date: 发生日期
            department: 所属部门
        """
        print(f"Submitting expense application: {amount}, {purpose}, {category}, {date}, {department}")
        
        # 创建员工智能体（如果不存在）
        if "employee" not in self.agents:
            self.create_agent("employee")
        
        # 更新报销申请信息
        self.expense_application = {
            "amount": amount,
            "purpose": purpose,
            "category": category,
            "date": date,
            "department": department,
            "receipts": ["模拟发票"],  # 简单模拟
            "status": "submitted"
        }
        
        # 记录流程历史
        self.process_history.append({
            "step": "employee_submission",
            "actor": "employee",
            "details": self.expense_application,
            "timestamp": self._get_current_timestamp()
        })
        
        self.current_status = "submitted"
        print("Expense application submitted successfully")
        
        # 返回提交确认
        return f"报销申请已提交成功，金额：{amount}元，事由：{purpose}，类别：{category}，日期：{date}，部门：{department}  提交时间：{self._get_current_timestamp()}"
        
    def manager_review(self):
        """
        直属上级审批
        """
        if self.current_status != "submitted":
            return f"当前状态为{self.current_status}，无法进行经理审批"
        
        # 创建经理智能体（如果不存在）
        if "manager" not in self.agents:
            self.create_agent("manager")
        
        manager = self.agents["manager"]
        
        # 准备审批请求
        # 引导manager使用工具获取政策信息，而不是直接提供
        review_request = BaseMessage.make_user_message(
            role_name="System",
            content = f"请审批以下报销申请。为做出合理决定，请使用get_policy_info工具获取相关政策信息（如max_daily_meal、allowed_categories等）。\n\n申请信息：\n金额：{self.expense_application['amount']}元\n事由：{self.expense_application['purpose']}\n类别：{self.expense_application['category']}\n日期：{self.expense_application['date']}\n部门：{self.expense_application['department']}"
                f"\n\n如果审批通过请明确输出：<审批通过>，如果审批不通过请明确输出：<审批不通过>"
        )
        
        # 获取经理审批意见
        response = manager.step(review_request)
        print(f"Manager response: {response}")
        
        # 提取审批结果
        if hasattr(response, 'msgs') and response.msgs:
            review_result = response.msgs[0].content
        else:
            review_result = "审批过程中出现问题"
        
        # 记录到comet监控
        self._log_agent_interaction(
            agent_role="manager",
            prompt=review_request.content,
            response=review_result,
            step="manager_review"
        )
        
        # 简单的审批逻辑（根据金额和事由决定是否通过）
        # 这里我们模拟经理审批通过的情况，但在实际应用中可以根据业务规则进行更复杂的判断
        is_approved = "同意" in review_result or "通过" in review_result or "批准" in review_result # or self.expense_application['amount'] < 5000
        
        # 更新报销状态
        self.expense_application['status'] = "manager_approved" if is_approved else "manager_rejected"
        self.current_status = self.expense_application['status']
        
        # 记录流程历史
        self.process_history.append({
            "step": "manager_review",
            "actor": "manager",
            "details": {
                "review_result": review_result,
                "is_approved": is_approved
            },
            "timestamp": self._get_current_timestamp()
        })
        
        print(f"Manager review completed, status: {self.current_status}")
        
        return {
            "is_approved": is_approved,
            "review_comment": review_result
        }
        
    def department_head_review(self):
        """
        部门负责人审批
        """
        if self.current_status != "manager_approved" or self.expense_application['amount'] < 5000:
            return f"当前状态为{self.current_status}或金额低于5000元，无需部门负责人审批"
        
        # 创建部门负责人智能体（如果不存在）
        if "department_head" not in self.agents:
            self.create_agent("department_head")
        
        department_head = self.agents["department_head"]
        department = self.expense_application['department']
        current_budget = self.department_budgets.get(department, 0)
        
        # 准备审批请求
        review_request = BaseMessage.make_user_message(
            role_name="System",
            content=f"请审批以下报销申请：\n金额：{self.expense_application['amount']}元\n事由：{self.expense_application['purpose']}\n类别：{self.expense_application['category']}\n日期：{self.expense_application['date']}\n部门：{department}\n部门当前预算：{current_budget}元"
        )
        
        # 获取部门负责人审批意见
        response = department_head.step(review_request)
        
        # 提取审批结果
        if hasattr(response, 'msgs') and response.msgs:
            review_result = response.msgs[0].content
        else:
            review_result = "审批过程中出现问题"
        
        # 记录到comet监控
        self._log_agent_interaction(
            agent_role="department_head",
            prompt=review_request.content,
            response=review_result,
            step="department_head_review"
        )
        
        # 简单的审批逻辑（检查预算是否足够）
        is_approved = "同意" in review_result or "通过" in review_result or (current_budget > self.expense_application['amount'])
        
        # 更新报销状态
        self.expense_application['status'] = "department_head_approved" if is_approved else "department_head_rejected"
        self.current_status = self.expense_application['status']
        
        # 记录流程历史
        self.process_history.append({
            "step": "department_head_review",
            "actor": "department_head",
            "details": {
                "review_result": review_result,
                "is_approved": is_approved
            },
            "timestamp": self._get_current_timestamp()
        })
        
        # 如果审批通过，减少部门预算
        if is_approved:
            self.department_budgets[department] -= self.expense_application['amount']
        
        print(f"Department head review completed, status: {self.current_status}")
        
        return {
            "is_approved": is_approved,
            "review_comment": review_result,
            "remaining_budget": self.department_budgets.get(department, 0)
        }
        
    def financial_audit(self):
        """
        财务审核
        """
        if self.current_status not in ["manager_approved", "department_head_approved"]:
            return f"当前状态为{self.current_status}，无法进行财务审核"
        
        # 创建财务审核人智能体（如果不存在）
        if "financial_auditor" not in self.agents:
            self.create_agent("financial_auditor")
        
        financial_auditor = self.agents["financial_auditor"]
        
        # 准备审核请求
        # 从重构后的报销政策字典中获取餐饮和住宿的最高标准
        meal_max = self.reimbursement_policy.get('meal', {}).get('max_daily_amount', '未设置')
        hotel_max = self.reimbursement_policy.get('hotel', {}).get('max_per_night', '未设置')
        
        # 使用单独的allowed_categories列表获取允许的报销类别
        allowed_categories_str = ', '.join(self.allowed_categories)
        
        policy_info = f"公司报销政策：\n- 每日餐饮最高标准：{meal_max}元\n- 每晚住宿最高标准：{hotel_max}元\n- 允许的费用类别：{allowed_categories_str}"
        
        audit_request = BaseMessage.make_user_message(
            role_name="System",
            content=f"请审核以下报销申请的合规性：\n金额：{self.expense_application['amount']}元\n事由：{self.expense_application['purpose']}\n类别：{self.expense_application['category']}\n日期：{self.expense_application['date']}\n\n{policy_info}"
        )
        
        # 获取财务审核意见
        response = financial_auditor.step(audit_request)
        
        # 提取审核结果
        if hasattr(response, 'msgs') and response.msgs:
            audit_result = response.msgs[0].content
        else:
            audit_result = "审核过程中出现问题"
        
        # 记录到comet监控
        self._log_agent_interaction(
            agent_role="financial_auditor",
            prompt=audit_request.content,
            response=audit_result,
            step="financial_audit"
        )
        
        # 简单的审核逻辑（检查类别是否允许）
        is_approved = "同意" in audit_result or "通过" in audit_result or \
                      self.expense_application['category'] in self.allowed_categories
        
        # 更新报销状态
        self.expense_application['status'] = "financial_approved" if is_approved else "financial_rejected"
        self.current_status = self.expense_application['status']
        
        # 记录流程历史
        self.process_history.append({
            "step": "financial_audit",
            "actor": "financial_auditor",
            "details": {
                "audit_result": audit_result,
                "is_approved": is_approved
            },
            "timestamp": self._get_current_timestamp()
        })
        
        print(f"Financial audit completed, status: {self.current_status}")
        
        return {
            "is_approved": is_approved,
            "audit_comment": audit_result
        }
        
    def process_payment(self):
        """
        出纳付款
        """
        if self.current_status != "financial_approved":
            return f"当前状态为{self.current_status}，无法进行付款"
        
        # 创建出纳智能体（如果不存在）
        if "cashier" not in self.agents:
            self.create_agent("cashier")
        
        cashier = self.agents["cashier"]
        
        # 准备付款请求
        payment_request = BaseMessage.make_user_message(
            role_name="System",
            content=f"请处理以下报销的付款：\n金额：{self.expense_application['amount']}元\n员工：模拟员工\n银行账户：模拟账户1234"
        )
        
        # 获取付款结果
        response = cashier.step(payment_request)
        
        # 提取付款结果
        if hasattr(response, 'msgs') and response.msgs:
            payment_result = response.msgs[0].content
        else:
            payment_result = "付款过程中出现问题"
        
        # 记录到comet监控
        self._log_agent_interaction(
            agent_role="cashier",
            prompt=payment_request.content,
            response=payment_result,
            step="process_payment"
        )
        
        # 更新报销状态
        self.expense_application['status'] = "paid"
        self.current_status = "paid"
        
        # 记录流程历史
        self.process_history.append({
            "step": "payment",
            "actor": "cashier",
            "details": {
                "payment_result": payment_result,
                "amount": self.expense_application['amount']
            },
            "timestamp": self._get_current_timestamp()
        })
        
        # 执行会计记账（自动触发）
        self.accounting_recording()
        
        print(f"Payment processed, status: {self.current_status}")
        
        return {
            "status": "success",
            "payment_comment": payment_result,
            "amount": self.expense_application['amount']
        }
        
    def accounting_recording(self):
        """
        会计记账与归档
        """
        # 创建会计智能体（如果不存在）
        if "accountant" not in self.agents:
            self.create_agent("accountant")
        
        accountant = self.agents["accountant"]
        
        # 准备记账请求
        recording_request = BaseMessage.make_user_message(
            role_name="System",
            content=f"请为以下已付款的报销进行记账：\n金额：{self.expense_application['amount']}元\n事由：{self.expense_application['purpose']}\n类别：{self.expense_application['category']}\n日期：{self.expense_application['date']}"
        )
        
        # 获取记账结果
        response = accountant.step(recording_request)
        
        # 提取记账结果
        if hasattr(response, 'msgs') and response.msgs:
            recording_result = response.msgs[0].content
        else:
            recording_result = "记账过程中出现问题"
        
        # 记录到comet监控
        self._log_agent_interaction(
            agent_role="accountant",
            prompt=recording_request.content,
            response=recording_result,
            step="accounting_recording"
        )
        
        # 记录流程历史
        self.process_history.append({
            "step": "accounting",
            "actor": "accountant",
            "details": {
                "recording_result": recording_result
            },
            "timestamp": self._get_current_timestamp()
        })
        
        print("Accounting recording completed")
        
    def run_full_workflow(self, amount: float, purpose: str, category: str, date: str, department: str):
        """
        运行完整的报销流程 (传统Workflow模式)
        
        Args:
            amount: 报销金额
            purpose: 报销事由
            category: 费用类别
            date: 发生日期
            department: 所属部门
        
        Returns:
            流程运行结果
        """
        print(f"Running full expense reimbursement workflow for: {amount}, {purpose}, {category}, {date}, {department}")
        
        results = {}
        
        # 1. 员工提交报销
        submission_result = self.submit_expense_application(amount, purpose, category, date, department)
        results['submission'] = submission_result
        
        # 2. 直属上级审批
        manager_result = self.manager_review()
        results['manager_review'] = manager_result
        
        # 如果经理审批通过，继续流程
        if manager_result['is_approved']:
            # 3. 部门负责人审批（仅适用于大额报销）
            if amount >= 5000:
                dept_head_result = self.department_head_review()
                results['department_head_review'] = dept_head_result
                
                # 如果部门负责人审批拒绝，结束流程
                if not dept_head_result['is_approved']:
                    results['status'] = "rejected_at_department_head"
                    return results
            
            # 4. 财务审核
            financial_result = self.financial_audit()
            results['financial_audit'] = financial_result
            
            # 如果财务审核通过，继续付款流程
            if financial_result['is_approved']:
                # 5. 出纳付款
                payment_result = self.process_payment()
                results['payment'] = payment_result
                results['status'] = "completed"
            else:
                results['status'] = "rejected_at_finance"
        else:
            results['status'] = "rejected_at_manager"
        
        print(f"Expense reimbursement workflow completed with status: {results['status']}")
        
        return results
        
    def run_role_play_workflow(self, amount: float, purpose: str, category: str, date: str, department: str):
        """
        使用RolePlaying模式运行报销流程
        
        Args:
            amount: 报销金额
            purpose: 报销事由
            category: 费用类别
            date: 发生日期
            department: 所属部门
        
        Returns:
            流程运行结果
        """
        print("Starting CAMEL RolePlaying expense reimbursement conversation")
        
        # 更新报销申请信息
        self.expense_application = {
            "amount": amount,
            "purpose": purpose,
            "category": category,
            "date": date,
            "department": department,
            "receipts": ["模拟发票"],  # 简单模拟
            "status": "submitted"
        }
        
        # 记录流程历史
        self.process_history.append({
            "step": "initialization",
            "actor": "system",
            "details": self.expense_application,
            "timestamp": self._get_current_timestamp()
        })
        
        # 准备任务描述
        task_description = f"处理一笔报销申请，金额为{amount}元，事由为{purpose}，类别为{category}，日期为{date}，部门为{department}。"
        
        # 设置报销流程中的角色序列
        role_sequence = ["employee", "manager", "financial_auditor"]
        
        # 如果金额大于等于5000元，添加部门负责人审批环节
        if amount >= 5000:
            role_sequence.insert(2, "department_head")
        
        # 添加付款和记账环节
        role_sequence.extend(["cashier", "accountant"])
        
        results = {"status": "completed", "process_steps": []}
        
        # 初始化当前角色索引
        current_role_index = 0
        
        # 模拟多轮角色之间的对话
        while current_role_index < len(role_sequence):
            current_role = role_sequence[current_role_index]
            next_role = role_sequence[current_role_index + 1] if current_role_index + 1 < len(role_sequence) else None
            
            # 如果是最后一个角色（会计），处理完后结束流程
            if not next_role:
                break
            
            print(f"Creating RolePlaying society between {current_role} and {next_role}")
            
            # 获取当前角色和下一个角色的信息
            current_role_info = self.roles[current_role]
            next_role_info = self.roles[next_role]
            
            # 准备系统提示
            system_prompt = f"这是公司的报销流程，当前处理步骤是：{current_role}处理完毕后，将申请传递给{next_role}进行下一步处理。"
            
            # 创建特定任务的TaskSpecifyAgent
            task_specify_agent = TaskSpecifyAgent(model=self.model)
            task_specify_msg = BaseMessage.make_user_message(
                role_name="TaskSpecifier",
                content=f"你需要将一个基本任务细化为更具体的任务，以便于两个智能体之间的角色对话。\n基本任务：{task_description}\n当前角色：{current_role_info['role_name']}\n下一个角色：{next_role_info['role_name']}"
            )
            
            # 获取细化后的任务
            specified_task_msg = task_specify_agent.step(task_specify_msg)
            specified_task = specified_task_msg.content
            
            # 根据当前角色类型选择工具
            tools = [self._get_policy_info_tool()]
            
            # 为会计角色添加记账工具
            if current_role == "accountant":
                tools.append(self._generate_accounting_entry_tool())
            
            # 为出纳角色添加付款工具
            if current_role == "cashier":
                tools.append(self._generate_pay_tool())
            
            # 创建RolePlaying实例
            role_play_session = RolePlaying(
                assistant_role_name=current_role_info['role_name'],
                assistant_role_description=current_role_info['role_description'],
                user_role_name=next_role_info['role_name'],
                user_role_description=next_role_info['role_description'],
                model=self.model,
                assistant_tools=tools,
                system_message=system_prompt,
            )
            
            # 保存会话实例
            session_id = f"{current_role}_{next_role}_{self._get_current_timestamp().replace(' ', '_').replace(':', '-')}"
            self.role_play_sessions[session_id] = role_play_session
            
            # 创建初始消息
            initial_msg = BaseMessage.make_user_message(
                role_name=next_role_info['role_name'],
                content=f"我是{next_role_info['role_name']}，请你作为{current_role_info['role_name']}处理以下报销申请：\n{self.expense_application}"
            )
            
            # 启动RolePlaying对话
            print(f"Starting RolePlaying conversation between {current_role_info['role_name']} and {next_role_info['role_name']}")
            
            chat_turn_limit = 5
            chat_turn_counter = 0
            
            # 处理多轮对话
            while chat_turn_counter < chat_turn_limit:
                # 获取当前智能体的回复
                response = role_play_session.step(initial_msg)
                
                # 提取回复内容
                if hasattr(response, 'msgs') and response.msgs:
                    response_content = response.msgs[0].content
                else:
                    response_content = "对话过程中出现问题"
                
                # 记录到comet监控
                self._log_agent_interaction(
                    agent_role=current_role,
                    prompt=initial_msg.content,
                    response=response_content,
                    step=f"{current_role}_to_{next_role}_conversation",
                    turn=chat_turn_counter
                )
                
                # 记录流程历史
                self.process_history.append({
                    "step": f"{current_role}_to_{next_role}_conversation",
                    "actor": current_role,
                    "details": {
                        "prompt": initial_msg.content,
                        "response": response_content
                    },
                    "timestamp": self._get_current_timestamp()
                })
                
                # 检查是否有明确的审批结果
                if current_role in ["manager", "department_head", "financial_auditor"]:
                    # 获取当前角色的智能体
                    agent = role_play_session.assistant_agent
                    
                    # 检查是否有审批结果
                    if "<审批通过>" in response_content or "通过" in response_content or "同意" in response_content:
                        results['process_steps'].append({
                            "role": current_role,
                            "status": "approved",
                            "comment": response_content
                        })
                        self.expense_application['status'] = f"{current_role}_approved"
                        
                        # 如果是财务审核通过，自动进入下一步
                        if current_role == "financial_auditor":
                            current_role_index += 1  # 进入出纳环节
                        else:
                            current_role_index += 1  # 进入下一个审批环节
                        break
                    elif "<审批不通过>" in response_content or "不通过" in response_content or "拒绝" in response_content:
                        results['process_steps'].append({
                            "role": current_role,
                            "status": "rejected",
                            "comment": response_content
                        })
                        self.expense_application['status'] = f"{current_role}_rejected"
                        results['status'] = f"rejected_at_{current_role}"
                        return results
                    
                # 如果是出纳或会计，处理完后进入下一步
                elif current_role in ["cashier", "accountant"]:
                    results['process_steps'].append({
                        "role": current_role,
                        "status": "completed",
                        "comment": response_content
                    })
                    current_role_index += 1
                    break
                
                # 准备下一轮对话的消息
                initial_msg = BaseMessage.make_user_message(
                    role_name=next_role_info['role_name'],
                    content=f"我是{next_role_info['role_name']}，请继续处理。"
                )
                
                chat_turn_counter += 1
                
                # 如果达到最大对话轮数，仍然没有明确结果，默认通过
                if chat_turn_counter >= chat_turn_limit:
                    results['process_steps'].append({
                        "role": current_role,
                        "status": "approved",
                        "comment": "对话达到最大轮数，默认通过"
                    })
                    self.expense_application['status'] = f"{current_role}_approved"
                    current_role_index += 1
                    break
        
        print("CAMEL RolePlaying expense reimbursement conversation completed")
        
        # 最终状态设置为已完成
        self.current_status = "completed"
        
        return results
        
    def _get_current_timestamp(self):
        """
        获取当前时间戳（用于记录）
        """
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def get_process_status(self):
        """
        获取当前流程状态
        """
        return {
            "current_status": self.current_status,
            "expense_application": self.expense_application,
            "process_history": self.process_history
        }

# 简单的工具函数，用于模拟内部查询和操作
def check_receipt_validity(receipt_info):
    """
    检查发票有效性（模拟）
    """
    print(f"Checking receipt validity: {receipt_info}")
    # 简单模拟：只要有内容就认为有效
    return bool(receipt_info)

def check_department_budget(department, amount):
    """
    检查部门预算是否充足（模拟）
    """
    print(f"Checking department budget for {department}: {amount}")
    # 简单模拟：总是返回充足
    return True

def make_payment(employee_id, amount):
    """
    执行付款操作（模拟）
    """
    print(f"Making payment to employee {employee_id}: {amount}")
    # 简单模拟：总是返回成功
    import time
    transaction_str = f"{employee_id}{amount}{time.time()}"
    transaction_id = f"TX{hash(transaction_str) % 1000000}"
    return {"status": "success", "transaction_id": transaction_id}

# 主函数，用于测试
def main():
    """
    运行CAMEL-AI报销流程多智能体系统的主函数 - 支持Workflow和RolePlaying两种模式
    """
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
        print("\n请选择运行模式：")
        print("1. 使用传统Workflow模式")
        print("2. 使用RolePlaying模式")
        print("3. 退出")
        
        mode_choice = input("请输入选择 (1-3): ").strip()
        
        if mode_choice == "3":
            print("感谢使用CAMEL-AI报销流程多智能体系统！")
            break
        
        print("\n请选择测试场景：")
        print("1. 小额报销（1200.50元，销售部客户午餐）")
        print("2. 大额报销（6500.00元，工程部差旅费）")
        print("3. 自定义报销")
        
        choice = input("请输入选择 (1-3): ").strip()
        
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
        
        # 根据选择的模式运行报销流程
        if mode_choice == "1":
            print("使用传统Workflow模式处理...")
            result = reimbursement_system.run_full_workflow(
                amount=expense_data['amount'],
                purpose=expense_data['purpose'],
                category=expense_data['category'],
                date=expense_data['date'],
                department=expense_data['department']
            )
        else:
            print("使用RolePlaying模式处理...")
            result = reimbursement_system.run_role_play_workflow(
                amount=expense_data['amount'],
                purpose=expense_data['purpose'],
                category=expense_data['category'],
                date=expense_data['date'],
                department=expense_data['department']
            )
        
        # 显示结果
        print("\n" + "=" * 60)
        print("报销流程结果总结:")
        print("=" * 60)
        print(f"最终状态: {result['status']}")
        
        # 显示各步骤详情
        print("\n流程详情:")
        
        # 对于Workflow模式的结果显示
        if mode_choice == "1":
            if 'submission' in result:
                print(f"1. 提交申请: {result['submission']}")
            
            if 'manager_review' in result:
                manager_result = result['manager_review']
                approval_status = "通过" if manager_result['is_approved'] else "拒绝"
                print(f"2. 直属上级审批: {approval_status} - {manager_result['review_comment']}")
            
            if 'department_head_review' in result:
                dept_head_result = result['department_head_review']
                approval_status = "通过" if dept_head_result['is_approved'] else "拒绝"
                print(f"3. 部门负责人审批: {approval_status} - {dept_head_result['review_comment']}")
            
            if 'financial_audit' in result:
                financial_result = result['financial_audit']
                approval_status = "通过" if financial_result['is_approved'] else "拒绝"
                print(f"4. 财务审核: {approval_status} - {financial_result['audit_comment']}")
            
            if 'payment' in result:
                payment_result = result['payment']
                print(f"5. 出纳付款: {payment_result['status']} - 金额: {payment_result['amount']}元")
        
        # 对于RolePlaying模式的结果显示
        else:
            if 'process_steps' in result:
                for i, step in enumerate(result['process_steps'], 1):
                    status = "通过" if step['status'] == "approved" else "拒绝" if step['status'] == "rejected" else "完成"
                    print(f"{i}. {reimbursement_roles[step['role']]['role_name']}: {status} - {step['comment']}")
        
        # 显示完整流程历史
        if input("\n是否查看完整流程历史？(y/n): ").strip().lower() == 'y':
            print("\n完整流程历史:")
            process_status = reimbursement_system.get_process_status()
            for step in process_status['process_history']:
                print(f"- {step['timestamp']} [{step['step']}] {step['actor']}: {step['details']}")
        
        # 询问是否继续
        if input("\n是否继续测试？(y/n): ").strip().lower() != 'y':
            print("感谢使用CAMEL-AI报销流程多智能体系统！")
            break

if __name__ == "__main__":
    main()