from typing import Dict, List, Callable

import pygame


class EventManager:
    """事件管理器类，负责统一管理和分发事件"""

    def __init__(self):
        """初始化事件管理器"""
        # 事件处理器字典，键为事件类型，值为处理器列表
        self._event_handlers: Dict[int, List[Callable]] = {}
        # 键盘事件处理器字典，键为按键，值为处理器列表
        self._key_handlers: Dict[int, List[Callable]] = {}
        # 连续按键处理器列表
        self._continuous_key_handlers: List[Callable] = []

    def register_event_handler(self, event_type: int, handler: Callable):
        """注册事件处理器
        
        Args:
            event_type: pygame事件类型
            handler: 事件处理函数，接收event参数
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def register_key_handler(self, key: int, handler: Callable):
        """注册按键事件处理器
        
        Args:
            key: pygame按键常量
            handler: 按键处理函数，接收key参数
        """
        if key not in self._key_handlers:
            self._key_handlers[key] = []
        self._key_handlers[key].append(handler)

    def register_continuous_key_handler(self, handler: Callable):
        """注册连续按键处理器
        
        Args:
            handler: 连续按键处理函数，接收keys参数
        """
        self._continuous_key_handlers.append(handler)

    def unregister_event_handler(self, event_type: int, handler: Callable):
        """注销事件处理器"""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
            except ValueError:
                pass

    def unregister_key_handler(self, key: int, handler: Callable):
        """注销按键事件处理器"""
        if key in self._key_handlers:
            try:
                self._key_handlers[key].remove(handler)
            except ValueError:
                pass

    def unregister_continuous_key_handler(self, handler: Callable):
        """注销连续按键处理器"""
        try:
            self._continuous_key_handlers.remove(handler)
        except ValueError:
            pass

    def handle_events(self):
        """处理所有pygame事件"""
        for event in pygame.event.get():
            # 分发通用事件
            if event.type in self._event_handlers:
                for handler in self._event_handlers[event.type]:
                    handler(event)

            # 分发按键事件
            if event.type == pygame.KEYDOWN and event.key in self._key_handlers:
                for handler in self._key_handlers[event.key]:
                    handler(event.key)

    def handle_continuous_keys(self):
        """处理连续按键"""
        keys = pygame.key.get_pressed()
        for handler in self._continuous_key_handlers:
            handler(keys)

    def clear_all_handlers(self):
        """清除所有事件处理器"""
        self._event_handlers.clear()
        self._key_handlers.clear()
        self._continuous_key_handlers.clear()
