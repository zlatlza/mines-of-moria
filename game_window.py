import pygame
from player import Player
from tile_types import TileTypes
from items import ItemRegistry
from map_data import Map

class Game:
    def __init__(self):
        pygame.init()
        self.TILE_SIZE = 50
        self.VIEWPORT_WIDTH = 16  # Number of tiles visible horizontally
        self.VIEWPORT_HEIGHT = 12  # Number of tiles visible vertically
        self.GUI_HEIGHT = 60
        
        # Create window based on viewport size (not map size)
        self.screen = pygame.display.set_mode((
            self.VIEWPORT_WIDTH * self.TILE_SIZE,
            self.VIEWPORT_HEIGHT * self.TILE_SIZE + self.GUI_HEIGHT
        ))
        
        # Load map
        self.current_map = Map.load_from_file("test_map")
        
        # Initialize game state manager
        from game_state import GameState
        self.state_manager = GameState(self.current_map)
        
        # Camera position (in tile coordinates)
        self.camera_x = 0
        self.camera_y = 0
        
        # Create player at spawn point
        self.player = Player(self.TILE_SIZE, self.current_map.tiles)
        self.player.grid_x, self.player.grid_y = self.current_map.player_spawn
        self.player.game = self
        
        # Use items from map
        self.ground_items = self.current_map.items  # This is a reference to map's items
        
        # GUI colors and dimensions
        self.GUI_COLOR = (50, 50, 50)
        self.BUTTON_COLOR = (70, 70, 70)
        self.BUTTON_HOVER_COLOR = (90, 90, 90)
        self.HEALTH_COLOR = (255, 0, 0)
        self.BUTTON_WIDTH = 100
        self.BUTTON_HEIGHT = 40
        
        # Game state
        self.running = True
        
        # Add message system
        self.messages = []
        self.MESSAGE_DURATION = 3000  # Messages last 3 seconds
        self.MAX_MESSAGES = 3  # Show up to 3 messages at once
        
        # Add sleep animation state
        self.sleeping = False
        self.sleep_start_time = 0
        self.sleep_duration = 1000  # 1 second
        self.fade_alpha = 0
        self.sleep_surface = None
        
        # Load tile images
        TileTypes.load_images(self.TILE_SIZE)
        
        # Add font for hover text
        self.hover_font = pygame.font.Font(None, 24)
        self.hover_text = None
        self.hover_text_pos = None
        self.show_hover_text = False  # New toggle variable
        self.show_tooltips = False  # Add this line to track tooltip state
        
        # Add menu manager
        from menu_manager import MenuManager
        self.menu_manager = MenuManager()
        
        # Add crafting menu
        from crafting_menu import CraftingMenu
        self.crafting_menu = CraftingMenu()
        
    def update_camera(self):
        # Center camera on player
        self.camera_x = self.player.grid_x - self.VIEWPORT_WIDTH // 2
        self.camera_y = self.player.grid_y - self.VIEWPORT_HEIGHT // 2
        
        # Ensure camera doesn't go out of map bounds
        self.camera_x = max(0, min(self.camera_x, len(self.current_map.tiles[0]) - self.VIEWPORT_WIDTH))
        self.camera_y = max(0, min(self.camera_y, len(self.current_map.tiles) - self.VIEWPORT_HEIGHT))
    
    def world_to_screen(self, grid_x, grid_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (grid_x - self.camera_x) * self.TILE_SIZE
        screen_y = (grid_y - self.camera_y) * self.TILE_SIZE
        return screen_x, screen_y
    
    def draw(self):
        # Fill with floor color instead of black
        self.screen.fill(TileTypes.get_tile_properties(TileTypes.FLOOR)['color'])
        
        # Update camera to follow player
        self.update_camera()
        
        # Draw map and items
        self._draw_map_tiles()
        self._draw_ground_items()
        
        # Draw player
        screen_x = (self.player.grid_x - self.camera_x) * self.TILE_SIZE
        screen_y = (self.player.grid_y - self.camera_y) * self.TILE_SIZE
        self.player.draw_at_position(self.screen, screen_x, screen_y)
        
        # Draw GUI
        self.draw_gui()
        
        # Draw sleep animation if active
        if self.sleeping:
            self._draw_sleep_animation()
        
        # Draw hover text if active
        if self.hover_text and self.hover_text_pos:
            self._draw_hover_text()
        
        # Draw crafting menu if open
        if hasattr(self, 'crafting_menu') and self.crafting_menu.is_open:
            self.crafting_menu.draw(self.screen, self.player.skills.smithing_level)
        
        pygame.display.flip()
    
    def _draw_map_tiles(self):
        """Draw the visible map tiles"""
        for y in range(self.VIEWPORT_HEIGHT):
            for x in range(self.VIEWPORT_WIDTH):
                map_x = int(x + self.camera_x)
                map_y = int(y + self.camera_y)
                
                screen_x = x * self.TILE_SIZE
                screen_y = y * self.TILE_SIZE
                
                # Draw actual tiles if within map bounds
                if (0 <= map_x < len(self.current_map.tiles[0]) and 
                    0 <= map_y < len(self.current_map.tiles)):
                    
                    tile = self.current_map.tiles[map_y][map_x]
                    tile_props = TileTypes.get_tile_properties(tile, (map_x, map_y))
                    
                    if tile_props.get('has_image', False) and tile in TileTypes.tile_images:
                        self.screen.blit(TileTypes.tile_images[tile], (screen_x, screen_y))
                    else:
                        color = tile_props.get('color', (100, 100, 100))
                        pygame.draw.rect(self.screen, color, 
                                      (screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE))
    
    def _draw_ground_items(self):
        """Draw items on the ground"""
        for pos, items in self.ground_items.items():
            screen_x = (pos[0] - self.camera_x) * self.TILE_SIZE
            screen_y = (pos[1] - self.camera_y) * self.TILE_SIZE
            
            if (0 <= screen_x < self.VIEWPORT_WIDTH * self.TILE_SIZE and
                0 <= screen_y < self.VIEWPORT_HEIGHT * self.TILE_SIZE):
                # If it's a list, draw the last item in the stack
                if isinstance(items, list) and items:
                    items[-1].draw(self.screen, screen_x, screen_y, self.TILE_SIZE)
                # Handle old format (single item)
                elif not isinstance(items, list):
                    items.draw(self.screen, screen_x, screen_y, self.TILE_SIZE)
    
    def _draw_hover_text(self):
        """Draw hover text with background"""
        text_surface = self.hover_font.render(self.hover_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.hover_text_pos)
        
        # Draw background for better visibility
        padding = 4
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
    
    def _draw_sleep_animation(self):
        """Draw the sleep animation overlay"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.sleep_start_time
        
        if elapsed < self.sleep_duration:
            # Fade to black during sleep animation
            self.fade_alpha = min(255, (elapsed / self.sleep_duration) * 255)
        else:
            self.fade_alpha = 255
        
        # Draw sleep overlay
        self.sleep_surface.set_alpha(self.fade_alpha)
        self.screen.blit(self.sleep_surface, (0, 0))
        
        # Draw "Zzzzz" text
        if self.fade_alpha > 128:  # Show text when mostly faded
            font = pygame.font.Font(None, 72)
            text = font.render("Zzzzz...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.VIEWPORT_WIDTH * self.TILE_SIZE // 2,
                                            self.VIEWPORT_HEIGHT * self.TILE_SIZE // 2))
            self.screen.blit(text, text_rect)
            
            if elapsed >= self.sleep_duration:
                # Show wake up prompt
                font = pygame.font.Font(None, 36)
                prompt = font.render("Click or press any key to wake up", True, (200, 200, 200))
                prompt_rect = prompt.get_rect(center=(self.VIEWPORT_WIDTH * self.TILE_SIZE // 2,
                                                    text_rect.bottom + 40))
                self.screen.blit(prompt, prompt_rect)
    
    def add_message(self, text):
        # Add new message with timestamp
        self.messages.append({
            'text': text,
            'time': pygame.time.get_ticks()
        })
        # Keep only the most recent messages
        if len(self.messages) > self.MAX_MESSAGES:
            self.messages.pop(0)
            
    def draw_gui(self):
        # Draw GUI background
        gui_y = self.VIEWPORT_HEIGHT * self.TILE_SIZE
        pygame.draw.rect(self.screen, self.GUI_COLOR,
                        (0, gui_y, self.VIEWPORT_WIDTH * self.TILE_SIZE, self.GUI_HEIGHT))
        
        # Draw messages
        current_time = pygame.time.get_ticks()
        font = pygame.font.Font(None, 24)
        message_y = 5  # Start at top of screen
        
        # Filter out old messages and draw remaining ones
        self.messages = [msg for msg in self.messages 
                        if current_time - msg['time'] < self.MESSAGE_DURATION]
        
        for msg in self.messages:
            text_surface = font.render(msg['text'], True, (255, 255, 255))
            self.screen.blit(text_surface, (10, message_y))
            message_y += 20  # Space between messages
        
        # Draw health bar
        health_width = (self.player.health / 100) * 200  # 200px max width
        pygame.draw.rect(self.screen, self.HEALTH_COLOR,
                        (10, gui_y + 10, health_width, 20))
        
        # Draw GUI buttons
        font = pygame.font.Font(None, 24)
        
        # Inventory button
        inv_button_rect = pygame.Rect(self.VIEWPORT_WIDTH * self.TILE_SIZE - 220, 
                                     gui_y + 10, 
                                     self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button_color = self.BUTTON_HOVER_COLOR if self.player.inventory.is_open else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, inv_button_rect)
        inv_text = font.render("Inventory (I)", True, (255, 255, 255))
        self.screen.blit(inv_text, (inv_button_rect.x + 10, inv_button_rect.y + 10))
        
        # Skills button
        skills_button_rect = pygame.Rect(self.VIEWPORT_WIDTH * self.TILE_SIZE - 110, 
                                       gui_y + 10, 
                                       self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button_color = self.BUTTON_HOVER_COLOR if self.player.skills.is_open else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, skills_button_rect)
        skills_text = font.render("Skills (K)", True, (255, 255, 255))
        self.screen.blit(skills_text, (skills_button_rect.x + 15, skills_button_rect.y + 10))
        
        # Draw inventory if open
        if self.player.inventory.is_open:
            self.player.inventory.draw(self.screen)
        
        # Draw skills if open
        if self.player.skills.is_open:
            self.player.skills.draw(self.screen)
    
    def handle_click(self, pos, button):
        # If crafting menu is open, check if click is outside
        if hasattr(self, 'crafting_menu') and self.crafting_menu.is_open:
            menu_rect = pygame.Rect(
                (self.screen.get_width() - 400) // 2,  # x
                (self.screen.get_height() - 300) // 2,  # y
                400,  # width
                300   # height
            )
            if not menu_rect.collidepoint(pos):
                self.crafting_menu.close()
                return True
            if self.crafting_menu.handle_click(pos, self.player):
                return True
            
        # If inventory is open, let it handle clicks first
        if self.player.inventory.is_open:
            # Let inventory handle the click
            if self.player.inventory.handle_click(pos, button):
                return True
            # If click wasn't on inventory, close it
            self.player.inventory.is_open = False
            return True
            
        mouse_x, mouse_y = pos
        tile_x = mouse_x // self.TILE_SIZE + self.camera_x
        tile_y = mouse_y // self.TILE_SIZE + self.camera_y
        
        # Only handle map clicks if inventory is closed
        if (0 <= tile_x < len(self.current_map.tiles[0]) and 
            0 <= tile_y < len(self.current_map.tiles)):
            
            # Handle interaction if player has equipped item (left click only)
            if button == 1 and self.player.equipped_item:
                self.player.equipped_item.use(self.player, tile_x, tile_y)
            
            # Show tooltip on right click
            elif button == 3:
                tile = self.current_map.tiles[tile_y][tile_x]
                tile_props = TileTypes.get_tile_properties(tile, (tile_x, tile_y))
                
                # Show tile info
                info = f"Tile: {tile_props.get('name', 'Unknown')}"
                if tile == TileTypes.ROCK and (tile_x, tile_y) in TileTypes.rock_data:
                    rock_data = TileTypes.rock_data[(tile_x, tile_y)]
                    info += f" ({rock_data['name']}, Level {rock_data['mining_level']})"
                
                self.add_message(info)
        
        return True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.sleeping and pygame.time.get_ticks() - self.sleep_start_time >= self.sleep_duration:
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    self.sleeping = False
                    self.player.complete_sleep()
            elif not self.sleeping:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right click
                        self.show_tooltips = not self.show_tooltips
                    if self.handle_click(event.pos, event.button):
                        continue
                elif event.type == pygame.KEYDOWN:
                    self.player.handle_input(event)
            
            # Only update hover text if tooltips are enabled
            if self.show_tooltips:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.update_hover_text(mouse_x, mouse_y)
            else:
                self.hover_text = ''
                self.hover_text_pos = None
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.player.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

    def start_sleep_animation(self):
        print("Starting sleep animation")  # Debug print
        self.sleeping = True
        self.sleep_start_time = pygame.time.get_ticks()
        self.fade_alpha = 0
        self.sleep_surface = pygame.Surface((self.VIEWPORT_WIDTH * self.TILE_SIZE,
                                          self.VIEWPORT_HEIGHT * self.TILE_SIZE + self.GUI_HEIGHT))
        self.sleep_surface.fill((0, 0, 0))

    def update_ground_items(self):
        """Update ground_items to match map's items"""
        self.ground_items = self.current_map.items

    def update_hover_text(self, mouse_x, mouse_y):
        # Convert mouse position to tile coordinates
        tile_x = mouse_x // self.TILE_SIZE + self.camera_x
        tile_y = mouse_y // self.TILE_SIZE + self.camera_y
        
        # Check if mouse is within map area
        if (0 <= tile_x < len(self.current_map.tiles[0]) and 
            0 <= tile_y < len(self.current_map.tiles) and
            mouse_y < self.VIEWPORT_HEIGHT * self.TILE_SIZE):  # Not in GUI area
            
            # Check for items first (they're on top)
            pos = (tile_x, tile_y)
            if pos in self.ground_items:
                items = self.ground_items[pos]
                # Handle both single items and lists of items
                if isinstance(items, list):
                    if len(items) == 1:
                        self.hover_text = f"Item: {items[0].name}"
                    else:
                        item_names = [item.name for item in items]
                        self.hover_text = f"Items: {', '.join(item_names)}"
                else:
                    # Single item (old format)
                    self.hover_text = f"Item: {items.name}"
            else:
                # If no item, show tile info
                tile = self.current_map.tiles[tile_y][tile_x]
                tile_props = TileTypes.get_tile_properties(tile, (tile_x, tile_y))
                self.hover_text = tile_props.get('name', '')
            
            # Position text above the tile
            self.hover_text_pos = (
                mouse_x,
                mouse_y - 20  # 20 pixels above mouse
            )
        else:
            self.hover_text = ''

if __name__ == "__main__":
    game = Game()
    game.run()
