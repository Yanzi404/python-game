import pygame

from config.config import CONFIG, GREEN
from core.vector2d import Vector2D
from graphics.coordinate_system import CoordinateSystem
from managers.screen_manager import ScreenManager


class Centroid:
    """质心类，用于计算和管理三体系统的质心"""

    def __init__(self):
        """
        质心类
        """
        self.trail_length = 200
        self.trail = []  # 质心轨迹点列表（物理坐标）
        self.position = Vector2D(0.0, 0.0)  # 质心位置向量
        self.velocity = Vector2D(0.0, 0.0)  # 质心速度向量
        self.total_mass = 0.0  # 系统总质量
        self.is_show = True
        
        # 为了兼容性，保留x, y, vx, vy属性
        self._update_legacy_attributes()

    def _update_legacy_attributes(self):
        """更新兼容性属性"""
        self.x = self.position.x
        self.y = self.position.y
        self.vx = self.velocity.x
        self.vy = self.velocity.y

    def calculate_position(self, balls):
        """
        计算质心的物理坐标
        
        Args:
            balls: 球对象列表
            
        Returns:
            tuple: (center_x, center_y) 质心的物理坐标
        """
        if not balls:
            self.position = Vector2D(0.0, 0.0)
            self.total_mass = 0.0
            self._update_legacy_attributes()
            return 0.0, 0.0

        total_mass = 0.0
        weighted_position = Vector2D(0.0, 0.0)

        for ball in balls:
            total_mass += ball.mass
            weighted_position = weighted_position + ball.position * ball.mass

        if total_mass > 0:
            self.position = weighted_position / total_mass
            self.total_mass = total_mass
            self._update_legacy_attributes()
            return self.position.x, self.position.y
        else:
            self.position = Vector2D(0.0, 0.0)
            self.total_mass = 0.0
            self._update_legacy_attributes()
            return 0.0, 0.0

    def calculate_velocity(self, balls):
        """
        计算质心的速度
        
        Args:
            balls: 球对象列表
            
        Returns:
            tuple: (velocity_x, velocity_y) 质心的速度
        """
        if not balls or self.total_mass <= 0:
            self.velocity = Vector2D(0.0, 0.0)
            self._update_legacy_attributes()
            return 0.0, 0.0

        weighted_velocity = Vector2D(0.0, 0.0)

        for ball in balls:
            weighted_velocity = weighted_velocity + ball.velocity * ball.mass

        self.velocity = weighted_velocity / self.total_mass
        self._update_legacy_attributes()

        return self.velocity.x, self.velocity.y

    def update(self, balls):
        """
        更新质心状态（位置、速度、轨迹）
        
        Args:
            balls: 球对象列表
        """
        if not self.is_show:
            return
        # 计算质心位置和速度
        self.calculate_position(balls)
        self.calculate_velocity(balls)

        # 添加到轨迹
        self.add_to_trail(self.x, self.y)

    def add_to_trail(self, x, y):
        """
        添加点到质心轨迹
        
        Args:
            x: x坐标（物理坐标）
            y: y坐标（物理坐标）
        """
        self.trail.append((x, y))

        # 限制轨迹长度
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

    def get_screen_position(self):
        """
        获取质心的屏幕坐标
        
        Returns:
            tuple: (screen_x, screen_y) 质心的屏幕坐标
        """
        coord_system = CoordinateSystem.get_instance()
        return coord_system.physics_to_screen(self.position.x, self.position.y)

    def draw(self, show_trail=False):
        """
        绘制质心和轨迹
        
        Args:
            show_trail: 是否显示轨迹
        """
        # 绘制质心轨迹
        if show_trail and len(self.trail) > 1:
            self.draw_trail()

        # 绘制质心点
        self.draw_center_point()

    def draw_center_point(self):
        """
        绘制质心点
        """
        if not self.is_show:
            return
        coord_system = CoordinateSystem.get_instance()
        screen = ScreenManager.get_instance().screen
        # 获取质心的屏幕坐标
        screen_x, screen_y = self.get_screen_position()

        # 缩放质心圆的半径
        scaled_radius = coord_system.scale_radius(CONFIG.get('center_radius', 3))
        scaled_circle_radius = coord_system.scale_radius(CONFIG.get('center_circle_radius', 8))

        # 绘制质心
        pygame.draw.circle(screen, GREEN, (int(screen_x), int(screen_y)), max(1, int(scaled_radius)))
        pygame.draw.circle(screen, GREEN, (int(screen_x), int(screen_y)), max(1, int(scaled_circle_radius)), 1)

    def draw_trail(self):
        """
        绘制质心轨迹
        """
        if len(self.trail) < 2:
            return

        coord_system = CoordinateSystem.get_instance()
        screen = ScreenManager.get_instance().screen
        # 转换轨迹点到屏幕坐标
        screen_points = []
        for x, y in self.trail:
            screen_x, screen_y = coord_system.physics_to_screen(x, y)
            screen_points.append((int(screen_x), int(screen_y)))

        # 绘制轨迹线
        if len(screen_points) >= 2:
            # 使用渐变透明度绘制轨迹
            for i in range(len(screen_points) - 1):
                alpha = int(255 * (i + 1) / len(screen_points))  # 渐变透明度
                color = (*GREEN[:3], alpha) if len(GREEN) == 4 else GREEN

                try:
                    pygame.draw.line(screen, color, screen_points[i], screen_points[i + 1], 1)
                except (ValueError, TypeError):
                    # 如果颜色格式不支持透明度，使用普通颜色
                    pygame.draw.line(screen, GREEN, screen_points[i], screen_points[i + 1], 1)

    def __str__(self):
        """
        返回质心状态的字符串表示
        """
        return f"CenterOfMass(position=({self.position.x}, {self.position.y}), velocity=({self.velocity.x}, {self.velocity.y}), mass={self.total_mass})"
