import pygame
from managers.camera_manager import CameraManager
from managers.screen_manager import ScreenManager


class CoordinateSystem:
    """坐标系统单例类，处理物理坐标和显示坐标的转换"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoordinateSystem, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 单例模式，避免重复初始化
        if CoordinateSystem._initialized:
            return
        
        # 默认屏幕尺寸，需要通过initialize方法设置实际值
        self.screen_width = 800
        self.screen_height = 600
        # 使用CameraManager单例获取摄像头
        self.camera_manager = CameraManager.get_instance()
        self.unit_scale = 1.0  # 一个距离单位等于1个像素点

        # 网格参数
        self.grid_enabled = True
        self.base_grid_unit = 100  # 基础网格大小（距离单位）
        self.grid_color = (40, 40, 40)  # 深灰色网格线
        self.major_grid_color = (80, 80, 80)  # 主网格线颜色 - 更明显
        self.major_grid_interval = 5  # 每5条线绘制一条主网格线

        # 网格缓存相关
        self.grid_surface = None
        self.grid_cache_valid = False
        self.last_zoom = None
        self.last_camera_x = None
        self.last_camera_y = None
        self.last_grid_enabled = None
        
        CoordinateSystem._initialized = True
    
    @classmethod
    def get_instance(cls):
        """获取CoordinateSystem单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, screen_width, screen_height):
        """初始化屏幕尺寸（必须在使用前调用）"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        # 重置网格缓存
        self.grid_surface = None
        self.grid_cache_valid = False
        return self

    def set_zoom(self, zoom):
        """设置缩放比例"""
        if self.camera_manager.get_zoom() != zoom:
            self.camera_manager.set_zoom(zoom)
            self.grid_cache_valid = False  # 缩放改变，网格缓存失效

    def physics_to_screen(self, physics_x, physics_y):
        """将物理坐标转换为屏幕坐标"""
        # 应用单位转换
        world_x = physics_x * self.unit_scale
        world_y = physics_y * self.unit_scale
        
        # 使用摄像头管理器进行坐标转换
        return self.camera_manager.world_to_screen(world_x, world_y)

    def scale_radius(self, physics_radius):
        """缩放半径"""
        return self.camera_manager.scale_radius(physics_radius * self.unit_scale)

    def invalidate_grid_cache(self):
        """使网格缓存失效"""
        self.grid_cache_valid = False

    def _is_grid_cache_valid(self):
        """检查网格缓存是否有效"""
        camera = self.camera_manager.camera
        return (self.grid_cache_valid and
                self.last_zoom == camera.zoom and
                self.last_camera_x == camera.x and
                self.last_camera_y == camera.y and
                self.last_grid_enabled == self.grid_enabled)

    def _update_grid_cache_state(self):
        """更新网格缓存状态"""
        camera = self.camera_manager.camera
        self.last_zoom = camera.zoom
        self.last_camera_x = camera.x
        self.last_camera_y = camera.y
        self.last_grid_enabled = self.grid_enabled
        self.grid_cache_valid = True

    def _render_grid_to_surface(self):
        """将网格渲染到缓存surface"""
        if self.grid_surface is None:
            self.grid_surface = pygame.Surface((self.screen_width, self.screen_height))

        # 清空surface（透明背景）
        self.grid_surface.fill((0, 0, 0, 0))
        self.grid_surface.set_colorkey((0, 0, 0))  # 设置黑色为透明

        if not self.grid_enabled:
            return

        # 计算当前缩放下的网格大小（基于距离单位）
        grid_size_pixels = self.base_grid_unit * self.unit_scale * self.camera_manager.get_zoom()

        # 动态调整网格密度以保持合适的视觉效果
        actual_grid_size = grid_size_pixels

        # 如果网格太小，增大网格间距
        while actual_grid_size < 20:
            actual_grid_size *= 2

        # 如果网格太大，减小网格间距
        while actual_grid_size > 150:
            actual_grid_size *= 0.5

        # 计算网格原点在屏幕上的位置（使用摄像头管理器）
        grid_origin_screen_x, grid_origin_screen_y = self.camera_manager.world_to_screen(0, 0)

        # 计算需要绘制的网格线范围，确保覆盖整个屏幕
        # 计算第一条可见的垂直线位置
        first_vertical_line = grid_origin_screen_x % actual_grid_size
        if first_vertical_line > 0:
            first_vertical_line -= actual_grid_size

        # 计算第一条可见的水平线位置  
        first_horizontal_line = grid_origin_screen_y % actual_grid_size
        if first_horizontal_line > 0:
            first_horizontal_line -= actual_grid_size

        # 绘制垂直网格线
        line_count = 0
        x = first_vertical_line
        while x <= self.screen_width and line_count < 200:  # 安全限制
            # 判断是否为主网格线
            grid_index = round((x - grid_origin_screen_x) / actual_grid_size)
            if grid_index % self.major_grid_interval == 0:
                color = self.major_grid_color
                line_width = 2  # 主网格线更粗
            else:
                color = self.grid_color
                line_width = 1

            # 绘制线条（只要在屏幕范围内就绘制）
            if x >= 0:
                pygame.draw.line(self.grid_surface, color, (int(x), 0), (int(x), self.screen_height), line_width)
            x += actual_grid_size
            line_count += 1

        # 绘制水平网格线
        line_count = 0
        y = first_horizontal_line
        while y <= self.screen_height and line_count < 200:  # 安全限制
            # 判断是否为主网格线
            grid_index = round((y - grid_origin_screen_y) / actual_grid_size)
            if grid_index % self.major_grid_interval == 0:
                color = self.major_grid_color
                line_width = 2  # 主网格线更粗
            else:
                color = self.grid_color
                line_width = 1

            # 绘制线条（只要在屏幕范围内就绘制）
            if y >= 0:
                pygame.draw.line(self.grid_surface, color, (0, int(y)), (self.screen_width, int(y)), line_width)
            y += actual_grid_size
            line_count += 1

    def draw_grid(self):
        """绘制背景网格（使用缓存优化）"""
        if not self._is_grid_cache_valid():
            # 缓存无效，重新渲染网格
            self._render_grid_to_surface()
            self._update_grid_cache_state()

        # 将缓存的网格surface绘制到屏幕上
        if self.grid_enabled and self.grid_surface:
            screen = ScreenManager.get_instance().screen
            screen.blit(self.grid_surface, (0, 0))

    def toggle_grid(self):
        """切换网格显示状态"""
        self.grid_enabled = not self.grid_enabled
        self.grid_cache_valid = False  # 网格状态改变，缓存失效
