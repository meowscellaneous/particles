import pygame

class PSG:
    def __init__(self, hotbin_x, hotbin_y, hotbin_width):
        self.width = hotbin_width  # Width of PSG in grid cells
        self.height = 5  # Height of PSG in grid cells
        
        # Position PSG underneath the hot bin, centered
        self.x = hotbin_x + (hotbin_width - self.width) // 2
        self.y = hotbin_y + 8 + 6  # 2 cells below hot bin
        
        # Cooling parameters
        self.cooling_rate = 20  # Heat removed per time unit
        self.cooling_interval = 1  # frames between cooling applications
        self.frame_counter = 0
        
        # Statistics tracking
        self.total_heat_extracted = 0
        
        # Speed reduction parameters
        self.slow_factor = 5  # Particles move 5x slower in PSG
        
    def is_inside(self, x, y):
        """Check if position is inside the PSG"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def should_particle_move_slow(self, x, y):
        """Check if particle at position should move slowly"""
        return self.is_inside(x, y)
    
    def update_particles_in_psg(self, grid):
        """Update cooling for particles inside the PSG"""
        self.frame_counter += 1
        
        # Only apply cooling every cooling_interval frames
        if self.frame_counter % self.cooling_interval != 0:
            return
        
        # Find all particles inside the PSG and cool them
        for y in range(self.y, self.y + self.height):
            for x in range(self.x, self.x + self.width):
                particle = grid.get_particle(x, y)
                if particle and self.is_inside(x, y):
                    # Calculate heat to remove (don't go below 0)
                    heat_to_remove = min(self.cooling_rate, particle.temperature)
                    particle.temperature = max(0, particle.temperature - heat_to_remove)
                    self.total_heat_extracted += heat_to_remove
    
    def cool_particle(self, particle):
        """Legacy method - now handled by update_particles_in_psg"""
        # Keep this for backwards compatibility but don't do anything
        pass
    
    def get_stats(self):
        """Return PSG statistics"""
        return {
            'total_heat_extracted': self.total_heat_extracted
        }
    
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