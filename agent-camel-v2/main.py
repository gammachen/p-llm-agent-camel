#!/usr/bin/env python3
"""
Main entry point for Agent-Camel V2 using CAMEL-AI framework.
使用CAMEL-AI框架的Agent-Camel V2的主入口点
"""
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
# 从.env文件加载环境变量
load_dotenv()

# 设置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from examples.camel_travel_planner import camel_travel_planning_conversation


def main():
    """Main function to run the Agent-Camel application.
    运行Agent-Camel应用程序的主函数"""
    print("Starting Agent-Camel V2 application")
    print("Agent-Camel V2 - Intelligent Agent Application (Powered by CAMEL-AI)")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        # If command line arguments provided, use them as the user request
        # 如果提供了命令行参数，则将其用作用户请求
        user_request = " ".join(sys.argv[1:])
        print(f"Using command line arguments as user request: {user_request}")
    else:
        # Otherwise, prompt the user for input
        # 否则，提示用户输入
        print("Prompting user for input")
        print("请输入您的旅行需求，例如：")
        print("- 我想在10月去日本旅行，预算5000美元")
        print("- 计划一次为期两周的欧洲旅行，重点是历史景点")
        print()
        user_request = input("请输入您的旅行需求: ")
    
    if not user_request.strip():
        logger.warning("No valid travel request provided")
        print("未提供有效的旅行需求。")
        return
    
    print(f"\n正在处理您的请求: {user_request}")
    print("请稍候...")
    print(f"Processing user request: {user_request}")
    
    # Process the travel request using CAMEL-AI
    # 使用CAMEL-AI处理旅行请求
    print("Calling camel_travel_planning_conversation function")
    result = camel_travel_planning_conversation(user_request)
    print("Travel request processing completed")
    
    # Display the result
    # 显示结果
    print("\n" + "=" * 50)
    print("旅行计划结果:")
    print("=" * 50)
    print(result["response"])
    print("Displayed travel plan result to user")
    
    # Display detailed results if available
    # 如果有详细结果则显示
    if "details" in result:
        print("Displaying detailed results")
        print("\n详细信息:")
        for key, value in result["details"].items():
            print(f"- {key}: {value}")
    print("Application execution completed")


if __name__ == "__main__":
    main()