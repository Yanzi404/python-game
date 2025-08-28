import pygame
import math
import sys

# 导入自定义模块
from config import CONFIG, auto_params, G, WIDTH, HEIGHT, FPS, FIXED_PHYSICS_DT
from config import BLACK, WHITE, RED, BLUE, YELLOW, GREEN, PURPLE
from ball import Ball
from physics_engine import PhysicsEngine
from ui_components import SpeedSlider, ZoomSlider,EnergyGraph
from coordinate_system import CoordinateSystem


# 初始化pygame
pygame.init()


def main():
    """主函数"""
    # 创建屏幕
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(
        f"Scalable Physics Engine - Mass({CONFIG['mass1']},{CONFIG['mass2']},{CONFIG['mass3']}) Speed({CONFIG['initial_speed']}) Distance({CONFIG['separation']})")
    clock = pygame.time.Clock()

    # 初始化字体
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont('arial', 20)

    # 创建坐标系统
    coord_system = CoordinateSystem(WIDTH, HEIGHT)

    # 创建高精度物理引擎
    engine = PhysicsEngine(integration_method='verlet')

    # 创建三个质点 - 三角形配置
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    separation = CONFIG['separation']
    mass1 = CONFIG['mass1']
    mass2 = CONFIG['mass2']
    mass3 = CONFIG['mass3']
    initial_speed = CONFIG['initial_speed']
    total_mass = mass1 + mass2 + mass3

    # 三角形配置：三个球形成等边三角形
    angle1 = 0  # 球1在右侧
    angle2 = 2 * math.pi / 3  # 球2在左上
    angle3 = 4 * math.pi / 3  # 球3在左下

    # 计算三个球的初始位置（围绕质心形成三角形）
    radius = separation / 2  # 三角形的外接圆半径

    # 球1位置和速度
    x1 = center_x + radius * math.cos(angle1)
    y1 = center_y + radius * math.sin(angle1)
    # 切向速度（垂直于半径方向）
    vx1 = -initial_speed * math.sin(angle1) * mass2 * mass3 / (total_mass * total_mass)
    vy1 = initial_speed * math.cos(angle1) * mass2 * mass3 / (total_mass * total_mass)

    # 球2位置和速度
    x2 = center_x + radius * math.cos(angle2)
    y2 = center_y + radius * math.sin(angle2)
    vx2 = -initial_speed * math.sin(angle2) * mass1 * mass3 / (total_mass * total_mass)
    vy2 = initial_speed * math.cos(angle2) * mass1 * mass3 / (total_mass * total_mass)

    # 球3位置和速度
    x3 = center_x + radius * math.cos(angle3)
    y3 = center_y + radius * math.sin(angle3)
    vx3 = -initial_speed * math.sin(angle3) * mass1 * mass2 / (total_mass * total_mass)
    vy3 = initial_speed * math.cos(angle3) * mass1 * mass2 / (total_mass * total_mass)

    # 创建三个球
    ball1 = Ball(
        x=x1, y=y1, vx=vx1, vy=vy1,
        mass=mass1,
        radius=auto_params['radius1'],
        color=BLUE
    )

    ball2 = Ball(
        x=x2, y=y2, vx=vx2, vy=vy2,
        mass=mass2,
        radius=auto_params['radius2'],
        color=RED
    )

    ball3 = Ball(
        x=x3, y=y3, vx=vx3, vy=vy3,
        mass=mass3,
        radius=auto_params['radius3'],
        color=PURPLE
    )

    # 添加质点到物理引擎
    engine.add_ball(ball1)
    engine.add_ball(ball2)
    engine.add_ball(ball3)

    # 创建能量图表
    energy_graph = EnergyGraph(
        x=CONFIG['energy_graph_x'],
        y=CONFIG['energy_graph_y'],
        width=CONFIG['energy_graph_width'],
        height=CONFIG['energy_graph_height']
    )

    # 游戏主循环
    running = True
    paused = False
    show_center = True

    # 物理模拟参数
    physics_accumulator = 0.0

    # 创建控制滑块
    speed_slider = SpeedSlider(
        x=WIDTH - 250,
        y=30,
        width=200,
        height=20,
        min_val=0.1,
        max_val=5.0,
        initial_val=1.0
    )

    zoom_slider = ZoomSlider(
        x=WIDTH - 250,
        y=80,  # 在速度滑块下方
        width=200,
        height=20,
        min_val=0.1,
        max_val=3.0,
        initial_val=1.0
    )

    while running:
        frame_dt = clock.tick(FPS) / 1000.0  # 帧时间增量
        simulation_speed = speed_slider.val
        zoom_level = zoom_slider.val

        # 更新坐标系统缩放
        coord_system.set_zoom(zoom_level)

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # 让滑块处理鼠标事件
            speed_slider.handle_event(event)
            zoom_slider.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    pass
                    # 重置质点位置
                    # ball1.reset_verlet_state(x1, y1, vx1, vy1, FIXED_PHYSICS_DT)
                    # ball2.reset_verlet_state(x2, y2, vx2, vy2, FIXED_PHYSICS_DT)
                    # ball3.reset_verlet_state(x3, y3, vx3, vy3, FIXED_PHYSICS_DT)
                    # physics_accumulator = 0.0
                elif event.key == pygame.K_c:
                    # 切换质心显示
                    show_center = not show_center
                elif event.key == pygame.K_e:
                    # 切换能量图表显示
                    energy_graph.toggle_visibility()
                elif event.key == pygame.K_0:
                    # 重置速度为1.0
                    speed_slider.val = 1.0
                elif event.key == pygame.K_9:
                    # 重置缩放为1.0
                    zoom_slider.val = 1.0

        # 清屏
        screen.fill(BLACK)

        # 物理更新（固定时间步长，累积器方法）
        if not paused:
            physics_accumulator += frame_dt * simulation_speed
            while physics_accumulator >= FIXED_PHYSICS_DT:
                engine.update(FIXED_PHYSICS_DT)
                physics_accumulator -= FIXED_PHYSICS_DT

        # 绘制质心（如果启用）
        if show_center:
            # 获取质心的物理坐标
            physics_cx, physics_cy = engine.get_center_of_mass()
            # 转换为屏幕坐标
            screen_cx, screen_cy = coord_system.physics_to_screen(physics_cx, physics_cy)
            # 缩放质心圆的半径
            scaled_radius = coord_system.scale_radius(CONFIG['center_radius'])
            scaled_circle_radius = coord_system.scale_radius(CONFIG['center_circle_radius'])
            # 绘制质心
            pygame.draw.circle(screen, GREEN, (screen_cx, screen_cy), scaled_radius)
            pygame.draw.circle(screen, GREEN, (screen_cx, screen_cy), scaled_circle_radius, 1)

        # 绘制物理系统
        engine.draw(screen, coord_system)

        # 绘制控制滑块
        speed_slider.draw(screen, font)
        zoom_slider.draw(screen, font)

        # 获取能量守恒信息
        energy_drift = engine.check_energy_conservation()

        # 绘制能量图表
        energy_graph.draw(screen, font, energy_drift)

        # 计算距离和速度（物理值，不受缩放影响）
        distance12 = math.sqrt((ball1.x - ball2.x) ** 2 + (ball1.y - ball2.y) ** 2)
        distance13 = math.sqrt((ball1.x - ball3.x) ** 2 + (ball1.y - ball3.y) ** 2)
        distance23 = math.sqrt((ball2.x - ball3.x) ** 2 + (ball2.y - ball3.y) ** 2)
        speed1 = math.sqrt(ball1.vx ** 2 + ball1.vy ** 2)
        speed2 = math.sqrt(ball2.vx ** 2 + ball2.vy ** 2)
        speed3 = math.sqrt(ball3.vx ** 2 + ball3.vy ** 2)

        # 显示信息
        info_text = [
            f"FPS: {int(clock.get_fps())}",
            f"Integration: {engine.integration_method.upper()} (Fixed dt={FIXED_PHYSICS_DT * 1000:.1f}ms)",
            f"Simulation Speed: {simulation_speed:.1f}x",
            f"Display Zoom: {zoom_level:.1f}x",
            f"Config: Mass({mass1},{mass2},{mass3}) Speed({initial_speed}) Distance({separation})",
            f"Distances: 1-2={distance12:.1f} 1-3={distance13:.1f} 2-3={distance23:.1f}",
            f"Speeds: Ball1={speed1:.1f} Ball2={speed2:.1f} Ball3={speed3:.1f}",
            "Controls: SPACE=Pause, R=Reset, C=Center, E=Toggle UI, 0=Speed Reset, 9=Zoom Reset",
        ]

        for i, text in enumerate(info_text):
            try:
                text_surface = font.render(text, True, WHITE)
                screen.blit(text_surface, (10, 10 + i * 25))
            except Exception as e:
                pygame.draw.rect(screen, WHITE, (10, 10 + i * 25, 300, 20), 1)

        if paused:
            try:
                pause_text = font.render("PAUSED", True, YELLOW)
                text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(pause_text, text_rect)
            except:
                pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - 50, HEIGHT // 2 - 20, 100, 40), 3)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
