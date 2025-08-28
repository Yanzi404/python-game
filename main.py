import math
import sys

import pygame

from ball import Ball
from config import BLACK, RED, BLUE, YELLOW, GREEN, PURPLE
# 导入自定义模块
from config import CONFIG, auto_params, WIDTH, HEIGHT, FPS, FIXED_PHYSICS_DT
from coordinate_system import CoordinateSystem
from physics_engine import PhysicsEngine
from ui_components import SpeedSlider, ZoomSlider, EnergyGraph, InfoText

# 初始化pygame
pygame.init()


class Game:
    """主类"""

    def __init__(self):
        """初始化"""
        # 创建屏幕
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(
            f"Scalable Physics Engine - Mass({CONFIG['mass1']},{CONFIG['mass2']},{CONFIG['mass3']}) Speed({CONFIG['initial_speed']}) Distance({CONFIG['separation']})")
        self.clock = pygame.time.Clock()

        # 创建坐标系统
        self.coord_system = CoordinateSystem(WIDTH, HEIGHT)

        # 创建物理引擎
        self.engine = PhysicsEngine(integration_method='verlet')

        # 初始化物理参数
        self.init_physics()

        # 创建UI组件
        self.init_ui()

        # 游戏状态
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
        self.vx1 = -self.initial_speed * math.sin(angle1) * self.mass2 * self.mass3 / (
                self.total_mass ** 2)
        self.vy1 = self.initial_speed * math.cos(angle1) * self.mass2 * self.mass3 / (self.total_mass ** 2)

        # 球2位置和速度
        self.x2 = center_x + radius * math.cos(angle2)
        self.y2 = center_y + radius * math.sin(angle2)
        self.vx2 = -self.initial_speed * math.sin(angle2) * self.mass1 * self.mass3 / (
                    self.total_mass ** 2)
        self.vy2 = self.initial_speed * math.cos(angle2) * self.mass1 * self.mass3 / (self.total_mass ** 2)

        # 球3位置和速度
        self.x3 = center_x + radius * math.cos(angle3)
        self.y3 = center_y + radius * math.sin(angle3)
        self.vx3 = -self.initial_speed * math.sin(angle3) * self.mass1 * self.mass2 / (self.total_mass ** 2)
        self.vy3 = self.initial_speed * math.cos(angle3) * self.mass1 * self.mass2 / (self.total_mass ** 2)

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

    def init_ui(self):
        """初始化UI组件"""
        self.font = pygame.font.Font(None, 24)

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
            initial_val=1.0
        )

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # 让滑块处理鼠标事件
            self.speed_slider.handle_event(event)
            self.zoom_slider.handle_event(event)

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
                elif event.key == pygame.K_e:
                    # 切换UI显示
                    self.energy_graph.toggle_visibility()
                    self.info_text_display.toggle_visibility()
                    self.speed_slider.toggle_visibility()
                    self.zoom_slider.toggle_visibility()
                elif event.key == pygame.K_0:
                    # 重置速度为1.0
                    self.speed_slider.val = 1.0
                    # 重置缩放为1.0
                    self.zoom_slider.val = 1.0

    def update_physics(self, frame_dt, simulation_speed):
        """更新物理系统"""
        if not self.paused:
            self.physics_accumulator += frame_dt * simulation_speed
            while self.physics_accumulator >= FIXED_PHYSICS_DT:
                self.engine.update(FIXED_PHYSICS_DT)
                self.physics_accumulator -= FIXED_PHYSICS_DT

    def draw(self):
        """绘制游戏画面"""
        # 清屏
        self.screen.fill(BLACK)

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

        # 绘制控制滑块
        self.speed_slider.draw(self.screen, self.font)
        self.zoom_slider.draw(self.screen, self.font)

        # 获取能量守恒信息
        energy_drift = self.engine.check_energy_conservation()

        # 绘制能量图表
        self.energy_graph.draw(self.screen, self.font, energy_drift)

        # 更新并绘制信息文本
        self.info_text_display.update(
            self.engine, self.ball1, self.ball2, self.ball3, self.clock,
            self.speed_slider.val, self.zoom_slider.val,
            self.mass1, self.mass2, self.mass3, self.initial_speed,
            self.separation, FIXED_PHYSICS_DT
        )
        self.info_text_display.draw(self.screen, self.font)

        if self.paused:
            try:
                pause_text = self.font.render("PAUSED", True, YELLOW)
                text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(pause_text, text_rect)
            except:
                pygame.draw.rect(self.screen, YELLOW, (WIDTH // 2 - 50, HEIGHT // 2 - 20, 100, 40), 3)

        pygame.display.flip()

    def loop(self):
        """游戏主循环"""
        while self.running:
            frame_dt = self.clock.tick(FPS) / 1000.0  # 帧时间增量
            simulation_speed = self.speed_slider.val
            zoom_level = self.zoom_slider.val

            # 更新坐标系统缩放
            self.coord_system.set_zoom(zoom_level)

            # 处理事件
            self.handle_events()

            # 更新物理
            self.update_physics(frame_dt, simulation_speed)

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
