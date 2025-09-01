import pygame

from config.config import CONFIG, WIDTH
from ui.ui_components import SpeedSlider, ZoomSlider, EnergyGraph, InfoText
from .camera_manager import CameraManager
from graphics.coordinate_system import CoordinateSystem
from .screen_manager import ScreenManager


class UIManager:
    """UI管理器类，负责UI组件的初始化、事件处理和绘制"""
    _instance = None
    
    def __init__(self, font=None):
        """初始化UI管理器"""
        # 通过单例获取CoordinateSystem实例
        self.coord_system = CoordinateSystem.get_instance()
        self.font = font if font else pygame.font.Font(None, 24)
        # 获取CameraManager实例
        self.camera_manager = CameraManager.get_instance()
        
        # UI组件
        self.energy_graph = None
        self.info_text_display = None
        self.speed_slider = None
        self.zoom_slider = None
        
        # 拖动相关状态
        self.dragging = False
        self.last_mouse_pos = None
        
        # UI可见性控制
        self.ui_visible = True
        
        # 初始化UI组件
        self._init_ui_components()
    
    @classmethod
    def get_instance(cls, font=None):
        """获取UIManager单例实例"""
        if cls._instance is None:
            cls._instance = cls(font)
        return cls._instance
    
    def _init_ui_components(self):
        """初始化UI组件"""
        # 创建能量图表
        self.energy_graph = EnergyGraph(
            x=CONFIG['energy_graph_x'],
            y=CONFIG['energy_graph_y'],
            width=CONFIG['energy_graph_width'],
            height=CONFIG['energy_graph_height']
        )
        
        # 创建信息文本显示组件
        self.info_text_display = InfoText(x=10, y=10)
        
        # 创建控制滑块
        self.speed_slider = SpeedSlider(
            x=WIDTH - 250,
            y=30,
            width=200,
            height=20,
            min_val=0.1,
            max_val=100.0,
            initial_val=1.0
        )
        
        self.zoom_slider = ZoomSlider(
            x=WIDTH - 250,
            y=80,  # 在速度滑块下方
            width=200,
            height=20,
            min_val=0.1,
            max_val=3.0,
            initial_val=0.3
        )
    
    def handle_event(self, event):
        """处理UI相关事件"""
        # 让滑块处理鼠标事件
        self.speed_slider.handle_event(event)
        self.zoom_slider.handle_event(event)
        
        # 检查是否点击在UI组件上
        mouse_x, mouse_y = event.pos if hasattr(event, 'pos') else (0, 0)
        is_on_ui = self._is_mouse_on_ui(mouse_x, mouse_y)
        
        # 让摄像头处理鼠标事件（如果不在UI上）
        if not is_on_ui:
            self.camera_manager.handle_mouse_event(event)
        
        # 处理滚轮缩放事件（同时更新滑块）
        if event.type == pygame.MOUSEWHEEL and not is_on_ui:
            # 更新滑块值以反映摄像头的缩放
            self.zoom_slider.val = self.camera_manager.get_zoom()
    
    def handle_keyboard_event(self, key):
        """处理键盘事件"""
        if key == pygame.K_g:
            # 切换网格显示
            self.coord_system.toggle_grid()
        elif key == pygame.K_e:
            # 切换UI显示
            self.energy_graph.toggle_visibility()
            self.info_text_display.toggle_visibility()
            self.speed_slider.toggle_visibility()
            self.zoom_slider.toggle_visibility()
        elif key == pygame.K_0:
            # 重置速度为1.0
            self.speed_slider.val = 1.0
            # 重置缩放为1.0
            self.zoom_slider.val = 1.0
            self.camera_manager.camera.reset_zoom()
        elif key == pygame.K_HOME:
            # 重置摄像头位置和缩放
            self.camera_manager.reset_camera()
            self.zoom_slider.val = 1.0
            # 使网格缓存失效
            if hasattr(self.coord_system, '_invalidate_grid_cache'):
                self.coord_system._invalidate_grid_cache()
        elif key == pygame.K_f:
            # 切换跟踪模式
            self.camera_manager.toggle_follow_mode()
        
        # 让摄像头处理按键事件
        self.camera_manager.handle_key_press(key)
    
    def _is_mouse_on_ui(self, mouse_x, mouse_y):
        """检查鼠标是否在UI组件上"""
        # 检查速度滑块区域
        if (WIDTH - 250 <= mouse_x <= WIDTH - 50 and 
            20 <= mouse_y <= 60):
            return True
            
        # 检查缩放滑块区域  
        if (WIDTH - 250 <= mouse_x <= WIDTH - 50 and 
            70 <= mouse_y <= 110):
            return True
            
        # 检查能量图表区域
        if (CONFIG['energy_graph_x'] <= mouse_x <= CONFIG['energy_graph_x'] + CONFIG['energy_graph_width'] and
            CONFIG['energy_graph_y'] <= mouse_y <= CONFIG['energy_graph_y'] + CONFIG['energy_graph_height']):
            return True
            
        # 检查信息文本区域
        if 10 <= mouse_x <= 300 and 10 <= mouse_y <= 200:
            return True
            
        return False
    
    def draw_ui(self, engine, ball1, ball2, ball3, clock, mass1, mass2, mass3, 
                initial_speed, separation, fixed_physics_dt):
        """绘制所有UI组件"""
        if not self.ui_visible:
            return
            
        screen = ScreenManager.get_instance().screen
        
        # 绘制控制滑块
        self.speed_slider.draw(screen, self.font)
        self.zoom_slider.draw(screen, self.font)

        # 获取能量守恒信息
        energy_drift = engine.check_energy_conservation()

        # 绘制能量图表
        self.energy_graph.draw(screen, self.font, energy_drift)

        # 更新并绘制信息文本
        self.info_text_display.update(
            engine, ball1, ball2, ball3, clock,
            mass1, mass2, mass3, initial_speed,
            separation, fixed_physics_dt, self.camera_manager.camera
        )
        self.info_text_display.draw(screen, self.font)
    
    def draw_pause_overlay(self, paused):
        """绘制暂停覆盖层"""
        if paused:
            screen = ScreenManager.get_instance().screen
            try:
                pause_text = self.font.render("PAUSED", True, (255, 255, 0))  # YELLOW
                text_rect = pause_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                screen.blit(pause_text, text_rect)
            except:
                # 如果字体渲染失败，绘制一个简单的矩形
                pygame.draw.rect(screen, (255, 255, 0), 
                               (screen.get_width() // 2 - 50, screen.get_height() // 2 - 20, 100, 40), 3)
    
    def get_simulation_speed(self):
        """获取模拟速度"""
        return self.speed_slider.val
    
    def get_zoom_level(self):
        """获取缩放级别"""
        return self.zoom_slider.val
    
    def reset_sliders(self):
        """重置滑块到默认值"""
        self.speed_slider.val = 1.0
        self.zoom_slider.val = 1.0