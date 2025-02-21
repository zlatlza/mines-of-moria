import pygame
import os
from tkinter import filedialog
import tkinter as tk
from map_data import Map
from tile_types import TileTypes, RockTypes
from items import ItemRegistry
from sidebar import Sidebar

class MapEditor:
    def __init__(self):
        # Initialize tkinter root window but hide it
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        
        pygame.init()
        self.TILE_SIZE = 50
        self.SIDEBAR_WIDTH = 200
        self.VIEWPORT_WIDTH = 16  # Fixed viewport width in tiles
        self.VIEWPORT_HEIGHT = 12  # Fixed viewport height in tiles
        
        # Create window with fixed size
        self.screen = pygame.display.set_mode((
            self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH,
            self.VIEWPORT_HEIGHT * self.TILE_SIZE
        ))
        pygame.display.set_caption("Map Editor")
        
        # Default map size
        self.MAP_WIDTH = 32  # Larger than viewport
        self.MAP_HEIGHT = 24
        
        # Initialize map
        self.current_map = Map(self.MAP_WIDTH, self.MAP_HEIGHT)
        
        # Camera position (in tile coordinates)
        self.camera_x = 0
        self.camera_y = 0
        self.CAMERA_SPEED = 1  # Tiles per keypress
        
        # Editor state
        self.selected_category = "Tiles"
        self.selected_tile = TileTypes.FLOOR
        self.selected_item = None
        self.selected_rock_type = None
        
        # UI colors
        self.BUTTON_COLOR = (70, 70, 70)
        self.BUTTON_HOVER_COLOR = (90, 90, 90)
        self.SELECTED_COLOR = (100, 200, 100)
        
        # Load available items
        self.available_items = ItemRegistry.get_all_items()
        
        # Create save/load message
        self.message = ""
        self.message_timer = 0
        
        # Add scroll offset for sidebar
        self.sidebar_scroll = 0
        self.max_scroll = 0
        
        # Create sidebar
        sidebar_x = self.VIEWPORT_WIDTH * self.TILE_SIZE
        self.sidebar = Sidebar(
            x=sidebar_x,
            width=self.SIDEBAR_WIDTH,
            height=self.VIEWPORT_HEIGHT * self.TILE_SIZE,
            tile_size=self.TILE_SIZE
        )
        
    def show_message(self, text, duration=2000):
        self.message = text
        self.message_timer = pygame.time.get_ticks() + duration
        
    def handle_camera_movement(self, keys):
        if keys[pygame.K_LEFT]:
            self.camera_x = max(0, self.camera_x - self.CAMERA_SPEED)
        if keys[pygame.K_RIGHT]:
            self.camera_x = min(self.MAP_WIDTH - self.VIEWPORT_WIDTH, self.camera_x + self.CAMERA_SPEED)
        if keys[pygame.K_UP]:
            self.camera_y = max(0, self.camera_y - self.CAMERA_SPEED)
        if keys[pygame.K_DOWN]:
            self.camera_y = min(self.MAP_HEIGHT - self.VIEWPORT_HEIGHT, self.camera_y + self.CAMERA_SPEED)
    
    def world_to_screen(self, grid_x, grid_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (grid_x - self.camera_x) * self.TILE_SIZE
        screen_y = (grid_y - self.camera_y) * self.TILE_SIZE
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        grid_x = screen_x // self.TILE_SIZE + self.camera_x
        grid_y = screen_y // self.TILE_SIZE + self.camera_y
        return grid_x, grid_y
        
    def resize_map(self, new_width, new_height):
        # Create new map with desired size
        new_map = Map(new_width, new_height)
        
        # Copy existing tiles and items where possible
        for y in range(min(new_height, self.MAP_HEIGHT)):
            for x in range(min(new_width, self.MAP_WIDTH)):
                new_map.tiles[y][x] = self.current_map.tiles[y][x]
                
        # Copy items that are within new bounds
        for pos, item in self.current_map.items.items():
            x, y = pos
            if x < new_width and y < new_height:
                new_map.items[pos] = item
                
        # Ensure spawn point is within new bounds
        spawn_x, spawn_y = self.current_map.player_spawn
        new_map.player_spawn = (
            min(spawn_x, new_width - 1),
            min(spawn_y, new_height - 1)
        )
        
        # Update map
        self.current_map = new_map
        self.MAP_WIDTH = new_width
        self.MAP_HEIGHT = new_height
        
        # Reset camera if it's out of bounds
        self.camera_x = min(self.camera_x, self.MAP_WIDTH - self.VIEWPORT_WIDTH)
        self.camera_y = min(self.camera_y, self.MAP_HEIGHT - self.VIEWPORT_HEIGHT)
        
    def draw_sidebar(self):
        # Draw sidebar background
        pygame.draw.rect(self.screen, (50, 50, 50),
                        (self.VIEWPORT_WIDTH * self.TILE_SIZE, 0,
                         self.SIDEBAR_WIDTH, self.VIEWPORT_HEIGHT * self.TILE_SIZE))
        
        font = pygame.font.Font(None, 24)
        y = 10 - self.sidebar_scroll  # Apply scroll offset
        
        # Draw map dimensions and controls
        if y + 25 > 0:  # Only draw if visible
            text = font.render(f"Map Size: {self.MAP_WIDTH}x{self.MAP_HEIGHT}", True, (255, 255, 255))
            self.screen.blit(text, (self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y))
        y += 25
        
        if y + 25 > 0:
            text = font.render("R to resize map", True, (255, 255, 255))
            self.screen.blit(text, (self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y))
        y += 25
        
        if y + 25 > 0:
            text = font.render("Ctrl+S to Save", True, (255, 255, 255))
            self.screen.blit(text, (self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y))
        y += 25
        
        if y + 25 > 0:
            text = font.render("Ctrl+L to Load", True, (255, 255, 255))
            self.screen.blit(text, (self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y))
        y += 40
        
        # Draw category buttons
        for category in ["Tiles", "Items", "Spawn"]:
            if 0 < y < self.VIEWPORT_HEIGHT * self.TILE_SIZE:
                color = self.SELECTED_COLOR if category == self.selected_category else self.BUTTON_COLOR
                button_rect = pygame.Rect(self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y, 180, 30)
                pygame.draw.rect(self.screen, color, button_rect)
                
                text = font.render(category, True, (255, 255, 255))
                self.screen.blit(text, (button_rect.x + 10, button_rect.y + 5))
            y += 40
        
        # Draw options for selected category
        y += 20
        if self.selected_category == "Tiles":
            tile_types = [getattr(TileTypes, attr) for attr in dir(TileTypes) 
                         if not attr.startswith('_') and isinstance(getattr(TileTypes, attr), int)]
            
            for tile_type in tile_types:
                if 0 < y < self.VIEWPORT_HEIGHT * self.TILE_SIZE:
                    button_rect = pygame.Rect(self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y, 180, 30)
                    color = self.SELECTED_COLOR if self.selected_tile == tile_type else self.BUTTON_COLOR
                    pygame.draw.rect(self.screen, color, button_rect)
                    
                    props = TileTypes.get_tile_properties(tile_type)
                    text = font.render(props['name'], True, (255, 255, 255))
                    self.screen.blit(text, (button_rect.x + 10, button_rect.y + 5))
                y += 40
            
            if self.selected_tile == TileTypes.ROCK:
                y += 10
                for rock_name, rock_data in RockTypes.get_all_rocks().items():
                    if not rock_name.startswith('_'):
                        if 0 < y < self.VIEWPORT_HEIGHT * self.TILE_SIZE:
                            button_rect = pygame.Rect(self.VIEWPORT_WIDTH * self.TILE_SIZE + 20, y, 160, 30)
                            color = self.SELECTED_COLOR if self.selected_rock_type == rock_data else self.BUTTON_COLOR
                            pygame.draw.rect(self.screen, color, button_rect)
                            
                            text = font.render(rock_data['name'], True, (255, 255, 255))
                            self.screen.blit(text, (button_rect.x + 10, button_rect.y + 5))
                        y += 40
        
        elif self.selected_category == "Items":
            for item_name in ItemRegistry.get_all_items():
                if 0 < y < self.VIEWPORT_HEIGHT * self.TILE_SIZE:
                    item = ItemRegistry.create_item(item_name)
                    button_rect = pygame.Rect(self.VIEWPORT_WIDTH * self.TILE_SIZE + 10, y, 30, 30)
                    color = self.SELECTED_COLOR if item_name == self.selected_item else item.icon_color
                    pygame.draw.rect(self.screen, color, button_rect)
                    
                    text = font.render(item.name, True, (255, 255, 255))
                    self.screen.blit(text, (button_rect.x + 40, button_rect.y + 5))
                y += 40
        
        # Update max scroll
        self.max_scroll = max(0, y + self.sidebar_scroll - self.VIEWPORT_HEIGHT * self.TILE_SIZE + 40)
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            if self.sidebar_scroll > 0:
                pygame.draw.polygon(self.screen, (255, 255, 255),
                    [(self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH - 20, 10),
                     (self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH - 10, 20),
                     (self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH - 30, 20)])
            
            if self.sidebar_scroll < self.max_scroll:
                pygame.draw.polygon(self.screen, (255, 255, 255),
                    [(self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH - 20, self.VIEWPORT_HEIGHT * self.TILE_SIZE - 10),
                     (self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH - 10, self.VIEWPORT_HEIGHT * self.TILE_SIZE - 20),
                     (self.VIEWPORT_WIDTH * self.TILE_SIZE + self.SIDEBAR_WIDTH - 30, self.VIEWPORT_HEIGHT * self.TILE_SIZE - 20)])
    
    def handle_click(self, pos):
        x, y = pos
        if x > self.VIEWPORT_WIDTH * self.TILE_SIZE:
            # Sidebar click
            self.handle_sidebar_click(x, y)
        else:
            # Map click
            self.handle_map_click(x, y)
    
    def handle_sidebar_click(self, x, y):
        sidebar_x = self.VIEWPORT_WIDTH * self.TILE_SIZE
        actual_y = y + self.sidebar_scroll  # Convert screen Y to scrolled Y
        y_offset = 10
        button_height = 30
        
        # Check category buttons
        for category in ["Tiles", "Items", "Rocks"]:
            button_rect = pygame.Rect(sidebar_x + 10, y_offset, self.SIDEBAR_WIDTH - 20, button_height)
            if button_rect.collidepoint(x, actual_y):
                self.selected_category = category
                return
            y_offset += button_height + 5
        
        y_offset += 10
        
        # Check items based on selected category
        if self.selected_category == "Tiles":
            for tile in [TileTypes.FLOOR, TileTypes.WALL, TileTypes.ROCK]:
                button_rect = pygame.Rect(sidebar_x + 10, y_offset, self.SIDEBAR_WIDTH - 20, self.TILE_SIZE)
                if button_rect.collidepoint(x, actual_y):
                    self.selected_tile = tile
                    self.selected_item = None
                    self.selected_rock_type = None
                    return
                y_offset += self.TILE_SIZE + 5
            
        elif self.selected_category == "Items":
            for item_name in self.available_items:
                button_rect = pygame.Rect(sidebar_x + 10, y_offset, self.SIDEBAR_WIDTH - 20, self.TILE_SIZE)
                if button_rect.collidepoint(x, actual_y):
                    self.selected_item = item_name
                    self.selected_tile = None
                    self.selected_rock_type = None
                    return
                y_offset += self.TILE_SIZE + 5
            
        elif self.selected_category == "Rocks":
            for rock_name in RockTypes.get_all_rocks():
                button_rect = pygame.Rect(sidebar_x + 10, y_offset, self.SIDEBAR_WIDTH - 20, self.TILE_SIZE)
                if button_rect.collidepoint(x, actual_y):
                    self.selected_rock_type = rock_name
                    self.selected_tile = TileTypes.ROCK
                    self.selected_item = None
                    return
                y_offset += self.TILE_SIZE + 5
    
    def handle_map_click(self, x, y):
        tile_x = x // self.TILE_SIZE + self.camera_x
        tile_y = y // self.TILE_SIZE + self.camera_y
        
        if (0 <= tile_x < len(self.current_map.tiles[0]) and 
            0 <= tile_y < len(self.current_map.tiles)):
            
            if self.sidebar.selected_tile is not None:
                self.current_map.tiles[tile_y][tile_x] = self.sidebar.selected_tile
                if self.sidebar.selected_rock_type:
                    rock_data = getattr(RockTypes, self.sidebar.selected_rock_type)
                    TileTypes.rock_data[(tile_x, tile_y)] = rock_data.copy()
            elif self.sidebar.selected_item:
                # Create the item and add it to the map
                new_item = ItemRegistry.create_item(self.sidebar.selected_item)
                self.current_map.items[(tile_x, tile_y)] = new_item
    
    def draw_map(self):
        # Calculate visible range
        start_x = int(self.camera_x)
        start_y = int(self.camera_y)
        end_x = min(start_x + self.VIEWPORT_WIDTH, self.MAP_WIDTH)
        end_y = min(start_y + self.VIEWPORT_HEIGHT, self.MAP_HEIGHT)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x, screen_y = self.world_to_screen(x, y)
                tile_type = self.current_map.tiles[y][x]
                tile_props = TileTypes.get_tile_properties(tile_type)
                
                pygame.draw.rect(self.screen, tile_props['color'],
                               (screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE))
                
                # Draw grid lines
                pygame.draw.rect(self.screen, (50, 50, 50),
                               (screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE), 1)
        
        # Draw items
        for pos, item in self.current_map.items.items():
            x, y = pos
            if start_x <= x < end_x and start_y <= y < end_y:
                screen_x, screen_y = self.world_to_screen(x, y)
                item.draw(self.screen, screen_x, screen_y, self.TILE_SIZE)
            
        # Draw player spawn point if visible
        spawn_x, spawn_y = self.current_map.player_spawn
        if (start_x <= spawn_x < end_x and start_y <= spawn_y < end_y):
            screen_x, screen_y = self.world_to_screen(spawn_x, spawn_y)
            pygame.draw.rect(self.screen, (255, 0, 0),
                           (screen_x + 5, screen_y + 5,
                            self.TILE_SIZE - 10, self.TILE_SIZE - 10))
    
    def handle_input(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # Scroll sidebar when mouse is over it
            mouse_x, _ = pygame.mouse.get_pos()
            if mouse_x >= self.VIEWPORT_WIDTH * self.TILE_SIZE:
                self.sidebar_scroll = max(0, min(self.max_scroll,
                    self.sidebar_scroll - event.y * 20))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    
                    # Handle sidebar interactions
                    if mouse_x > self.VIEWPORT_WIDTH * self.TILE_SIZE:
                        if event.button == 4:  # Mouse wheel up
                            self.sidebar.handle_scroll(True)
                        elif event.button == 5:  # Mouse wheel down
                            self.sidebar.handle_scroll(False)
                        elif event.button == 1:  # Left click
                            self.sidebar.handle_click(mouse_x, mouse_y)
                    # Handle map clicks
                    elif event.button == 1:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        try:
                            # Create maps directory if it doesn't exist
                            os.makedirs("maps", exist_ok=True)
                            
                            # Open save file dialog
                            filename = filedialog.asksaveasfilename(
                                initialdir="maps",
                                title="Save Map",
                                defaultextension=".json",
                                filetypes=[("JSON files", "*.json")]
                            )
                            
                            if filename:  # Only save if filename was provided
                                # Remove .json extension and maps/ prefix if present
                                filename = os.path.basename(filename)
                                filename = filename.replace('.json', '')
                                
                                self.current_map.save_to_file(filename)
                                self.show_message(f"Map saved as '{filename}'!")
                            else:
                                self.show_message("Save cancelled")
                        except Exception as e:
                            self.show_message(f"Error saving map: {str(e)}")
                            
                    elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        try:
                            # Open load file dialog
                            filename = filedialog.askopenfilename(
                                initialdir="maps",
                                title="Load Map",
                                filetypes=[("JSON files", "*.json")]
                            )
                            
                            if filename:  # Only load if filename was provided
                                # Remove .json extension and maps/ prefix if present
                                filename = os.path.basename(filename)
                                filename = filename.replace('.json', '')
                                
                                self.current_map = Map.load_from_file(filename)
                                self.MAP_WIDTH = len(self.current_map.tiles[0])
                                self.MAP_HEIGHT = len(self.current_map.tiles)
                                self.show_message(f"Map '{filename}' loaded!")
                                
                                # Reset camera position when loading new map
                                self.camera_x = 0
                                self.camera_y = 0
                            else:
                                self.show_message("Load cancelled")
                        except Exception as e:
                            self.show_message(f"Error loading map: {str(e)}")
                            
                    elif event.key == pygame.K_r:
                        try:
                            # Create a simple Tkinter dialog for dimensions
                            dialog = tk.Toplevel()
                            dialog.title("Resize Map")
                            dialog.geometry("200x150")
                            
                            width_var = tk.StringVar(value=str(self.MAP_WIDTH))
                            height_var = tk.StringVar(value=str(self.MAP_HEIGHT))
                            
                            tk.Label(dialog, text="Width:").pack(pady=5)
                            tk.Entry(dialog, textvariable=width_var).pack()
                            
                            tk.Label(dialog, text="Height:").pack(pady=5)
                            tk.Entry(dialog, textvariable=height_var).pack()
                            
                            def apply_resize():
                                try:
                                    new_width = int(width_var.get())
                                    new_height = int(height_var.get())
                                    self.resize_map(new_width, new_height)
                                    self.show_message(f"Map resized to {new_width}x{new_height}")
                                    dialog.destroy()
                                except ValueError:
                                    self.show_message("Invalid dimensions!")
                                    dialog.destroy()
                            
                            tk.Button(dialog, text="Resize", command=apply_resize).pack(pady=10)
                            
                            # Make dialog modal
                            dialog.transient(self.tk_root)
                            dialog.grab_set()
                            self.tk_root.wait_window(dialog)
                            
                        except Exception as e:
                            self.show_message(f"Error resizing map: {str(e)}")
            
            # Handle camera movement
            keys = pygame.key.get_pressed()
            self.handle_camera_movement(keys)
            
            # Handle input
            self.handle_input(event)
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Draw map and sidebar
            self.draw_map()
            self.sidebar.draw(self.screen)
            
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    editor = MapEditor()
    editor.run() 