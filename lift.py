import pygame

class Lift:
    def __init__(self, coldbin, receiver_y):
        self.coldbin_bounds = coldbin.get_bin_bounds()
        self.receiver_y = receiver_y
        
        # Lift dimensions
        self.shaft_width = 5  # Width of vertical shaft
        
        # Vertical cold bin shaft (connects to bottom of cold bin)
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
                                     + self.shaft_width
                                     - self.main_shaft_y)

        # Horizontal receiver shaft
        self.rcv_hz_shaft_x = self.cb_shaft_x
        self.rcv_hz_shaft_y = self.main_shaft_y
        self.rcv_hz_shaft_length = self.main_shaft_x - self.cb_shaft_x

        # Vertical receiver shaft
        self.rcv_vt_shaft_x = self.rcv_hz_shaft_x
        self.rcv_vt_shaft_y = self.rcv_hz_shaft_y + self.shaft_width
        self.rcv_vt_shaft_height = 5
        
        # Particle movement speed (cells per update)
        self.lift_speed = 0.3  # Slower than gravity for realistic movement
        self.frame_counter = 0
        
        # Particle conservation tracking
        self.particles_entered = 0
        self.particles_exited = 0
        
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
        return (self.cb_shaft_x <= x < self.cb_shaft_x + self.shaft_width and
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
        return (self.cb_shaft_x <= x < self.cb_shaft_x + self.shaft_width and
                y == self.cb_shaft_y)
    
    def update_particles_in_lift(self, grid):
        """Update particles moving through the lift system with multi-file support"""
        self.frame_counter += 1
        
        # Only move particles every few frames to control speed
        if self.frame_counter % max(1, int(1 / self.lift_speed)) != 0:
            return
        
        # Track particles entering the lift (at entry point)
        entry_x, entry_y = self.get_entry_position()
        for x in range(entry_x, entry_x + self.shaft_width):
            if (grid.is_valid_position(x, entry_y) and 
                grid.get_particle(x, entry_y) is not None and
                not hasattr(grid.get_particle(x, entry_y), '_just_entered_lift')):
                # Mark particle as just entered to avoid double counting
                grid.get_particle(x, entry_y)._just_entered_lift = True
                self.particles_entered += 1
        
        particles_to_move = []
        # Find all particles in lift system
        for y in range(grid.height):
            for x in range(grid.width):
                particle = grid.get_particle(x, y)
                if particle and self.is_inside_lift(x, y):
                    # Clear the entry marker after first frame
                    if hasattr(particle, '_just_entered_lift'):
                        delattr(particle, '_just_entered_lift')
                    particles_to_move.append((x, y, particle))
        
        # Group particles by segment and process each segment separately
        # This allows multiple particles to move in parallel within each segment
        segments = {
            'cb_vertical': [],
            'cb_horizontal': [],
            'main_vertical': [],
            'rcv_horizontal': [],
            'rcv_vertical': []
        }
        
        # Classify particles by segment
        for x, y, particle in particles_to_move:
            if self.is_inside_cb_vertical(x, y):
                segments['cb_vertical'].append((x, y, particle))
            elif self.is_inside_cb_horizontal(x, y):
                segments['cb_horizontal'].append((x, y, particle))
            elif self.is_inside_main_vertical(x, y):
                segments['main_vertical'].append((x, y, particle))
            elif self.is_inside_rcv_horizontal(x, y):
                segments['rcv_horizontal'].append((x, y, particle))
            elif self.is_inside_rcv_vertical(x, y):
                segments['rcv_vertical'].append((x, y, particle))
        
        # Process each segment in reverse order (exit first)
        segment_order = ['rcv_vertical', 'rcv_horizontal', 'main_vertical', 'cb_horizontal', 'cb_vertical']
        
        for segment_name in segment_order:
            particles = segments[segment_name]
            self._process_segment_particles(grid, particles, segment_name)
    
    def _process_segment_particles(self, grid, particles, segment_name):
        """Process all particles in a specific segment ensuring no particles are lost"""
        # Sort particles by their position to avoid conflicts
        if segment_name == 'cb_vertical':
            # Sort by y descending (bottom particles move first)
            particles.sort(key=lambda p: p[1], reverse=True)
        elif segment_name == 'cb_horizontal':
            # Sort by x descending (rightmost particles move first)
            particles.sort(key=lambda p: p[0], reverse=True)
        elif segment_name == 'main_vertical':
            # Sort by y ascending (top particles move first)
            particles.sort(key=lambda p: p[1])
        elif segment_name == 'rcv_horizontal':
            # Sort by x ascending (leftmost particles move first)
            particles.sort(key=lambda p: p[0])
        elif segment_name == 'rcv_vertical':
            # Sort by y descending (bottom particles move first)
            particles.sort(key=lambda p: p[1], reverse=True)
        
        # Track which destinations are already claimed this frame to prevent conflicts
        claimed_positions = set()
        
        for x, y, particle in particles:
            next_positions = self._get_next_positions(x, y, segment_name)
            
            # Try each possible next position, avoiding already claimed positions
            moved = False
            for new_x, new_y in next_positions:
                if (new_x is not None and new_y is not None and 
                    (new_x, new_y) not in claimed_positions):
                    # Check if destination is valid and empty
                    if (grid.is_valid_position(new_x, new_y) and 
                        grid.is_empty(new_x, new_y)):
                        grid.move_particle(x, y, new_x, new_y)
                        claimed_positions.add((new_x, new_y))
                        moved = True
                        break
            
            # Special handling for particles trying to exit the lift
            if not moved and segment_name == 'rcv_vertical':
                # Try to exit to adjacent positions if blocked, but only if at exit point
                if y >= self.rcv_vt_shaft_y + self.rcv_vt_shaft_height - 1:
                    exit_positions = self._get_exit_positions(x, y)
                    for exit_x, exit_y in exit_positions:
                        if ((exit_x, exit_y) not in claimed_positions and
                            grid.is_valid_position(exit_x, exit_y) and 
                            grid.is_empty(exit_x, exit_y) and
                            not self.is_inside_lift(exit_x, exit_y)):
                            grid.move_particle(x, y, exit_x, exit_y)
                            claimed_positions.add((exit_x, exit_y))
                            moved = True
                            # Track particles exiting the lift
                            self.particles_exited += 1
                            break
            
            # If particle moved to a position outside the lift system, count as exit
            elif moved and segment_name == 'rcv_vertical':
                new_x, new_y = next_positions[0]  # Get the position it moved to
                if (new_x is not None and new_y is not None and 
                    not self.is_inside_lift(new_x, new_y)):
                    self.particles_exited += 1
            
            # If particle still can't move and is at a transition point, 
            # it will wait until next frame - this prevents particle loss
    
    def _get_next_positions(self, x, y, segment_name):
        """Get possible next positions for a particle based on its current segment"""
        positions = []
        
        if segment_name == 'cb_vertical':
            # Move down until we reach the bottom of this segment
            if y < self.cb_shaft_y + self.cb_shaft_height - 1:
                positions.append((x, y + 1))
            else:
                # Transition to horizontal segment - maintain relative position within shaft
                relative_x = x - self.cb_shaft_x
                horizontal_x = self.cb_hz_shaft_x + relative_x
                # Ensure we stay within bounds of horizontal segment
                if (self.cb_hz_shaft_x <= horizontal_x < 
                    self.cb_hz_shaft_x + min(self.cb_hz_shaft_length, self.shaft_width)):
                    positions.append((horizontal_x, self.cb_hz_shaft_y))
                # If primary position is not available, try adjacent positions
                else:
                    # Try center positions in horizontal segment
                    for offset in range(min(self.cb_hz_shaft_length, self.shaft_width)):
                        alt_x = self.cb_hz_shaft_x + offset
                        positions.append((alt_x, self.cb_hz_shaft_y))
        
        elif segment_name == 'cb_horizontal':
            # Move right until we reach the end of this segment
            if x < self.cb_hz_shaft_x + self.cb_hz_shaft_length - 1:
                positions.append((x + 1, y))
            else:
                # Transition to main vertical segment
                relative_y = y - self.cb_hz_shaft_y
                main_shaft_x = self.main_shaft_x + relative_y
                # Ensure we stay within bounds of main vertical segment
                if (self.main_shaft_x <= main_shaft_x < 
                    self.main_shaft_x + self.shaft_width):
                    positions.append((main_shaft_x, self.main_shaft_y + self.main_shaft_height - 1))
                # If primary position is not available, try adjacent positions
                else:
                    # Try center positions in main vertical segment
                    for offset in range(self.shaft_width):
                        alt_x = self.main_shaft_x + offset
                        positions.append((alt_x, self.main_shaft_y + self.main_shaft_height - 1))
        
        elif segment_name == 'main_vertical':
            # Move up until we reach the top of this segment
            if y > self.main_shaft_y:
                positions.append((x, y - 1))
            else:
                # Transition to receiver horizontal segment
                relative_x = x - self.main_shaft_x
                horizontal_y = self.rcv_hz_shaft_y + relative_x
                # Ensure we stay within bounds of horizontal segment
                if (self.rcv_hz_shaft_y <= horizontal_y < 
                    self.rcv_hz_shaft_y + self.shaft_width):
                    positions.append((self.rcv_hz_shaft_x + self.rcv_hz_shaft_length - 1, horizontal_y))
                # If primary position is not available, try adjacent positions
                else:
                    # Try center positions in horizontal segment
                    for offset in range(self.shaft_width):
                        alt_y = self.rcv_hz_shaft_y + offset
                        positions.append((self.rcv_hz_shaft_x + self.rcv_hz_shaft_length - 1, alt_y))
        
        elif segment_name == 'rcv_horizontal':
            # Move left until we reach the receiver vertical shaft
            if x > self.rcv_hz_shaft_x:
                positions.append((x - 1, y))
            else:
                # Transition to receiver vertical segment
                relative_y = y - self.rcv_hz_shaft_y
                vertical_x = self.rcv_vt_shaft_x + relative_y
                # Ensure we stay within bounds of vertical segment
                if (self.rcv_vt_shaft_x <= vertical_x < 
                    self.rcv_vt_shaft_x + self.shaft_width):
                    positions.append((vertical_x, self.rcv_vt_shaft_y))
                # If primary position is not available, try adjacent positions
                else:
                    # Try center positions in vertical segment
                    for offset in range(self.shaft_width):
                        alt_x = self.rcv_vt_shaft_x + offset
                        positions.append((alt_x, self.rcv_vt_shaft_y))
        
        elif segment_name == 'rcv_vertical':
            # Move down until we exit the lift system
            if y < self.rcv_vt_shaft_y + self.rcv_vt_shaft_height - 1:
                positions.append((x, y + 1))
            else:
                # Exit the lift system - particle will fall normally
                positions.append((x, y + 1))
        
        return positions
    
    def _get_exit_positions(self, x, y):
        """Get possible exit positions when particle is blocked at lift exit"""
        positions = []
        # Try center, left, then right
        for dx in [0, -1, 1]:
            exit_x = x + dx
            exit_y = y + 1
            positions.append((exit_x, exit_y))
        return positions
    
    def get_conservation_stats(self):
        """Get particle conservation statistics"""
        return {
            'entered': self.particles_entered,
            'exited': self.particles_exited,
            'in_lift': self.particles_entered - self.particles_exited
        }
    
    def draw(self, screen, cell_size):
        """Draw the lift system"""
        wall_color = (128, 128, 128)  # Gray for lift structure
        
        # Vertical shaft connected to cold bin
        shaft_rect = pygame.Rect(
            self.cb_shaft_x * cell_size,
            self.cb_shaft_y * cell_size,
            self.shaft_width * cell_size,
            self.cb_shaft_height * cell_size
        )
        pygame.draw.rect(screen, wall_color, shaft_rect)
        
        # Horizontal shaft connecting to cold bin
        cb_hz_rect = pygame.Rect(
            self.cb_hz_shaft_x * cell_size,
            self.cb_hz_shaft_y * cell_size,
            self.cb_hz_shaft_length * cell_size,
            self.shaft_width * cell_size
        )
        pygame.draw.rect(screen, wall_color, cb_hz_rect)
        
        main_shaft_rect = pygame.Rect(
            self.main_shaft_x * cell_size,
            self.main_shaft_y * cell_size,
            self.shaft_width * cell_size,
            self.main_shaft_height * cell_size
        )
        pygame.draw.rect(screen, wall_color, main_shaft_rect)

        # Horizontal shaft connecting to receiver
        rcv_hz_rect = pygame.Rect(
            self.rcv_hz_shaft_x * cell_size,
            self.rcv_hz_shaft_y * cell_size,
            self.rcv_hz_shaft_length * cell_size,
            self.shaft_width * cell_size
        )
        pygame.draw.rect(screen, wall_color, rcv_hz_rect)

        # Vertical shaft connecting to receiver
        rcv_vt_rect = pygame.Rect(
            self.rcv_vt_shaft_x * cell_size,
            self.rcv_vt_shaft_y * cell_size,
            self.shaft_width * cell_size,
            self.rcv_vt_shaft_height * cell_size
        )
        pygame.draw.rect(screen, wall_color, rcv_vt_rect)