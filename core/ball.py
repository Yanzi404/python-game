import numpy as np
import pygame

from config.config import auto_params, WHITE
from graphics.coordinate_system import CoordinateSystem
from managers.camera_manager import CameraManager
from managers.screen_manager import ScreenManager


class Ball:
    """质点类，包含位置、速度、质量等物理属性"""

    def __init__(self, x, y, vx, vy, mass, radius, color):
        self.x = np.float64(x)  # x坐标（物理坐标）
        self.y = np.float64(y)  # y坐标（物理坐标）
        self.vx = np.float64(vx)  # x方向速度
        self.vy = np.float64(vy)  # y方向速度
        self.mass = np.float64(mass)  # 质量
        self.radius = radius  # 显示半径（物理半径）
        self.color = color  # 颜色
        self.trail = []  # 轨迹点列表（物理坐标）
        self.base_trail_length = auto_params['trail_length']  # 基础轨迹长度
        self.max_trail = self.base_trail_length * 10  # 最大存储长度

        # 为Verlet积分法添加前一帧的位置
        dt = np.float64(1.0 / 60.0)
        self.prev_x = self.x - self.vx * dt
        self.prev_y = self.y - self.vy * dt
        self.ax = 0
        self.ay = 0

    def apply_force_verlet(self, fx, fy, dt):
        """使用Verlet积分法更新位置和速度"""
        # 确保输入参数为高精度
        fx = np.float64(fx)
        fy = np.float64(fy)
        dt = np.float64(dt)

        # 计算加速度
        self.ax = fx / self.mass
        self.ay = fy / self.mass

        # Verlet积分：x(t+dt) = 2*x(t) - x(t-dt) + a*dt²
        dt_squared = dt * dt
        new_x = 2 * self.x - self.prev_x + self.ax * dt_squared
        new_y = 2 * self.y - self.prev_y + self.ay * dt_squared

        # 计算速度：v = (x(t+dt) - x(t-dt)) / (2*dt)
        if dt > 0:
            two_dt = 2 * dt
            self.vx = (new_x - self.prev_x) / two_dt
            self.vy = (new_y - self.prev_y) / two_dt

        # 更新位置
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = new_x
        self.y = new_y

        # 添加轨迹点（转换为整数用于显示）
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

    # def reset_verlet_state(self, x, y, vx, vy, dt=1 / 60):
    #     """重置Verlet积分状态（用于重置功能）"""
    #     # 使用高精度类型
    #     self.x = np.float64(x)
    #     self.y = np.float64(y)
    #     self.vx = np.float64(vx)
    #     self.vy = np.float64(vy)
    #     dt = np.float64(dt)
    #
    #     # 重新计算前一帧位置
    #     self.prev_x = self.x - self.vx * dt
    #     self.prev_y = self.y - self.vy * dt
    #     self.ax = 0.0
    #     self.ay = 0.0
    #     self.trail.clear()
    #     """施加力并更新速度和位置（原始欧拉方法，保留作为备用）"""
    #     # 计算加速度 a = F/m
    #     ax = fx / self.mass
    #     ay = fy / self.mass
    #
    #     # 更新速度 v = v0 + a*t
    #     self.vx += ax * dt
    #     self.vy += ay * dt
    #
    #     # 更新位置 x = x0 + v*t
    #     self.x += self.vx * dt
    #     self.y += self.vy * dt
    #
    #     # 添加轨迹点
    #     self.trail.append((int(self.x), int(self.y)))
    #     if len(self.trail) > self.max_trail:
    #         self.trail.pop(0)

    def draw(self):
        """绘制质点（使用坐标转换）"""
        # 通过单例获取坐标系统和屏幕对象
        coord_system = CoordinateSystem.get_instance()
        screen = ScreenManager.get_instance().screen
        # 转换物理坐标到屏幕坐标
        screen_x, screen_y = coord_system.physics_to_screen(self.x, self.y)
        scaled_radius = coord_system.scale_radius(self.radius)

        # 根据缩放比例动态调整轨迹显示长度（反向关系）
        camera_manager = CameraManager.get_instance()
        zoom_factor = camera_manager.get_zoom()
        # 缩放越小，轨迹越长：使用反比关系
        dynamic_trail_length = int(self.base_trail_length / zoom_factor)
        # 限制在合理范围内：最少50个点，最多不超过存储的轨迹点数
        dynamic_trail_length = max(50, min(dynamic_trail_length, len(self.trail)))

        # 绘制轨迹（只显示最近的dynamic_trail_length个点）
        if len(self.trail) > 1:
            # 获取要显示的轨迹点
            display_trail = self.trail[-dynamic_trail_length:] if len(self.trail) > dynamic_trail_length else self.trail

            # 根据缩放比例计算轨迹点稀疏程度
            # 缩放越小，跳过的点越多，实现稀疏绘制
            skip_factor = max(1, int(1 / zoom_factor))  # zoom=0.1时skip_factor=500
            sparse_trail = display_trail[::skip_factor]  # 每skip_factor个点取一个

            screen_trail = []
            for trail_x, trail_y in sparse_trail:
                trail_screen_x, trail_screen_y = coord_system.physics_to_screen(trail_x, trail_y)
                # 只添加在屏幕范围内的点
                if (-50 <= trail_screen_x <= coord_system.screen_width + 50 and
                        -50 <= trail_screen_y <= coord_system.screen_height + 50):
                    screen_trail.append((trail_screen_x, trail_screen_y))

            if len(screen_trail) > 1:
                try:
                    # 轨迹线条粗细保持为1，避免缩小时线条过粗
                    pygame.draw.lines(screen, self.color, False, screen_trail, 1)
                except:
                    pass

        # 绘制质点（只在屏幕范围内绘制）
        if (-scaled_radius <= screen_x <= coord_system.screen_width + scaled_radius and
                -scaled_radius <= screen_y <= coord_system.screen_height + scaled_radius):
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), scaled_radius)
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), scaled_radius, 1)
