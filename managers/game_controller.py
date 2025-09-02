import pygame

from core.physics_engine import PhysicsEngine
from .camera_manager import CameraManager
from .event_manager import EventManager
from .game_state_manager import GameStateManager
from .ui_manager import UIManager


class GameController:
    """游戏控制器，负责协调各个管理器和处理游戏逻辑"""

    def __init__(self):
        """
        游戏控制器
        """
        self.event_manager = EventManager()
        self.state_manager = GameStateManager()
        self.camera_manager = CameraManager.get_instance()
        self.ui_manager = UIManager.get_instance()
        self.engine=PhysicsEngine.get_instance()

        # 跟踪目标列表
        self.targets = self.engine.balls.copy()
        self.targets.append(self.engine.centroid)
        self.camera_manager.set_target(self.targets[0]) #设置默认跟踪目标

        # 注册事件处理器
        self._register_event_handlers()

    def _register_event_handlers(self):
        """注册所有事件处理器"""
        # 注册退出事件
        self.event_manager.register_event_handler(
            pygame.QUIT, self._handle_quit_event
        )

        # 注册按键事件
        self.event_manager.register_key_handler(
            pygame.K_SPACE, self._handle_pause_toggle
        )
        self.event_manager.register_key_handler(
            pygame.K_c, self._handle_center_toggle
        )
        self.event_manager.register_key_handler(
            pygame.K_1, lambda key: self._handle_target_selection(0)
        )
        self.event_manager.register_key_handler(
            pygame.K_2, lambda key: self._handle_target_selection(1)
        )
        self.event_manager.register_key_handler(
            pygame.K_3, lambda key: self._handle_target_selection(2)
        )
        self.event_manager.register_key_handler(
            pygame.K_4, lambda key: self._handle_target_selection(3)
        )
        self.event_manager.register_key_handler(
            pygame.K_TAB, self._handle_target_cycle
        )

        # 注册连续按键处理器
        self.event_manager.register_continuous_key_handler(
            self.camera_manager.handle_keyboard_event
        )

        # 注册其他事件处理器
        self.event_manager.register_event_handler(
            pygame.KEYDOWN, self._handle_keydown_event
        )

        # 注册UI事件处理器
        self.event_manager.register_event_handler(
            pygame.MOUSEBUTTONDOWN, self.ui_manager.handle_event
        )
        self.event_manager.register_event_handler(
            pygame.MOUSEBUTTONUP, self.ui_manager.handle_event
        )
        self.event_manager.register_event_handler(
            pygame.MOUSEMOTION, self.ui_manager.handle_event
        )
        self.event_manager.register_event_handler(
            pygame.MOUSEWHEEL, self.ui_manager.handle_event
        )

    def _handle_quit_event(self, event):
        """处理退出事件"""
        self.state_manager.stop_game()

    def _handle_pause_toggle(self, key):
        """处理暂停切换"""
        self.state_manager.toggle_pause()

    def _handle_center_toggle(self, key):
        """处理质心显示切换"""
        self.state_manager.toggle_center_display()

    def _handle_target_selection(self, target_index: int):
        """处理跟踪目标选择
        
        Args:
            target_index: 目标索引
        """
        self.camera_manager.set_target(self.targets[target_index])
        self.state_manager.set_target_index(target_index)


    def _handle_target_cycle(self, key):
        """处理跟踪目标循环切换"""
        current_index = self.state_manager.get_current_target_index()
        next_index = (current_index + 1) % len(self.targets)
        self._handle_target_selection(next_index)

    def _handle_keydown_event(self, event):
        """处理按键按下事件"""
        # 让UI管理器处理其他键盘事件
        self.ui_manager.handle_keyboard_event(event.key)

    def handle_events(self):
        """处理所有事件"""
        # 处理连续按键
        self.event_manager.handle_continuous_keys()

        # 处理事件队列
        self.event_manager.handle_events()

    def is_running(self) -> bool:
        """游戏是否在运行"""
        return self.state_manager.is_running()

    def is_paused(self) -> bool:
        """游戏是否暂停"""
        return self.state_manager.is_paused()

    def should_show_centroid(self) -> bool:
        """是否显示质心"""
        return self.state_manager.should_show_centroid()

    def cleanup(self):
        """清理资源"""
        self.event_manager.clear_all_handlers()