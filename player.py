import pygame
from tile_types import TileTypes
from inventory import Inventory
from skills import Skills
from items import ItemRegistry
from map_data import Map

class Player:
    def __init__(self, tile_size, map_data):
        self.tile_size = tile_size
        self.map_data = map_data
        # Position in grid coordinates
        self.grid_x = 1
        self.grid_y = 1
        self.size = tile_size - 10  # Slightly smaller than tile
        self.color = (255, 0, 0)
        
        # Equipment slots
        self.equipment = {
            'head': None,
            'body': None,
            'main_hand': None,
            'off_hand': None,
            'legs': None,
            'feet': None
        }
        
        self.inventory = Inventory()
        self.inventory.player = self  # Add reference to player in inventory
        self.health = 100
        self.skills = Skills()  # Add skills system
        self.direction = 'right'  # Added for direction indicator
        self.smelting_timer = 0
        self.smelting_in_progress = False
        self.smelting_ores = None  # Will store (copper_slot, tin_slot) while smelting

    @property
    def equipped_item(self):
        """For backwards compatibility - returns main hand item"""
        return self.equipment['main_hand']
    
    @equipped_item.setter
    def equipped_item(self, item):
        """For backwards compatibility - sets main hand item"""
        self.equipment['main_hand'] = item

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.inventory.toggle()
                return
            
            # Close inventory for any other action
            self.inventory.is_open = False
            
            if event.key == pygame.K_e:
                # Get tile in front of player
                target_x, target_y = self.get_facing_tile()
                target_tile = self.map_data[target_y][target_x]
                tile_props = TileTypes.get_tile_properties(target_tile)
                
                # Check for bed interaction
                if tile_props.get('interactable', False) and target_tile == TileTypes.BED:
                    self.use_bed()
                # If facing a furnace, try smelting regardless of equipped item
                elif tile_props.get('smeltable', False):
                    self.try_smelting()
                # Otherwise, if we have a pickaxe equipped, try mining
                elif self.equipped_item and self.equipped_item.name == "Pickaxe":
                    self.use_equipped_item()
                return
            elif event.key == pygame.K_k:
                self.skills.toggle()
                return
            
            # Movement handling
            if event.key == pygame.K_LEFT:
                self.direction = 'left'
                if self.can_move(self.grid_x - 1, self.grid_y):
                    self.grid_x -= 1
                    self.check_for_items()
            elif event.key == pygame.K_RIGHT:
                self.direction = 'right'
                if self.can_move(self.grid_x + 1, self.grid_y):
                    self.grid_x += 1
                    self.check_for_items()
            elif event.key == pygame.K_UP:
                self.direction = 'up'
                if self.can_move(self.grid_x, self.grid_y - 1):
                    self.grid_y -= 1
                    self.check_for_items()
            elif event.key == pygame.K_DOWN:
                self.direction = 'down'
                if self.can_move(self.grid_x, self.grid_y + 1):
                    self.grid_y += 1
                    self.check_for_items()

    def draw(self, screen):
        # Draw player base
        screen_x = self.grid_x * self.tile_size
        screen_y = self.grid_y * self.tile_size
        pygame.draw.rect(screen, self.color, 
                        (screen_x + 5, screen_y + 5, self.size, self.size))
        
        # Draw direction indicator
        indicator_color = (255, 255, 0)  # Yellow
        indicator_size = 8
        center_x = screen_x + self.tile_size // 2
        center_y = screen_y + self.tile_size // 2
        
        if self.direction == 'right':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x + 5, center_y - 4, indicator_size, indicator_size))
        elif self.direction == 'left':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x - 13, center_y - 4, indicator_size, indicator_size))
        elif self.direction == 'up':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x - 4, center_y - 13, indicator_size, indicator_size))
        elif self.direction == 'down':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x - 4, center_y + 5, indicator_size, indicator_size))
        
        # Draw inventory if open
        self.inventory.draw(screen)
        # Draw skills if open
        self.skills.draw(screen)

    def draw_at_position(self, screen, screen_x, screen_y):
        # Draw player base
        pygame.draw.rect(screen, self.color, 
                        (screen_x + 5, screen_y + 5, self.size, self.size))
        
        # Draw direction indicator
        indicator_color = (255, 255, 0)  # Yellow
        indicator_size = 8
        center_x = screen_x + self.tile_size // 2
        center_y = screen_y + self.tile_size // 2
        
        if self.direction == 'right':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x + 5, center_y - 4, indicator_size, indicator_size))
        elif self.direction == 'left':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x - 13, center_y - 4, indicator_size, indicator_size))
        elif self.direction == 'up':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x - 4, center_y - 13, indicator_size, indicator_size))
        elif self.direction == 'down':
            pygame.draw.rect(screen, indicator_color, 
                            (center_x - 4, center_y + 5, indicator_size, indicator_size))

    def pickup_item(self, item):
        return self.inventory.add_item(item)

    def use_equipped_item(self):
        if self.equipped_item:
            target_x, target_y = self.get_facing_tile()
            self.equipped_item.use(self, target_x, target_y)

    def update(self):
        # Add this new method to handle smelting timer
        current_time = pygame.time.get_ticks()
        
        # Check if smelting is done
        if self.smelting_in_progress and current_time >= self.smelting_timer:
            self.complete_smelting()
    
    def try_smelting(self):
        # Get tile in front of player based on direction
        target_x, target_y = self.get_facing_tile()
        target_tile = self.map_data[target_y][target_x]
        tile_props = TileTypes.get_tile_properties(target_tile)
        
        if tile_props.get('smeltable', False) and not self.smelting_in_progress:
            # Check for required ores
            copper_ore = None
            tin_ore = None
            copper_slot = None
            tin_slot = None
            
            # Find copper and tin ores in inventory
            for i, item in enumerate(self.inventory.items):
                if item:
                    if item.name == "Copper Ore" and not copper_ore:
                        copper_ore = item
                        copper_slot = i
                    elif item.name == "Tin Ore" and not tin_ore:
                        tin_ore = item
                        tin_slot = i
            
            # If we have both ores, start smelting
            if copper_ore and tin_ore:
                # Remove the ores
                self.inventory.items[copper_slot] = None
                self.inventory.items[tin_slot] = None
                
                # Start smelting timer (2 seconds = 2000 milliseconds)
                self.smelting_timer = pygame.time.get_ticks() + 2000
                self.smelting_in_progress = True
                self.smelting_ores = (copper_slot, tin_slot)
                self.game.add_message("Smelting Bronze Bar...")
            else:
                self.game.add_message("Need 1 Copper Ore and 1 Tin Ore to smelt Bronze Bar")

    def get_facing_tile(self):
        target_x = self.grid_x
        target_y = self.grid_y
        
        if self.direction == 'right':
            target_x += 1
        elif self.direction == 'left':
            target_x -= 1
        elif self.direction == 'up':
            target_y -= 1
        elif self.direction == 'down':
            target_y += 1
        
        return target_x, target_y

    def complete_smelting(self):
        # Create and add bronze bar
        bronze_bar = ItemRegistry.create_item("bronze_bar")
        if self.inventory.add_item(bronze_bar):
            self.game.add_message("Successfully smelted a Bronze Bar!")
            # Award smithing XP
            self.skills.add_smithing_xp(20)
            self.game.add_message("20xp gained")
        else:
            self.game.add_message("Inventory full! Cannot smelt Bronze Bar.")
            # Return the ores to inventory if smelting_ores exists
            if self.smelting_ores:
                copper_slot, tin_slot = self.smelting_ores
                self.inventory.items[copper_slot] = ItemRegistry.create_item("copper_ore")
                self.inventory.items[tin_slot] = ItemRegistry.create_item("tin_ore")
        
        # Reset smelting state
        self.smelting_in_progress = False
        self.smelting_ores = None

    def can_move(self, x, y):
        # Check map bounds
        if x < 0 or x >= len(self.map_data[0]) or y < 0 or y >= len(self.map_data):
            return False
        
        # Get tile properties
        tile_type = self.map_data[y][x]
        tile_props = TileTypes.get_tile_properties(tile_type)
        
        # Return whether tile is walkable
        return tile_props.get('walkable', False)

    def check_for_items(self):
        current_pos = (self.grid_x, self.grid_y)
        if current_pos in self.game.ground_items:
            item = self.game.ground_items[current_pos]
            if self.inventory.add_item(item):
                del self.game.ground_items[current_pos]
                self.game.add_message(f"Picked up {item.name}")

    def use_bed(self):
        """Called when player interacts with bed"""
        print("Bed interaction triggered")  # Debug print
        self.game.add_message("Getting sleepy...")
        self.game.start_sleep_animation()

    def complete_sleep(self):
        """Called after sleep animation completes"""
        print("Sleep completion triggered")
        equipped_item = self.equipped_item
        
        # Reset game state
        self.game.state_manager.reset_state()
        
        # Update game's ground items reference
        self.game.ground_items = self.game.current_map.items
        
        # Restore equipped item
        self.equipped_item = equipped_item
        
        self.game.add_message("You wake up feeling refreshed!")