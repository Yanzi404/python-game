import math
import sys

import pygame

from core.ball import Ball
from config.config import BLACK, RED, BLUE, GREEN, PURPLE

from config.config import CONFIG, auto_params, WIDTH, HEIGHT, FPS, FIXED_PHYSICS_DT
from graphics.coordinate_system import CoordinateSystem
from core.physics_engine import PhysicsEngine
from managers.ui_manager import UIManager
from managers.camera_manager import CameraManager

# 初始化pygame
pygame.init()


class Game:
    """主类"""

    def __init__(self):
        """初始化"""
        # 创建屏幕
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Scalable Physics Engine")
        self.clock = pygame.time.Clock()

        # 创建摄像机

        # 创建坐标系统
        self.coord_system = CoordinateSystem(WIDTH, HEIGHT)
        
        # 获取摄像头管理器实例
        self.camera_manager = CameraManager.get_instance(WIDTH, HEIGHT)

        # 创建物理引擎
        self.engine = PhysicsEngine(integration_method='verlet')

        # 初始化物理参数
        self.init_physics()

        # 创建UI管理器
        self.ui_manager = UIManager(self.coord_system, pygame.font.Font(None, 24))

        # 状态
        self.running = True
        self.paused = False
        self.show_center = True

        # 物理模拟固定时间步长
        self.physics_accumulator = 0.0

    def init_physics(self):
        """初始化物理系统"""
        # 创建三个质点 - 三角形配置
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        self.separation = CONFIG['separation']
        self.mass1 = CONFIG['mass1']
        self.mass2 = CONFIG['mass2']
        self.mass3 = CONFIG['mass3']
        self.initial_speed = CONFIG['initial_speed']
        self.total_mass = self.mass1 + self.mass2 + self.mass3

        # 三角形配置：三个球形成等边三角形
        angle1 = 0  # 球1在右侧
        angle2 = 2 * math.pi / 3  # 球2在左上
        angle3 = 4 * math.pi / 3  # 球3在左下

        # 计算三个球的初始位置（围绕质心形成三角形）
        radius = self.separation / 2  # 三角形的外接圆半径

        # 球1位置和速度
        self.x1 = center_x + radius * math.cos(angle1)
        self.y1 = center_y + radius * math.sin(angle1)
        # 切向速度（垂直于半径方向）
        self.vx1 = -self.initial_speed * math.sin(angle1)
        self.vy1 = self.initial_speed * math.cos(angle1)
        # 球2位置和速度
        self.x2 = center_x + radius * math.cos(angle2)
        self.y2 = center_y + radius * math.sin(angle2)
        self.vx2 = -self.initial_speed * math.sin(angle2)
        self.vy2 = self.initial_speed * math.cos(angle2)
        # 球3位置和速度
        self.x3 = center_x + radius * math.cos(angle3)
        self.y3 = center_y + radius * math.sin(angle3)
        self.vx3 = -self.initial_speed * math.sin(angle3)
        self.vy3 = self.initial_speed * math.cos(angle3)
        # 创建三个球
        self.ball1 = Ball(
            x=self.x1, y=self.y1, vx=self.vx1, vy=self.vy1,
            mass=self.mass1,
            radius=auto_params['radius1'],
            color=BLUE
        )

        self.ball2 = Ball(
            x=self.x2, y=self.y2, vx=self.vx2, vy=self.vy2,
            mass=self.mass2,
            radius=auto_params['radius2'],
            color=RED
        )

        self.ball3 = Ball(
            x=self.x3, y=self.y3, vx=self.vx3, vy=self.vy3,
            mass=self.mass3,
            radius=auto_params['radius3'],
            color=PURPLE
        )

        # 添加质点到物理引擎
        self.engine.add_ball(self.ball1)
        self.engine.add_ball(self.ball2)
        self.engine.add_ball(self.ball3)
        
        # 设置摄像头默认跟踪目标为第一个球
        self.camera_manager.set_target(self.ball1)
        
        # 当前跟踪目标索引（用于切换）
        self.current_target_index = 0
        self.targets = [self.ball1, self.ball2, self.ball3]

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # 让UI管理器处理事件
            self.ui_manager.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    pass
                    # 重置质点位置
                    # self.ball1.reset_verlet_state(self.x1, self.y1, self.vx1, self.vy1, FIXED_PHYSICS_DT)
                    # self.ball2.reset_verlet_state(self.x2, self.y2, self.vx2, self.vy2, FIXED_PHYSICS_DT)
                    # self.ball3.reset_verlet_state(self.x3, self.y3, self.vx3, self.vy3, FIXED_PHYSICS_DT)
                    # self.physics_accumulator = 0.0
                elif event.key == pygame.K_c:
                    # 切换质心显示
                    self.show_center = not self.show_center
                elif event.key == pygame.K_1:
                    # 跟踪球1
                    self.camera_manager.set_target(self.ball1)
                    self.current_target_index = 0
                elif event.key == pygame.K_2:
                    # 跟踪球2
                    self.camera_manager.set_target(self.ball2)
                    self.current_target_index = 1
                elif event.key == pygame.K_3:
                    # 跟踪球3
                    self.camera_manager.set_target(self.ball3)
                    self.current_target_index = 2
                elif event.key == pygame.K_TAB:
                    # 切换到下一个跟踪目标
                    self.current_target_index = (self.current_target_index + 1) % len(self.targets)
                    self.camera_manager.set_target(self.targets[self.current_target_index])
                else:
                    # 让UI管理器处理其他键盘事件
                    self.ui_manager.handle_keyboard_event(event.key)

    def update_physics(self, frame_dt):
        """更新物理系统"""
        if not self.paused:
            simulation_speed = self.ui_manager.get_simulation_speed()
            self.physics_accumulator += frame_dt * simulation_speed
            while self.physics_accumulator >= FIXED_PHYSICS_DT:
                self.engine.update(FIXED_PHYSICS_DT)
                self.physics_accumulator -= FIXED_PHYSICS_DT
        
        # 更新摄像头（无论是否暂停）
        self.camera_manager.update()

    def draw(self):
        """绘制游戏画面"""
        # 清屏
        self.screen.fill(BLACK)

        # 绘制背景网格
        self.coord_system.draw_grid(self.screen)

        # 绘制质心（如果启用）
        if self.show_center:
            # 获取质心的物理坐标
            physics_cx, physics_cy = self.engine.get_center_of_mass()
            # 转换为屏幕坐标
            screen_cx, screen_cy = self.coord_system.physics_to_screen(physics_cx, physics_cy)
            # 缩放质心圆的半径
            scaled_radius = self.coord_system.scale_radius(CONFIG['center_radius'])
            scaled_circle_radius = self.coord_system.scale_radius(CONFIG['center_circle_radius'])
            # 绘制质心
            pygame.draw.circle(self.screen, GREEN, (screen_cx, screen_cy), scaled_radius)
            pygame.draw.circle(self.screen, GREEN, (screen_cx, screen_cy), scaled_circle_radius, 1)

        # 绘制物理系统
        self.engine.draw(self.screen, self.coord_system)

        # 绘制UI组件
        self.ui_manager.draw_ui(
            self.screen, self.engine, self.ball1, self.ball2, self.ball3, self.clock,
            self.mass1, self.mass2, self.mass3, self.initial_speed,
            self.separation, FIXED_PHYSICS_DT
        )

        # 绘制暂停覆盖层
        self.ui_manager.draw_pause_overlay(self.screen, self.paused)

        pygame.display.flip()

    def loop(self):
        """游戏主循环"""
        while self.running:
            frame_dt = self.clock.tick(FPS) / 1000.0  # 帧时间增量
            zoom_level = self.ui_manager.get_zoom_level()

            # 更新坐标系统缩放
            self.coord_system.set_zoom(zoom_level)

            # 处理连续按键输入（WASD移动摄像头）
            keys = pygame.key.get_pressed()
            self.camera_manager.handle_keyboard_event(keys)

            # 处理事件
            self.handle_events()

            # 更新物理
            self.update_physics(frame_dt)

            # 绘制
            self.draw()

        # 退出游戏
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = Game()
    game.loop()


if __name__ == "__main__":
    main()
