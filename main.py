import pygame
import math
import sys
import numpy as np  # 添加 numpy 导入

# 初始化pygame
pygame.init()

# ==================== 用户配置参数 ====================
# 只需要调节这些核心参数
CONFIG = {
    # 物理参数
    'mass1': 200,  # 质点1的质量
    'mass2': 50,  # 质点2的质量
    'mass3': 50,  # 质点3的质量
    'initial_speed': 20,  # 初始环绕速度
    'separation': 500,  # 两个质点之间的初始距离

    # 窗口和显示参数
    'window_width': 1200,
    'window_height': 800,
    'fps': 60.0,

    # 物理引擎参数
    'physics_frequency': 60.0,  # 物理更新频率 (Hz)
    'fixed_physics': False,
    'min_distance_factor': 1,  # 最小距离系数（相对于质点半径）
    'potential_min_distance': 5.0,  # 势能计算的最小距离

    # 能量图表参数
    'energy_graph_width': 300,
    'energy_graph_height': 150,
    'energy_graph_x': 10,
    'energy_graph_y': 250,
    'energy_graph_color': (0, 200, 0),
    'energy_graph_bg_color': (20, 20, 20),
    'energy_graph_border_color': (100, 100, 100),
    'energy_graph_line_width': 2,
    'energy_graph_max_points': 200,  # 图表上显示的最大点数

    # UI控件参数
    'slider_width': 200,
    'slider_height': 20,
    'slider_x_offset': 250,  # 距离右边缘的距离
    'speed_slider_y': 30,
    'zoom_slider_y': 80,
    'speed_min': 0.1,
    'speed_max': 5.0,
    'speed_initial': 1.0,
    'zoom_min': 0.1,
    'zoom_max': 3.0,
    'zoom_initial': 1.0,

    # 滑块手柄参数
    'handle_width': 20,
    'handle_height_offset': 10,
    'handle_y_offset': 5,
    'handle_border_size': 10,

    # 质心显示参数
    'center_radius': 4,
    'center_circle_radius': 20,

    # 字体参数
    'font_size': 24,
    'fallback_font_size': 20,
    'label_y_offset': 25,

    # 颜色配置
    'colors': {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'green': (0, 255, 0),
        'purple': (255, 0, 255),
        'gray': (100, 100, 100),
        'light_blue': (0, 150, 255),
        'light_gray': (200, 200, 200)
    }
}


# 自动计算的参数 - 不需要手动修改
def calculate_auto_params():
    """根据核心参数自动计算其他参数"""
    mass1 = np.float64(CONFIG['mass1'])
    mass2 = np.float64(CONFIG['mass2'])
    mass3 = np.float64(CONFIG['mass3'])
    separation = np.float64(CONFIG['separation'])
    speed = np.float64(CONFIG['initial_speed'])

    # 根据质量自动计算万有引力常数
    # 使用公式：G = v² * r / (m1 + m2 + m3)
    gravity_constant = speed * speed * separation / (mass1 + mass2 + mass3)

    # 根据质量自动计算显示半径
    # 根据单位质量推算半径关系，假设密度固定：半径 = √(质量/密度*PI)
    radius1 = math.sqrt(mass1 / 1 * math.pi)
    radius2 = math.sqrt(mass2 / 1 * math.pi)
    radius3 = math.sqrt(mass3 / 1 * math.pi)

    # 根据速度自动计算轨迹长度
    # 速度越快，轨迹越长
    trail_length = int(200 + speed * 2)

    return {
        'gravity_constant': gravity_constant,
        'radius1': radius1,
        'radius2': radius2,
        'radius3': radius3,
        'trail_length': trail_length
    }


# 计算自动参数
auto_params = calculate_auto_params()
# ====================================================

# 常量定义
G = auto_params['gravity_constant']
WIDTH = CONFIG['window_width']
HEIGHT = CONFIG['window_height']
FPS = CONFIG['fps']
FIXED_PHYSICS_DT = np.float64(1.0 / CONFIG['physics_frequency'])

# 颜色定义
# 添加新的颜色
BLACK = CONFIG['colors']['black']
WHITE = CONFIG['colors']['white']
RED = CONFIG['colors']['red']
BLUE = CONFIG['colors']['blue']
YELLOW = CONFIG['colors']['yellow']
GREEN = CONFIG['colors']['green']
PURPLE = CONFIG['colors']['purple']


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

        # 为Verlet积分法添加前一帧的位置（高精度）
        dt = np.float64(1.0 / 60.0)
        self.prev_x = self.x - self.vx * dt
        self.prev_y = self.y - self.vy * dt
        self.ax = 0
        self.ay = 0

    def apply_force_verlet(self, fx, fy, dt):
        """使用Verlet积分法更新位置和速度（numpy.float64高精度方法）"""
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

    def draw(self, screen, coord_system):
        """绘制质点（使用坐标转换）"""
        # 转换物理坐标到屏幕坐标
        screen_x, screen_y = coord_system.physics_to_screen(self.x, self.y)
        scaled_radius = coord_system.scale_radius(self.radius)

        # 根据缩放比例动态调整轨迹显示长度（反向关系）
        zoom_factor = coord_system.zoom
        # 缩放越小，轨迹越长：使用反比关系
        dynamic_trail_length = int(self.base_trail_length / zoom_factor)
        # 限制在合理范围内：最少50个点，最多不超过存储的轨迹点数
        dynamic_trail_length = max(50, min(dynamic_trail_length, len(self.trail)))

        # 绘制轨迹（只显示最近的dynamic_trail_length个点）
        if len(self.trail) > 1:
            # 获取要显示的轨迹点
            display_trail = self.trail[-dynamic_trail_length:] if len(self.trail) > dynamic_trail_length else self.trail

            screen_trail = []
            for trail_x, trail_y in display_trail:
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
                    pass  # 忽略绘制错误

        # 绘制质点（只在屏幕范围内绘制）
        if (-scaled_radius <= screen_x <= coord_system.screen_width + scaled_radius and
                -scaled_radius <= screen_y <= coord_system.screen_height + scaled_radius):
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), scaled_radius)
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), scaled_radius, 1)


class PhysicsEngine:
    """物理引擎类"""

    def __init__(self, integration_method='verlet'):
        self.balls = []
        self.integration_method = integration_method
        self.energy_history = []
        self.initial_energy = None
        self.G = G

    def calculate_gravity_force(self, ball1, ball2):
        """计算两个质点之间的引力"""
        # 计算距离
        dx = ball2.x - ball1.x
        dy = ball2.y - ball1.y
        distance_squared = dx * dx + dy * dy

        # 避免除零错误和数值不稳定（添加最小距离）
        min_distance = ball1.radius + ball2.radius
        min_distance_squared = min_distance * min_distance * 1.05

        if distance_squared <= min_distance_squared:
            distance_squared = min_distance_squared
            distance = min_distance
        else:
            distance = np.sqrt(distance_squared)

        # 万有引力公式 F = G * m1 * m2 / r²
        force_magnitude = self.G * ball1.mass * ball2.mass / distance_squared

        # 计算力的方向（单位向量）
        force_direction_x = dx / distance
        force_direction_y = dy / distance

        # 计算力的分量
        fx = force_magnitude * force_direction_x
        fy = force_magnitude * force_direction_y

        return fx, fy

    def calculate_total_energy(self):
        """计算系统总能量"""
        kinetic_energy = 0.0
        potential_energy = 0.0

        # 计算动能
        for ball in self.balls:
            velocity_squared = ball.vx * ball.vx + ball.vy * ball.vy
            kinetic_energy += 0.5 * ball.mass * velocity_squared

        # 计算势能
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                dx = self.balls[j].x - self.balls[i].x
                dy = self.balls[j].y - self.balls[i].y
                distance = np.sqrt(dx * dx + dy * dy)
                min_distance = self.balls[i].radius + self.balls[j].radius
                if distance > min_distance:
                    potential_energy -= self.G * self.balls[i].mass * self.balls[j].mass / distance

        return kinetic_energy + potential_energy

    def add_ball(self, ball):
        """添加质点"""
        self.balls.append(ball)

    def update(self, dt):
        """更新物理状态"""
        # 计算每个质点受到的总力
        forces = [(0, 0) for _ in self.balls]

        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                # 计算质点i和质点j之间的引力
                fx, fy = self.calculate_gravity_force(self.balls[i], self.balls[j])

                # 牛顿第三定律：作用力与反作用力
                forces[i] = (forces[i][0] + fx, forces[i][1] + fy)
                forces[j] = (forces[j][0] - fx, forces[j][1] - fy)

        # 应用力并更新位置
        for i, ball in enumerate(self.balls):
            if self.integration_method == 'verlet':
                ball.apply_force_verlet(forces[i][0], forces[i][1], dt)

    def check_energy_conservation(self):
        """检查能量守恒情况，返回能量漂移百分比"""
        current_energy = self.calculate_total_energy()

        if self.initial_energy is None:
            self.initial_energy = current_energy
            return 0.0

        self.energy_history.append(current_energy)

        # 保持历史记录在合理范围内
        if len(self.energy_history) > 1000:
            self.energy_history.pop(0)

        # 计算能量变化百分比
        if abs(self.initial_energy) > 1e-10:
            energy_drift = (current_energy - self.initial_energy) / self.initial_energy * 100
            return energy_drift
        return 0.0

    def draw(self, screen, coord_system):
        """绘制所有质点（使用坐标转换）"""
        for ball in self.balls:
            ball.draw(screen, coord_system)

    def get_center_of_mass(self):
        """计算质心的物理坐标"""
        if not self.balls:
            return 0, 0

        total_mass = 0
        weighted_x = 0
        weighted_y = 0

        for ball in self.balls:
            total_mass += ball.mass
            weighted_x += ball.x * ball.mass
            weighted_y += ball.y * ball.mass

        if total_mass > 0:
            center_x = weighted_x / total_mass
            center_y = weighted_y / total_mass
            return center_x, center_y
        else:
            return 0, 0

    def get_center_of_mass_screen(self, coord_system):
        """计算质心的屏幕坐标"""
        physics_cx, physics_cy = self.get_center_of_mass()
        return coord_system.physics_to_screen(physics_cx, physics_cy)


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


class CoordinateSystem:
    """坐标系统类，处理物理坐标和显示坐标的转换"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.unit_scale = 1.0  # 一个距离单位等于1个像素点

    def set_zoom(self, zoom):
        """设置缩放比例"""
        self.zoom = zoom

    def physics_to_screen(self, physics_x, physics_y):
        """将物理坐标转换为屏幕坐标"""
        # 以屏幕中心为原点进行缩放
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # 相对于中心的物理坐标
        rel_x = physics_x - center_x
        rel_y = physics_y - center_y

        # 应用单位转换和缩放
        scaled_x = rel_x * self.unit_scale * self.zoom
        scaled_y = rel_y * self.unit_scale * self.zoom

        # 转换回屏幕坐标
        screen_x = center_x + scaled_x + self.offset_x
        screen_y = center_y + scaled_y + self.offset_y

        return int(screen_x), int(screen_y)

    def scale_radius(self, physics_radius):
        """缩放半径"""
        return max(1, int(physics_radius * self.unit_scale * self.zoom))


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
                        scale_text = f"+{max_scale/2}%"
                    elif i == 2:
                        scale_text = "0%"
                    elif i == 3:
                        scale_text = f"-{max_scale/2}%"
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


class CoordinateSystem:
    """坐标系统类，处理物理坐标和显示坐标的转换"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.unit_scale = 1.0  # 一个距离单位等于1个像素点

    def set_zoom(self, zoom):
        """设置缩放比例"""
        self.zoom = zoom

    def physics_to_screen(self, physics_x, physics_y):
        """将物理坐标转换为屏幕坐标"""
        # 以屏幕中心为原点进行缩放
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # 相对于中心的物理坐标
        rel_x = physics_x - center_x
        rel_y = physics_y - center_y

        # 应用单位转换和缩放
        scaled_x = rel_x * self.unit_scale * self.zoom
        scaled_y = rel_y * self.unit_scale * self.zoom

        # 转换回屏幕坐标
        screen_x = center_x + scaled_x + self.offset_x
        screen_y = center_y + scaled_y + self.offset_y

        return int(screen_x), int(screen_y)

    def scale_radius(self, physics_radius):
        """缩放半径"""
        return max(1, int(physics_radius * self.unit_scale * self.zoom))


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
                    # engine.initial_energy = None
                    # engine.energy_history.clear()
                elif event.key == pygame.K_c:
                    show_center = not show_center
                elif event.key == pygame.K_e:  # 修改E键事件处理
                    # 切换所有UI元素的可见性
                    energy_graph.toggle_visibility()
                    speed_slider.toggle_visibility()
                    zoom_slider.toggle_visibility()
                elif event.key == pygame.K_0:
                    speed_slider.val = 1.0
                elif event.key == pygame.K_9:
                    zoom_slider.val = 1.0  # 重置缩放
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if not paused:
            # 固定时间步长物理更新
            physics_accumulator += frame_dt * simulation_speed
            while physics_accumulator >= FIXED_PHYSICS_DT:
                engine.update(FIXED_PHYSICS_DT)
                physics_accumulator -= FIXED_PHYSICS_DT

        # 绘制（使用坐标转换）
        screen.fill(BLACK)

        # 绘制质心
        if show_center:
            screen_cx, screen_cy = engine.get_center_of_mass_screen(coord_system)
            scaled_radius = coord_system.scale_radius(CONFIG['center_radius'])
            scaled_circle_radius = coord_system.scale_radius(CONFIG['center_circle_radius'])

            if 0 <= screen_cx <= WIDTH and 0 <= screen_cy <= HEIGHT:
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
