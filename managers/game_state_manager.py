from typing import Any, Dict


class GameStateManager:
    """游戏状态管理器，负责管理游戏的各种状态"""
    
    def __init__(self):
        """初始化游戏状态管理器"""
        self._state: Dict[str, Any] = {
            'running': True,
            'paused': False,
            'show_center': True,
            'current_target_index': 0
        }
        
        # 状态变化监听器
        self._state_listeners: Dict[str, list] = {}
    
    def get_state(self, key: str, default=None):
        """获取状态值
        
        Args:
            key: 状态键
            default: 默认值
            
        Returns:
            状态值
        """
        return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any):
        """设置状态值
        
        Args:
            key: 状态键
            value: 状态值
        """
        old_value = self._state.get(key)
        self._state[key] = value
        
        # 通知监听器
        if key in self._state_listeners:
            for listener in self._state_listeners[key]:
                listener(key, old_value, value)
    
    def toggle_state(self, key: str):
        """切换布尔状态
        
        Args:
            key: 状态键
            
        Returns:
            切换后的状态值
        """
        current_value = self.get_state(key, False)
        new_value = not current_value
        self.set_state(key, new_value)
        return new_value
    
    def add_state_listener(self, key: str, listener):
        """添加状态变化监听器
        
        Args:
            key: 状态键
            listener: 监听器函数，接收(key, old_value, new_value)参数
        """
        if key not in self._state_listeners:
            self._state_listeners[key] = []
        self._state_listeners[key].append(listener)
    
    def remove_state_listener(self, key: str, listener):
        """移除状态变化监听器
        
        Args:
            key: 状态键
            listener: 监听器函数
        """
        if key in self._state_listeners:
            try:
                self._state_listeners[key].remove(listener)
            except ValueError:
                pass
    
    def is_running(self) -> bool:
        """游戏是否在运行"""
        return self.get_state('running', True)
    
    def is_paused(self) -> bool:
        """游戏是否暂停"""
        return self.get_state('paused', False)
    
    def should_show_center(self) -> bool:
        """是否显示质心"""
        return self.get_state('show_center', False)
    
    def get_current_target_index(self) -> int:
        """获取当前跟踪目标索引"""
        return self.get_state('current_target_index', 0)
    
    def stop_game(self):
        """停止游戏"""
        self.set_state('running', False)
    
    def toggle_pause(self):
        """切换暂停状态"""
        return self.toggle_state('paused')
    
    def toggle_center_display(self):
        """切换质心显示"""
        return self.toggle_state('show_center')
    
    def set_target_index(self, index: int):
        """设置跟踪目标索引"""
        self.set_state('current_target_index', index)

    
    def reset_states(self):
        """重置所有状态到初始值"""
        self._state = {
            'running': True,
            'paused': False,
            'show_center': True,
            'current_target_index': 0
        }