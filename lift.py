import pygame

class Lift:
    def __init__(self, coldbin, receiver_y):
        self.coldbin_bounds = coldbin.get_bin_bounds()
        self.receiver_y = receiver_y
        
        # Lift dimensions
        self.shaft_width = 5  # Width of vertical shaft
        self.thickness = 0   # Wall thickness
        
        # Vertical cold bin shaft (connects to bottom of cold bin)
        #self.cb_shaft_x = (self.coldbin_bounds['right'] - self.coldbin_bounds['left']) // 2 + self.coldbin_bounds['left']  # Start at right edge of cold bin
        self.cb_shaft_x = coldbin.opening_start_x  # Start at right edge of cold bin
        self.cb_shaft_y = self.coldbin_bounds['inner_bottom']  # Bottom of cold bin
        self.cb_shaft_height = 5  # Height of vertical section
        
        # Horizontal cold bin shaft (elbow going right connecting to main length)
        self.cb_hz_shaft_x = self.cb_shaft_x
        self.cb_hz_shaft_y = self.cb_shaft_y + self.cb_shaft_height
        self.cb_hz_shaft_length = self.coldbin_bounds['right'] - self.coldbin_bounds['left']

        # Vertical main shaft
        self.main_shaft_x = self.cb_hz_shaft_x + self.cb_hz_shaft_length
        self.main_shaft_y = self.receiver_y - 15 # offset of 15 above receiver
        self.main_shaft_height = (self.cb_hz_shaft_y 
                                     + (self.shaft_width + 2 * self.thickness)
                                     - self.main_shaft_y)

        # Horizontal receiver shaft
        self.rcv_hz_shaft_x = self.cb_shaft_x
        self.rcv_hz_shaft_y = self.main_shaft_y
        self.rcv_hz_shaft_length = self.main_shaft_x - self.cb_shaft_x

        # Vertical receiver shaft
        self.rcv_vt_shaft_x = self.rcv_hz_shaft_x
        self.rcv_vt_shaft_y = self.rcv_hz_shaft_y + (self.shaft_width + 2 * self.thickness)
        self.rcv_vt_shaft_height = 5
        
        # Particle movement speed (cells per update)
        self.lift_speed = 0.3  # Slower than gravity for realistic movement
        self.frame_counter = 0
        
    def is_wall(self, x, y):
        """Check if position is a wall of the lift system - since we don't draw walls, return False"""
        return False
    
    def is_inside_lift(self, x, y):
        """Check if position is inside any part of the lift system"""
        return (self.is_inside_cb_vertical(x, y) or 
                self.is_inside_cb_horizontal(x, y) or 
                self.is_inside_main_vertical(x, y) or
                self.is_inside_rcv_horizontal(x, y) or
                self.is_inside_rcv_vertical(x, y))
    
    def is_inside_cb_vertical(self, x, y):
        """Check if position is inside the vertical shaft going down from cold bin"""
        return (self.cb_shaft_x <= x <= self.cb_shaft_x + self.shaft_width and
                self.cb_shaft_y <= y < self.cb_shaft_y + self.cb_shaft_height)
    
    def is_inside_cb_horizontal(self, x, y):
        """Check if position is inside the horizontal section going right"""
        return (self.cb_hz_shaft_x <= x < self.cb_hz_shaft_x + self.cb_hz_shaft_length and
                self.cb_hz_shaft_y <= y < self.cb_hz_shaft_y + self.shaft_width)
    
    def is_inside_main_vertical(self, x, y):
        """Check if position is inside the main vertical shaft going up"""
        return (self.main_shaft_x <= x < self.main_shaft_x + self.shaft_width and
                self.main_shaft_y <= y < self.main_shaft_y + self.main_shaft_height)
    
    def is_inside_rcv_horizontal(self, x, y):
        """Check if position is inside the horizontal section going left to receiver"""
        return (self.rcv_hz_shaft_x <= x < self.rcv_hz_shaft_x + self.rcv_hz_shaft_length and
                self.rcv_hz_shaft_y <= y < self.rcv_hz_shaft_y + self.shaft_width)
    
    def is_inside_rcv_vertical(self, x, y):
        """Check if position is inside the vertical section going down to receiver"""
        return (self.rcv_vt_shaft_x <= x < self.rcv_vt_shaft_x + self.shaft_width and
                self.rcv_vt_shaft_y <= y < self.rcv_vt_shaft_y + self.rcv_vt_shaft_height)
    
    def get_entry_position(self):
        """Get the position where particles enter the lift (top of cb vertical shaft)"""
        return (self.cb_shaft_x, self.cb_shaft_y)
    
    def can_enter_lift(self, x, y):
        return (self.cb_shaft_x <= x <= self.cb_shaft_x + self.shaft_width and
                y == self.cb_shaft_y) # <= or <
    
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
                if particle and self.is_inside_lift(x, y):
                    particles_to_move.append((x, y, particle))
        
        # Process particle movements (in reverse order to avoid conflicts)
        # Sort by segment priority: exit first, then work backwards
        particles_to_move.sort(key=lambda p: self._get_movement_priority(p[0], p[1]), reverse=True)
        
        for x, y, particle in particles_to_move:
            new_x, new_y = self._get_next_position(x, y)
            
            if new_x is not None and new_y is not None:
                # Check if destination is valid and empty
                if (grid.is_valid_position(new_x, new_y) and 
                    grid.is_empty(new_x, new_y)):
                    grid.move_particle(x, y, new_x, new_y)
                # If destination is blocked but we're trying to exit, try adjacent positions
                elif self.is_inside_rcv_vertical(x, y) and y >= self.rcv_vt_shaft_y + self.rcv_vt_shaft_height - 1:
                    # Try to exit to adjacent positions
                    for dx in [-1, 0, 1]:
                        exit_x, exit_y = new_x + dx, new_y
                        if (grid.is_valid_position(exit_x, exit_y) and 
                            grid.is_empty(exit_x, exit_y) and
                            not self.is_inside_lift(exit_x, exit_y)):
                            grid.move_particle(x, y, exit_x, exit_y)
                            break
    
    def _get_movement_priority(self, x, y):
        """Get movement priority - higher numbers move first"""
        if self.is_inside_rcv_vertical(x, y):
            return 5  # Exit particles first
        elif self.is_inside_rcv_horizontal(x, y):
            return 4
        elif self.is_inside_main_vertical(x, y):
            return 3
        elif self.is_inside_cb_horizontal(x, y):
            return 2
        elif self.is_inside_cb_vertical(x, y):
            return 1
        return 0
    
    def _get_next_position(self, x, y):
        """Calculate next position for particle in lift based on which segment it's in"""
        
        # Segment 1: Vertical down from cold bin
        if self.is_inside_cb_vertical(x, y):
            # Move down until we reach the bottom of this segment
            if y < self.cb_shaft_y + self.cb_shaft_height - 1:
                return x, y + 1
            else:
                # Transition to horizontal segment - maintain x position within shaft bounds
                # Map from vertical shaft position to horizontal shaft position
                horizontal_x = self.cb_hz_shaft_x + (x - self.cb_shaft_x)
                return horizontal_x, self.cb_hz_shaft_y
        
        # Segment 2: Horizontal right
        elif self.is_inside_cb_horizontal(x, y):
            # Move right until we reach the end of this segment
            if x < self.cb_hz_shaft_x + self.cb_hz_shaft_length - 1:
                return x + 1, y
            else:
                # Transition to main vertical segment - map to main shaft
                # Map y position in horizontal shaft to x position in main shaft
                main_shaft_x = self.main_shaft_x + (y - self.cb_hz_shaft_y)
                return main_shaft_x, self.main_shaft_y + self.main_shaft_height - 1
        
        # Segment 3: Vertical up (main shaft)
        elif self.is_inside_main_vertical(x, y):
            # Move up until we reach the top of this segment
            if y > self.main_shaft_y:
                return x, y - 1
            else:
                # Transition to receiver horizontal segment
                # Map x position in main shaft to y position in horizontal shaft
                horizontal_y = self.rcv_hz_shaft_y + (x - self.main_shaft_x)
                return self.rcv_hz_shaft_x + self.rcv_hz_shaft_length - 1, horizontal_y
        
        # Segment 4: Horizontal left to receiver
        elif self.is_inside_rcv_horizontal(x, y):
            # Move left until we reach the receiver vertical shaft
            if x > self.rcv_hz_shaft_x:
                return x - 1, y
            else:
                # Transition to receiver vertical segment
                # Map y position in horizontal shaft to x position in vertical shaft
                vertical_x = self.rcv_vt_shaft_x + (y - self.rcv_hz_shaft_y)
                return vertical_x, self.rcv_vt_shaft_y
       
        # Segment 5: Vertical down to receiver
        elif self.is_inside_rcv_vertical(x, y):
            # Move down until we exit the lift system
            if y < self.rcv_vt_shaft_y + self.rcv_vt_shaft_height - 1:
                return x, y + 1
            else:
                # Exit the lift system - particle will fall normally
                return x, y + 1
        
        return None, None
    
    def draw(self, screen, cell_size):
        """Draw the lift system"""
        wall_color = (128, 128, 128)  # Gray for lift structure
        
        # Vertical shaft connected to cold bin
        shaft_rect = pygame.Rect(
            self.cb_shaft_x * cell_size,
            self.cb_shaft_y * cell_size,
            (self.shaft_width + 2 * self.thickness) * cell_size,
            self.cb_shaft_height * cell_size
        )
        pygame.draw.rect(screen, wall_color, shaft_rect)
        
        # Horizontal shaft connecting to cold bin
        cb_hz_rect = pygame.Rect(
            self.cb_hz_shaft_x * cell_size,
            self.cb_hz_shaft_y * cell_size,
            self.cb_hz_shaft_length * cell_size,
            (self.shaft_width + 2 * self.thickness) * cell_size
        )
        pygame.draw.rect(screen, wall_color, cb_hz_rect)
        
        main_shaft_rect = pygame.Rect(
            self.main_shaft_x * cell_size,
            self.main_shaft_y * cell_size,
            (self.shaft_width + 2 * self.thickness) * cell_size,
            self.main_shaft_height * cell_size
        )
        pygame.draw.rect(screen, wall_color, main_shaft_rect)

        # Horizontal shaft connecting to receiver
        rcv_hz_rect = pygame.Rect(
            self.rcv_hz_shaft_x * cell_size,
            self.rcv_hz_shaft_y * cell_size,
            self.rcv_hz_shaft_length * cell_size,
            (self.shaft_width + 2 * self.thickness) * cell_size
        )
        pygame.draw.rect(screen, wall_color, rcv_hz_rect)

        # Vertical shaft connecting to receiver
        rcv_vt_rect = pygame.Rect(
            self.rcv_vt_shaft_x * cell_size,
            self.rcv_vt_shaft_y * cell_size,
            (self.shaft_width + 2 * self.thickness) * cell_size,
            self.rcv_vt_shaft_height * cell_size
        )
        pygame.draw.rect(screen, wall_color, rcv_vt_rect)