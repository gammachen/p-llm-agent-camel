"""
Comet ML Monitor for Agent-Camel V2.
用于监控大模型调用的Comet ML监控器。
"""
import time
from typing import Dict, Any, Optional
from config.settings import settings

# 尝试导入comet_ml，如果不可用则提供一个空的实现
try:
    import comet_ml
    COMET_AVAILABLE = True
except ImportError:
    COMET_AVAILABLE = False
    print("警告: comet_ml库不可用，监控功能将被禁用。请安装comet_ml以启用监控。")


class CometMonitor:
    """
    Comet ML监控器，用于跟踪和记录模型调用。
    """
    _instance = None
    
    def __new__(cls):
        # 单例模式
        if cls._instance is None:
            cls._instance = super(CometMonitor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        初始化Comet ML监控器
        """
        self.experiment = None
        self.is_active = False
        
        print(f"Initializing Comet ML monitor...{COMET_AVAILABLE} {settings.COMET_API_KEY} {settings.COMET_LOG_MODEL_CALLS}")
        
        # 仅当comet_ml可用且配置了API密钥时才初始化
        if COMET_AVAILABLE and settings.COMET_API_KEY and settings.COMET_LOG_MODEL_CALLS:
            try:
                self.experiment = comet_ml.Experiment(
                    api_key=settings.COMET_API_KEY,
                    project_name=settings.COMET_PROJECT_NAME,
                    workspace=settings.COMET_WORKSPACE,
                    auto_param_logging=True,
                    auto_metric_logging=True,
                    auto_histogram_weight_logging=False,
                    auto_histogram_gradient_logging=False,
                    auto_histogram_activation_logging=False,
                )
                self.is_active = True
                print(f"Comet ML监控已初始化，项目: {settings.COMET_PROJECT_NAME}")
            except Exception as e:
                print(f"初始化Comet ML监控失败: {str(e)}")
                self.experiment = None
                self.is_active = False
        elif not settings.COMET_LOG_MODEL_CALLS:
            print("Comet ML监控已禁用 (COMET_LOG_MODEL_CALLS=False)")
        
    def log_parameter(self, name: str, value):
        """
        记录单个参数到Comet ML
        
        Args:
            name: 参数名称
            value: 参数值
        """
        if not self.is_active or self.experiment is None:
            return
        
        try:
            self.experiment.log_parameter(name, value)
        except Exception as e:
            print(f"记录参数到Comet ML失败: {str(e)}")
            
    def log_model_call(self, provider_name: str, prompt: str, response: str, **kwargs):
        """
        记录模型调用信息到Comet ML
        
        Args:
            provider_name: 模型提供商名称
            prompt: 输入的提示文本
            response: 模型的响应
            **kwargs: 其他参数（如模型名称、温度等）
        """
        if not self.is_active or self.experiment is None:
            return
        
        try:
            # 创建调用的唯一标识符
            call_id = f"{provider_name}_{int(time.time())}_{hash(prompt) % 1000000}"
            
            # 记录基本信息
            self.experiment.log_parameter(f"{call_id}_provider", provider_name)
            self.experiment.log_parameter(f"{call_id}_model", kwargs.get('model', 'unknown'))
            
            # 记录性能参数
            if 'temperature' in kwargs:
                self.experiment.log_parameter(f"{call_id}_temperature", kwargs.get('temperature'))
            if 'max_tokens' in kwargs:
                self.experiment.log_parameter(f"{call_id}_max_tokens", kwargs.get('max_tokens'))
            
            # 记录输入输出文本
            # 注意：为了保护隐私，实际应用中可能需要过滤敏感信息
            self.experiment.log_text(f"{call_id}_prompt {prompt[:1000]}")  # 限制长度以避免过大的日志
            self.experiment.log_text(f"{call_id}_response {response[:1000]}")
            
            # 计算并记录令牌数（近似值）
            prompt_tokens = len(prompt.split())
            response_tokens = len(response.split())
            self.experiment.log_metric(f"{call_id}_prompt_tokens", prompt_tokens)
            self.experiment.log_metric(f"{call_id}_response_tokens", response_tokens)
            self.experiment.log_metric(f"{call_id}_total_tokens", prompt_tokens + response_tokens)
            
            # 记录类别和标签以便分析
            self.experiment.add_tag(provider_name)
            
        except Exception as e:
            print(f"记录模型调用到Comet ML失败: {str(e)}")
    
    def end_experiment(self):
        """
        结束当前的Comet ML实验
        """
        if self.is_active and self.experiment is not None:
            try:
                self.experiment.end()
                self.is_active = False
                print("Comet ML实验已结束")
            except Exception as e:
                print(f"结束Comet ML实验失败: {str(e)}")


# 创建全局监控器实例
comet_monitor = CometMonitor()