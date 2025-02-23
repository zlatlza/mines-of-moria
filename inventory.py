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
        
    def handle_click(self, pos, button):
        if not self.is_open:
            return False
        
        mouse_x, mouse_y = pos
        padding = 10
        slot_size = 40
        slots_per_row = 4
        
        # Calculate inventory window dimensions
        width = (slot_size * slots_per_row) + (padding * 2)
        height = (slot_size * (self.size // slots_per_row)) + (padding * 2)
        window_x = (pygame.display.get_surface().get_width() - width) // 2
        window_y = (pygame.display.get_surface().get_height() - height) // 2
        
        # Check if click is within inventory window
        if (window_x <= mouse_x <= window_x + width and 
            window_y <= mouse_y <= window_y + height):
            
            # Calculate which slot was clicked
            rel_x = mouse_x - (window_x + padding)
            rel_y = mouse_y - (window_y + padding)
            
            slot_x = rel_x // slot_size
            slot_y = rel_y // slot_size
            
            if 0 <= slot_x < slots_per_row and 0 <= rel_x % slot_size < slot_size - 2:
                slot_index = slot_y * slots_per_row + slot_x
                if 0 <= slot_index < self.size and self.items[slot_index]:
                    if button == 1:  # Left click to equip
                        self.items[slot_index].equip(self.player)
                    elif button == 3:  # Right click to drop
                        self.drop_item(slot_index)
                    return True
                
        return False
        
    def drop_item(self, slot_index):
        dropped_item = self.items[slot_index]
        if dropped_item:
            self.items[slot_index] = None
            if dropped_item.equipped:
                dropped_item.equip(self.player)  # Unequip if equipped
            
            # Get player's position
            pos = (self.player.grid_x, self.player.grid_y)
            
            # Initialize list for position if it doesn't exist
            if pos not in self.player.game.ground_items:
                self.player.game.ground_items[pos] = []
            
            # Add item to the stack
            self.player.game.ground_items[pos].append(dropped_item)
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
        
        # Calculate tooltip dimensions
        width = max(name_text.get_width(), desc_text.get_width()) + padding * 2
        height = name_text.get_height() + desc_text.get_height() + padding * 3
        
        # Position tooltip near mouse but ensure it stays on screen
        x = min(self.tooltip_pos[0], screen.get_width() - width)
        y = min(self.tooltip_pos[1], screen.get_height() - height)
        
        # Draw tooltip background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 1)
        
        # Draw text
        screen.blit(name_text, (x + padding, y + padding))
        screen.blit(desc_text, (x + padding, y + name_text.get_height() + padding * 2)) 