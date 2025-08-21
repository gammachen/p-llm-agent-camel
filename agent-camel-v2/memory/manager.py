"""
Memory Manager for Agent-Camel V2.
Agent-Camel V2的记忆管理器
"""
from typing import Dict, Any, List, Optional
import json
import os
import logging
from datetime import datetime, timedelta

# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages agent memory and context.
    管理Agent记忆和上下文"""
    
    def __init__(self, agent_id: str, storage_path: Optional[str] = None):
        """
        Initialize the memory manager.
        初始化记忆管理器
        
        Args:
            agent_id: ID of the agent this memory manager belongs to
                  属于此记忆管理器的Agent ID
            storage_path: Optional path to persistent storage
                      持久化存储的可选路径
        """
        self.agent_id = agent_id
        self.storage_path = storage_path
        self.contexts: Dict[str, List[Dict[str, Any]]] = {}  # Session contexts
                                                    # 会话上下文
        self.interactions: Dict[str, List[Dict[str, Any]]] = {}  # Interaction history
                                                      # 交互历史
        logger.info(f"Initialized MemoryManager for agent {agent_id}")
        self.load_from_storage()  # Load existing memory from storage
                        # 从存储中加载现有记忆
    
    def update_context(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        Update the context for a session.
        更新会话的上下文
        
        Args:
            session_id: Session identifier
                    会话标识符
            message: Message to add to context
                 要添加到上下文的消息
        """
        logger.debug(f"Updating context for session {session_id} in agent {self.agent_id}")
        if session_id not in self.contexts:
            self.contexts[session_id] = []
            logger.debug(f"Created new context for session {session_id}")
        
        self.contexts[session_id].append(message)
        logger.debug(f"Added message to context for session {session_id}. Context now has {len(self.contexts[session_id])} messages")
        
        # Limit context size and compress if necessary
        # 限制上下文大小并在必要时压缩
        if len(self.contexts[session_id]) > 50:
            logger.warning(f"Context for session {session_id} exceeds 50 messages, compressing")
            self.compress_context(session_id)
            
        # Automatically clean up old sessions
        # 自动清理旧会话
        self.cleanup_old_sessions()
    
    def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the context for a session.
        获取会话的上下文
        
        Args:
            session_id: Session identifier
                    会话标识符
            
        Returns:
            Context messages
            上下文消息
        """
        logger.debug(f"Getting context for session {session_id} in agent {self.agent_id}")
        context = self.contexts.get(session_id, [])
        logger.debug(f"Retrieved context with {len(context)} messages for session {session_id}")
        return context
    
    def store_interaction(self, session_id: str, input_message: Dict[str, Any], 
                         output_message: Dict[str, Any], plan: Dict[str, Any]) -> None:
        """
        Store an interaction in memory.
        在记忆中存储一次交互
        
        Args:
            session_id: Session identifier
                    会话标识符
            input_message: Input message
                       输入消息
            output_message: Output message
                        输出消息
            plan: Action plan
              动作计划
        """
        logger.debug(f"Storing interaction for session {session_id} in agent {self.agent_id}")
        if session_id not in self.interactions:
            self.interactions[session_id] = []
            logger.debug(f"Created new interaction history for session {session_id}")
        
        interaction = {
            'input': input_message,
            'output': output_message,
            'plan': plan
        }
        
        self.interactions[session_id].append(interaction)
        logger.debug(f"Stored interaction for session {session_id}. History now has {len(self.interactions[session_id])} interactions")
    
    def get_interaction_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get interaction history for a session.
        获取会话的交互历史
        
        Args:
            session_id: Session identifier
                    会话标识符
            
        Returns:
            Interaction history
            交互历史
        """
        logger.debug(f"Getting interaction history for session {session_id} in agent {self.agent_id}")
        history = self.interactions.get(session_id, [])
        logger.debug(f"Retrieved interaction history with {len(history)} entries for session {session_id}")
        return history
    
    def compress_context(self, session_id: str) -> None:
        """
        Compress the context for a session to reduce memory usage.
        压缩会话的上下文以减少内存使用
        
        Args:
            session_id: Session identifier
                    会话标识符
        """
        logger.info(f"Compressing context for session {session_id} in agent {self.agent_id}")
        # Simple implementation - keep last 20 messages
        # 简单实现 - 保留最后20条消息
        if session_id in self.contexts:
            original_length = len(self.contexts[session_id])
            self.contexts[session_id] = self.contexts[session_id][-20:]
            logger.info(f"Compressed context for session {session_id} from {original_length} to {len(self.contexts[session_id])} messages")
    
    def cleanup_old_sessions(self) -> None:
        """
        Clean up old sessions to free up memory.
        清理旧会话以释放内存
        """
        logger.debug(f"Cleaning up old sessions in agent {self.agent_id}")
        # Remove sessions older than 24 hours
        # 删除超过24小时的会话
        # Placeholder implementation
        # 占位符实现
        pass
    
    def save_to_storage(self) -> None:
        """
        Save memory to persistent storage.
        将记忆保存到持久化存储
        """
        logger.info(f"Saving memory to storage for agent {self.agent_id}")
        # Placeholder implementation
        # 占位符实现
        # In a real implementation, we would save to a database or file system
        # 在实际实现中，我们会保存到数据库或文件系统
        pass
    
    def load_from_storage(self) -> None:
        """
        Load memory from persistent storage.
        从持久化存储加载记忆
        """
        logger.info(f"Loading memory from storage for agent {self.agent_id}")
        # Placeholder implementation
        # 占位符实现
        # In a real implementation, we would load from a database or file system
        # 在实际实现中，我们会从数据库或文件系统加载
        pass