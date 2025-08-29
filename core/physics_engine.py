import numpy as np

from config.config import G


class PhysicsEngine:
    """物理引擎类"""

    def __init__(self, integration_method='verlet'):
        self.balls = []
        self.integration_method = integration_method
        self.initial_energy = None
        self.G = G
        # 物理模拟固定时间步长
        self.physics_accumulator = 0.0

    def calculate_gravity_force(self, ball1, ball2):
        """计算两个质点之间的引力"""
        # 计算距离
        dx = ball2.x - ball1.x
        dy = ball2.y - ball1.y
        distance_squared = dx * dx + dy * dy
        # distance = np.sqrt(distance_squared)

        # 避免除零错误和数值不稳定（添加最小距离）
        min_distance = ball1.radius + ball2.radius
        min_distance_squared = min_distance * min_distance
        if distance_squared <= min_distance_squared:
            distance_squared = min_distance_squared

        # 万有引力公式 F = G * m1 * m2 / r²
        force_magnitude = self.G * ball1.mass * ball2.mass / distance_squared

        # 计算力的方向（单位向量）
        direction_vector = np.array([dx, dy], dtype=np.float64)
        direction_norm = np.linalg.norm(direction_vector)
        if direction_norm > 0:
            unit_direction = direction_vector / direction_norm
            force_direction_x = unit_direction[0]
            force_direction_y = unit_direction[1]
        else:
            # 处理零向量情况
            force_direction_x = 0.0
            force_direction_y = 0.0

        # force_direction_x = dx / distance
        # force_direction_y = dy / distance

        # 计算力的分量
        fx = force_magnitude * force_direction_x
        fy = force_magnitude * force_direction_y

        return fx, fy

    def calculate_total_energy(self):
        """计算系统总能量"""
        kinetic_energy = np.float64(0.0)
        potential_energy = np.float64(0.0)

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

                # 牛顿第三定律
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