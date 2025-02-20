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
        
    def update_camera(self):
        # Center camera on player with some margin from edges
        margin_x = self.VIEWPORT_WIDTH // 3
        margin_y = self.VIEWPORT_HEIGHT // 3
        
        # Calculate desired camera position
        desired_x = self.player.grid_x - self.VIEWPORT_WIDTH // 2
        desired_y = self.player.grid_y - self.VIEWPORT_HEIGHT // 2
        
        # Clamp camera to map bounds
        self.camera_x = max(0, min(desired_x, self.current_map.width - self.VIEWPORT_WIDTH))
        self.camera_y = max(0, min(desired_y, self.current_map.height - self.VIEWPORT_HEIGHT))
    
    def world_to_screen(self, grid_x, grid_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (grid_x - self.camera_x) * self.TILE_SIZE
        screen_y = (grid_y - self.camera_y) * self.TILE_SIZE
        return screen_x, screen_y
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Update camera position
        self.update_camera()
        
        # Calculate visible range
        start_x = int(self.camera_x)
        start_y = int(self.camera_y)
        end_x = min(start_x + self.VIEWPORT_WIDTH, self.current_map.width)
        end_y = min(start_y + self.VIEWPORT_HEIGHT, self.current_map.height)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                map_x = x + self.camera_x
                map_y = y + self.camera_y
                
                if (0 <= map_x < len(self.current_map.tiles[0]) and 
                    0 <= map_y < len(self.current_map.tiles)):
                    
                    tile = self.current_map.tiles[map_y][map_x]
                    screen_x = x * self.TILE_SIZE
                    screen_y = y * self.TILE_SIZE
                    
                    tile_props = TileTypes.get_tile_properties(tile, (map_x, map_y))
                    
                    # If tile has an image, use it
                    if tile_props.get('has_image', False) and tile in TileTypes.tile_images:
                        self.screen.blit(TileTypes.tile_images[tile], (screen_x, screen_y))
                    else:
                        # Fall back to colored rectangle
                        color = tile_props.get('color', (100, 100, 100))
                        pygame.draw.rect(self.screen, color, 
                                       (screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE))
                
        # Draw visible ground items
        for pos, item in self.ground_items.items():
            x, y = pos
            if start_x <= x < end_x and start_y <= y < end_y:
                screen_x, screen_y = self.world_to_screen(x, y)
                item.draw(self.screen, screen_x, screen_y, self.TILE_SIZE)
        
        # Draw player
        screen_x, screen_y = self.world_to_screen(self.player.grid_x, self.player.grid_y)
        self.player.draw_at_position(self.screen, screen_x, screen_y)
        
        # Draw GUI
        self.draw_gui()
        
        if self.sleeping:
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
        
        # Draw hover text if it exists
        if self.hover_text and self.hover_text_pos:
            text_surface = self.hover_font.render(self.hover_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.hover_text_pos)
            
            # Draw background for better visibility
            padding = 4
            bg_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            
            # Draw text
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
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
    
    def handle_gui_click(self, pos):
        # Try to handle inventory click first
        if self.player.inventory.handle_click(pos):
            return True
        
        # If click wasn't in inventory, close it
        self.player.inventory.is_open = False
        
        # Handle GUI buttons
        gui_y = self.VIEWPORT_HEIGHT * self.TILE_SIZE
        
        # Inventory button
        inv_button_rect = pygame.Rect(
            self.VIEWPORT_WIDTH * self.TILE_SIZE - 220,
            gui_y + 10,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        if inv_button_rect.collidepoint(pos):
            self.player.inventory.toggle()
            return True
        
        # Skills button
        skills_button_rect = pygame.Rect(
            self.VIEWPORT_WIDTH * self.TILE_SIZE - 110,
            gui_y + 10,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        if skills_button_rect.collidepoint(pos):
            self.player.skills.toggle()
            return True
            
        return False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.sleeping and pygame.time.get_ticks() - self.sleep_start_time >= self.sleep_duration:
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    self.sleeping = False
                    self.player.complete_sleep()
            elif not self.sleeping:
                # Toggle hover text with left click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.show_hover_text = not self.show_hover_text
                    if self.handle_gui_click(event.pos):
                        continue
                elif event.type == pygame.KEYDOWN:
                    self.player.handle_input(event)
            
            # Only update hover text if it's enabled
            if self.show_hover_text:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.update_hover_text(mouse_x, mouse_y)
            else:
                self.hover_text = None
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

    def draw_map(self):
        for y in range(self.VIEWPORT_HEIGHT):
            for x in range(self.VIEWPORT_WIDTH):
                map_x = x + self.camera_x
                map_y = y + self.camera_y
                
                if (0 <= map_x < len(self.current_map.tiles[0]) and 
                    0 <= map_y < len(self.current_map.tiles)):
                    
                    tile = self.current_map.tiles[map_y][map_x]
                    screen_x = x * self.TILE_SIZE
                    screen_y = y * self.TILE_SIZE
                    
                    tile_props = TileTypes.get_tile_properties(tile, (map_x, map_y))
                    
                    # If tile has an image, use it
                    if tile_props.get('has_image', False) and tile in TileTypes.tile_images:
                        self.screen.blit(TileTypes.tile_images[tile], (screen_x, screen_y))
                    else:
                        # Fall back to colored rectangle
                        color = tile_props.get('color', (100, 100, 100))
                        pygame.draw.rect(self.screen, color, 
                                       (screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE))
        
        # Draw items
        for pos, item in self.ground_items.items():
            screen_x = (pos[0] - self.camera_x) * self.TILE_SIZE
            screen_y = (pos[1] - self.camera_y) * self.TILE_SIZE
            if (0 <= screen_x < self.VIEWPORT_WIDTH * self.TILE_SIZE and
                0 <= screen_y < self.VIEWPORT_HEIGHT * self.TILE_SIZE):
                pygame.draw.rect(self.screen, item.icon_color,
                               (screen_x + 10, screen_y + 10,
                                self.TILE_SIZE - 20, self.TILE_SIZE - 20))

    def update_hover_text(self, mouse_x, mouse_y):
        # Convert mouse position to tile coordinates
        tile_x = mouse_x // self.TILE_SIZE + self.camera_x
        tile_y = mouse_y // self.TILE_SIZE + self.camera_y
        
        # Check if mouse is within map area
        if (0 <= tile_x < len(self.current_map.tiles[0]) and 
            0 <= tile_y < len(self.current_map.tiles) and
            mouse_y < self.VIEWPORT_HEIGHT * self.TILE_SIZE):  # Not in GUI area
            
            tile = self.current_map.tiles[tile_y][tile_x]
            tile_props = TileTypes.get_tile_properties(tile, (tile_x, tile_y))
            
            # Get tile name from properties
            self.hover_text = tile_props.get('name', '')
            # Position text above the tile
            self.hover_text_pos = (
                mouse_x,
                mouse_y - 20  # 20 pixels above mouse
            )
        else:
            self.hover_text = None
            self.hover_text_pos = None

if __name__ == "__main__":
    game = Game()
    game.run()
