import pygame
from tile_types import TileTypes, RockTypes
from items import ItemRegistry

class Sidebar:
    def __init__(self, x, width, height, tile_size):
        self.x = x
        self.width = width
        self.height = height
        self.tile_size = tile_size
        
        # Colors
        self.BG_COLOR = (50, 50, 50)
        self.BUTTON_COLOR = (70, 70, 70)
        self.SELECTED_COLOR = (100, 100, 100)
        
        # Scroll state
        self.scroll = 0
        self.max_scroll = 0
        
        # Selection state
        self.selected_category = "Tiles"
        self.selected_tile = None
        self.selected_item = None
        self.selected_rock_type = None
        
        # Button dimensions
        self.button_height = 30
        self.button_padding = 5
        self.category_buttons = ["Tiles", "Items", "Rocks"]
        
    def handle_scroll(self, scroll_up):
        scroll_amount = -20 if scroll_up else 20
        self.scroll = max(0, min(self.max_scroll, self.scroll + scroll_amount))
    
    def handle_click(self, x, y):
        if x < self.x or x > self.x + self.width:
            return False
            
        # Adjust y for scroll
        actual_y = y + self.scroll
        current_y = 10
        
        # Check category buttons
        for category in self.category_buttons:
            button_rect = pygame.Rect(
                self.x + 10,
                current_y,
                self.width - 20,
                self.button_height
            )
            if button_rect.collidepoint(x, actual_y):
                self.selected_category = category
                return True
            current_y += self.button_height + self.button_padding
        
        current_y += 10  # Extra spacing after categories
        
        # Check content buttons based on category
        if self.selected_category == "Tiles":
            all_tiles = [
                TileTypes.FLOOR,
                TileTypes.WALL,
                TileTypes.ROCK,
                TileTypes.DEPLETED_ROCK,
                TileTypes.FURNACE,
                TileTypes.BED
            ]
            
            for tile in all_tiles:
                button_rect = pygame.Rect(
                    self.x + 10,
                    current_y,
                    self.width - 20,
                    self.tile_size
                )
                if button_rect.collidepoint(x, actual_y):
                    self.selected_tile = tile
                    self.selected_item = None
                    self.selected_rock_type = None
                    return True
                current_y += self.tile_size + self.button_padding
                
        elif self.selected_category == "Items":
            for item_name in ItemRegistry.get_all_items():
                button_rect = pygame.Rect(
                    self.x + 10,
                    current_y,
                    self.width - 20,
                    self.tile_size
                )
                if button_rect.collidepoint(x, actual_y):
                    self.selected_item = item_name
                    self.selected_tile = None
                    self.selected_rock_type = None
                    return True
                current_y += self.tile_size + self.button_padding
                
        elif self.selected_category == "Rocks":
            for rock_name in RockTypes.get_all_rocks():
                button_rect = pygame.Rect(
                    self.x + 10,
                    current_y,
                    self.width - 20,
                    self.tile_size
                )
                if button_rect.collidepoint(x, actual_y):
                    self.selected_rock_type = rock_name
                    self.selected_tile = TileTypes.ROCK
                    self.selected_item = None
                    return True
                current_y += self.tile_size + self.button_padding
        
        return False
    
    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, self.BG_COLOR, 
                        (self.x, 0, self.width, self.height))
        
        current_y = 10 - self.scroll
        
        # Draw category buttons
        for category in self.category_buttons:
            button_rect = pygame.Rect(
                self.x + 10,
                current_y,
                self.width - 20,
                self.button_height
            )
            color = self.SELECTED_COLOR if category == self.selected_category else self.BUTTON_COLOR
            pygame.draw.rect(screen, color, button_rect)
            
            # Draw category text
            font = pygame.font.Font(None, 24)
            text = font.render(category, True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            
            current_y += self.button_height + self.button_padding
        
        current_y += 10  # Extra spacing after categories
        
        # Draw content based on selected category
        if self.selected_category == "Tiles":
            # Get all tile types from TileTypes
            all_tiles = [
                TileTypes.FLOOR,
                TileTypes.WALL,
                TileTypes.ROCK,
                TileTypes.DEPLETED_ROCK,
                TileTypes.FURNACE,
                TileTypes.BED
            ]
            
            for tile in all_tiles:
                tile_props = TileTypes.get_tile_properties(tile)
                button_rect = pygame.Rect(
                    self.x + 10,
                    current_y,
                    self.width - 20,
                    self.tile_size
                )
                color = self.SELECTED_COLOR if tile == self.selected_tile else self.BUTTON_COLOR
                pygame.draw.rect(screen, color, button_rect)
                
                # Draw tile preview
                preview_rect = pygame.Rect(
                    self.x + 15,
                    current_y + 5,
                    self.tile_size - 10,
                    self.tile_size - 10
                )
                pygame.draw.rect(screen, tile_props['color'], preview_rect)
                
                # Draw tile name
                font = pygame.font.Font(None, 20)
                text = font.render(tile_props['name'], True, (255, 255, 255))
                text_rect = text.get_rect(midleft=(preview_rect.right + 5, preview_rect.centery))
                screen.blit(text, text_rect)
                
                current_y += self.tile_size + self.button_padding
                
        elif self.selected_category == "Items":
            for item_name in ItemRegistry.get_all_items():
                self._draw_item_button(screen, item_name, current_y)
                current_y += self.tile_size + self.button_padding
                
        elif self.selected_category == "Rocks":
            for rock_name, rock_data in RockTypes.get_all_rocks().items():
                self._draw_rock_button(screen, rock_name, rock_data, current_y)
                current_y += self.tile_size + self.button_padding
        
        # Update max scroll
        self.max_scroll = max(0, current_y - self.height + self.scroll)
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            if self.scroll > 0:
                pygame.draw.polygon(screen, (255, 255, 255),
                    [(self.x + self.width//2 - 10, 15),
                     (self.x + self.width//2 + 10, 15),
                     (self.x + self.width//2, 5)])
            if self.scroll < self.max_scroll:
                pygame.draw.polygon(screen, (255, 255, 255),
                    [(self.x + self.width//2 - 10, self.height - 15),
                     (self.x + self.width//2 + 10, self.height - 15),
                     (self.x + self.width//2, self.height - 5)])
    
    def _draw_item_button(self, screen, item_name, y):
        button_rect = pygame.Rect(
            self.x + 10,
            y,
            self.width - 20,
            self.tile_size
        )
        color = self.SELECTED_COLOR if item_name == self.selected_item else self.BUTTON_COLOR
        pygame.draw.rect(screen, color, button_rect)
        
        # Draw item preview
        item = ItemRegistry.create_item(item_name)
        preview_rect = pygame.Rect(
            self.x + 15,
            y + 5,
            self.tile_size - 10,
            self.tile_size - 10
        )
        pygame.draw.rect(screen, item.icon_color, preview_rect)
        
        # Draw item name
        font = pygame.font.Font(None, 20)
        text = font.render(item_name, True, (255, 255, 255))
        text_rect = text.get_rect(midleft=(preview_rect.right + 5, preview_rect.centery))
        screen.blit(text, text_rect)
    
    def _draw_rock_button(self, screen, rock_name, rock_data, y):
        button_rect = pygame.Rect(
            self.x + 10,
            y,
            self.width - 20,
            self.tile_size
        )
        color = self.SELECTED_COLOR if rock_name == self.selected_rock_type else self.BUTTON_COLOR
        pygame.draw.rect(screen, color, button_rect)
        
        # Draw rock preview
        preview_rect = pygame.Rect(
            self.x + 15,
            y + 5,
            self.tile_size - 10,
            self.tile_size - 10
        )
        pygame.draw.rect(screen, rock_data['color'], preview_rect)
        
        # Draw rock name and level
        font = pygame.font.Font(None, 20)
        text = font.render(f"{rock_data['name']} (Lvl {rock_data['mining_level']})", True, (255, 255, 255))
        text_rect = text.get_rect(midleft=(preview_rect.right + 5, preview_rect.centery))
        screen.blit(text, text_rect) 