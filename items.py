import pygame
from tile_types import TileTypes

class ItemRegistry:
    _items = {}
    
    @classmethod
    def register_item(cls, item_class):
        """Register a class directly"""
        if item_class.__name__ in ['Ore', 'MetalBar']:
            # Don't register these base classes directly
            return item_class
        cls._items[item_class.__name__] = item_class
        return item_class
    
    @classmethod
    def register_item_type(cls, name, creator_func):
        """Register an item type with a custom name and creator function"""
        cls._items[name] = creator_func
        
    @classmethod
    def create_item(cls, item_name):
        if item_name not in cls._items:
            raise ValueError(f"Unknown item: {item_name}")
            
        item_creator = cls._items[item_name]
        if isinstance(item_creator, type):  # If it's a class
            return item_creator()
        return item_creator()  # If it's a lambda/function
    
    @classmethod
    def get_all_items(cls):
        # Return all registered items except base classes
        return [name for name in cls._items.keys()]

class Item:
    def __init__(self, name, description, icon_color=(200, 200, 0)):
        self.name = name
        self.description = description
        self.icon_color = icon_color
        self.equipped = False
        self.equippable = True  # Add default equippable property
        
    def draw(self, screen, x, y, size):
        pygame.draw.rect(screen, self.icon_color, 
                        (x + 5, y + 5, size - 12, size - 12))
        
    def use(self, player, target_x, target_y):
        pass
        
    def equip(self, player):
        if not self.equippable:
            player.game.add_message(f"{self.name} cannot be equipped")
            return
            
        if self.equipped:
            self.equipped = False
            player.equipped_item = None
            player.game.add_message(f"{self.name} unequipped")
        else:
            self.equipped = True
            player.equipped_item = self
            player.game.add_message(f"{self.name} equipped")

# Base classes (won't be registered directly)
class Ore(Item):
    def __init__(self, name, color):
        super().__init__(
            name=f"{name} Ore",
            description=f"Raw {name.lower()} ore from mining",
            icon_color=color
        )
        self.equippable = False

class MetalBar(Item):
    def __init__(self, name, color):
        super().__init__(
            name=f"{name} Bar",
            description=f"A {name.lower()} bar",
            icon_color=color
        )
        self.equippable = False

@ItemRegistry.register_item
class Pickaxe(Item):
    def __init__(self):
        super().__init__(
            name="Pickaxe",
            description="A sturdy pickaxe for mining",
            icon_color=(139, 69, 19)
        )
    
    def use(self, player, target_x, target_y):
        if not self.equipped:
            return
            
        target_tile = player.map_data[target_y][target_x]
        tile_props = TileTypes.get_tile_properties(target_tile, (target_x, target_y))
        
        print(f"Mining at position ({target_x}, {target_y})")  # Debug
        print(f"Tile properties: {tile_props}")  # Debug
        print(f"Rock data: {TileTypes.rock_data}")  # Debug
        
        if tile_props.get('mineable', False):
            required_level = tile_props.get('mining_level', 0)
            if player.skills.mining_level >= required_level:
                # Handle ore drops if it's a rock
                if target_tile == TileTypes.ROCK:
                    ore_type = tile_props.get('ore_type')
                    print(f"Found ore type: {ore_type}")  # Debug
                    
                    if ore_type:
                        # Create and add ore to inventory
                        ore_item = ItemRegistry.create_item(f"{ore_type}_ore")
                        if player.inventory.add_item(ore_item):
                            player.game.add_message(f"Added {ore_item.name} to inventory")
                            # Add and show XP gain
                            xp_gain = tile_props.get('mining_xp', 10)
                            player.skills.add_mining_xp(xp_gain)
                            player.game.add_message(f"{xp_gain}xp gained")
                        else:
                            player.game.add_message("Inventory full!")
                    
                    # Replace with depleted rock
                    player.map_data[target_y][target_x] = TileTypes.DEPLETED_ROCK
                else:
                    # Normal mining behavior for non-rock tiles
                    player.map_data[target_y][target_x] = TileTypes.FLOOR

# Register specific items with their creation functions
ItemRegistry.register_item_type("copper_ore", 
    lambda: Ore("Copper", (184, 115, 51)))
ItemRegistry.register_item_type("tin_ore", 
    lambda: Ore("Tin", (211, 212, 213)))
ItemRegistry.register_item_type("bronze_bar", 
    lambda: MetalBar("Bronze", (205, 127, 50)))

class Player:
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.try_smelting()
            # ... rest of input handling ...
    
    def try_smelting(self):
        # Get tile in front of player based on direction
        target_x, target_y = self.get_facing_tile()
        target_tile = self.map_data[target_y][target_x]
        tile_props = TileTypes.get_tile_properties(target_tile)
        
        if tile_props.get('smeltable', False):
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
            
            # If we have both ores, create bronze bar
            if copper_ore and tin_ore:
                # Remove the ores
                self.inventory.items[copper_slot] = None
                self.inventory.items[tin_slot] = None
                
                # Create and add bronze bar
                bronze_bar = ItemRegistry.create_item("bronze_bar")
                if self.inventory.add_item(bronze_bar):
                    print("Successfully smelted a Bronze Bar!")
                    # Award smithing XP
                    self.skills.add_smithing_xp(20)
                else:
                    print("Inventory full! Cannot smelt Bronze Bar.")
                    # Return the ores to inventory
                    self.inventory.items[copper_slot] = copper_ore
                    self.inventory.items[tin_slot] = tin_ore
            else:
                print("Need 1 Copper Ore and 1 Tin Ore to smelt Bronze Bar")
    
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