import pygame
import random

class Separator:
    def __init__(self, receiver_x, receiver_y, receiver_width):
        # Position separator above the receiver
        self.width = receiver_width
        self.height = 3  # Height of the U-shaped separator
        self.thickness = 1  # Thickness of walls
        
        # Center separator above receiver
        self.x = receiver_x - (self.width - receiver_width) // 2
        self.y = receiver_y - 10  # 10 cells above receiver
        
        # Ensure separator doesn't go outside grid bounds
        self.x = max(0, self.x)
        
        # U-shape dimensions
        self.left_wall_x = self.x
        self.right_wall_x = self.x + self.width - self.thickness
        self.bottom_y = self.y + self.height - self.thickness
        
        # Distribution area (where particles can be redistributed)
        self.distribution_start_x = self.x + self.thickness
        self.distribution_end_x = self.x + self.width - self.thickness
        self.distribution_width = self.distribution_end_x - self.distribution_start_x
        
    def is_wall(self, x, y):
        """Check if position is a wall of the separator (solid)"""
        # Left wall
        if (x >= self.left_wall_x and x < self.left_wall_x + self.thickness and 
            y >= self.y and y < self.y + self.height):
            return True
        
        # Right wall
        if (x >= self.right_wall_x and x < self.right_wall_x + self.thickness and
            y >= self.y and y < self.y + self.height):
            return True
            
        # Bottom wall (floor of the U)
        if (x >= self.x and x < self.x + self.width and
            y >= self.bottom_y and y < self.bottom_y + self.thickness):
            return True
            
        return False
    
    def is_inside(self, x, y):
        """Check if position is inside the separator (where particles can be redistributed)"""
        return (x >= self.distribution_start_x and 
                x < self.distribution_end_x and
                y >= self.y and 
                y < self.bottom_y)
    
    def can_enter_separator(self, x, y):
        """Check if a particle can enter the separator from above"""
        # Particles can enter from the top opening of the U
        return (y == self.y - 1 and 
                x >= self.distribution_start_x and 
                x < self.distribution_end_x)
    
    def separate_particle(self, particle, grid):
        """Separate a particle by redistributing its x position within the separator"""
        # Find a random x position within the distribution area
        attempts = 0
        max_attempts = self.distribution_width
        
        while attempts < max_attempts:
            # Random x position within the separator width
            new_x = random.randint(self.distribution_start_x, self.distribution_end_x - 1)
            
            # Try to place at the bottom of the separator
            exit_y = self.bottom_y + self.thickness
            
            # Check if the exit position is available
            if (grid.is_valid_position(new_x, exit_y) and 
                grid.is_empty(new_x, exit_y)):
                return new_x, exit_y
            
            attempts += 1
        
        # If no random position is available, try sequential positions
        for offset in range(self.distribution_width):
            new_x = self.distribution_start_x + offset
            exit_y = self.bottom_y + self.thickness
            
            if (grid.is_valid_position(new_x, exit_y) and 
                grid.is_empty(new_x, exit_y)):
                return new_x, exit_y
        
        # If still no position available, return None (particle waits)
        return None, None
    
    def update_particles_in_separator(self, grid):
        """Update particles inside the separator, redistributing them"""
        particles_to_separate = []
        
        # Find all particles inside the separator
        for y in range(self.y, self.bottom_y + self.thickness):
            for x in range(self.distribution_start_x, self.distribution_end_x):
                particle = grid.get_particle(x, y)
                if particle and self.is_inside(x, y):
                    particles_to_separate.append((x, y, particle))
        
        # Process particles for separation
        for x, y, particle in particles_to_separate:
            # Try to separate the particle (redistribute its x position)
            new_x, new_y = self.separate_particle(particle, grid)
            
            if new_x is not None and new_y is not None:
                # Move particle to new distributed position
                grid.move_particle(x, y, new_x, new_y)
    
    def get_separator_bounds(self):
        """Get the bounds of the separator for collision detection"""
        return {
            'left': self.x,
            'right': self.x + self.width,
            'top': self.y,
            'bottom': self.y + self.height,
            'inner_left': self.distribution_start_x,
            'inner_right': self.distribution_end_x,
            'inner_bottom': self.bottom_y
        }
    
    def draw(self, screen, cell_size):
        """Draw the U-shaped separator on screen"""
        # Draw walls as dark gray rectangles
        wall_color = (80, 80, 80)  # Dark gray
        
        # Left wall
        left_wall = pygame.Rect(
            self.left_wall_x * cell_size,
            self.y * cell_size,
            self.thickness * cell_size,
            self.height * cell_size
        )
        pygame.draw.rect(screen, wall_color, left_wall)
        
        # Right wall
        right_wall = pygame.Rect(
            self.right_wall_x * cell_size,
            self.y * cell_size,
            self.thickness * cell_size,
            self.height * cell_size
        )
        pygame.draw.rect(screen, wall_color, right_wall)
        
        # Bottom wall (floor of U)
        bottom_wall = pygame.Rect(
            self.x * cell_size,
            self.bottom_y * cell_size,
            self.width * cell_size,
            self.thickness * cell_size
        )
        pygame.draw.rect(screen, wall_color, bottom_wall)
        
        # Draw a subtle inner indication to show distribution area
        inner_rect = pygame.Rect(
            self.distribution_start_x * cell_size,
            self.y * cell_size,
            self.distribution_width * cell_size,
            (self.height - self.thickness) * cell_size
        )
        # Draw a translucent overlay to show separation area
        glow_surface = pygame.Surface((inner_rect.width, inner_rect.height))
        glow_surface.set_alpha(20)
        glow_surface.fill((150, 150, 150))
        screen.blit(glow_surface, (inner_rect.x, inner_rect.y))