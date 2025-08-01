import pygame

class Lift:
    def __init__(self, coldbin, receiver_y):
        self.width = 3  # Width of lift shaft
        self.thickness = 1  # Wall thickness
        
        # Position lift to the right of the cold bin
        self.x = coldbin.x + coldbin.width + 2  # 2 cells gap from cold bin
        
        # Calculate height - from cold bin floor to above receiver with leeway
        self.bottom_y = coldbin.y + coldbin.height - coldbin.thickness  # Cold bin floor level
        self.top_y = max(0, receiver_y - 3)  # 3 cells above receiver for leeway
        self.height = self.bottom_y - self.top_y + 1
        
        # Connection to cold bin
        self.connection_start_x = coldbin.x + (coldbin.width - 3) // 2  # Center of cold bin
        self.connection_end_x = self.connection_start_x + 3
        self.connection_y = self.bottom_y
        
        # Lift movement parameters
        self.lift_speed = 2  # How many cells particles move up per update
        
    def is_wall(self, x, y):
        """Check if position is a wall of the lift shaft"""
        # Left wall of shaft
        if (x >= self.x and x < self.x + self.thickness and 
            y >= self.top_y and y <= self.bottom_y):
            return True
        
        # Right wall of shaft
        if (x >= self.x + self.width - self.thickness and x < self.x + self.width and
            y >= self.top_y and y <= self.bottom_y):
            return True
            
        # Connection tunnel walls (horizontal connection from cold bin)
        tunnel_y = self.connection_y
        if y == tunnel_y:
            # Top of tunnel
            if ((x >= self.connection_start_x and x < self.x) or
                (x >= self.x + self.width and x <= self.connection_start_x + 3)):
                return True
        elif y == tunnel_y + 1:
            # Bottom of tunnel  
            if ((x >= self.connection_start_x and x < self.x) or
                (x >= self.x + self.width and x <= self.connection_start_x + 3)):
                return True
                
        return False
    
    def is_inside_shaft(self, x, y):
        """Check if position is inside the lift shaft (where particles move up)"""
        return (x >= self.x + self.thickness and 
                x < self.x + self.width - self.thickness and
                y >= self.top_y and y <= self.bottom_y)
    
    def is_inside_connection(self, x, y):
        """Check if position is inside the connection tunnel"""
        return (x >= self.connection_start_x and x < self.connection_end_x and
                y == self.connection_y)
    
    def is_exit_point(self, x, y):
        """Check if position is at the exit point (top of lift)"""
        return (x >= self.x + self.thickness and 
                x < self.x + self.width - self.thickness and
                y == self.top_y)
    
    def move_particle_up(self, grid, x, y):
        """Move particle up in the lift shaft"""
        if not self.is_inside_shaft(x, y):
            return False
            
        # Try to move up by lift_speed cells
        for move_distance in range(self.lift_speed, 0, -1):
            target_y = y - move_distance
            
            # Check if target position is valid and empty
            if (target_y >= self.top_y and 
                grid.is_empty(x, target_y) and
                (self.is_inside_shaft(x, target_y) or target_y < self.top_y)):
                
                return grid.move_particle(x, y, x, target_y)
        
        return False
    
    def update_particles_in_lift(self, grid):
        """Update all particles in the lift system"""
        # Move particles in connection tunnel toward shaft
        for x in range(self.connection_start_x, self.connection_end_x):
            if grid.get_particle(x, self.connection_y) is not None:
                # Try to move toward shaft entrance
                if x < self.x + self.thickness:
                    target_x = x + 1
                    if (target_x < self.x + self.width - self.thickness and 
                        grid.is_empty(target_x, self.connection_y)):
                        grid.move_particle(x, self.connection_y, target_x, self.connection_y)
        
        # Move particles up in shaft (from bottom to top to avoid double moves)
        for y in range(self.top_y, self.bottom_y + 1):
            for x in range(self.x + self.thickness, self.x + self.width - self.thickness):
                if grid.get_particle(x, y) is not None:
                    self.move_particle_up(grid, x, y)
    
    def draw(self, screen, cell_size):
        """Draw the lift system"""
        wall_color = (105, 105, 105)  # Dark gray for lift
        
        # Draw lift shaft walls
        # Left wall
        left_wall = pygame.Rect(
            self.x * cell_size,
            self.top_y * cell_size,
            self.thickness * cell_size,
            (self.height) * cell_size
        )
        pygame.draw.rect(screen, wall_color, left_wall)
        
        # Right wall
        right_wall = pygame.Rect(
            (self.x + self.width - self.thickness) * cell_size,
            self.top_y * cell_size,
            self.thickness * cell_size,
            (self.height) * cell_size
        )
        pygame.draw.rect(screen, wall_color, right_wall)
        
        # Draw connection tunnel
        # Top of tunnel
        tunnel_top = pygame.Rect(
            self.connection_start_x * cell_size,
            self.connection_y * cell_size,
            (self.x + self.width - self.connection_start_x) * cell_size,
            self.thickness * cell_size
        )
        pygame.draw.rect(screen, wall_color, tunnel_top)
        
        # Bottom of tunnel
        tunnel_bottom = pygame.Rect(
            self.connection_start_x * cell_size,
            (self.connection_y + 1) * cell_size,
            (self.x + self.width - self.connection_start_x) * cell_size,
            self.thickness * cell_size
        )
        pygame.draw.rect(screen, wall_color, tunnel_bottom)
        
        # Draw shaft interior with subtle glow to indicate upward movement
        shaft_interior = pygame.Rect(
            (self.x + self.thickness) * cell_size,
            self.top_y * cell_size,
            (self.width - 2 * self.thickness) * cell_size,
            self.height * cell_size
        )
        glow_surface = pygame.Surface((shaft_interior.width, shaft_interior.height))
        glow_surface.set_alpha(20)
        glow_surface.fill((150, 150, 255))  # Blue glow for upward movement
        screen.blit(glow_surface, (shaft_interior.x, shaft_interior.y))