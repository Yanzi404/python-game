import math
import sys

import pygame

from core.ball import Ball
from config.config import BLACK, RED, BLUE, PURPLE

from config.config import CONFIG, auto_params, WIDTH, HEIGHT, FPS, FIXED_PHYSICS_DT
from graphics.coordinate_system import CoordinateSystem
from core.physics_engine import PhysicsEngine
from managers.ui_manager import UIManager
from managers.camera_manager import CameraManager
from managers.game_controller import GameController
from managers.screen_manager import ScreenManager

# 初始化pygame
pygame.init()


class Game:
    """主类"""

    def __init__(self):
        self.clock = pygame.time.Clock()

    def init(self):
        """初始化"""

        # 初始化屏幕管理器
        self.screen_manager = ScreenManager.get_instance().initialize(WIDTH, HEIGHT, "Scalable Physics Engine")

        # 初始化摄像机管理器
        self.camera_manager = CameraManager.get_instance().initialize(WIDTH, HEIGHT)

        # 创建坐标系统（单例模式）
        self.coord_system = CoordinateSystem.get_instance().initialize(WIDTH, HEIGHT)

        # 创建UI管理器（单例模式）
        self.ui_manager = UIManager.get_instance()

        # 创建物理引擎
        self.engine = PhysicsEngine()

        # 初始化物理参数
        self.init_physics()

        # 初始化游戏控制器
        self.game_controller = GameController()

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

    def update_physics(self, frame_dt):
        """更新物理系统"""
        if not self.game_controller.is_paused():
            simulation_speed = self.ui_manager.get_simulation_speed()
            self.engine.physics_accumulator += frame_dt * simulation_speed
            while self.engine.physics_accumulator >= FIXED_PHYSICS_DT:
                self.engine.update(FIXED_PHYSICS_DT)
                self.engine.physics_accumulator -= FIXED_PHYSICS_DT

    def draw(self):
        """绘制画面"""
        # 清屏
        self.screen_manager.fill(BLACK)

        # 更新摄像头
        self.camera_manager.update()

        # 更新坐标系统缩放
        self.coord_system.set_zoom(self.ui_manager.get_zoom_level())

        # 绘制背景网格
        self.coord_system.draw_grid()

        # 绘制物体
        self.engine.draw(self.game_controller.should_show_centroid())

        # 绘制UI
        self.ui_manager.draw_ui(
            self.clock,
            self.initial_speed,
            self.separation, FIXED_PHYSICS_DT
        )

        # 绘制暂停覆盖层
        self.ui_manager.draw_pause_overlay(self.game_controller.is_paused())

        pygame.display.flip()

    def loop(self):
        """主循环"""
        while self.game_controller.is_running():
            frame_dt = self.clock.tick(FPS) / 1000.0  # 帧时间增量

            # 处理事件
            self.game_controller.handle_events()

            # 物理计算
            self.update_physics(frame_dt)

            # 绘制
            self.draw()

        # 清理资源
        self.game_controller.cleanup()

        # 退出
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    """主函数"""
    game = Game()
    game.init()
    game.loop()
