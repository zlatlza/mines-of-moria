import pygame

class Inventory:
    def __init__(self):
        self.size = 16
        self.items = [None] * self.size
        self.is_open = False
        self.show_tooltip = False
        self.tooltip_item = None
        self.tooltip_pos = None
        self.player = None  # Will be set by Player class
        
    def toggle(self):
        self.is_open = not self.is_open
        
    def add_item(self, item):
        for i in range(self.size):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False
        
    def handle_click(self, mouse_pos):
        if not self.is_open:
            return False
            
        padding = 10
        slot_size = 40
        slots_per_row = 4
        
        # Calculate inventory position
        width = (slot_size * slots_per_row) + (padding * 2)
        height = (slot_size * (self.size // slots_per_row)) + (padding * 2)
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        inv_x = (screen_width - width) // 2
        inv_y = (screen_height - height) // 2
        
        # Check slot clicks
        for i in range(self.size):
            slot_x = inv_x + padding + (i % slots_per_row) * slot_size
            slot_y = inv_y + padding + (i // slots_per_row) * slot_size
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            
            if slot_rect.collidepoint(mouse_pos) and self.items[i]:
                if pygame.mouse.get_pressed()[0]:  # Left click to equip
                    self.items[i].equip(self.player)
                elif pygame.mouse.get_pressed()[2]:  # Right click to drop
                    self.drop_item(i)
                return True
                
        return False
        
    def drop_item(self, slot_index):
        dropped_item = self.items[slot_index]
        self.items[slot_index] = None
        if dropped_item.equipped:
            dropped_item.equip(self.player)
        self.player.game.ground_items[(self.player.grid_x, self.player.grid_y)] = dropped_item
        print(f"Dropped {dropped_item.name}")
        
    def draw(self, screen):
        if not self.is_open:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        padding = 10
        slot_size = 40
        slots_per_row = 4
        
        # Calculate dimensions
        width = (slot_size * slots_per_row) + (padding * 2)
        height = (slot_size * (self.size // slots_per_row)) + (padding * 2)
        x = (screen.get_width() - width) // 2
        y = (screen.get_height() - height) // 2
        
        # Draw background
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        
        # Draw slots and items
        for i in range(self.size):
            slot_x = x + padding + (i % slots_per_row) * slot_size
            slot_y = y + padding + (i // slots_per_row) * slot_size
            
            pygame.draw.rect(screen, (50, 50, 50),
                           (slot_x, slot_y, slot_size - 2, slot_size - 2))
            
            if self.items[i]:
                if self.items[i].equipped:
                    pygame.draw.rect(screen, (255, 215, 0),
                                   (slot_x, slot_y, slot_size - 2, slot_size - 2), 2)
                self.items[i].draw(screen, slot_x, slot_y, slot_size)
                
                # Check for tooltip
                if (slot_x <= mouse_pos[0] <= slot_x + slot_size and 
                    slot_y <= mouse_pos[1] <= slot_y + slot_size):
                    self.tooltip_item = self.items[i]
                    self.tooltip_pos = mouse_pos
                    self.show_tooltip = True
        
        if self.show_tooltip:
            self.draw_tooltip(screen)
            self.show_tooltip = False

    def draw_tooltip(self, screen):
        padding = 5
        font = pygame.font.Font(None, 24)
        
        # Create tooltip text
        name_text = font.render(self.tooltip_item.name, True, (255, 255, 255))
        desc_text = font.render(self.tooltip_item.description, True, (255, 255, 255))
        drop_text = font.render("Right click again to drop", True, (255, 200, 200))
        
        # Calculate tooltip dimensions
        width = max(name_text.get_width(), desc_text.get_width(), drop_text.get_width()) + padding * 2
        height = name_text.get_height() + desc_text.get_height() + drop_text.get_height() + padding * 4
        
        # Position tooltip near mouse but ensure it stays on screen
        x = min(self.tooltip_pos[0], screen.get_width() - width)
        y = min(self.tooltip_pos[1], screen.get_height() - height)
        
        # Draw tooltip background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 1)
        
        # Draw text
        screen.blit(name_text, (x + padding, y + padding))
        screen.blit(desc_text, (x + padding, y + name_text.get_height() + padding * 2))
        screen.blit(drop_text, (x + padding, y + name_text.get_height() + desc_text.get_height() + padding * 3))
        
        # Check for second right click to drop
        if pygame.mouse.get_pressed()[2]:
            slot_index = self.items.index(self.tooltip_item)
            dropped_item = self.items[slot_index]
            self.items[slot_index] = None
            if dropped_item.equipped:
                dropped_item.equip(self.player)  # Unequip if equipped
            
            # Drop item at player's position
            self.player.game.ground_items[(self.player.grid_x, self.player.grid_y)] = dropped_item
            print(f"Dropped {dropped_item.name}")
            self.show_tooltip = False 