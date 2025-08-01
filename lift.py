import pygame

class Lift:
    def __init__(self, coldbin, receiver_y):
        self.coldbin_bounds = coldbin.get_bin_bounds()
        self.receiver_y = receiver_y
        
        # Lift dimensions
        self.shaft_width = 2  # Width of vertical shaft
        self.thickness = 1    # Wall thickness
        
        # Vertical shaft (connects to bottom of cold bin)
        self.shaft_x = self.coldbin_bounds['right']  # Start at right edge of cold bin
        self.shaft_start_y = self.coldbin_bounds['inner_bottom']  # Bottom of cold bin
        self.shaft_height = 15  # Height of vertical section
        
        # Horizontal section (elbow going right)
        self.horizontal_length = 8  # Length going right
        self.horizontal_y = self.shaft_start_y - self.shaft_height
        
        # Return section (elbow going back left, above receiver)
        self.return_length = self.horizontal_length + self.shaft_width + 2  # Go back past shaft
        self.return_y = self.horizontal_y - 3  # 3 cells above horizontal section
        self.return_end_x = self.shaft_x - 2  # End above receiver area
        
        # Particle movement speed (cells per update)
        self.lift_speed = 0.5  # Slower than gravity for realistic movement
        self.frame_counter = 0
        
    def is_wall(self, x, y):
        """Check if position is a wall of the lift system"""
        # Vertical shaft walls
        if (y >= self.horizontal_y and y < self.shaft_start_y):
            # Left wall of shaft
            if x == self.shaft_x:
                return True
            # Right wall of shaft
            if x == self.shaft_x + self.shaft_width + self.thickness:
                return True
        
        # Horizontal section walls
        horizontal_end_x = self.shaft_x + self.horizontal_length + self.shaft_width
        if (x >= self.shaft_x and x <= horizontal_end_x and
            (y == self.horizontal_y - self.thickness or y == self.horizontal_y + self.thickness)):
            return True
        
        # Return section walls
        if (x >= self.return_end_x and x <= horizontal_end_x and
            (y == self.return_y - self.thickness or y == self.return_y + self.thickness)):
            return True
        
        # Vertical walls for return section
        if ((x == self.return_end_x or x == horizontal_end_x) and
            y >= self.return_y - self.thickness and y <= self.horizontal_y + self.thickness):
            return True
            
        return False
    
    def is_inside_shaft(self, x, y):
        """Check if position is inside the vertical shaft"""
        return (x > self.shaft_x and x < self.shaft_x + self.shaft_width and
                y >= self.horizontal_y and y < self.shaft_start_y)
    
    def is_inside_horizontal(self, x, y):
        """Check if position is inside the horizontal section"""
        horizontal_end_x = self.shaft_x + self.horizontal_length + self.shaft_width
        return (x >= self.shaft_x and x < horizontal_end_x and
                y == self.horizontal_y)
    
    def is_inside_return(self, x, y):
        """Check if position is inside the return section"""
        horizontal_end_x = self.shaft_x + self.horizontal_length + self.shaft_width
        return (x > self.return_end_x and x < horizontal_end_x and
                y == self.return_y)
    
    def is_inside_connection(self, x, y):
        """Check if position is inside any part of the lift system"""
        return (self.is_inside_shaft(x, y) or 
                self.is_inside_horizontal(x, y) or 
                self.is_inside_return(x, y))
    
    def get_entry_position(self):
        """Get the position where particles enter the lift (bottom of shaft)"""
        return (self.shaft_x + 1, self.shaft_start_y - 1)  # Center of shaft entrance
    
    def update_particles_in_lift(self, grid):
        """Update particles moving through the lift system"""
        self.frame_counter += 1
        
        # Only move particles every few frames to control speed
        if self.frame_counter % max(1, int(1 / self.lift_speed)) != 0:
            return
        
        particles_to_move = []
        
        # Find all particles in lift system
        for y in range(grid.height):
            for x in range(grid.width):
                particle = grid.get_particle(x, y)
                if particle and self.is_inside_connection(x, y):
                    particles_to_move.append((x, y, particle))
        
        # Process particle movements (in reverse order to avoid conflicts)
        for x, y, particle in reversed(particles_to_move):
            new_x, new_y = self._get_next_position(x, y)
            
            if new_x is not None and new_y is not None:
                # Check if destination is empty
                if grid.is_empty(new_x, new_y):
                    grid.move_particle(x, y, new_x, new_y)
                elif self._is_exit_position(new_x, new_y):
                    # Particle reached exit - let it fall out naturally
                    # Find a position below the return section where it can fall
                    fall_x, fall_y = new_x, new_y + 1
                    while fall_y < grid.height and grid.is_empty(fall_x, fall_y):
                        if not self.is_wall(fall_x, fall_y) and not self.is_inside_connection(fall_x, fall_y):
                            grid.move_particle(x, y, fall_x, fall_y)
                            break
                        fall_y += 1
    
    def _get_next_position(self, x, y):
        """Calculate next position for particle in lift"""
        # In vertical shaft - move up
        if self.is_inside_shaft(x, y):
            if y > self.horizontal_y:
                return x, y - 1
            else:
                # Transition to horizontal section
                return x + 1, self.horizontal_y
        
        # In horizontal section - move right
        elif self.is_inside_horizontal(x, y):
            horizontal_end_x = self.shaft_x + self.horizontal_length + self.shaft_width
            if x < horizontal_end_x - 1:
                return x + 1, y
            else:
                # Transition to return section
                return x, self.return_y
        
        # In return section - move left
        elif self.is_inside_return(x, y):
            if x > self.return_end_x:
                return x - 1, y
            else:
                # Exit point - particle will fall out
                return x, y + 1
        
        return None, None
    
    def _is_exit_position(self, x, y):
        """Check if position is the exit point of the lift"""
        return x == self.return_end_x and y == self.return_y + 1
    
    def draw(self, screen, cell_size):
        """Draw the lift system"""
        wall_color = (128, 128, 128)  # Gray for lift structure
        inner_color = (160, 160, 160)  # Lighter gray for interior
        
        # Draw vertical shaft
        shaft_rect = pygame.Rect(
            self.shaft_x * cell_size,
            self.horizontal_y * cell_size,
            (self.shaft_width + 2 * self.thickness) * cell_size,
            (self.shaft_start_y - self.horizontal_y) * cell_size
        )
        pygame.draw.rect(screen, wall_color, shaft_rect)
        
        # Draw shaft interior
        shaft_inner = pygame.Rect(
            (self.shaft_x + self.thickness) * cell_size,
            self.horizontal_y * cell_size,
            self.shaft_width * cell_size,
            (self.shaft_start_y - self.horizontal_y) * cell_size
        )
        pygame.draw.rect(screen, inner_color, shaft_inner)
        
        # Draw horizontal section
        horizontal_end_x = self.shaft_x + self.horizontal_length + self.shaft_width
        horizontal_rect = pygame.Rect(
            self.shaft_x * cell_size,
            (self.horizontal_y - self.thickness) * cell_size,
            (horizontal_end_x - self.shaft_x + self.thickness) * cell_size,
            (2 * self.thickness + 1) * cell_size
        )
        pygame.draw.rect(screen, wall_color, horizontal_rect)
        
        # Draw horizontal interior
        horizontal_inner = pygame.Rect(
            (self.shaft_x + self.thickness) * cell_size,
            self.horizontal_y * cell_size,
            (horizontal_end_x - self.shaft_x - self.thickness) * cell_size,
            cell_size
        )
        pygame.draw.rect(screen, inner_color, horizontal_inner)
        
        # Draw return section
        return_rect = pygame.Rect(
            self.return_end_x * cell_size,
            (self.return_y - self.thickness) * cell_size,
            (horizontal_end_x - self.return_end_x + self.thickness) * cell_size,
            (2 * self.thickness + 1) * cell_size
        )
        pygame.draw.rect(screen, wall_color, return_rect)
        
        # Draw return interior
        return_inner = pygame.Rect(
            (self.return_end_x + self.thickness) * cell_size,
            self.return_y * cell_size,
            (horizontal_end_x - self.return_end_x - self.thickness) * cell_size,
            cell_size
        )
        pygame.draw.rect(screen, inner_color, return_inner)
        
        # Draw connecting vertical sections
        # Right vertical connector (from horizontal to return)
        right_connector = pygame.Rect(
            horizontal_end_x * cell_size,
            self.return_y * cell_size,
            self.thickness * cell_size,
            (self.horizontal_y - self.return_y + 1) * cell_size
        )
        pygame.draw.rect(screen, wall_color, right_connector)
        
        # Left vertical connector (at return end)
        left_connector = pygame.Rect(
            self.return_end_x * cell_size,
            self.return_y * cell_size,
            self.thickness * cell_size,
            (self.horizontal_y - self.return_y + 1) * cell_size
        )
        pygame.draw.rect(screen, wall_color, left_connector)
        
        # Draw directional arrows to show particle flow
        self._draw_flow_indicators(screen, cell_size)
    
    def _draw_flow_indicators(self, screen, cell_size):
        """Draw small arrows indicating particle flow direction"""
        arrow_color = (255, 255, 255)
        
        # Upward arrow in shaft
        shaft_center_x = (self.shaft_x + 1) * cell_size + cell_size // 2
        shaft_mid_y = (self.horizontal_y + (self.shaft_start_y - self.horizontal_y) // 2) * cell_size + cell_size // 2
        self._draw_arrow(screen, shaft_center_x, shaft_mid_y, 0, -1, arrow_color)
        
        # Rightward arrow in horizontal section
        horiz_mid_x = (self.shaft_x + self.horizontal_length // 2) * cell_size + cell_size // 2
        horiz_y = self.horizontal_y * cell_size + cell_size // 2
        self._draw_arrow(screen, horiz_mid_x, horiz_y, 1, 0, arrow_color)
        
        # Leftward arrow in return section
        return_mid_x = (self.return_end_x + self.horizontal_length // 2) * cell_size + cell_size // 2
        return_y = self.return_y * cell_size + cell_size // 2
        self._draw_arrow(screen, return_mid_x, return_y, -1, 0, arrow_color)
    
    def _draw_arrow(self, screen, x, y, dx, dy, color):
        """Draw a small directional arrow"""
        arrow_size = 3
        # Arrow tip
        tip_x = x + dx * arrow_size
        tip_y = y + dy * arrow_size
        
        # Arrow base points
        if dx != 0:  # Horizontal arrow
            base1_x = x - dx * arrow_size
            base1_y = y - arrow_size
            base2_x = x - dx * arrow_size  
            base2_y = y + arrow_size
        else:  # Vertical arrow
            base1_x = x - arrow_size
            base1_y = y - dy * arrow_size
            base2_x = x + arrow_size
            base2_y = y - dy * arrow_size
        
        # Draw arrow as triangle
        points = [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)]
        pygame.draw.polygon(screen, color, points)