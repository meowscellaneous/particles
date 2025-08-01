import pygame

class PSG:
    def __init__(self, hotbin_x, hotbin_y, hotbin_width):
        self.width = 3  # Width of PSG in grid cells
        self.height = 1  # Height of PSG in grid cells
        
        # Position PSG underneath the hot bin, centered
        self.x = hotbin_x + (hotbin_width - self.width) // 2
        self.y = hotbin_y + 8 + 2  # 2 cells below hot bin
        
        self.cooling_amount = 25  # Amount of heat to remove from particles
        
    def is_inside(self, x, y):
        """Check if position is inside the PSG"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def cool_particle(self, particle):
        """Cool a particle that passes through"""
        particle.temperature = max(0, particle.temperature - self.cooling_amount)
    
    def draw(self, screen, cell_size):
        """Draw the PSG on screen"""
        rect = pygame.Rect(
            self.x * cell_size,
            self.y * cell_size,
            self.width * cell_size,
            self.height * cell_size
        )
        # Draw PSG as a bright yellow rectangle
        pygame.draw.rect(screen, (255, 255, 0), rect)
        pygame.draw.rect(screen, (255, 255, 150), rect, 2)  # Lighter yellow border