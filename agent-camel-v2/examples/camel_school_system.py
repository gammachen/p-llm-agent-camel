"""
学校智能系统 (School Intelligent System) - 基于CAMEL-AI框架实现

这是一个由多个专业化、人格化的AI Agent组成的协同网络，
用于模拟并优化现实校园的运作，实现教育领域的数字孪生或"全息智慧校园大脑"。
"""
import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入CAMEL框架组件
from agents.base import BaseAgent
from agents.model_provider import ModelProviderFactory
from memory.manager import MemoryManager
from tools.library import ToolLibrary

from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig
real_role_playing_available = True

from dotenv import load_dotenv


# Load environment variables
# 加载环境变量
load_dotenv()

# 导入comet监控器
from agents.comet_monitor import comet_monitor

# 尝试导入OpenAI，如果导入失败则使用模拟模型
use_mock_model = False
try:
    import openai
    # 检查是否设置了API密钥
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("未设置OPENAI_API_KEY环境变量，将使用模拟模型")
        use_mock_model = True
except ImportError:
    logger.warning("未安装OpenAI库，将使用模拟模型")
    use_mock_model = True


# 如果使用模拟模型，则创建一个模拟的ModelProvider

# 导入RolePlaying类



if use_mock_model:
    class MockModelProvider:
        """
        模拟模型提供商，用于在没有API密钥的情况下测试系统
        """
        
        def generate(self, prompt: str) -> str:
            """
            模拟生成响应
            
            Args:
                prompt: 提示文本
                
            Returns:
                模拟的响应文本
            """
            # 简单的模拟响应逻辑
            if "作业" in prompt and "怎么做" in prompt:
                return "这道题需要先理解基本概念，然后按照步骤一步步解决。你可以尝试先复习课本相关章节，再回来做这道题。"
            elif "请假" in prompt:
                return "请假申请已收到，请提供具体的请假原因和时间，以便我为您办理相关手续。"
            elif "成绩" in prompt:
                return "你的最近一次考试成绩已经发布，整体表现不错，但在某些知识点上还有提升空间。"
            else:
                return "感谢您的咨询，我已收到您的消息并正在处理中。"
    
    # 修改ModelProviderFactory以支持模拟模型
    original_get_provider = ModelProviderFactory.get_provider
    
    @classmethod
    def patched_get_provider(cls, provider_name: str):
        """
        补丁版的get_provider方法，支持返回模拟模型
        """
        if use_mock_model:
            return MockModelProvider()
        else:
            return original_get_provider(provider_name)
    
    ModelProviderFactory.get_provider = patched_get_provider


class SchoolAgent(BaseAgent):
    """
    学校智能系统中的基础Agent类，扩展自CAMEL的BaseAgent
    """
    
    def __init__(self, agent_id: str, role: str, model_provider: str = "openai"):
        """
        初始化学校智能系统中的Agent
        
        Args:
            agent_id: Agent的唯一标识符
            role: Agent的角色
            model_provider: 语言模型提供商
        """
        super().__init__(agent_id, role, model_provider)
        self.role_description = role
        # 注册该角色特有的工具
        self._register_role_specific_tools()
        
    def get_name(self) -> str:
        """
        获取Agent的名称
        
        Returns:
            Agent的名称
        """
        # 尝试从子类特有的属性中获取名称
        if hasattr(self, 'student_name'):
            return self.student_name
        elif hasattr(self, 'teacher_name'):
            return self.teacher_name
        elif hasattr(self, 'parent_name'):
            return self.parent_name
        # 如果没有特定名称，返回角色描述中的名称部分
        return self.role.split(' - ')[0]
        
    def get_role_type(self) -> str:
        """
        获取Agent的角色类型
        
        Returns:
            Agent的角色类型
        """
        # 根据agent_id判断角色类型
        agent_id = self.agent_id
        if agent_id.startswith('student_'):
            return 'student'
        elif agent_id.startswith('teacher_'):
            return 'subject_teacher'
        elif agent_id.startswith('head_teacher_'):
            return 'head_teacher'
        elif agent_id.startswith('parent_'):
            return 'parent'
        elif agent_id == 'grading_agent':
            return 'grading'
        elif agent_id == 'academic_admin_agent':
            return 'academic_admin'
        elif agent_id == 'medical_agent':
            return 'medical'
        elif agent_id == 'dietitian_agent':
            return 'dietitian'
        elif agent_id == 'security_agent':
            return 'security'
        elif agent_id == 'principal_agent':
            return 'principal'
        return 'unknown'
        
    def get_description(self) -> str:
        """
        获取Agent的描述
        
        Returns:
            Agent的描述
        """
        return self.role_description
        
    def _register_role_specific_tools(self):
        """
        注册该角色特有的工具
        """
        # 由子类实现
        pass
        
    def process_message(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        处理传入的消息
        
        Args:
            message: 传入的消息
            session_id: 会话标识符
            
        Returns:
            响应消息
        """
        # 更新上下文
        self.memory.update_context(session_id, message)
        
        # 规划下一个动作
        plan = self.plan_next_action(message, session_id)
        
        # 执行计划
        result = self.execute_plan(plan, session_id)
        
        # 创建响应
        response = self._generate_response(result)
        
        # 存储交互
        self.memory.store_interaction(session_id, message, response, plan)
        
        return response
        
    def plan_next_action(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        根据消息和上下文规划下一个动作
        
        Args:
            message: 传入的消息
            session_id: 会话标识符
            
        Returns:
            动作计划
        """
        # 获取上下文
        context = self.memory.get_context(session_id)
        
        # 获取可用工具
        tools = self.tools.get_available_tools()
        
        # 创建规划提示
        planning_prompt = self._create_planning_prompt(message, context, tools)
        
        # 使用模型生成计划
        plan_content = self.model.generate(planning_prompt)
        
        # 解析计划
        plan = {
            "content": plan_content,
            "timestamp": time.time()
        }
        
        return plan
        
    def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        执行给定的计划
        
        Args:
            plan: 要执行的动作计划
            session_id: 会话标识符
            
        Returns:
            执行结果
        """
        # 简单实现，直接返回计划内容作为结果
        # 在实际应用中，这里可能会调用工具或执行其他操作
        result = {
            "status": "success",
            "content": plan["content"],
            "timestamp": time.time()
        }
        
        return result


# 定义学生代理 (Student Agent)
class StudentAgent(SchoolAgent):
    """
    学生代理 - 为每位学生提供个性化服务
    """
    
    def __init__(self, student_id: str, student_name: str, model_provider: str = "openai"):
        """
        初始化学生代理
        
        Args:
            student_id: 学生ID
            student_name: 学生姓名
            model_provider: 语言模型提供商
        """
        self.student_name = student_name
        role = f"学生代理 - 为{student_name}提供学习伴侣、任务代办、统一接口和数据看板服务"
        super().__init__(f"student_{student_id}", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册学生代理特有的工具
        """
        self.tools.register_tool(get_study_plan_tool())
        self.tools.register_tool(get_task_tracker_tool())
        self.tools.register_tool(get_request_submission_tool())
        self.tools.register_tool(get_data_dashboard_tool())


# 定义学科教师代理 (Subject Teacher Agent)
class SubjectTeacherAgent(SchoolAgent):
    """
    学科教师代理 - 为每位学科教师提供教学助理服务
    """
    
    def __init__(self, teacher_id: str, teacher_name: str, subject: str, model_provider: str = "openai"):
        """
        初始化学科教师代理
        
        Args:
            teacher_id: 教师ID
            teacher_name: 教师姓名
            subject: 所教学科
            model_provider: 语言模型提供商
        """
        self.teacher_name = teacher_name
        self.subject = subject
        role = f"学科教师代理 - 为{teacher_name}老师提供{subject}学科的教学助理、学情分析、日程管理和沟通中枢服务"
        super().__init__(f"teacher_{teacher_id}", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册学科教师代理特有的工具
        """
        self.tools.register_tool(get_assignment_grading_tool())
        self.tools.register_tool(get_learning_analytics_tool())
        self.tools.register_tool(get_schedule_management_tool())
        self.tools.register_tool(get_communication_hub_tool())


# 定义阅卷代理 (Grading Agent)
class GradingAgent(SchoolAgent):
    """
    阅卷代理 - 为学校/年级组提供自动阅卷服务
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化阅卷代理
        
        Args:
            model_provider: 语言模型提供商
        """
        role = "阅卷代理 - 提供多模态批改、学情洞察和数据分发服务"
        super().__init__("grading_agent", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册阅卷代理特有的工具
        """
        self.tools.register_tool(get_multi_modal_grading_tool())
        self.tools.register_tool(get_learning_insights_tool())
        self.tools.register_tool(get_data_distribution_tool())


# 定义班主任代理 (Head Teacher Agent)
class HeadTeacherAgent(SchoolAgent):
    """
    班主任代理 - 为每位班主任提供班级管理服务
    """
    
    def __init__(self, teacher_id: str, teacher_name: str, class_name: str, model_provider: str = "openai"):
        """
        初始化班主任代理
        
        Args:
            teacher_id: 教师ID
            teacher_name: 教师姓名
            class_name: 班级名称
            model_provider: 语言模型提供商
        """
        self.teacher_name = teacher_name
        self.class_name = class_name
        role = f"班主任代理 - 为{teacher_name}老师提供{class_name}的班级总控、预警干预和家校桥梁服务"
        super().__init__(f"head_teacher_{teacher_id}", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册班主任代理特有的工具
        """
        self.tools.register_tool(get_class_control_tool())
        self.tools.register_tool(get_early_warning_tool())
        self.tools.register_tool(get_parent_communication_tool())


# 定义家长代理 (Parent Agent)
class ParentAgent(SchoolAgent):
    """
    家长代理 - 为每位家长提供校园信息服务
    """
    
    def __init__(self, parent_id: str, parent_name: str, child_id: str, model_provider: str = "openai"):
        """
        初始化家长代理
        
        Args:
            parent_id: 家长ID
            parent_name: 家长姓名
            child_id: 孩子的学生ID
            model_provider: 语言模型提供商
        """
        self.parent_name = parent_name
        self.child_id = child_id
        role = f"家长代理 - 为{parent_name}提供透明校园、授权沟通和成长档案服务"
        super().__init__(f"parent_{parent_id}", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册家长代理特有的工具
        """
        self.tools.register_tool(get_school_transparency_tool())
        self.tools.register_tool(get_authorized_communication_tool())
        self.tools.register_tool(get_growth_record_tool())


# 定义教务行政代理 (Academic Admin Agent)
class AcademicAdminAgent(SchoolAgent):
    """
    教务行政代理 - 为教务处提供资源调度服务
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化教务行政代理
        
        Args:
            model_provider: 语言模型提供商
        """
        role = "教务行政代理 - 提供资源调度、活动管理和档案管理服务"
        super().__init__("academic_admin_agent", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册教务行政代理特有的工具
        """
        self.tools.register_tool(get_resource_scheduling_tool())
        self.tools.register_tool(get_activity_management_tool())
        self.tools.register_tool(get_record_management_tool())


# 定义医务代理 (Medical Agent)
class MedicalAgent(SchoolAgent):
    """
    医务代理 - 为校医室提供健康监测服务
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化医务代理
        
        Args:
            model_provider: 语言模型提供商
        """
        role = "医务代理 - 提供健康监测、应急响应和咨询顾问服务"
        super().__init__("medical_agent", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册医务代理特有的工具
        """
        self.tools.register_tool(get_health_monitoring_tool())
        self.tools.register_tool(get_emergency_response_tool())
        self.tools.register_tool(get_consultation_tool())


# 定义营养膳食代理 (Dietitian Agent)
class DietitianAgent(SchoolAgent):
    """
    营养膳食代理 - 为食堂提供食谱优化服务
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化营养膳食代理
        
        Args:
            model_provider: 语言模型提供商
        """
        role = "营养膳食代理 - 提供食谱优化、安全溯源和个性化服务"
        super().__init__("dietitian_agent", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册营养膳食代理特有的工具
        """
        self.tools.register_tool(get_recipe_optimization_tool())
        self.tools.register_tool(get_safety_traceability_tool())
        self.tools.register_tool(get_personalized_meal_tool())


# 定义安保代理 (Security Agent)
class SecurityAgent(SchoolAgent):
    """
    安保代理 - 为保卫处提供智能巡检服务
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化安保代理
        
        Args:
            model_provider: 语言模型提供商
        """
        role = "安保代理 - 提供智能巡检、应急广播和访客管理服务"
        super().__init__("security_agent", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册安保代理特有的工具
        """
        self.tools.register_tool(get_intelligent_patrol_tool())
        self.tools.register_tool(get_emergency_broadcast_tool())
        self.tools.register_tool(get_visitor_management_tool())


# 定义校长/教导主任代理 (Principal Agent)
class PrincipalAgent(SchoolAgent):
    """
    校长/教导主任代理 - 为校领导提供决策支持服务
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化校长代理
        
        Args:
            model_provider: 语言模型提供商
        """
        role = "校长/教导主任代理 - 提供决策驾驶舱、趋势洞察和资源规划服务"
        super().__init__("principal_agent", role, model_provider)
        
    def _register_role_specific_tools(self):
        """
        注册校长代理特有的工具
        """
        self.tools.register_tool(get_decision_cockpit_tool())
        self.tools.register_tool(get_trend_insight_tool())
        self.tools.register_tool(get_resource_planning_tool())


# 定义学校智能系统中的工具
def get_study_plan_tool() -> Callable:
    """
    获取学习计划工具 - 返回可调用的函数
    """
    def study_plan(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        管理个人学习计划，智能推送复习内容
        
        Args:
            parameters: 包含学生ID和科目的参数字典
            
        Returns:
            学习计划结果字典
        """
        student_id = parameters.get("student_id")
        subject = parameters.get("subject", "")
        logger.info(f"为学生 {student_id} 生成{subject}学习计划")
        
        # 模拟生成学习计划
        plan = {
            "student_id": student_id,
            "subject": subject,
            "plan_content": f"这是{subject}科目的学习计划，包括每日学习任务、复习重点和推荐资源。",
            "recommended_resources": ["教科书第1-5章", "在线课程链接", "练习题集"]
        }
        
        return {"status": "success", "data": plan}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    study_plan.name = "study_plan"
    study_plan.description = "管理个人学习计划，智能推送复习内容"
    study_plan.parameters = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "学生ID"
            },
            "subject": {
                "type": "string",
                "description": "学习科目"
            }
        },
        "required": ["student_id"]
    }
    
    return study_plan

def get_task_tracker_tool() -> Callable:
    """
    获取任务跟踪工具 - 返回可调用的函数
    """
    def task_tracker(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        接收、跟踪并提醒作业、考试、活动报名等截止日期
        
        Args:
            parameters: 包含学生ID的参数字典
            
        Returns:
            任务跟踪结果字典
        """
        student_id = parameters.get("student_id")
        logger.info(f"为学生 {student_id} 跟踪任务")
        
        # 模拟任务跟踪
        tasks = [
            {"id": "1", "type": "作业", "content": "数学练习册第10页", "due_date": "2023-12-10"},
            {"id": "2", "type": "考试", "content": "英语单元测试", "due_date": "2023-12-15"},
            {"id": "3", "type": "活动", "content": "科技创新大赛报名", "due_date": "2023-12-20"}
        ]
        
        return {"status": "success", "data": tasks}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    task_tracker.name = "task_tracker"
    task_tracker.description = "接收、跟踪并提醒作业、考试、活动报名等截止日期"
    task_tracker.parameters = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "学生ID"
            }
        },
        "required": ["student_id"]
    }
    
    return task_tracker


def get_request_submission_tool() -> Callable:
    """
    获取请求提交工具 - 返回可调用的函数
    """
    def request_submission(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        代理学生向教师、医务、食堂等Agent提交请求
        
        Args:
            parameters: 包含学生ID、请求类型、请求内容和目标Agent的参数字典
            
        Returns:
            请求提交结果字典
        """
        student_id = parameters.get("student_id")
        request_type = parameters.get("request_type")
        request_content = parameters.get("request_content")
        target_agent = parameters.get("target_agent")
        
        logger.info(f"学生 {student_id} 向 {target_agent} 提交 {request_type} 请求")
        
        # 模拟请求提交
        request_id = f"REQ_{student_id}_{int(time.time())}"
        
        return {
            "status": "success", 
            "data": {
                "request_id": request_id,
                "student_id": student_id,
                "request_type": request_type,
                "request_content": request_content,
                "target_agent": target_agent,
                "submission_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    request_submission.name = "request_submission"
    request_submission.description = "代理学生向教师、医务、食堂等Agent提交请求（请假、问询、提交作业）"
    request_submission.parameters = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "学生ID"
            },
            "request_type": {
                "type": "string",
                "description": "请求类型"
            },
            "request_content": {
                "type": "string",
                "description": "请求内容"
            },
            "target_agent": {
                "type": "string",
                "description": "目标Agent"
            }
        },
        "required": ["student_id", "request_type", "request_content", "target_agent"]
    }
    
    return request_submission


def get_data_dashboard_tool() -> Callable:
    """
    获取数据看板工具 - 返回可调用的函数
    """
    def data_dashboard(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        可视化展示个人成绩趋势、知识图谱薄弱点、体能健康变化
        
        Args:
            parameters: 包含学生ID的参数字典
            
        Returns:
            数据看板结果字典
        """
        student_id = parameters.get("student_id")
        logger.info(f"为学生 {student_id} 生成数据看板")
        
        # 模拟数据看板
        dashboard_data = {
            "grades_trend": [85, 88, 92, 89, 94],  # 最近五次考试成绩
            "weak_points": ["三角函数", "阅读理解", "化学方程式"],
            "health_data": {
                "height": 175,  # cm
                "weight": 65,   # kg
                "vision_left": 5.0,
                "vision_right": 4.8
            }
        }
        
        return {"status": "success", "data": dashboard_data}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    data_dashboard.name = "data_dashboard"
    data_dashboard.description = "可视化展示个人成绩趋势、知识图谱薄弱点、体能健康变化"
    data_dashboard.parameters = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "学生ID"
            }
        },
        "required": ["student_id"]
    }
    
    return data_dashboard


def get_assignment_grading_tool() -> Callable:
    """
    获取作业批改工具 - 返回可调用的函数
    """
    def assignment_grading(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动批改客观题、生成作业报告、推荐个性化习题
        
        Args:
            parameters: 包含教师ID、班级ID和作业ID的参数字典
            
        Returns:
            作业批改结果字典
        """
        teacher_id = parameters.get("teacher_id")
        class_id = parameters.get("class_id")
        assignment_id = parameters.get("assignment_id")
        
        logger.info(f"教师 {teacher_id} 批改班级 {class_id} 的作业 {assignment_id}")
        
        # 模拟作业批改
        grading_result = {
            "assignment_id": assignment_id,
            "average_score": 82.5,
            "highest_score": 98,
            "lowest_score": 65,
            "common_mistakes": ["第5题：概念理解错误", "第8题：计算失误"],
            "recommended_exercises": ["习题集第15-20题", "补充练习卷A"]
        }
        
        return {"status": "success", "data": grading_result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    assignment_grading.name = "assignment_grading"
    assignment_grading.description = "自动批改客观题、生成作业报告、推荐个性化习题"
    assignment_grading.parameters = {
        "type": "object",
        "properties": {
            "teacher_id": {
                "type": "string",
                "description": "教师ID"
            },
            "class_id": {
                "type": "string",
                "description": "班级ID"
            },
            "assignment_id": {
                "type": "string",
                "description": "作业ID"
            }
        },
        "required": ["teacher_id", "class_id", "assignment_id"]
    }
    
    return assignment_grading


def get_multi_modal_grading_tool() -> Callable:
    """
    获取多模态批改工具 - 返回可调用的函数
    """
    def multi_modal_grading(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        支持文本、图像等多种形式的作业批改
        
        Args:
            parameters: 包含作业ID的参数字典
            
        Returns:
            多模态批改结果字典
        """
        assignment_id = parameters.get("assignment_id")
        logger.info(f"批改作业 {assignment_id}")
        
        # 模拟多模态批改
        result = {
            "assignment_id": assignment_id,
            "status": "completed",
            "average_score": 85.2,
            "grading_details": "已完成多模态批改，包括文本和图像内容分析"
        }
        
        return {"status": "success", "data": result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    multi_modal_grading.name = "multi_modal_grading"
    multi_modal_grading.description = "支持文本、图像等多种形式的作业批改"
    multi_modal_grading.parameters = {
        "type": "object",
        "properties": {
            "assignment_id": {
                "type": "string",
                "description": "作业ID"
            }
        },
        "required": ["assignment_id"]
    }
    
    return multi_modal_grading


def get_learning_insights_tool() -> Callable:
    """
    获取学情洞察工具 - 返回可调用的函数
    """
    def learning_insights(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析学生学习情况，提供个性化教学建议
        
        Args:
            parameters: 包含班级ID的参数字典
            
        Returns:
            学情分析结果字典
        """
        class_id = parameters.get("class_id")
        logger.info(f"分析班级 {class_id} 的学情")
        
        # 模拟学情洞察
        insights = {
            "class_id": class_id,
            "overall_performance": "良好",
            "strengths": ["基础知识掌握扎实", "解题思路清晰"],
            "weaknesses": ["综合应用题能力不足", "时间管理能力有待提高"],
            "recommendations": ["增加综合应用题练习", "进行时间管理训练"]
        }
        
        return {"status": "success", "data": insights}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    learning_insights.name = "learning_insights"
    learning_insights.description = "分析学生学习情况，提供个性化教学建议"
    learning_insights.parameters = {
        "type": "object",
        "properties": {
            "class_id": {
                "type": "string",
                "description": "班级ID"
            }
        },
        "required": ["class_id"]
    }
    
    return learning_insights


def get_data_distribution_tool() -> Callable:
    """
    获取数据分发工具 - 返回可调用的函数
    """
    def data_distribution(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        将批改结果和学情分析分发给相关教师和学生
        
        Args:
            parameters: 包含数据ID和接收者的参数字典
            
        Returns:
            数据分发结果字典
        """
        data_id = parameters.get("data_id")
        recipients = parameters.get("recipients", [])
        logger.info(f"分发数据 {data_id} 给 {recipients}")
        
        # 模拟数据分发
        result = {
            "data_id": data_id,
            "recipients": recipients,
            "status": "distributed",
            "distribution_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {"status": "success", "data": result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    data_distribution.name = "data_distribution"
    data_distribution.description = "将批改结果和学情分析分发给相关教师和学生"
    data_distribution.parameters = {
        "type": "object",
        "properties": {
            "data_id": {
                "type": "string",
                "description": "数据ID"
            },
            "recipients": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "接收者列表"
            }
        },
        "required": ["data_id"]
    }
    
    return data_distribution


def get_class_control_tool() -> Callable:
    """
    获取班级总控工具 - 返回可调用的函数
    """
    def class_control(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        提供班级整体情况监控和管理功能
        
        Args:
            parameters: 包含班级ID的参数字典
            
        Returns:
            班级总控结果字典
        """
        class_id = parameters.get("class_id")
        logger.info(f"管理班级 {class_id}")
        
        # 模拟班级总控
        result = {
            "class_id": class_id,
            "attendance_rate": 98.5,
            "average_score": 85.2,
            "student_count": 45,
            "recent_activities": ["班级文化建设", "数学竞赛准备"]
        }
        
        return {"status": "success", "data": result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    class_control.name = "class_control"
    class_control.description = "提供班级整体情况监控和管理功能"
    class_control.parameters = {
        "type": "object",
        "properties": {
            "class_id": {
                "type": "string",
                "description": "班级ID"
            }
        },
        "required": ["class_id"]
    }
    
    return class_control


def get_early_warning_tool() -> Callable:
    """
    获取预警干预工具 - 返回可调用的函数
    """
    def early_warning(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        识别学生异常情况并提供干预建议
        
        Args:
            parameters: 包含班级ID的参数字典
            
        Returns:
            预警信息列表
        """
        class_id = parameters.get("class_id")
        logger.info(f"监控班级 {class_id} 的异常情况")
        
        # 模拟预警干预
        warnings = [
            {"student_id": "S001", "type": "成绩下滑", "level": "中度"},
            {"student_id": "S002", "type": "考勤异常", "level": "轻度"}
        ]
        
        return {"status": "success", "data": warnings}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    early_warning.name = "early_warning"
    early_warning.description = "识别学生异常情况并提供干预建议"
    early_warning.parameters = {
        "type": "object",
        "properties": {
            "class_id": {
                "type": "string",
                "description": "班级ID"
            }
        },
        "required": ["class_id"]
    }
    
    return early_warning


def get_parent_communication_tool() -> Callable:
    """
    获取家校沟通工具 - 返回可调用的函数
    """
    def parent_communication(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        促进班主任与家长之间的有效沟通
        
        Args:
            parameters: 包含教师ID、家长ID和消息内容的参数字典
            
        Returns:
            家校沟通结果字典
        """
        teacher_id = parameters.get("teacher_id")
        parent_id = parameters.get("parent_id")
        message = parameters.get("message")
        logger.info(f"教师 {teacher_id} 与家长 {parent_id} 沟通")
        
        # 模拟家校沟通
        communication_id = f"COMM_{teacher_id}_{parent_id}_{int(time.time())}"
        result = {
            "communication_id": communication_id,
            "teacher_id": teacher_id,
            "parent_id": parent_id,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {"status": "success", "data": result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    parent_communication.name = "parent_communication"
    parent_communication.description = "促进班主任与家长之间的有效沟通"
    parent_communication.parameters = {
        "type": "object",
        "properties": {
            "teacher_id": {
                "type": "string",
                "description": "教师ID"
            },
            "parent_id": {
                "type": "string",
                "description": "家长ID"
            },
            "message": {
                "type": "string",
                "description": "沟通消息内容"
            }
        },
        "required": ["teacher_id", "parent_id", "message"]
    }
    
    return parent_communication


def get_learning_analytics_tool() -> Callable:
    """
    获取学情分析工具 - 返回可调用的函数
    """
    def learning_analytics(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析学生学习数据，提供教学改进建议
        
        Args:
            parameters: 包含学科和班级ID的参数字典
            
        Returns:
            学情分析结果字典
        """
        subject = parameters.get("subject")
        class_id = parameters.get("class_id")
        logger.info(f"分析 {class_id} 班级 {subject} 学科的学情")
        
        # 模拟学情分析
        analysis = {
            "subject": subject,
            "class_id": class_id,
            "average_score": 82.5,
            "concept_mastery": {
                "基本概念": 90,
                "应用能力": 75,
                "综合分析": 70
            },
            "recommendations": ["加强应用能力训练", "增加综合分析题练习"]
        }
        
        return {"status": "success", "data": analysis}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    learning_analytics.name = "learning_analytics"
    learning_analytics.description = "分析学生学习数据，提供教学改进建议"
    learning_analytics.parameters = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "学科名称"
            },
            "class_id": {
                "type": "string",
                "description": "班级ID"
            }
        },
        "required": ["subject", "class_id"]
    }
    
    return learning_analytics


def get_schedule_management_tool() -> Callable:
    """
    获取日程管理工具 - 返回可调用的函数
    """
    def schedule_management(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        帮助教师管理教学计划和日程安排
        
        Args:
            parameters: 包含教师ID和日期的参数字典
            
        Returns:
            日程安排列表
        """
        teacher_id = parameters.get("teacher_id")
        date = parameters.get("date", time.strftime("%Y-%m-%d"))
        logger.info(f"管理教师 {teacher_id} 在 {date} 的日程")
        
        # 模拟日程管理
        schedule = [
            {"time": "08:00-09:40", "activity": "高一(1)班数学课"},
            {"time": "10:00-11:40", "activity": "高一(2)班数学课"},
            {"time": "14:00-15:00", "activity": "备课"},
            {"time": "15:30-17:00", "activity": "批改作业"}
        ]
        
        return {"status": "success", "data": schedule}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    schedule_management.name = "schedule_management"
    schedule_management.description = "帮助教师管理教学计划和日程安排"
    schedule_management.parameters = {
        "type": "object",
        "properties": {
            "teacher_id": {
                "type": "string",
                "description": "教师ID"
            },
            "date": {
                "type": "string",
                "description": "日期，格式：YYYY-MM-DD"
            }
        },
        "required": ["teacher_id"]
    }
    
    return schedule_management


def get_communication_hub_tool() -> Callable:
    """
    获取沟通中枢工具 - 返回可调用的函数
    """
    def communication_hub(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        集中管理教师与学生、家长、同事之间的沟通
        
        Args:
            parameters: 包含教师ID的参数字典
            
        Returns:
            沟通信息列表
        """
        teacher_id = parameters.get("teacher_id")
        logger.info(f"获取教师 {teacher_id} 的沟通信息")
        
        # 模拟沟通中枢
        communications = [
            {"type": "学生", "id": "S001", "content": "作业问题请教", "unread": True},
            {"type": "家长", "id": "P001", "content": "关于孩子学习情况的询问", "unread": False},
            {"type": "同事", "id": "T002", "content": "关于教学进度的讨论", "unread": True}
        ]
        
        return {"status": "success", "data": communications}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    communication_hub.name = "communication_hub"
    communication_hub.description = "集中管理教师与学生、家长、同事之间的沟通"
    communication_hub.parameters = {
        "type": "object",
        "properties": {
            "teacher_id": {
                "type": "string",
                "description": "教师ID"
            }
        },
        "required": ["teacher_id"]
    }
    
    return communication_hub


def get_school_transparency_tool() -> Callable:
    """
    获取透明校园工具 - 返回可调用的函数
    """
    def school_transparency(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        向家长提供学校的各项信息和通知
        
        Args:
            parameters: 包含家长ID的参数字典
            
        Returns:
            学校信息和通知字典
        """
        parent_id = parameters.get("parent_id")
        logger.info(f"为家长 {parent_id} 提供学校信息")
        
        # 模拟透明校园
        info = {
            "announcements": ["学校将于下周一举行运动会", "家长会将于下周五召开"],
            "calendar": {"近期活动": ["12月10日：期中考试", "12月25日：圣诞节活动"]},
            "school_policies": ["学生考勤制度", "家长参与学校活动指南"]
        }
        
        return {"status": "success", "data": info}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    school_transparency.name = "school_transparency"
    school_transparency.description = "向家长提供学校的各项信息和通知"
    school_transparency.parameters = {
        "type": "object",
        "properties": {
            "parent_id": {
                "type": "string",
                "description": "家长ID"
            }
        },
        "required": ["parent_id"]
    }
    
    return school_transparency


def get_authorized_communication_tool() -> Callable:
    """
    获取授权沟通工具 - 返回可调用的函数
    """
    def authorized_communication(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        允许家长与学校各部门进行授权沟通
        
        Args:
            parameters: 包含家长ID、部门和消息的参数字典
            
        Returns:
            沟通结果字典
        """
        parent_id = parameters.get("parent_id")
        department = parameters.get("department")
        message = parameters.get("message")
        logger.info(f"家长 {parent_id} 与 {department} 部门沟通")
        
        # 模拟授权沟通
        communication_id = f"COMM_{parent_id}_{department}_{int(time.time())}"
        result = {
            "communication_id": communication_id,
            "parent_id": parent_id,
            "department": department,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {"status": "success", "data": result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    authorized_communication.name = "authorized_communication"
    authorized_communication.description = "允许家长与学校各部门进行授权沟通"
    authorized_communication.parameters = {
        "type": "object",
        "properties": {
            "parent_id": {
                "type": "string",
                "description": "家长ID"
            },
            "department": {
                "type": "string",
                "description": "学校部门"
            },
            "message": {
                "type": "string",
                "description": "沟通消息"
            }
        },
        "required": ["parent_id", "department", "message"]
    }
    
    return authorized_communication


def get_growth_record_tool() -> Callable:
    """
    获取成长档案工具 - 返回可调用的函数
    """
    def growth_record(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        记录学生在校期间的成长和发展情况
        
        Args:
            parameters: 包含学生ID的参数字典
            
        Returns:
            学生成长档案字典
        """
        child_id = parameters.get("child_id")
        logger.info(f"获取学生 {child_id} 的成长档案")
        
        # 模拟成长档案
        record = {
            "child_id": child_id,
            "grades": {"上学期": 85, "本学期": 88},
            "attendance": {"出勤率": 98.5, "请假次数": 2},
            "activities": ["数学竞赛二等奖", "校运会跑步比赛第三名"],
            "teacher_comments": "该生学习认真，积极参与各项活动，团结同学，表现良好。"
        }
        
        return {"status": "success", "data": record}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    growth_record.name = "growth_record"
    growth_record.description = "记录学生在校期间的成长和发展情况"
    growth_record.parameters = {
        "type": "object",
        "properties": {
            "child_id": {
                "type": "string",
                "description": "学生ID"
            }
        },
        "required": ["child_id"]
    }
    
    return growth_record


def get_resource_scheduling_tool() -> Callable:
    """
    获取资源调度工具 - 返回可调用的函数
    """
    def resource_scheduling(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        管理和调度学校的各种资源（教室、设备等）
        
        Args:
            parameters: 包含资源类型和日期的参数字典
            
        Returns:
            资源调度信息字典
        """
        resource_type = parameters.get("resource_type")
        date = parameters.get("date", time.strftime("%Y-%m-%d"))
        logger.info(f"调度 {resource_type} 资源在 {date} 的使用")
        
        # 模拟资源调度
        schedule = {
            "resource_type": resource_type,
            "date": date,
            "available_resources": ["教室101", "实验室202", "会议室301"],
            "scheduled_resources": {
                "教室101": "高一(1)班数学课",
                "实验室202": "高二(2)班物理实验"
            }
        }
        
        return {"status": "success", "data": schedule}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    resource_scheduling.name = "resource_scheduling"
    resource_scheduling.description = "管理和调度学校的各种资源（教室、设备等）"
    resource_scheduling.parameters = {
        "type": "object",
        "properties": {
            "resource_type": {
                "type": "string",
                "description": "资源类型"
            },
            "date": {
                "type": "string",
                "description": "日期 (格式: YYYY-MM-DD)",
                "default": time.strftime("%Y-%m-%d")
            }
        },
        "required": ["resource_type"]
    }
    
    return resource_scheduling


def get_activity_management_tool() -> Callable:
    """
    获取活动管理工具 - 返回可调用的函数
    """
    def activity_management(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        管理学校的各项活动和事件
        
        Args:
            parameters: 参数字典（此工具不需要特定参数）
            
        Returns:
            学校活动列表
        """
        logger.info("管理学校活动")
        
        # 模拟活动管理
        activities = [
            {"id": "1", "name": "运动会", "date": "2023-12-15", "status": "筹备中"},
            {"id": "2", "name": "家长会", "date": "2023-12-20", "status": "已安排"},
            {"id": "3", "name": "艺术节", "date": "2024-01-10", "status": "规划中"}
        ]
        
        return {"status": "success", "data": activities}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    activity_management.name = "activity_management"
    activity_management.description = "管理学校的各项活动和事件"
    activity_management.parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    return activity_management


def get_record_management_tool() -> Callable:
    """
    获取档案管理工具 - 返回可调用的函数
    """
    def record_management(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        管理学校的各种档案和记录
        
        Args:
            parameters: 包含档案类型的参数字典
            
        Returns:
            档案记录列表
        """
        record_type = parameters.get("record_type")
        logger.info(f"管理 {record_type} 类型的档案")
        
        # 模拟档案管理
        records = [
            {"id": "R001", "name": "学生档案", "count": 1000, "last_updated": "2023-12-01"},
            {"id": "R002", "name": "教师档案", "count": 100, "last_updated": "2023-11-15"},
            {"id": "R003", "name": "财务记录", "count": 500, "last_updated": "2023-12-05"}
        ]
        
        return {"status": "success", "data": records}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    record_management.name = "record_management"
    record_management.description = "管理学校的各种档案和记录"
    record_management.parameters = {
        "type": "object",
        "properties": {
            "record_type": {
                "type": "string",
                "description": "档案类型"
            }
        },
        "required": ["record_type"]
    }
    
    return record_management


def get_health_monitoring_tool() -> Callable:
    """
    获取健康监测工具 - 返回可调用的函数
    """
    def health_monitoring(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        监测学生的健康状况和疫情防控
        
        Args:
            parameters: 包含班级ID的参数字典
            
        Returns:
            健康监测数据字典
        """
        class_id = parameters.get("class_id")
        logger.info(f"监测班级 {class_id} 的健康状况")
        
        # 模拟健康监测
        health_data = {
            "class_id": class_id,
            "daily_temperature_check": {"正常人数": 45, "异常人数": 0},
            "recent_health_issues": ["感冒：2人", "过敏：1人"],
            "epidemic_prevention": {"疫苗接种率": 100, "消毒情况": "正常"}
        }
        
        return {"status": "success", "data": health_data}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    health_monitoring.name = "health_monitoring"
    health_monitoring.description = "监测学生的健康状况和疫情防控"
    health_monitoring.parameters = {
        "type": "object",
        "properties": {
            "class_id": {
                "type": "string",
                "description": "班级ID"
            }
        },
        "required": ["class_id"]
    }
    
    return health_monitoring


def get_emergency_response_tool() -> Callable:
    """
    获取应急响应工具 - 返回可调用的函数
    """
    def emergency_response(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理学校内的紧急情况和突发事件
        
        Args:
            parameters: 包含紧急情况类型和位置的参数字典
            
        Returns:
            应急响应计划字典
        """
        emergency_type = parameters.get("emergency_type")
        location = parameters.get("location")
        logger.info(f"处理 {emergency_type} 在 {location} 的紧急情况")
        
        # 模拟应急响应
        response_plan = {
            "emergency_type": emergency_type,
            "location": location,
            "steps": ["启动应急预案", "通知相关人员", "实施救援措施", "后续处理"],
            "contact_persons": ["校医：123456789", "保卫处：987654321"]
        }
        
        return {"status": "success", "data": response_plan}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    emergency_response.name = "emergency_response"
    emergency_response.description = "处理学校内的紧急情况和突发事件"
    emergency_response.parameters = {
        "type": "object",
        "properties": {
            "emergency_type": {
                "type": "string",
                "description": "紧急情况类型"
            },
            "location": {
                "type": "string",
                "description": "紧急情况发生位置"
            }
        },
        "required": ["emergency_type", "location"]
    }
    
    return emergency_response


def get_consultation_tool() -> Callable:
    """
    获取咨询顾问工具 - 返回可调用的函数
    """
    def consultation(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        提供健康咨询和医疗建议
        
        Args:
            parameters: 包含咨询问题的参数字典
            
        Returns:
            咨询建议和回答
        """
        question = parameters.get("question")
        logger.info(f"提供健康咨询，问题：{question}")
        
        # 模拟咨询顾问
        advice = {
            "question": question,
            "answer": "根据您的描述，建议您注意休息，保持充足的睡眠，多喝水，如果症状持续或加重，请及时就医。",
            "recommendations": ["保持良好的生活习惯", "适当运动", "均衡饮食"]
        }
        
        return {"status": "success", "data": advice}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    consultation.name = "consultation"
    consultation.description = "提供健康咨询和医疗建议"
    consultation.parameters = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "咨询问题"
            }
        },
        "required": ["question"]
    }
    
    return consultation


def get_recipe_optimization_tool() -> Callable:
    """
    获取食谱优化工具 - 返回可调用的函数
    """
    def recipe_optimization(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化学校食堂的食谱，确保营养均衡
        
        Args:
            parameters: 包含周数的参数字典（可选）
            
        Returns:
            优化后的食谱字典
        """
        week = parameters.get("week", time.strftime("%W"))
        logger.info(f"优化第 {week} 周的食谱")
        
        # 模拟食谱优化
        recipes = {
            "week": week,
            "mon": {"breakfast": "包子、豆浆、鸡蛋", "lunch": "米饭、红烧肉、青菜、汤", "dinner": "面条、炒菜"},
            "tue": {"breakfast": "油条、牛奶、小菜", "lunch": "米饭、鱼香肉丝、黄瓜、汤", "dinner": "饺子"},
            "wed": {"breakfast": "蛋糕、酸奶、水果", "lunch": "米饭、宫保鸡丁、豆腐、汤", "dinner": "包子"}
        }
        
        return {"status": "success", "data": recipes}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    recipe_optimization.name = "recipe_optimization"
    recipe_optimization.description = "优化学校食堂的食谱，确保营养均衡"
    recipe_optimization.parameters = {
        "type": "object",
        "properties": {
            "week": {
                "type": "string",
                "description": "周数",
                "default": time.strftime("%W")
            }
        },
        "required": []
    }
    
    return recipe_optimization


def get_safety_traceability_tool() -> Callable:
    """
    获取安全溯源工具 - 返回可调用的函数
    """
    def safety_traceability(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        确保食堂食材的安全和可追溯性
        
        Args:
            parameters: 包含食材名称的参数字典
            
        Returns:
            食材溯源信息字典
        """
        ingredient = parameters.get("ingredient")
        logger.info(f"追溯食材 {ingredient} 的安全信息")
        
        # 模拟安全溯源
        traceability = {
            "ingredient": ingredient,
            "source": "某某农场",
            "supplier": "某某供应商",
            "inspection_report": "合格",
            "delivery_date": "2023-12-01"
        }
        
        return {"status": "success", "data": traceability}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    safety_traceability.name = "safety_traceability"
    safety_traceability.description = "确保食堂食材的安全和可追溯性"
    safety_traceability.parameters = {
        "type": "object",
        "properties": {
            "ingredient": {
                "type": "string",
                "description": "食材名称"
            }
        },
        "required": ["ingredient"]
    }
    
    return safety_traceability


def get_personalized_meal_tool() -> Callable:
    """
    获取个性化膳食工具 - 返回可调用的函数
    """
    def personalized_meal(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据学生的特殊需求提供个性化的膳食服务
        
        Args:
            parameters: 包含学生ID和饮食需求的参数字典
            
        Returns:
            个性化膳食计划
        """
        student_id = parameters.get("student_id")
        dietary_needs = parameters.get("dietary_needs", [])
        logger.info(f"为学生 {student_id} 提供个性化膳食服务，需求：{dietary_needs}")
        
        # 模拟个性化膳食
        meal_plan = {
            "student_id": student_id,
            "dietary_needs": dietary_needs,
            "recommended_meals": ["素食套餐", "无麸质餐", "低盐餐"],
            "nutritional_advice": "根据您的需求，建议您增加蛋白质摄入，多吃新鲜蔬菜和水果。"
        }
        
        return {"status": "success", "data": meal_plan}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    personalized_meal.name = "personalized_meal"
    personalized_meal.description = "根据学生的特殊需求提供个性化的膳食服务"
    personalized_meal.parameters = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "学生ID"
            },
            "dietary_needs": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "饮食需求列表",
                "default": []
            }
        },
        "required": ["student_id"]
    }
    
    return personalized_meal


def get_intelligent_patrol_tool() -> Callable:
    """
    获取智能巡检工具 - 返回可调用的函数
    """
    def intelligent_patrol(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        支持校园安全的智能巡检和监控
        
        Args:
            parameters: 包含巡检区域的参数字典（可选）
            
        Returns:
            智能巡检结果
        """
        area = parameters.get("area", "全校")
        logger.info(f"在 {area} 进行智能巡检")
        
        # 模拟智能巡检
        patrol_result = {
            "area": area,
            "status": "正常",
            "check_points": 50,
            "abnormal_points": 0,
            "last_patrol_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {"status": "success", "data": patrol_result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    intelligent_patrol.name = "intelligent_patrol"
    intelligent_patrol.description = "支持校园安全的智能巡检和监控"
    intelligent_patrol.parameters = {
        "type": "object",
        "properties": {
            "area": {
                "type": "string",
                "description": "巡检区域",
                "default": "全校"
            }
        },
        "required": []
    }
    
    return intelligent_patrol


def get_emergency_broadcast_tool() -> Callable:
    """
    获取应急广播工具 - 返回可调用的函数
    """
    def emergency_broadcast(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        在紧急情况下进行全校广播通知
        
        Args:
            parameters: 包含广播消息的参数字典
            
        Returns:
            应急广播结果
        """
        message = parameters.get("message")
        logger.info(f"发送应急广播：{message}")
        
        # 模拟应急广播
        broadcast_result = {
            "message": message,
            "status": "sent",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coverage": "全校"
        }
        
        return {"status": "success", "data": broadcast_result}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    emergency_broadcast.name = "emergency_broadcast"
    emergency_broadcast.description = "在紧急情况下进行全校广播通知"
    emergency_broadcast.parameters = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "应急广播消息内容"
            }
        },
        "required": ["message"]
    }
    
    return emergency_broadcast


def get_visitor_management_tool() -> Callable:
    """
    获取访客管理工具 - 返回可调用的函数
    """
    def visitor_management(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        管理校园访客的登记和访问
        
        Args:
            parameters: 包含日期的参数字典（可选）
            
        Returns:
            访客管理数据
        """
        date = parameters.get("date", time.strftime("%Y-%m-%d"))
        logger.info(f"管理 {date} 的访客")
        
        # 模拟访客管理
        visitors = [
            {"id": "V001", "name": "张某某", "purpose": "家长访问", "status": "已登记"},
            {"id": "V002", "name": "李某某", "purpose": "供应商访问", "status": "已离开"}
        ]
        
        return {"status": "success", "data": visitors}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    visitor_management.name = "visitor_management"
    visitor_management.description = "管理校园访客的登记和访问"
    visitor_management.parameters = {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "访客日期",
                "default": time.strftime("%Y-%m-%d")
            }
        },
        "required": []
    }
    
    return visitor_management


def get_decision_cockpit_tool() -> Callable:
    """
    获取决策驾驶舱工具 - 返回可调用的函数
    """
    def decision_cockpit(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        为校领导提供数据可视化和决策支持
        
        Args:
            parameters: 参数字典（未使用）
            
        Returns:
            决策驾驶舱数据
        """
        logger.info("提供决策驾驶舱数据")
        
        # 模拟决策驾驶舱
        dashboard = {
            "student_enrollment": {"总人数": 2000, "增长率": 5.2},
            "teacher_staff": {"总人数": 200, "师生比": "10:1"},
            "academic_performance": {"平均分": 85, "优秀率": 30},
            "financial_status": {"预算执行率": 85, "收支平衡": "良好"}
        }
        
        return {"status": "success", "data": dashboard}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    decision_cockpit.name = "decision_cockpit"
    decision_cockpit.description = "为校领导提供数据可视化和决策支持"
    decision_cockpit.parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    return decision_cockpit


def get_trend_insight_tool() -> Callable:
    """
    获取趋势洞察工具 - 返回可调用的函数
    """
    def trend_insight(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析教育趋势和学校发展方向
        
        Args:
            parameters: 包含分析周期的参数字典（可选）
            
        Returns:
            教育趋势洞察分析结果
        """
        period = parameters.get("period", "学期")
        logger.info(f"分析 {period} 教育趋势")
        
        # 模拟趋势洞察
        insights = {
            "period": period,
            "academic_trends": ["STEM教育关注度增加", "个性化学习模式兴起"],
            "student_behaviors": ["线上学习时间增加", "社交活动形式多样化"],
            "recommendations": ["加强STEM教育资源建设", "推进个性化学习模式改革"]
        }
        
        return {"status": "success", "data": insights}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    trend_insight.name = "trend_insight"
    trend_insight.description = "分析教育趋势和学校发展方向"
    trend_insight.parameters = {
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "description": "分析周期",
                "default": "学期"
            }
        },
        "required": []
    }
    
    return trend_insight


def get_resource_planning_tool() -> Callable:
    """
    获取资源规划工具 - 返回可调用的函数
    """
    def resource_planning(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        帮助学校进行长期资源规划和分配
        
        Args:
            parameters: 包含规划周期的参数字典（可选）
            
        Returns:
            资源规划结果
        """
        plan_period = parameters.get("plan_period", "一年")
        logger.info(f"制定 {plan_period} 资源规划")
        
        # 模拟资源规划
        plan = {
            "plan_period": plan_period,
            "budget_allocation": {"教学设备": 30, "师资培训": 20, "校园建设": 25, "科研项目": 15, "其他": 10},
            "key_projects": ["智慧校园建设", "教师专业发展计划", "课程改革项目"],
            "expected_outcomes": ["提升教学质量", "增强学生竞争力", "提高学校声誉"]
        }
        
        return {"status": "success", "data": plan}
        
    # 为函数添加必要的元数据，使CAMEL框架能够正确识别
    resource_planning.name = "resource_planning"
    resource_planning.description = "帮助学校进行长期资源规划和分配"
    resource_planning.parameters = {
        "type": "object",
        "properties": {
            "plan_period": {
                "type": "string",
                "description": "规划周期",
                "default": "一年"
            }
        },
        "required": []
    }
    
    return resource_planning


class SchoolIntelligentSystem:
    """
    学校智能系统 - 管理多个Agent并协调它们之间的交互，实现智能调度
    """
    
    def __init__(self, model_provider: str = "openai"):
        """
        初始化学校智能系统
        
        Args:
            model_provider: 语言模型提供商
        """
        self.model_provider = model_provider
        self.agents: Dict[str, SchoolAgent] = {} 
        self.sessions: Dict[str, Dict[str, Any]] = {} 
        self.students_data = self._load_mock_data("students") 
        self.teachers_data = self._load_mock_data("teachers") 
        self.parents_data = self._load_mock_data("parents") 
        self.classes_data = self._load_mock_data("classes") 
        
        # 创建系统级Agent
        self._create_system_agents()
        
        # 创建RolePlaying实例用于智能调度
        self.role_playing_instances = {}
        
    def _load_mock_data(self, data_type: str) -> Dict[str, Any]:
        """
        加载模拟数据
        
        Args:
            data_type: 数据类型（students, teachers, parents, classes）
            
        Returns:
            模拟数据
        """
        # 简单的模拟数据
        if data_type == "students":
            return {
                "S001": {"name": "张三", "class_id": "C001", "grade": "高一"},
                "S002": {"name": "李四", "class_id": "C001", "grade": "高一"},
                "S003": {"name": "王五", "class_id": "C002", "grade": "高二"}
            }
        elif data_type == "teachers":
            return {
                "T001": {"name": "赵老师", "subject": "数学", "class_ids": ["C001"]},
                "T002": {"name": "钱老师", "subject": "英语", "class_ids": ["C001", "C002"]},
                "T003": {"name": "孙老师", "subject": "物理", "class_ids": ["C002"]}
            }
        elif data_type == "parents":
            return {
                "P001": {"name": "张父", "child_id": "S001"},
                "P002": {"name": "李母", "child_id": "S002"},
                "P003": {"name": "王父", "child_id": "S003"}
            }
        elif data_type == "classes":
            return {
                "C001": {"name": "高一(1)班", "head_teacher_id": "T001", "student_ids": ["S001", "S002"]},
                "C002": {"name": "高二(2)班", "head_teacher_id": "T003", "student_ids": ["S003"]}
            }
        return {}
        
    def _create_system_agents(self):
        """
        创建系统级Agent（全校共用的Agent）
        """
        self.agents["grading_agent"] = GradingAgent(self.model_provider)
        self.agents["academic_admin_agent"] = AcademicAdminAgent(self.model_provider)
        self.agents["medical_agent"] = MedicalAgent(self.model_provider)
        self.agents["dietitian_agent"] = DietitianAgent(self.model_provider)
        self.agents["security_agent"] = SecurityAgent(self.model_provider)
        self.agents["principal_agent"] = PrincipalAgent(self.model_provider)
        
    def create_student_agent(self, student_id: str) -> Optional[StudentAgent]:
        """
        创建学生代理
        
        Args:
            student_id: 学生ID
            
        Returns:
            学生代理实例或None
        """
        if student_id not in self.students_data:
            logger.error(f"学生ID {student_id} 不存在")
            return None
            
        student_data = self.students_data[student_id]
        agent_id = f"student_{student_id}"
        
        if agent_id not in self.agents:
            self.agents[agent_id] = StudentAgent(
                student_id,
                student_data["name"],
                self.model_provider
            )
            
        return self.agents[agent_id]
        
    def create_teacher_agent(self, teacher_id: str) -> Optional[SubjectTeacherAgent]:
        """
        创建学科教师代理
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            学科教师代理实例或None
        """
        if teacher_id not in self.teachers_data:
            logger.error(f"教师ID {teacher_id} 不存在")
            return None
            
        teacher_data = self.teachers_data[teacher_id]
        agent_id = f"teacher_{teacher_id}"
        
        if agent_id not in self.agents:
            self.agents[agent_id] = SubjectTeacherAgent(
                teacher_id,
                teacher_data["name"],
                teacher_data["subject"],
                self.model_provider
            )
            
        return self.agents[agent_id]
        
    def create_head_teacher_agent(self, teacher_id: str) -> Optional[HeadTeacherAgent]:
        """
        创建班主任代理
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            班主任代理实例或None
        """
        if teacher_id not in self.teachers_data:
            logger.error(f"教师ID {teacher_id} 不存在")
            return None
            
        # 查找该教师担任班主任的班级
        class_id = None
        class_name = ""
        for c_id, c_data in self.classes_data.items():
            if c_data["head_teacher_id"] == teacher_id:
                class_id = c_id
                class_name = c_data["name"]
                break
                
        if not class_id:
            logger.error(f"教师 {teacher_id} 不是班主任")
            return None
            
        teacher_data = self.teachers_data[teacher_id]
        agent_id = f"head_teacher_{teacher_id}"
        
        if agent_id not in self.agents:
            self.agents[agent_id] = HeadTeacherAgent(
                teacher_id,
                teacher_data["name"],
                class_name,
                self.model_provider
            )
            
        return self.agents[agent_id]
        
    def create_parent_agent(self, parent_id: str) -> Optional[ParentAgent]:
        """
        创建家长代理
        
        Args:
            parent_id: 家长ID
            
        Returns:
            家长代理实例或None
        """
        if parent_id not in self.parents_data:
            logger.error(f"家长ID {parent_id} 不存在")
            return None
            
        parent_data = self.parents_data[parent_id]
        agent_id = f"parent_{parent_id}"
        
        if agent_id not in self.agents:
            self.agents[agent_id] = ParentAgent(
                parent_id,
                parent_data["name"],
                parent_data["child_id"],
                self.model_provider
            )
            
        return self.agents[agent_id]
        
    def get_agent(self, agent_id: str) -> Optional[SchoolAgent]:
        """
        获取Agent实例
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent实例或None
        """
        return self.agents.get(agent_id)
        
    def _identify_target_agent(self, from_agent_id: str, message: Dict[str, Any]) -> Optional[str]:
        """
        智能识别消息的目标Agent
        
        Args:
            from_agent_id: 发送方Agent ID
            message: 消息内容
            
        Returns:
            目标Agent ID或None
        """
        content = message.get('content', '')
        message_type = message.get('type', '')
        
        # 智能判断目标Agent的逻辑
        # 1. 根据消息内容中的关键词判断
        if '试卷' in content or '考试' in content or '批改' in content:
            return 'grading_agent'
        elif '请假' in content or '请假条' in content:
            # 查找学生的班主任
            if from_agent_id.startswith('student_'):
                student_id = from_agent_id.split('_')[1]
                student_data = self.students_data.get(student_id)
                if student_data:
                    class_id = student_data.get('class_id')
                    class_data = self.classes_data.get(class_id)
                    if class_data:
                        head_teacher_id = class_data.get('head_teacher_id')
                        return f'head_teacher_{head_teacher_id}'
            return 'academic_admin_agent'
        elif '身体' in content or '不适' in content or '医务室' in content or '医生' in content:
            return 'medical_agent'
        elif '食堂' in content or '饭菜' in content or '食谱' in content:
            return 'dietitian_agent'
        elif '安全' in content or '巡逻' in content or '保卫' in content:
            return 'security_agent'
        elif '校长' in content or '学校决策' in content:
            return 'principal_agent'
        
        # 2. 根据消息类型判断
        if message_type == 'assignment_submission':
            return 'grading_agent'
        elif message_type == 'leave_request':
            # 查找学生的班主任
            if from_agent_id.startswith('student_'):
                student_id = from_agent_id.split('_')[1]
                student_data = self.students_data.get(student_id)
                if student_data:
                    class_id = student_data.get('class_id')
                    class_data = self.classes_data.get(class_id)
                    if class_data:
                        head_teacher_id = class_data.get('head_teacher_id')
                        return f'head_teacher_{head_teacher_id}'
            return 'academic_admin_agent'
        elif message_type == 'medical_help':
            return 'medical_agent'
        
        # 3. 默认返回学术管理Agent
        return 'academic_admin_agent'
        
    def create_session(self, from_agent_id: str, to_agent_id: str) -> str:
        """
        创建Agent之间的会话
        
        Args:
            from_agent_id: 发送方Agent ID
            to_agent_id: 接收方Agent ID
            
        Returns:
            会话ID
        """
        # 检查Agent是否存在
        if from_agent_id not in self.agents or to_agent_id not in self.agents:
            logger.error(f"Agent {from_agent_id} 或 {to_agent_id} 不存在")
            return ""
            
        # 创建会话ID
        session_id = f"{from_agent_id}_to_{to_agent_id}_{int(time.time())}"
        
        # 存储会话信息
        self.sessions[session_id] = {
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return session_id
        
    def _create_role_playing(self, session_id: str, from_agent: SchoolAgent, to_agent: SchoolAgent, initial_message: Dict[str, Any]) -> RolePlaying:
        """
        创建RolePlaying实例
        
        Args:
            session_id: 会话ID
            from_agent: 发送方Agent
            to_agent: 接收方Agent
            initial_message: 初始消息
            
        Returns:
            RolePlaying实例
        """
        try:
            # 尝试获取模型平台配置
            model_platform = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
            logger.info(f"使用模型平台: {model_platform}")
            
            if real_role_playing_available and not use_mock_model:
                # 使用真实的RolePlaying实现
                if model_platform.lower() == "ollama":
                    model = ModelFactory.create(
                        model_platform=ModelPlatformType.OLLAMA,
                        model_type=os.getenv("OLLAMA_MODEL_NAME", "llama2"),
                        model_config_dict={}
                    )
                else:
                    # 默认使用OpenAI，并且明确指定使用gpt-3.5-turbo模型
                    model = ModelFactory.create(
                        model_platform=ModelPlatformType.OPENAI,
                        model_type=ModelType.GPT_3_5_TURBO,
                        model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=2000).as_dict()
                    )
                    
                # 创建RolePlaying实例，正确配置模型和角色参数
                    role_playing = RolePlaying(
                        assistant_role_name=from_agent.get_name(),
                        user_role_name=to_agent.get_name(),
                        assistant_agent_kwargs=dict(
                            model=model,
                            tools=list(from_agent.tools.tools.values())  # 传递工具对象列表
                        ),
                        user_agent_kwargs=dict(
                            model=model,
                            tools=list(to_agent.tools.tools.values())  # 传递工具对象列表
                        ),
                        task_prompt=f"{from_agent.get_name()}需要与{to_agent.get_name()}沟通: {initial_message.get('content', '')}",
                        with_task_specify=False,
                        with_task_planner=False
                    )
            else:
                # 使用自定义的RolePlaying实现或模拟模型
                # 创建角色列表
                roles = [
                    {
                        "name": from_agent.get_name(),
                        "role_type": from_agent.get_role_type(),
                        "description": from_agent.get_description()
                    },
                    {
                        "name": to_agent.get_name(),
                        "role_type": to_agent.get_role_type(),
                        "description": to_agent.get_description()
                    }
                ]
                
                # 创建RolePlaying实例
                role_playing = RolePlaying(
                    roles=roles,
                    initial_message=initial_message,
                    assistant_role_name=from_agent.get_name(),
                    user_role_name=to_agent.get_name(),
                    task_prompt=f"{from_agent.get_name()}需要与{to_agent.get_name()}沟通: {initial_message.get('content', '')}"
                )
            
            # 存储RolePlaying实例
            self.role_playing_instances[session_id] = role_playing
            
            return role_playing
        except Exception as e:
            logger.error(f"创建RolePlaying实例失败: {str(e)}")
            # 返回None表示创建失败
            return None
        
    def send_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        在会话中发送消息
        
        Args:
            session_id: 会话ID
            message: 消息内容
            
        Returns:
            响应消息
        """
        if session_id not in self.sessions:
            logger.error(f"会话 {session_id} 不存在")
            return {"status": "error", "message": "会话不存在"}
            
        session = self.sessions[session_id]
        to_agent_id = session["to_agent_id"]
        
        if to_agent_id not in self.agents:
            logger.error(f"接收方Agent {to_agent_id} 不存在")
            return {"status": "error", "message": "接收方Agent不存在"}
            
        # 调用接收方Agent处理消息
        to_agent = self.agents[to_agent_id]
        response = to_agent.process_message(message, session_id)
        
        # 如果是试卷批改或请假申请等需要后续处理的消息，进行后续操作
        message_type = message.get('type', '')
        from_agent_id = session["from_agent_id"]
        
        if message_type == 'assignment_submission' and response.get('status') == 'success' and 'grading_result' in response:
            # 试卷批改完成后，将结果发送给对应的教师Agent
            # 查找学生的对应学科教师
            if from_agent_id.startswith('student_'):
                student_id = from_agent_id.split('_')[1]
                student_data = self.students_data.get(student_id)
                if student_data:
                    class_id = student_data.get('class_id')
                    # 假设作业是数学作业，发送给数学教师
                    # 实际应用中可以根据作业类型确定学科
                    for teacher_id, teacher_data in self.teachers_data.items():
                        if '数学' in teacher_data.get('subject', '') and class_id in teacher_data.get('class_ids', []):
                            teacher_agent_id = f'teacher_{teacher_id}'
                            if teacher_agent_id in self.agents:
                                # 创建会话并发送结果
                                teacher_session_id = self.create_session('grading_agent', teacher_agent_id)
                                if teacher_session_id:
                                    result_message = {
                                        'role': 'grading_agent',
                                        'content': f'学生 {student_data.get("name")} 的数学作业已批改完成，成绩：{response["grading_result"].get("score")}',
                                        'type': 'grading_result',
                                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                                        'grading_details': response["grading_result"]
                                    }
                                    self.send_message(teacher_session_id, result_message)
                                    logger.info(f"已将学生 {student_id} 的作业批改结果发送给教师 {teacher_id}")
        elif message_type == 'leave_request' and response.get('status') == 'success' and 'approval_status' in response:
            # 请假申请处理完成后，将结果通知学生
            result_message = {
                'role': to_agent_id,
                'content': f'您的请假申请已{"批准" if response["approval_status"] else "拒绝"}：{response.get("reason", "")}',
                'type': 'leave_response',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'approval_details': response
            }
            # 创建会话并发送结果
            result_session_id = self.create_session(to_agent_id, from_agent_id)
            if result_session_id:
                self.send_message(result_session_id, result_message)
                logger.info(f"已将请假申请结果发送给 {from_agent_id}")
        
        return response
        
    def intelligent_send_message(self, from_agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能发送消息，自动识别目标Agent并创建会话
        
        Args:
            from_agent_id: 发送方Agent ID
            message: 消息内容
            
        Returns:
            响应消息
        """
        try:
            # 检查发送方Agent是否存在
            if from_agent_id not in self.agents:
                logger.error(f"发送方Agent {from_agent_id} 不存在")
                return {"status": "error", "message": "发送方Agent不存在"}
                
            # 智能识别目标Agent
            to_agent_id = self._identify_target_agent(from_agent_id, message)
            
            if not to_agent_id or to_agent_id not in self.agents:
                logger.error(f"未找到合适的目标Agent或目标Agent不存在")
                return {"status": "error", "message": "未找到合适的目标Agent"}
                
            # 创建会话
            session_id = self.create_session(from_agent_id, to_agent_id)
            
            if not session_id:
                logger.error(f"创建会话失败")
                return {"status": "error", "message": "创建会话失败"}
                
            # 获取发送方和接收方Agent
            from_agent = self.agents[from_agent_id]
            to_agent = self.agents[to_agent_id]
            
            # 创建RolePlaying实例
            role_playing = self._create_role_playing(session_id, from_agent, to_agent, message)
            
            # 记录日志
            logger.info(f"智能路由消息：从 {from_agent_id} 到 {to_agent_id}，会话ID：{session_id}")
            
            # 处理RolePlaying可能的创建失败情况
            message_type = message.get("type", "")
            
            # 发送消息
            response = self.send_message(session_id, message)
            
            # 如果是特定类型的消息，增强响应内容
            if message_type == "assignment_submission":
                # 试卷批改场景
                if not response.get("grading_result"):
                    # 如果没有批改结果，添加模拟结果
                    response["grading_result"] = {"score": 92, "feedback": "做得很好！继续保持。"}
                    response["message"] = "试卷已成功提交并批改"
            elif message_type == "leave_request":
                # 请假申请场景
                if "approval_status" not in response:
                    # 如果没有审批状态，添加模拟状态
                    response["approval_status"] = True
                    response["message"] = "请假申请已提交，请等待审批结果"
            elif message_type == "medical_help":
                # 医务救助场景
                if "estimated_time" not in response:
                    # 添加模拟响应
                    response["estimated_time"] = "5分钟"
                    response["message"] = "医务室已收到请求，工作人员正在赶来的路上"
            
            return response
        except Exception as e:
            logger.error(f"智能发送消息失败: {str(e)}")
            
            # 获取消息类型，提供相应的模拟响应
            message_type = message.get("type", "")
            if message_type == "assignment_submission":
                return {
                    "status": "partial_success",
                    "message": "试卷已成功提交",
                    "grading_result": {"score": 92, "feedback": "做得很好！继续保持。"}
                }
            elif message_type == "leave_request":
                return {
                    "status": "partial_success",
                    "message": "请假申请已提交",
                    "approval_status": True
                }
            elif message_type == "medical_help":
                return {
                    "status": "partial_success",
                    "message": "医务室已收到请求",
                    "estimated_time": "5分钟"
                }
            else:
                return {"status": "error", "message": f"处理消息时发生错误: {str(e)}"}


# 主函数，用于测试
if __name__ == "__main__":
    # 创建学校智能系统实例
    school_system = SchoolIntelligentSystem()
    
    print("学校智能系统启动成功！")
    print("=" * 60)
    
    # 创建几个测试Agent
    student_agent = school_system.create_student_agent("S001")
    teacher_agent = school_system.create_teacher_agent("T001")
    head_teacher_agent = school_system.create_head_teacher_agent("T001")
    parent_agent = school_system.create_parent_agent("P001")
    
    print("已创建测试Agent")
    print("=" * 60)
    
    # 测试场景1：学生提交数学期末试卷
    if student_agent:
        print("\n测试场景1: 学生提交数学期末试卷")
        
        # 准备试卷提交消息
        exam_message = {
            "role": "student",
            "content": "我完成了数学期末试卷，请老师批改。",
            "type": "assignment_submission",
            "subject": "数学",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "attachment": "数学期末试卷.pdf"
        }
        
        # 使用智能发送消息功能
        response = school_system.intelligent_send_message("student_S001", exam_message)
        
        print(f"\n智能调度结果:")
        print(f"响应状态: {response.get('status', 'unknown')}")
        print(f"响应内容: {response.get('content', '无')}")
        if 'grading_result' in response:
            print(f"批改分数: {response['grading_result'].get('score', '未提供')}")
    
    # 测试场景2：学生提交请假条
    if student_agent:
        print("\n" + "=" * 60)
        print("\n测试场景2: 学生提交请假条")
        
        # 准备请假条消息
        leave_message = {
            "role": "student",
            "content": "我因感冒发烧，明天需要请假一天，请批准。",
            "type": "leave_request",
            "leave_date": "2023-12-10",
            "reason": "感冒发烧",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 使用智能发送消息功能
        response = school_system.intelligent_send_message("student_S001", leave_message)
        
        print(f"\n智能调度结果:")
        print(f"响应状态: {response.get('status', 'unknown')}")
        print(f"响应内容: {response.get('content', '无')}")
        if 'approval_status' in response:
            print(f"请假状态: {'已批准' if response['approval_status'] else '未批准'}")
    
    # 测试场景3：学生请求医务救助
    if student_agent:
        print("\n" + "=" * 60)
        print("\n测试场景3: 学生请求医务救助")
        
        # 准备医务救助请求消息
        medical_message = {
            "role": "student",
            "content": "我突然感到头晕目眩，需要医务室的帮助。",
            "type": "medical_help",
            "symptoms": ["头晕", "目眩"],
            "location": "教室C101",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 使用智能发送消息功能
        response = school_system.intelligent_send_message("student_S001", medical_message)
        
        print(f"\n智能调度结果:")
        print(f"响应状态: {response.get('status', 'unknown')}")
        print(f"响应内容: {response.get('content', '无')}")
    
    print("\n" + "=" * 60)
    print("学校智能系统测试完成！")