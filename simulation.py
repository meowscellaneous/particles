import pygame
import random
from grid import Grid
from particle import Particle
from receiver import Receiver
from hotbin import HotBin
from psg import PSG
from coldbin import ColdBin
from lift import Lift
from separator import Separator

class Simulation:
    def __init__(self, screen_width=800, screen_height=900, cell_size=8):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.grid_width = screen_width // cell_size
        self.grid_height = screen_height // cell_size
        
        # Initialize components
        self.grid = Grid(self.grid_width, self.grid_height, cell_size)
        self.receiver = Receiver(self.grid_width, self.grid_height)
        self.separator = Separator(self.receiver.x, self.receiver.y, self.receiver.width)
        self.hotbin = HotBin(self.receiver.x, self.receiver.y, self.receiver.width)
        self.psg = PSG(self.hotbin.x, self.hotbin.y, self.hotbin.width)
        self.coldbin = ColdBin(self.psg.x, self.psg.y, self.psg.width)
        self.lift = Lift(self.coldbin, self.separator.y + self.separator.height)
        
        # Spawning parameters
        self.spawn_count = 0
        self.max_spawn = 1
        self.spawn_delay = 3  # frames between spawns
        self.spawn_timer = 0
        self.spawning_complete = False
        
        # Hot bin opening/closing timer (10 seconds = 600 frames at 60 FPS)
        self.hotbin_timer = 0
        self.hotbin_cycle_duration = 300  # 10 seconds in frames
        
        # Cold bin opening/closing timer (same timing as hot bin)
        self.coldbin_timer = 0
        self.coldbin_cycle_duration = 300  # 10 seconds in frames
        
        # Calculate spawn position (above receiver)
        self.spawn_x = self.receiver.x + self.receiver.width // 2
        self.spawn_y = max(0, self.receiver.y - 3)  # - X cells above receiver
        
        # Frame counter for thermal loss calculations
        self.frame_counter = 0
        
        # Thermal loss rates for different equipment
        self.thermal_loss_rates = {
            'lift': 5,
            'hotbin': 5,
            'coldbin': 5,
            'psg': 5,
            'default': 0  # For particles not in specific equipment
        }
        
        self.running = False
        
    def start(self):
        """Start the simulation"""
        self.running = True
        
    def spawn_particle(self):
        """Spawn a new particle if conditions are met"""
        if (self.spawning_complete or 
            self.spawn_count >= self.max_spawn or 
            self.spawn_timer > 0):
            return
        
        # Try to spawn particle at spawn position
        if self.grid.is_empty(self.spawn_x, self.spawn_y):
            particle = Particle(self.spawn_x, self.spawn_y)
            if self.grid.place_particle(particle, self.spawn_x, self.spawn_y):
                self.spawn_count += 1
                self.spawn_timer = self.spawn_delay
                
                if self.spawn_count >= self.max_spawn:
                    self.spawning_complete = True
    
    def apply_thermal_losses(self):
        """Apply thermal losses to all particles based on their location"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                particle = self.grid.get_particle(x, y)
                if particle is None:
                    continue
                
                # Determine thermal loss rate based on location
                loss_rate = self.thermal_loss_rates['default']
                
                if self.lift.is_inside_lift(x, y):
                    loss_rate = self.thermal_loss_rates['lift']
                elif self.hotbin.is_inside(x, y):
                    loss_rate = self.thermal_loss_rates['hotbin']
                elif self.coldbin.is_inside(x, y):
                    loss_rate = self.thermal_loss_rates['coldbin']
                elif self.psg.is_inside(x, y):
                    loss_rate = self.thermal_loss_rates['psg']
                
                # Apply thermal loss
                particle.apply_thermal_loss(loss_rate, self.frame_counter)
    
    def update_physics(self):
        """Update particle physics for entire grid"""
        # Update lift particles first (special upward movement)
        self.lift.update_particles_in_lift(self.grid)
        
        # Update separator particles (redistribute x positions)
        self.separator.update_particles_in_separator(self.grid)
        
        # Update PSG particles (gradual cooling)
        self.psg.update_particles_in_psg(self.grid)
        
        # Update receiver particles (gradual heating)
        self.receiver.update_particles_in_receiver(self.grid)
        
        # Apply thermal losses to all particles
        self.apply_thermal_losses()
        
        # Update particles from bottom to top, right to left to avoid double updates
        for y in range(self.grid_height - 2, -1, -1):  # Skip bottom row
            for x in range(self.grid_width - 1, -1, -1):
                if self.grid.get_particle(x, y) is not None:
                    # Update particle position (pass all components for collision detection)
                    # Note: We pass PSG to enable speed reduction
                    self.grid.update_particle(x, y, self.hotbin, self.coldbin, self.lift, self.separator, self.psg)
    
    def update(self):
        """Update simulation state"""
        if not self.running:
            return
            
        # Increment frame counter
        self.frame_counter += 1
            
        # Update spawn timer
        if self.spawn_timer > 0:
            self.spawn_timer -= 1
            
        # Try to spawn new particle
        self.spawn_particle()
        
        # Update hot bin opening/closing cycle
        self.hotbin_timer += 1
        if self.hotbin_timer >= self.hotbin_cycle_duration * 2:  # Full cycle (open + closed)
            self.hotbin_timer = 0
            
        # Determine if hot bin should be open or closed
        # First 10 seconds (0-599): closed
        # Next 10 seconds (600-1199): open
        if self.hotbin_timer < self.hotbin_cycle_duration:
            self.hotbin.close_bin()
        else:
            self.hotbin.open_bin()
            
        # Update cold bin opening/closing cycle
        self.coldbin_timer += 1
        if self.coldbin_timer >= self.coldbin_cycle_duration * 2:  # Full cycle (open + closed)
            self.coldbin_timer = 0
            
        # Determine if cold bin should be open or closed
        if self.coldbin_timer < self.coldbin_cycle_duration:
            self.coldbin.close_bin()
        else:
            self.coldbin.open_bin()
        
        # Update physics
        self.update_physics()
    
    def draw(self, screen):
        """Draw the entire simulation"""
        # Fill background
        screen.fill((50, 50, 50))
        
        # Draw lift system first (as background)
        self.lift.draw(screen, self.cell_size)
        
        # Draw other components
        self.coldbin.draw(screen, self.cell_size)
        self.psg.draw(screen, self.cell_size)
        self.separator.draw(screen, self.cell_size)
        self.hotbin.draw(screen, self.cell_size)
        self.receiver.draw(screen, self.cell_size)
        
        # Draw particles on top of everything
        self.grid.draw(screen)
        
        # Draw spawn indicator (small circle above spawn point)
        if not self.spawning_complete:
            spawn_screen_x = self.spawn_x * self.cell_size + self.cell_size // 2
            spawn_screen_y = self.spawn_y * self.cell_size + self.cell_size // 2
            pygame.draw.circle(screen, (255, 255, 255), 
                             (spawn_screen_x, spawn_screen_y), 3)
    
    def get_stats(self):
        """Get simulation statistics"""
        # Calculate time remaining in current cycle for hot bin
        hotbin_cycle_position = self.hotbin_timer % (self.hotbin_cycle_duration * 2)
        if hotbin_cycle_position < self.hotbin_cycle_duration:
            # Currently closed
            time_remaining = (self.hotbin_cycle_duration - hotbin_cycle_position) // 60
            hotbin_status = f"Closed (opens in {time_remaining}s)"
        else:
            # Currently open
            time_remaining = (self.hotbin_cycle_duration * 2 - hotbin_cycle_position) // 60
            hotbin_status = f"Open (closes in {time_remaining}s)"
        
        # Calculate time remaining in current cycle for cold bin
        coldbin_cycle_position = self.coldbin_timer % (self.coldbin_cycle_duration * 2)
        if coldbin_cycle_position < self.coldbin_cycle_duration:
            # Currently closed
            time_remaining = (self.coldbin_cycle_duration - coldbin_cycle_position) // 60
            coldbin_status = f"Closed (opens in {time_remaining}s)"
        else:
            # Currently open
            time_remaining = (self.coldbin_cycle_duration * 2 - coldbin_cycle_position) // 60
            coldbin_status = f"Open (closes in {time_remaining}s)"
        
        # Get lift conservation stats
        lift_stats = self.lift.get_conservation_stats()
        
        # Get PSG and receiver stats
        psg_stats = self.psg.get_stats()
        receiver_stats = self.receiver.get_stats()
            
        return {
            'spawned': self.spawn_count,
            'max_spawn': self.max_spawn,
            'spawning_complete': self.spawning_complete,
            'hotbin_status': hotbin_status,
            'coldbin_status': coldbin_status,
            'lift_entered': lift_stats['entered'],
            'lift_exited': lift_stats['exited'],
            'lift_in_transit': lift_stats['in_lift'],
            'psg_heat_extracted': psg_stats['total_heat_extracted'],
            'receiver_heat_added': receiver_stats['total_heat_added']
        }