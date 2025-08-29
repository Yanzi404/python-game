import pygame
from graphics.camera import Camera


class CameraManager:
    """摄像头管理器单例类"""
    
    _instance = None
    _camera = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 单例模式，不在这里初始化Camera
        pass
    
    @classmethod
    def get_instance(cls):
        """获取CameraManager单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def camera(self):
        """获取Camera实例"""
        if self._camera is None:
            raise RuntimeError("Camera not initialized. Please call get_instance with screen dimensions first.")
        return self._camera
    
    def initialize_camera(self, screen_width, screen_height):
        """初始化摄像头（必须在使用前调用）"""
        if self._camera is None:
            self._camera = Camera(screen_width, screen_height)
        else:
            raise RuntimeError("Camera already initialized. Cannot initialize twice.")
        return self._camera
    
    def reset_camera(self):
        """重置摄像头状态"""
        if self._camera:
            self._camera.reset()
    
    def world_to_screen(self, world_x, world_y):
        """将世界坐标转换为屏幕坐标"""
        return self.camera.world_to_screen(world_x, world_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """将屏幕坐标转换为世界坐标"""
        return self.camera.screen_to_world(screen_x, screen_y)
    
    def scale_radius(self, radius):
        """缩放半径"""
        return self.camera.scale_radius(radius)
    
    def set_zoom(self, zoom):
        """设置缩放级别"""
        self.camera.set_zoom(zoom)
    
    def get_zoom(self):
        """获取当前缩放级别"""
        return self.camera.zoom
    
    def update(self):
        """更新摄像头状态"""
        self.camera.update()
    
    def handle_mouse_event(self, event):
        """处理鼠标事件"""
        self.camera.handle_mouse_event(event)
    
    def handle_keyboard_event(self, keys):
        """处理键盘事件（连续按键）"""
        self.camera.handle_keyboard_event(keys)
    
    def handle_key_press(self, key):
        """处理单次按键事件"""
        self.camera.handle_key_press(key)
    
    def set_target(self, target):
        """设置跟踪目标"""
        self.camera.set_target(target)
    
    def enable_follow_mode(self, enable=True):
        """启用/禁用跟踪模式"""
        self.camera.enable_follow_mode(enable)
    
    def toggle_follow_mode(self):
        """切换跟踪模式"""
        self.camera.toggle_follow_mode()
    
    def get_info(self):
        """获取摄像头信息"""
        return self.camera.get_info()