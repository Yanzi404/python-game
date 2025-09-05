import pygame
from core.vector2d import Vector2D


class Camera:
    """摄像头类，提供视角控制功能"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 摄像头位置（世界坐标）
        self.position = Vector2D(0.0, 0.0)

        # 缩放级别
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0

        # 跟踪目标
        self.target = None  # 要跟踪的对象
        self.follow_mode = False  # 是否启用跟踪模式

        # 平滑跟踪参数
        self.follow_smoothness = 0.1  # 跟踪平滑度 (0-1, 越小越平滑)

        # 拖动状态
        self.dragging = False
        self.last_mouse_pos = None

        # 移动速度（键盘控制）
        self.move_speed = 5.0

    def set_target(self, target):
        """设置跟踪目标"""
        self.target = target

    def enable_follow_mode(self, enable=True):
        """启用/禁用跟踪模式"""
        self.follow_mode = enable

    def toggle_follow_mode(self):
        """切换跟踪模式"""
        self.follow_mode = not self.follow_mode

    def set_zoom(self, zoom):
        """设置缩放级别"""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))

    def zoom_in(self, factor=1.1):
        """放大"""
        self.set_zoom(self.zoom * factor)

    def zoom_out(self, factor=1.1):
        """缩小"""
        self.set_zoom(self.zoom / factor)

    def move_to(self, x, y):
        """移动摄像头到指定位置"""
        self.position = Vector2D(x, y)

    def move_by(self, dx, dy):
        """相对移动摄像头"""
        self.position = self.position + Vector2D(dx, dy)

    def reset_position(self):
        """重置摄像头位置到原点"""
        self.position = Vector2D(0.0, 0.0)

    def reset_zoom(self):
        """重置缩放到1.0"""
        self.zoom = 1.0

    def reset(self):
        """重置摄像头到初始状态"""
        self.reset_position()
        self.reset_zoom()
        self.follow_mode = False

    def update(self):
        """更新摄像头状态"""
        if self.follow_mode and self.target:
            # 平滑跟踪目标
            target_position = self.target.position

            # 使用线性插值实现平滑跟踪
            self.position = self.position + (target_position - self.position) * self.follow_smoothness

    def world_to_screen(self, world_x, world_y):
        """将世界坐标转换为屏幕坐标"""
        # 相对于摄像头的坐标
        rel_pos = Vector2D(world_x, world_y) - self.position

        # 应用缩放
        scaled_pos = rel_pos * self.zoom

        # 转换到屏幕坐标（以屏幕中心为原点）
        screen_x = self.screen_width // 2 + scaled_pos.x
        screen_y = self.screen_height // 2 + scaled_pos.y

        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """将屏幕坐标转换为世界坐标"""
        # 相对于屏幕中心的坐标
        rel_pos = Vector2D(screen_x - self.screen_width // 2, screen_y - self.screen_height // 2)

        # 应用逆缩放
        world_rel_pos = rel_pos / self.zoom

        # 转换到世界坐标
        world_pos = self.position + world_rel_pos

        return world_pos.x, world_pos.y

    def scale_radius(self, radius):
        """缩放半径"""
        return max(1, int(radius * self.zoom))

    def handle_mouse_event(self, event):
        """处理鼠标事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键按下
                self.dragging = True
                self.last_mouse_pos = event.pos
                # 拖动时禁用跟踪模式
                self.follow_mode = False

        elif event.type == pygame.MOUSEWHEEL:
            # 处理鼠标滚轮缩放
            if event.y > 0:
                self.zoom_in(1.1)
            elif event.y < 0:
                self.zoom_out(1.1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.last_mouse_pos:
                # 计算鼠标移动距离
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]

                # 将屏幕移动转换为世界移动（考虑缩放）
                world_dx = -dx / self.zoom
                world_dy = -dy / self.zoom

                # 移动摄像头
                self.move_by(world_dx, world_dy)

                # 更新鼠标位置
                self.last_mouse_pos = event.pos

    def handle_keyboard_event(self, keys):
        """处理键盘事件（连续按键）"""
        move_speed = self.move_speed / self.zoom  # 缩放时调整移动速度

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move_by(0, -move_speed)
            self.follow_mode = False
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move_by(0, move_speed)
            self.follow_mode = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.move_by(-move_speed, 0)
            self.follow_mode = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.move_by(move_speed, 0)
            self.follow_mode = False

    def handle_key_press(self, key):
        """处理单次按键事件"""
        if key == pygame.K_HOME:
            # 重置摄像头
            self.reset()
        elif key == pygame.K_0:
            # 重置缩放
            self.reset_zoom()
        elif key == pygame.K_EQUALS or key == pygame.K_PLUS:
            # 放大
            self.zoom_in(1.2)
        elif key == pygame.K_MINUS:
            # 缩小
            self.zoom_out(1.2)

    def get_view_bounds(self):
        """获取当前视野边界（世界坐标）"""
        half_width = (self.screen_width / 2) / self.zoom
        half_height = (self.screen_height / 2) / self.zoom

        left = self.position.x - half_width
        right = self.position.x + half_width
        top = self.position.y - half_height
        bottom = self.position.y + half_height

        return left, right, top, bottom

    def is_point_visible(self, x, y, margin=0):
        """检查点是否在视野内"""
        left, right, top, bottom = self.get_view_bounds()
        return (left - margin <= x <= right + margin and
                top - margin <= y <= bottom + margin)

    def get_info(self):
        """获取摄像头信息"""
        return {
            'position': (self.position.x, self.position.y),
            'zoom': self.zoom,
            'follow_mode': self.follow_mode,
            'target': self.target.__class__.__name__ if self.target else None
        }

    @property
    def x(self):
        """向后兼容的x坐标属性"""
        return self.position.x

    @property
    def y(self):
        """向后兼容的y坐标属性"""
        return self.position.y
