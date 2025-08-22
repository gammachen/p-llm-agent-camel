"""
Tool Library for Agent-Camel V2.
Agent-Camel V2的工具库
"""
from typing import Dict, Any, List, Callable
import logging

# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ToolLibrary:
    """Library of available tools.
    可用工具库"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        print("Initializing ToolLibrary")
        # Register some basic tools
        # 注册一些基本工具
        self.register_tool(self._get_search_tool())
        self.register_tool(self._get_calculator_tool())
    
    def _get_search_tool(self) -> Callable:
        """获取搜索工具 - 返回可调用的函数"""
        def search(query: str) -> Dict[str, Any]:
            """
            在网络上搜索信息
            
            Args:
                query: 搜索查询词
                
            Returns:
                搜索结果字典
            """
            print(f"Executing search tool with query: {query}")
            # This is a placeholder implementation
            # 这是一个占位符实现
            # In a real implementation, we would integrate with a search API
            # 在实际实现中，我们会与搜索API集成
            result = {
                "result": f"Search results for '{query}' would be displayed here in a real implementation."
                          f"在实际实现中，'{query}'的搜索结果将显示在这里。"
            }
            print(f"Search tool execution completed for query: {query}")
            return result
        
        # 为函数添加必要的元数据，使CAMEL框架能够正确识别
        search.name = "search"
        search.description = "Search the web for information\n在网络上搜索信息"
        search.parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string\n搜索查询字符串"
                }
            },
            "required": ["query"]
        }
        
        return search
    
    def _get_calculator_tool(self) -> Callable:
        """获取计算器工具 - 返回可调用的函数"""
        def calculator(expression: str) -> Dict[str, Any]:
            """
            执行数学计算
            
            Args:
                expression: 数学表达式
                
            Returns:
                计算结果字典
            """
            print(f"Executing calculator tool with expression: {expression}")
            # This is a placeholder implementation
            # 这是一个占位符实现
            # In a real implementation, we would evaluate the expression
            # 在实际实现中，我们会计算表达式
            result = {
                "result": f"Result of '{expression}' would be calculated here in a real implementation."
                          f"在实际实现中，'{expression}'的结果将在这里计算。"
            }
            print(f"Calculator tool execution completed for expression: {expression}")
            return result
        
        # 为函数添加必要的元数据，使CAMEL框架能够正确识别
        calculator.name = "calculator"
        calculator.description = "Perform mathematical calculations\n执行数学计算"
        calculator.parameters = {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate\n要计算的数学表达式"
                }
            },
            "required": ["expression"]
        }
        
        return calculator
    
    def register_tool(self, tool: Callable) -> None:
        """Register a tool in the library.
        在库中注册一个工具"""
        print(f"Registering tool: {tool.name}")
        self.tools[tool.name] = tool
        print(f"Tool {tool.name} registered successfully")
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get a list of available tools with their descriptions.
        获取可用工具及其描述的列表"""
        print(f"Getting available tools. Count: {len(self.tools)}")
        tools_list = [
            {
                'name': tool.name,
                'description': tool.description
            }
            for tool in self.tools.values()
        ]
        print(f"Available tools: {[tool['name'] for tool in tools_list]}")
        return tools_list
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given parameters.
        根据名称和给定参数执行工具"""
        print(f"Executing tool: {tool_name}")
        if tool_name not in self.tools:
            logger.error(f"Tool '{tool_name}' not found in library")
            raise ValueError(f"Tool '{tool_name}' not found in library")
        
        # 直接调用工具函数，传入参数
        result = self.tools[tool_name](**parameters)
        print(f"Tool {tool_name} execution completed")
        return result