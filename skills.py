import pygame

class Skills:
    def __init__(self):
        self.mining_level = 1
        self.mining_xp = 0
        self.smithing_level = 1
        self.smithing_xp = 0
        self.is_open = False  # For skills menu
        
        # XP required for each level (index is level - 1)
        self.xp_requirements = [100]  # Level 1->2 needs 100 XP
        for i in range(98):  # Generate requirements up to level 99
            last_req = self.xp_requirements[-1]
            self.xp_requirements.append(int(last_req * 1.1))  # 10% more XP each level
    
    def toggle(self):
        self.is_open = not self.is_open
        print(f"Skills menu {'opened' if self.is_open else 'closed'}")
    
    def add_mining_xp(self, xp):
        self.mining_xp += xp
        self.check_mining_level_up()
        
    def add_smithing_xp(self, xp):
        self.smithing_xp += xp
        self.check_smithing_level_up()
        
    def check_mining_level_up(self):
        # Check for level up
        while (self.mining_level - 1) < len(self.xp_requirements) and \
              self.mining_xp >= self.xp_requirements[self.mining_level - 1]:
            self.mining_level += 1
            print(f"Mining level up! Now level {self.mining_level}")
    
    def check_smithing_level_up(self):
        next_level = self.smithing_level + 1
        xp_needed = next_level * 100  # Simple XP curve
        
        if self.smithing_xp >= xp_needed:
            self.smithing_level += 1
            print(f"Smithing level up! Now level {self.smithing_level}")
    
    def draw(self, screen):
        if not self.is_open:
            return
            
        # Draw skills menu (similar to inventory menu)
        padding = 10
        width = 200
        height = 300
        
        # Center on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Draw background
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        
        # Draw mining skill info
        font = pygame.font.Font(None, 36)
        mining_text = f"Mining: {self.mining_level}"
        text_surface = font.render(mining_text, True, (255, 255, 255))
        screen.blit(text_surface, (x + padding, y + padding))
        
        # Draw XP bar
        xp_bar_width = width - (padding * 2)
        xp_bar_height = 20
        xp_bar_y = y + padding + 30
        
        # Background bar (total)
        pygame.draw.rect(screen, (50, 50, 50),
                        (x + padding, xp_bar_y, xp_bar_width, xp_bar_height))
        
        # Progress bar
        if self.mining_level < len(self.xp_requirements):
            xp_needed = self.xp_requirements[self.mining_level - 1]
            progress = min(1.0, self.mining_xp / xp_needed)
            progress_width = int(xp_bar_width * progress)
            pygame.draw.rect(screen, (0, 255, 0),
                           (x + padding, xp_bar_y, progress_width, xp_bar_height))
        
        # Draw smithing skill info
        smithing_text = f"Smithing: {self.smithing_level}"
        text_surface = font.render(smithing_text, True, (255, 255, 255))
        screen.blit(text_surface, (x + padding, y + padding + 50))
        
        # Draw smithing XP bar
        smithing_xp_bar_width = width - (padding * 2)
        smithing_xp_bar_height = 20
        smithing_xp_bar_y = y + padding + 80
        
        # Background bar (total)
        pygame.draw.rect(screen, (50, 50, 50),
                        (x + padding, smithing_xp_bar_y, smithing_xp_bar_width, smithing_xp_bar_height))
        
        # Progress bar
        if self.smithing_level < len(self.xp_requirements):
            smithing_xp_needed = self.xp_requirements[self.smithing_level - 1]
            smithing_progress = min(1.0, self.smithing_xp / smithing_xp_needed)
            smithing_progress_width = int(smithing_xp_bar_width * smithing_progress)
            pygame.draw.rect(screen, (0, 255, 0),
                           (x + padding, smithing_xp_bar_y, smithing_progress_width, smithing_xp_bar_height))
    
    def handle_click(self, mouse_pos):
        if not self.is_open:
            return False
        
        # Calculate skills window dimensions and position
        padding = 10
        width = 300
        height = 400
        x = (pygame.display.get_surface().get_width() - width) // 2
        y = (pygame.display.get_surface().get_height() - height) // 2
        
        # Check if click is within skills window
        skills_rect = pygame.Rect(x, y, width, height)
        if skills_rect.collidepoint(mouse_pos):
            # Handle any skill-specific clicks here
            return True
        
        return False 