import pygame


class ScreenManager:
    """屏幕管理器单例类，管理pygame的screen对象"""

    _instance = None
    _screen = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScreenManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.width = 800
        self.height = 600

    @classmethod
    def get_instance(cls):
        """获取ScreenManager单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, width, height, caption="Game"):
        """初始化屏幕（必须在使用前调用）"""
        self.width = width
        self.height = height
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        return self

    @property
    def screen(self):
        """获取screen对象"""
        if self._screen is None:
            raise RuntimeError("Screen not initialized. Please call initialize() first.")
        return self._screen

    def get_size(self):
        """获取屏幕尺寸"""
        return self.width, self.height

    def fill(self, color):
        """填充屏幕背景色"""
        self.screen.fill(color)

    def blit(self, surface, position):
        """在屏幕上绘制surface"""
        self.screen.blit(surface, position)

    def get_width(self):
        """获取屏幕宽度"""
        return self.width

    def get_height(self):
        """获取屏幕高度"""
        return self.height
