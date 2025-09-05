from config.config import G
from core.centroid import Centroid
from core.vector2d import Vector2D


class PhysicsEngine:
    """物理引擎类"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PhysicsEngine, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.balls = []
        self.integration_method = 'verlet'
        self.initial_energy = None
        self.G = G
        # 物理模拟固定时间步长
        self.physics_accumulator = 0.0
        # 质心对象
        self.centroid = Centroid()

    def calculate_gravity_force(self, ball1, ball2):
        """计算两个质点之间的引力"""
        # 计算距离向量
        distance_vector = ball2.position - ball1.position
        distance_squared = distance_vector.magnitude_squared()

        # 避免除零错误和数值不稳定（添加最小距离）
        min_distance = ball1.radius + ball2.radius
        min_distance_squared = min_distance * min_distance
        if distance_squared <= min_distance_squared:
            distance_squared = min_distance_squared

        # 万有引力公式 F = G * m1 * m2 / r²
        force_magnitude = self.G * ball1.mass * ball2.mass / distance_squared

        # 计算力的方向（单位向量）
        distance_magnitude = distance_vector.magnitude()
        if distance_magnitude > 0:
            unit_direction = distance_vector.normalize()
            force_vector = unit_direction * force_magnitude
        else:
            # 处理零向量情况
            force_vector = Vector2D(0.0, 0.0)

        return force_vector.x, force_vector.y

    def calculate_total_energy(self):
        """计算系统总能量"""
        kinetic_energy = 0.0
        potential_energy = 0.0

        # 计算动能
        for ball in self.balls:
            velocity_squared = ball.velocity.magnitude_squared()
            kinetic_energy += 0.5 * ball.mass * velocity_squared

        # 计算势能
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                distance_vector = self.balls[j].position - self.balls[i].position
                distance = distance_vector.magnitude()
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

        # 更新质心状态
        self.centroid.update(self.balls)

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

    def draw(self, centroid: bool):
        """绘制所有质点"""
        for ball in self.balls:
            ball.draw()

        if centroid:
            # 绘制质心
            self.centroid.draw()
