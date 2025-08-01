import pygame

class Receiver:
    def __init__(self, grid_width, grid_height):
        self.width = 3  # Width of receiver in grid cells
        self.height = 1  # Height of receiver in grid cells
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Position receiver in center of grid
        self.x = (grid_width - self.width) // 2
        self.y = 7
        
        self.heat_amount = 30  # Amount of heat to add to particles
        
    def is_inside(self, x, y):
        """Check if position is inside the receiver"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def heat_particle(self, particle):
        """Heat a particle that passes through"""
        particle.heat(self.heat_amount)
    
    def draw(self, screen, cell_size):
        """Draw the receiver on screen"""
        rect = pygame.Rect(
            self.x * cell_size,
            self.y * cell_size,
            self.width * cell_size,
            self.height * cell_size
        )
        # Draw receiver as a bright orange/red rectangle
        pygame.draw.rect(screen, (255, 100, 0), rect)
        pygame.draw.rect(screen, (255, 200, 0), rect, 2)  # Border