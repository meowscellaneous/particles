import pygame
import colorsys

class Particle:
    def __init__(self, x, y, temperature=0):
        self.x = x
        self.y = y
        self.temperature = temperature
        self.max_temperature = 100
        
    def get_color(self):
        """Get particle color based on temperature (cooler = yellow/brown, hotter = red)"""
        if self.temperature == 0:
            # Base sand color
            return (194, 178, 128)  # Light brown/sand color
        
        # Interpolate from sand color to red based on temperature
        temp_ratio = min(self.temperature / self.max_temperature, 1.0)
        
        # Base sand color (HSV: hue=45, sat=0.34, val=0.76)
        base_h, base_s, base_v = 0.125, 0.34, 0.76
        # Red color (HSV: hue=0, sat=1.0, val=1.0)
        target_h, target_s, target_v = 0.0, 1.0, 1.0
        
        # Interpolate HSV values
        h = base_h + (target_h - base_h) * temp_ratio
        s = base_s + (target_s - base_s) * temp_ratio
        v = base_v + (target_v - base_v) * temp_ratio
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def heat(self, amount):
        """Increase particle temperature"""
        self.temperature = min(self.temperature + amount, self.max_temperature)
    
    def move_to(self, new_x, new_y):
        """Move particle to new position"""
        self.x = new_x
        self.y = new_y