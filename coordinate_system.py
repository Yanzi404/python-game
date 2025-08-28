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