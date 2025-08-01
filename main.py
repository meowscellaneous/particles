import pygame
import sys
from simulation import Simulation

def main():
    # Initialize Pygame
    pygame.init()
    
    # Constants
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    CELL_SIZE = 8
    FPS = 60
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sand Particle Simulation")
    clock = pygame.time.Clock()
    
    # Initialize simulation
    simulation = Simulation(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE)
    
    # Set up font for UI
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Game state
    started = False
    
    print("Sand Particle Simulation")
    print("Press SPACE to start the simulation")
    print("Press ESC or close window to quit")
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    simulation.start()
                    started = True
                    print("Simulation started!")
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update simulation
        if started:
            simulation.update()
        
        # Draw everything
        simulation.draw(screen)
        
        # Draw UI
        if not started:
            # Start instruction
            text = font.render("Press SPACE to start", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(text, text_rect)
        else:
            # Show stats
            stats = simulation.get_stats()
            stats_text = small_font.render(
                f"Spawned: {stats['spawned']}/{stats['max_spawn']}", 
                True, (255, 255, 255)
            )
            screen.blit(stats_text, (10, 10))
            
            # Show hot bin status
            hotbin_text = small_font.render(
                f"Hot Bin: {stats['hotbin_status']}", 
                True, (255, 255, 255)
            )
            screen.blit(hotbin_text, (10, 35))
            
            # Show cold bin status
            coldbin_text = small_font.render(
                f"Cold Bin: {stats['coldbin_status']}", 
                True, (255, 255, 255)
            )
            screen.blit(coldbin_text, (10, 60))
            
            # Show lift conservation stats
            lift_text = small_font.render(
                f"Lift: In={stats['lift_entered']} Out={stats['lift_exited']} Transit={stats['lift_in_transit']}", 
                True, (255, 255, 255)
            )
            screen.blit(lift_text, (10, 85))
            
            if stats['spawning_complete']:
                complete_text = small_font.render(
                    "Spawning complete - particles cycling!", 
                    True, (0, 255, 0)
                )
                screen.blit(complete_text, (10, 110))
        
        # Draw instructions
        instructions = [
            "Complete cycle: Heat → Cool → Lift → Repeat",
            "Gray lift transports particles upward",
            "Both bins open/close every 10 seconds",
            "Lift conservation: particles in = particles out"
        ]
        
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (10, SCREEN_HEIGHT - 100 + i * 20))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()