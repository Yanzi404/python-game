import math

import numpy as np


class Vector2D:
    """二维向量类，用于处理位置、速度等向量运算"""
    
    def __init__(self, x=0.0, y=0.0):
        self.x = np.float64(x)
        self.y = np.float64(y)
    
    def __add__(self, other):
        """向量加法"""
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """向量减法"""
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        """向量数乘"""
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        """右乘"""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        """向量除法"""
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def magnitude(self):
        """计算向量的模长"""
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def magnitude_squared(self):
        """计算向量模长的平方（避免开方运算）"""
        return self.x ** 2 + self.y ** 2
    
    def normalize(self):
        """返回单位向量"""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)
    
    def distance_to(self, other):
        """计算到另一个向量的距离"""
        return (self - other).magnitude()
    
    def distance_squared_to(self, other):
        """计算到另一个向量距离的平方"""
        return (self - other).magnitude_squared()
    
    def copy(self):
        """复制向量"""
        return Vector2D(self.x, self.y)
    
    def __str__(self):
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_tuple(self):
        """转换为元组"""
        return (self.x, self.y)