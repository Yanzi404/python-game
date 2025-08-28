import math

import numpy as np

# ==================== 用户配置参数 ====================
# 只需要调节这些核心参数
CONFIG = {
    # 物理参数
    'mass1': 20000,  # 质点1的质量
    'mass2': 40,  # 质点2的质量
    'mass3': 40,  # 质点3的质量
    'initial_speed': 3000,  # 初始环绕速度 方向与系统质心的连线垂直
    'separation': 2000,  # 两个质点之间的初始距离 1单位距离=1像素
    'gravity_constant': 5,  # 万有引力常数,值越大引力越大

    # 窗口和显示参数
    'window_width': 1200,
    'window_height': 800,
    'fps': 60.0,

    # 物理引擎参数
    'physics_frequency': 60.0,  # 物理更新频率 (Hz)

    # 能量图表参数
    'energy_graph_width': 300,
    'energy_graph_height': 150,
    'energy_graph_x': 10,
    'energy_graph_y': 200,
    'energy_graph_color': (0, 200, 0),
    'energy_graph_bg_color': (20, 20, 20),
    'energy_graph_border_color': (100, 100, 100),
    'energy_graph_line_width': 2,
    'energy_graph_max_points': 200,  # 图表上显示的最大点数
    'min_energy_graph_range': 1,  # 图表显示的最小偏差范围(%)
    'max_energy_graph_range': 1000,  # 图表显示的最大偏差范围(%)

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

    # 基于二体近似，使期望的初始速度产生稳定轨道
    # 对于二体系统：v² = GM/r，因此 G = v²r/M
    # 这里M可以是系统的特征质量
    characteristic_mass = (mass1 * mass2 + mass2 * mass3 + mass1 * mass3) / (mass1 + mass2 + mass3)
    gravity_constant = speed * speed * separation / characteristic_mass

    if CONFIG['gravity_constant']:
        gravity_constant=CONFIG['gravity_constant']


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

# 常量定义
G = auto_params['gravity_constant']
WIDTH = CONFIG['window_width']
HEIGHT = CONFIG['window_height']
FPS = CONFIG['fps']
FIXED_PHYSICS_DT = np.float64(1.0 / CONFIG['physics_frequency'])

# 颜色定义
BLACK = CONFIG['colors']['black']
WHITE = CONFIG['colors']['white']
RED = CONFIG['colors']['red']
BLUE = CONFIG['colors']['blue']
YELLOW = CONFIG['colors']['yellow']
GREEN = CONFIG['colors']['green']
PURPLE = CONFIG['colors']['purple']
