import pygame
import random
from particle import Particle

class Grid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        
        # Speed tracking for PSG particles
        self.psg_speed_counter = {}  # Track frame counters for particles in PSG
        
    def is_valid_position(self, x, y):
        """Check if position is within grid bounds"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_empty(self, x, y):
        """Check if position is empty"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] is None
    
    def place_particle(self, particle, x, y):
        """Place particle at position"""
        if self.is_valid_position(x, y):
            self.grid[y][x] = particle
            particle.move_to(x, y)
            return True
        return False
    
    def remove_particle(self, x, y):
        """Remove particle from position"""
        if self.is_valid_position(x, y):
            particle = self.grid[y][x]
            self.grid[y][x] = None
            # Clean up PSG speed tracking if particle is removed
            particle_id = id(particle) if particle else None
            if particle_id in self.psg_speed_counter:
                del self.psg_speed_counter[particle_id]
            return particle
        return None
    
    def get_particle(self, x, y):
        """Get particle at position"""
        if self.is_valid_position(x, y):
            return self.grid[y][x]
        return None
    
    def move_particle(self, from_x, from_y, to_x, to_y):
        """Move particle from one position to another"""
        if not self.is_valid_position(from_x, from_y) or not self.is_valid_position(to_x, to_y):
            return False
        
        if self.grid[from_y][from_x] is None or self.grid[to_y][to_x] is not None:
            return False
        
        particle = self.grid[from_y][from_x]
        self.grid[from_y][from_x] = None
        self.grid[to_y][to_x] = particle
        particle.move_to(to_x, to_y)
        return True
    
    def can_particle_fall(self, x, y):
        """Check if particle can fall down"""
        if not self.is_valid_position(x, y) or self.grid[y][x] is None:
            return False
        
        # Check if can fall straight down
        if y + 1 < self.height and self.is_empty(x, y + 1):
            return True
        
        # Check if can fall diagonally
        directions = []
        if x > 0 and y + 1 < self.height and self.is_empty(x - 1, y + 1):
            directions.append(-1)
        if x < self.width - 1 and y + 1 < self.height and self.is_empty(x + 1, y + 1):
            directions.append(1)
        
        return len(directions) > 0
    
    def should_particle_move_slowly(self, x, y, psg=None):
        """Check if particle should move slowly due to PSG"""
        if psg and psg.should_particle_move_slow(x, y):
            particle = self.get_particle(x, y)
            if particle:
                particle_id = id(particle)
                # Initialize or increment counter for this particle
                if particle_id not in self.psg_speed_counter:
                    self.psg_speed_counter[particle_id] = 0
                self.psg_speed_counter[particle_id] += 1
                
                # Only allow movement every psg.slow_factor frames
                return self.psg_speed_counter[particle_id] % psg.slow_factor == 0
        else:
            # Clean up counter if particle is no longer in PSG
            particle = self.get_particle(x, y)
            if particle:
                particle_id = id(particle)
                if particle_id in self.psg_speed_counter:
                    del self.psg_speed_counter[particle_id]
        
        return True  # Normal speed movement
    
    def update_particle(self, x, y, hotbin=None, coldbin=None, lift=None, separator=None, psg=None):
        """Update single particle physics"""
        if not self.is_valid_position(x, y) or self.grid[y][x] is None:
            return False
        
        # Check if particle should move slowly due to PSG
        if psg and not self.should_particle_move_slowly(x, y, psg):
            return False
        
        # Special handling for particles in lift system
        if lift and lift.is_inside_lift(x, y):
            # Don't apply normal gravity in lift - let lift handle movement
            return False
        
        # Special handling for particles in separator
        if separator and separator.is_inside(x, y):
            # Don't apply normal gravity in separator - let separator handle redistribution
            return False
        
        # Try to fall straight down first
        target_y = y + 1
        
        # Check if particle can enter lift system - allow entry across the full width
        can_enter_lift = False
        if lift and lift.is_inside_lift(x, target_y):
            # Allow entry into lift if it's at the entry level
            entry_x, entry_y = lift.get_entry_position()
            # Check if we're at the right y level and within the shaft width
            if (target_y == entry_y and 
                entry_x <= x < entry_x + lift.shaft_width):
                can_enter_lift = True
        
        # Check if particle can enter separator
        can_enter_separator = False
        if separator and separator.can_enter_separator(x, target_y):
            can_enter_separator = True
        
        if (target_y < self.height and 
            self.is_empty(x, target_y) and 
            (hotbin is None or not hotbin.is_wall(x, target_y)) and
            (coldbin is None or not coldbin.is_wall(x, target_y)) and
            (separator is None or not separator.is_wall(x, target_y) or can_enter_separator) and
            (lift is None or not lift.is_inside_lift(x, target_y) or can_enter_lift)):
            return self.move_particle(x, y, x, target_y)
        
        # Try to fall diagonally
        directions = []
        
        # Check left diagonal
        can_enter_lift_left = False
        if lift and lift.is_inside_lift(x - 1, target_y):
            entry_x, entry_y = lift.get_entry_position()
            if (target_y == entry_y and 
                entry_x <= x - 1 < entry_x + lift.shaft_width):
                can_enter_lift_left = True
        
        can_enter_separator_left = False
        if separator and separator.can_enter_separator(x - 1, target_y):
            can_enter_separator_left = True
                
        if (x > 0 and target_y < self.height and 
            self.is_empty(x - 1, target_y) and 
            (hotbin is None or not hotbin.is_wall(x - 1, target_y)) and
            (coldbin is None or not coldbin.is_wall(x - 1, target_y)) and
            (separator is None or not separator.is_wall(x - 1, target_y) or can_enter_separator_left) and
            (lift is None or not lift.is_inside_lift(x - 1, target_y) or can_enter_lift_left)):
            directions.append(-1)
            
        # Check right diagonal
        can_enter_lift_right = False
        if lift and lift.is_inside_lift(x + 1, target_y):
            entry_x, entry_y = lift.get_entry_position()
            if (target_y == entry_y and 
                entry_x <= x + 1 < entry_x + lift.shaft_width):
                can_enter_lift_right = True
        
        can_enter_separator_right = False
        if separator and separator.can_enter_separator(x + 1, target_y):
            can_enter_separator_right = True
                
        if (x < self.width - 1 and target_y < self.height and 
            self.is_empty(x + 1, target_y) and 
            (hotbin is None or not hotbin.is_wall(x + 1, target_y)) and
            (coldbin is None or not coldbin.is_wall(x + 1, target_y)) and
            (separator is None or not separator.is_wall(x + 1, target_y) or can_enter_separator_right) and
            (lift is None or not lift.is_inside_lift(x + 1, target_y) or can_enter_lift_right)):
            directions.append(1)
        
        if directions:
            direction = random.choice(directions)
            return self.move_particle(x, y, x + direction, target_y)
        
        return False
    
    def draw(self, screen):
        """Draw the particles only (background handled by simulation)"""
        # Draw particles
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] is not None:
                    particle = self.grid[y][x]
                    color = particle.get_color()
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(screen, color, rect)