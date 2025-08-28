import math
import pygame
from config import CONFIG


class SpeedSlider:
    """速度控制滑块"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False
        self.visible = True  # 添加可见性属性

        # 滑块手柄
        self.handle_width = CONFIG['handle_width']
        self.handle_height = height + CONFIG['handle_height_offset']

    def toggle_visibility(self):
        """切换可见性"""
        self.visible = not self.visible

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
        """获取滑块手柄的矩形"""
        progress = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + progress * self.rect.width - self.handle_width // 2
        handle_y = self.rect.y - CONFIG['handle_y_offset']
        return pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)

    def draw(self, screen, font):
        """绘制滑块"""
        if not self.visible:  # 如果不可见，不绘制
            return

        # 绘制滑块轨道
        pygame.draw.rect(screen, CONFIG['colors']['gray'], self.rect)
        pygame.draw.rect(screen, CONFIG['colors']['white'], self.rect, 2)

        # 绘制进度条
        progress = (self.val - self.min_val) / (self.max_val - self.min_val)
        progress_width = int(progress * self.rect.width)
        if progress_width > 0:
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(screen, CONFIG['colors']['light_blue'], progress_rect)

        # 绘制滑块手柄
        handle_rect = self.get_handle_rect()
        pygame.draw.rect(screen, CONFIG['colors']['white'], handle_rect)
        pygame.draw.rect(screen, CONFIG['colors']['light_gray'], handle_rect, 2)

        # 绘制数值标签
        try:
            label_text = f"Speed: {self.val:.1f}x"
            text_surface = font.render(label_text, True, CONFIG['colors']['white'])
            label_x = self.rect.x
            label_y = self.rect.y - CONFIG['label_y_offset']
            screen.blit(text_surface, (label_x, label_y))
        except:
            # 如果字体渲染失败，绘制简单标识
            pygame.draw.rect(screen, CONFIG['colors']['white'],
                             (self.rect.x, self.rect.y - CONFIG['label_y_offset'], 100, 20), 1)


class ZoomSlider:
    """缩放控制滑块"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False
        self.visible = True  # 添加可见性属性

    def toggle_visibility(self):
        """切换可见性"""
        self.visible = not self.visible

    def handle_event(self, event):
        if not self.visible:  # 如果不可见，不处理事件
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_handle_rect().collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # 计算新值
            relative_x = event.pos[0] - self.rect.x
            relative_x = max(0, min(relative_x, self.rect.width))
            ratio = relative_x / self.rect.width
            self.val = self.min_val + ratio * (self.max_val - self.min_val)

    def get_handle_rect(self):
        # 计算滑块手柄位置
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + ratio * self.rect.width
        return pygame.Rect(handle_x - CONFIG['handle_y_offset'], self.rect.y - 2, CONFIG['handle_border_size'],
                           self.rect.height + 4)

    def draw(self, screen, font):
        if not self.visible:  # 如果不可见，不绘制
            return

        # 绘制滑块轨道
        pygame.draw.rect(screen, CONFIG['colors']['white'], self.rect, 2)

        # 绘制滑块手柄
        handle_rect = self.get_handle_rect()
        pygame.draw.rect(screen, CONFIG['colors']['yellow'], handle_rect)

        # 绘制标签和数值
        try:
            label_text = font.render(f"Zoom: {self.val:.1f}x", True, CONFIG['colors']['white'])
            screen.blit(label_text, (self.rect.x, self.rect.y - CONFIG['label_y_offset']))
        except:
            pygame.draw.rect(screen, CONFIG['colors']['white'],
                             (self.rect.x, self.rect.y - CONFIG['label_y_offset'], 100, 20), 1)


class EnergyGraph:
    """能量历史折线图"""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = CONFIG['energy_graph_bg_color']
        self.border_color = CONFIG['energy_graph_border_color']
        self.line_color = CONFIG['energy_graph_color']
        self.line_width = CONFIG['energy_graph_line_width']
        self.max_points = CONFIG['energy_graph_max_points']
        self.visible = True  # 默认显示
        self.drift_history = []  # 存储能量漂移历史数据
        self.max_abs_drift = 0.0  # 存储历史上最大的绝对值

    def toggle_visibility(self):
        """切换可见性"""
        self.visible = not self.visible

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

                # 如果最大值小于10，则使用默认的±10%范围
                # 否则，向上取整到最接近的10的倍数
                if self.max_abs_drift <= 10.0:
                    max_scale = 10.0
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