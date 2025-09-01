import math

import pygame

from config.config import CONFIG, G


class UIComponent:
    """UI组件基类"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.visible = True  # 默认可见

    def toggle_visibility(self):
        """切换可见性"""
        self.visible = not self.visible

    def draw(self, screen, font):
        """绘制组件（子类必须实现）"""
        pass


class Slider(UIComponent):
    """滑块基类"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label_prefix="Value"):
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False
        self.label_prefix = label_prefix

        # 滑块手柄配置
        self.handle_width = CONFIG.get('handle_width', 10)
        self.handle_height = height + CONFIG.get('handle_height_offset', 4)

    def handle_event(self, event):
        """处理鼠标事件"""
        if not self.visible:  # 如果不可见，不处理事件
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_handle_rect().collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # 计算新的值
            relative_x = event.pos[0] - self.rect.x
            relative_x = max(0, min(relative_x, self.rect.width))
            self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)

    def get_handle_rect(self):
        """获取滑块手柄的矩形（子类可以重写）"""
        progress = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + progress * self.rect.width - self.handle_width // 2
        handle_y = self.rect.y - CONFIG.get('handle_y_offset', 2)
        return pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)

    def get_track_color(self):
        """获取轨道颜色（子类可以重写）"""
        return CONFIG['colors']['gray']

    def get_progress_color(self):
        """获取进度条颜色（子类可以重写）"""
        return CONFIG['colors']['light_blue']

    def get_handle_color(self):
        """获取手柄颜色（子类可以重写）"""
        return CONFIG['colors']['white']

    def get_handle_border_color(self):
        """获取手柄边框颜色（子类可以重写）"""
        return CONFIG['colors']['light_gray']

    def draw_track(self, screen):
        """绘制滑块轨道"""
        pygame.draw.rect(screen, self.get_track_color(), self.rect)
        pygame.draw.rect(screen, CONFIG['colors']['white'], self.rect, 2)

    def draw_progress(self, screen):
        """绘制进度条"""
        progress = (self.val - self.min_val) / (self.max_val - self.min_val)
        progress_width = int(progress * self.rect.width)
        if progress_width > 0:
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(screen, self.get_progress_color(), progress_rect)

    def draw_handle(self, screen):
        """绘制滑块手柄"""
        handle_rect = self.get_handle_rect()
        pygame.draw.rect(screen, self.get_handle_color(), handle_rect)
        pygame.draw.rect(screen, self.get_handle_border_color(), handle_rect, 2)

    def draw_label(self, screen, font):
        """绘制数值标签"""
        try:
            label_text = f"{self.label_prefix}: {self.val:.1f}x"
            text_surface = font.render(label_text, True, CONFIG['colors']['white'])
            label_x = self.rect.x
            label_y = self.rect.y - CONFIG.get('label_y_offset', 25)
            screen.blit(text_surface, (label_x, label_y))
        except:
            # 如果字体渲染失败，绘制简单标识
            pygame.draw.rect(screen, CONFIG['colors']['white'],
                             (self.rect.x, self.rect.y - CONFIG.get('label_y_offset', 25), 100, 20), 1)

    def draw(self, screen, font):
        """绘制滑块"""
        if not self.visible:  # 如果不可见，不绘制
            return

        self.draw_track(screen)
        self.draw_progress(screen)
        self.draw_handle(screen)
        self.draw_label(screen, font)


class SpeedSlider(Slider):
    """速度控制滑块"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        super().__init__(x, y, width, height, min_val, max_val, initial_val, "Speed")


class ZoomSlider(Slider):
    """缩放控制滑块"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        super().__init__(x, y, width, height, min_val, max_val, initial_val, "Zoom")

    def get_handle_rect(self):
        """重写手柄矩形计算，使用ZoomSlider特有的样式"""
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + ratio * self.rect.width
        return pygame.Rect(handle_x - CONFIG.get('handle_y_offset', 2), self.rect.y - 2,
                           CONFIG.get('handle_border_size', 8), self.rect.height + 4)

    def get_track_color(self):
        """ZoomSlider使用透明轨道"""
        return None  # 不绘制填充轨道

    def get_handle_color(self):
        """ZoomSlider使用黄色手柄"""
        return CONFIG['colors']['yellow']

    def draw_track(self, screen):
        """重写轨道绘制，只绘制边框"""
        pygame.draw.rect(screen, CONFIG['colors']['white'], self.rect, 2)

    def draw_progress(self, screen):
        """ZoomSlider不绘制进度条"""
        pass


class EnergyGraph(UIComponent):
    """能量历史折线图"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.bg_color = CONFIG['energy_graph_bg_color']
        self.border_color = CONFIG['energy_graph_border_color']
        self.line_color = CONFIG['energy_graph_color']
        self.line_width = CONFIG['energy_graph_line_width']
        self.max_points = CONFIG['energy_graph_max_points']
        self.drift_history = [0] * self.max_points  # 存储能量漂移历史数据
        self.max_abs_drift = 0.0  # 存储历史上最大的绝对值

    def draw(self, screen, font, energy_drift=None):
        """绘制折线图"""
        if not self.visible:  # 如果不可见，不绘制
            return

        # 绘制背景和边框
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        # 显示当前energy_drift值和折线图
        if energy_drift is not None:
            try:
                # 更新历史数据
                self.drift_history.append(energy_drift)
                if len(self.drift_history) > self.max_points:
                    self.drift_history.pop(0)

                # 更新最大值
                self.max_abs_drift = max(self.max_abs_drift, abs(energy_drift))

                if self.max_abs_drift <= CONFIG['min_energy_graph_range']:
                    max_scale = CONFIG['min_energy_graph_range']
                else:
                    max_scale = math.ceil(self.max_abs_drift / 10) * 10

                # 添加刻度线
                # 绘制水平刻度线，中间线代表0%
                for i in range(5):
                    y_pos = self.rect.y + i * (self.rect.height / 4)
                    line_color = CONFIG['colors']['white'] if i == 2 else CONFIG['colors']['gray']
                    line_width = 2 if i == 2 else 1  # 中间线加粗
                    pygame.draw.line(screen, line_color,
                                     (self.rect.x, y_pos),
                                     (self.rect.x + self.rect.width, y_pos), line_width)

                    # 添加刻度值（上正下负）
                    if i == 0:
                        scale_text = f"+{max_scale}%"
                    elif i == 1:
                        scale_text = f"+{max_scale / 2}%"
                    elif i == 2:
                        scale_text = "0%"
                    elif i == 3:
                        scale_text = f"-{max_scale / 2}%"
                    elif i == 4:
                        scale_text = f"-{max_scale}%"

                    scale_surface = font.render(scale_text, True, CONFIG['colors']['white'])
                    screen.blit(scale_surface, (self.rect.x + self.rect.width, y_pos - 10))

                # 绘制垂直刻度线
                for i in range(5):
                    x_pos = self.rect.x + i * (self.rect.width / 4)
                    pygame.draw.line(screen, CONFIG['colors']['gray'],
                                     (x_pos, self.rect.y),
                                     (x_pos, self.rect.y + self.rect.height), 1)

                # 绘制energy_drift折线图和轨迹
                # 计算y坐标，将energy_drift值映射到图表高度
                mid_y = self.rect.y + self.rect.height // 2  # 中间位置代表0%
                y_scale = self.rect.height / (2 * max_scale)  # 缩放因子

                # 绘制历史轨迹
                if len(self.drift_history) > 1:
                    points = []
                    for i, drift in enumerate(self.drift_history):
                        # 计算x坐标（从左到右均匀分布）
                        x = self.rect.x + (i / (len(self.drift_history) - 1)) * self.rect.width
                        # 计算y坐标（上小下大，所以用减法）
                        y = mid_y - (drift * y_scale)
                        points.append((int(x), int(y)))

                    # 绘制连接线
                    if len(points) > 1:
                        pygame.draw.lines(screen, self.line_color, False, points, self.line_width)

                    # 绘制轨迹点
                    for point in points:
                        pygame.draw.circle(screen, self.line_color, point, 2)

                    text_surface = font.render(f"Energy Drift: {energy_drift:.6f}%", True, CONFIG['colors']['white'])
                    screen.blit(text_surface, (self.rect.x, self.rect.y - 25))

            except Exception as e:
                print(f"Error in energy graph: {e}")
                pass


class InfoText(UIComponent):
    """信息文本显示组件"""

    def __init__(self, x, y, line_height=25):
        # 对于InfoText，我们传递0作为宽度和高度，因为它没有固定的矩形区域
        super().__init__(x, y, 0, 0)
        self.line_height = line_height
        self.texts = []

    def update(self, engine, clock, initial_speed, separation, FIXED_PHYSICS_DT, camera=None):
        """更新显示信息"""

        ball1=engine.balls[0]
        ball2=engine.balls[1]
        ball3=engine.balls[2]

        # 计算距离和速度（物理值，不受缩放影响）
        distance12 = math.sqrt((ball1.x - ball2.x) ** 2 + (ball1.y - ball2.y) ** 2)
        distance13 = math.sqrt((ball1.x - ball3.x) ** 2 + (ball1.y - ball3.y) ** 2)
        distance23 = math.sqrt((ball2.x - ball3.x) ** 2 + (ball2.y - ball3.y) ** 2)
        speed1 = math.sqrt(ball1.vx ** 2 + ball1.vy ** 2)
        speed2 = math.sqrt(ball2.vx ** 2 + ball2.vy ** 2)
        speed3 = math.sqrt(ball3.vx ** 2 + ball3.vy ** 2)

        # 摄像头信息
        camera_info = []
        if camera:
            target_name = "None"
            if camera.target == ball1:
                target_name = "Ball1"
            elif camera.target == ball2:
                target_name = "Ball2"
            elif camera.target == ball3:
                target_name = "Ball3"
            
            follow_status = "ON" if camera.follow_mode else "OFF"
            camera_info = [
                f"Camera: ({camera.x:.1f}, {camera.y:.1f}) Zoom: {camera.zoom:.2f}",
                f"Follow: {follow_status} | Target: {target_name}"
            ]

        # 更新信息文本
        self.texts = [
            f"FPS: {int(clock.get_fps())}",
            f"Integration: {engine.integration_method.upper()} (Fixed dt={FIXED_PHYSICS_DT * 1000:.1f}ms)",
            f"Config: Mass({ball1.mass},{ball2.mass},{ball3.mass}) Speed({initial_speed}) Distance({separation})",
            f"Distances: 1-2={distance12:.1f} 1-3={distance13:.1f} 2-3={distance23:.1f}",
            f"Speeds: Ball1={speed1:.1f} Ball2={speed2:.1f} Ball3={speed3:.1f}",
            f"G={G}",
        ] + camera_info + [
            "Controls: SPACE=Pause, R=Reset, C=Centroid, E=Toggle UI, 0=UI Reset",
            "Camera: F=Follow, 1/2/3=Track Ball, TAB=Next Target, WASD=Move, HOME=Reset"
        ]

    def draw(self, screen, font):
        """绘制信息文本"""
        if not self.visible:
            return

        for i, text in enumerate(self.texts):
            try:
                text_surface = font.render(text, True, CONFIG['colors']['white'])
                screen.blit(text_surface, (self.x, self.y + i * self.line_height))
            except Exception as e:
                pygame.draw.rect(screen, CONFIG['colors']['white'],
                                 (self.x, self.y + i * self.line_height, 300, 20), 1)
