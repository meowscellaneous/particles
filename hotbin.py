import pygame

class HotBin:
    def __init__(self, receiver_x, receiver_y, receiver_width):
        # Position bin underneath the receiver
        self.width = receiver_width + 6  # Wider than receiver
        self.height = 8  # Height of the bin
        self.thickness = 1  # Thickness of walls
        
        # Center bin under receiver
        self.x = receiver_x - (self.width - receiver_width) // 2
        self.y = receiver_y + 8  # 8 cells below receiver
        
        # Ensure bin doesn't go outside grid bounds
        self.x = max(0, self.x)
        
        # Opening/closing mechanism
        self.is_open = False
        self.opening_width = 3  # Number of floor tiles to remove when open
        
        # Calculate opening position (center of bottom wall)
        self.opening_start_x = self.x + (self.width - self.opening_width) // 2
        self.opening_end_x = self.opening_start_x + self.opening_width
        self.floor_y = self.y + self.height - self.thickness
        
    def open_bin(self):
        """Open the bin by removing center floor tiles"""
        self.is_open = True
        
    def close_bin(self):
        """Close the bin by restoring center floor tiles"""
        self.is_open = False
    
    def is_wall(self, x, y):
        """Check if position is a wall of the bin (solid)"""
        # Left wall
        if (x >= self.x and x < self.x + self.thickness and 
            y >= self.y and y < self.y + self.height):
            return True
        
        # Right wall  
        if (x >= self.x + self.width - self.thickness and x < self.x + self.width and
            y >= self.y and y < self.y + self.height):
            return True
            
        # Bottom wall - check if opening is active
        if (x >= self.x and x < self.x + self.width and
            y >= self.y + self.height - self.thickness and y < self.y + self.height):
            # If bin is open and this is within the opening area, not a wall
            if (self.is_open and 
                x >= self.opening_start_x and x < self.opening_end_x):
                return False
            return True
            
        return False
    
    def is_inside(self, x, y):
        """Check if position is inside the bin (empty space where particles can settle)"""
        return (x > self.x + self.thickness - 1 and 
                x < self.x + self.width - self.thickness and
                y >= self.y and 
                y < self.y + self.height - self.thickness)
    
    def get_bin_bounds(self):
        """Get the bounds of the bin for collision detection"""
        return {
            'left': self.x,
            'right': self.x + self.width,
            'top': self.y,
            'bottom': self.y + self.height,
            'inner_left': self.x + self.thickness,
            'inner_right': self.x + self.width - self.thickness,
            'inner_bottom': self.y + self.height - self.thickness
        }
    
    def draw(self, screen, cell_size):
        """Draw the hot bin on screen"""
        # Draw walls as dark red/brown rectangles
        wall_color = (139, 69, 19)  # Dark brown
        
        # Left wall
        left_wall = pygame.Rect(
            self.x * cell_size,
            self.y * cell_size,
            self.thickness * cell_size,
            self.height * cell_size
        )
        pygame.draw.rect(screen, wall_color, left_wall)
        
        # Right wall
        right_wall = pygame.Rect(
            (self.x + self.width - self.thickness) * cell_size,
            self.y * cell_size,
            self.thickness * cell_size,
            self.height * cell_size
        )
        pygame.draw.rect(screen, wall_color, right_wall)
        
        # Bottom wall - draw in sections if open
        if self.is_open:
            # Draw left part of bottom wall
            if self.opening_start_x > self.x:
                left_bottom = pygame.Rect(
                    self.x * cell_size,
                    self.floor_y * cell_size,
                    (self.opening_start_x - self.x) * cell_size,
                    self.thickness * cell_size
                )
                pygame.draw.rect(screen, wall_color, left_bottom)
            
            # Draw right part of bottom wall
            if self.opening_end_x < self.x + self.width:
                right_bottom = pygame.Rect(
                    self.opening_end_x * cell_size,
                    self.floor_y * cell_size,
                    (self.x + self.width - self.opening_end_x) * cell_size,
                    self.thickness * cell_size
                )
                pygame.draw.rect(screen, wall_color, right_bottom)
                
            # Draw opening indicator (dashed line or different color)
            opening_rect = pygame.Rect(
                self.opening_start_x * cell_size,
                self.floor_y * cell_size,
                self.opening_width * cell_size,
                self.thickness * cell_size
            )
            pygame.draw.rect(screen, (100, 50, 0), opening_rect)  # Darker brown for opening
        else:
            # Draw complete bottom wall when closed
            bottom_wall = pygame.Rect(
                self.x * cell_size,
                self.floor_y * cell_size,
                self.width * cell_size,
                self.thickness * cell_size
            )
            pygame.draw.rect(screen, wall_color, bottom_wall)
        
        # Draw a subtle inner glow to show it's hot
        inner_rect = pygame.Rect(
            (self.x + self.thickness) * cell_size,
            self.y * cell_size,
            (self.width - 2 * self.thickness) * cell_size,
            (self.height - self.thickness) * cell_size
        )
        # Draw a translucent red overlay
        glow_surface = pygame.Surface((inner_rect.width, inner_rect.height))
        glow_surface.set_alpha(30)
        glow_surface.fill((255, 100, 0))
        screen.blit(glow_surface, (inner_rect.x, inner_rect.y))