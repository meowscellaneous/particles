import pygame

class Receiver:
    def __init__(self, grid_width, grid_height):
        self.width = 10  # Width of receiver in grid cells
        self.height = 1  # Height of receiver in grid cells
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Position receiver in center of grid
        self.x = (grid_width - self.width) // 2
        self.y = 22
        
        # Heating parameters
        self.heating_rate = 500  # Heat added per time unit
        self.heating_interval = 1  # frames between heating applications
        self.frame_counter = 0
        
        # Statistics tracking
        self.total_heat_added = 0
        
    def is_inside(self, x, y):
        """Check if position is inside the receiver"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def update_particles_in_receiver(self, grid):
        """Update heating for particles inside the receiver"""
        self.frame_counter += 1
        
        # Only apply heating every heating_interval frames
        if self.frame_counter % self.heating_interval != 0:
            return
        
        # Find all particles inside the receiver and heat them
        for y in range(self.y, self.y + self.height):
            for x in range(self.x, self.x + self.width):
                particle = grid.get_particle(x, y)
                if particle and self.is_inside(x, y):
                    # Calculate heat to add (don't exceed max temperature)
                    heat_to_add = min(self.heating_rate, particle.max_temperature - particle.temperature)
                    particle.temperature = min(particle.max_temperature, particle.temperature + heat_to_add)
                    self.total_heat_added += heat_to_add
    
    def heat_particle(self, particle):
        """Legacy method - now handled by update_particles_in_receiver"""
        # Keep this for backwards compatibility but don't do anything
        pass
    
    def get_stats(self):
        """Return receiver statistics"""
        return {
            'total_heat_added': self.total_heat_added
        }
    
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