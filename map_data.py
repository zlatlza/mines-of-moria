import json
from tile_types import TileTypes
from items import ItemRegistry
import os

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[TileTypes.WALL for x in range(width)] for y in range(height)]
        self.items = {}  # Current items on ground
        self.initial_items = {}  # Initial item positions
        self.initial_rock_data = {}  # Initial rock states
        self.player_spawn = (1, 1)
        
    @classmethod
    def load_from_file(cls, filename):
        """Load map from file"""
        with open(f"maps/{filename}.json", 'r') as f:
            data = json.load(f)
            
        map_instance = cls(data['width'], data['height'])
        map_instance.tiles = data['tiles']
        
        # Load items
        for pos_str, item_name in data['items'].items():
            # Convert string position to tuple
            pos = eval(pos_str)  # Safely converts "(x, y)" to (x, y)
            map_instance.items[pos] = ItemRegistry.create_item(item_name)
        
        # Load other data
        map_instance.player_spawn = tuple(data['player_spawn'])
        TileTypes.rock_data = data['rock_data']
        
        print("Map loaded from file")  # Debug print
        print("Initial items loaded:", map_instance.items)  # Debug print
        
        # Save initial state
        map_instance.save_initial_state()
        return map_instance
        
    def save_to_file(self, filename):
        # Create maps directory if it doesn't exist
        os.makedirs("maps", exist_ok=True)
        
        # Convert items dictionary to serializable format
        items_data = {}
        for pos, item in self.items.items():
            items_data[str(pos)] = item.name
            
        # Save rock data
        rock_data = {}
        for pos, rock_type in TileTypes.rock_data.items():
            rock_data[str(pos)] = rock_type
            
        data = {
            'width': self.width,
            'height': self.height,
            'tiles': self.tiles,
            'items': items_data,
            'player_spawn': list(self.player_spawn),
            'rock_data': rock_data  # Add rock data to save file
        }
        
        with open(f"maps/{filename}.json", "w") as f:
            json.dump(data, f, indent=2) 

    def save_initial_state(self):
        """Save the initial state of resettable elements"""
        # Save initial tile state
        self.initial_tiles = [[tile for tile in row] for row in self.tiles]
        
        # Save initial rock data
        self.initial_rock_data = {}
        for pos, data in TileTypes.rock_data.items():
            self.initial_rock_data[pos] = data
        
        # Save initial item positions and types
        self.initial_items = {}
        for pos, item in self.items.items():
            self.initial_items[pos] = item.name
        print("Initial state saved:")  # Debug print
        print("Initial items:", self.initial_items)  # Debug print

    def reset_map(self):
        """Reset resettable elements to their initial state"""
        print("Resetting map...")  # Debug print
        print("Initial items to restore:", self.initial_items)  # Debug print
        
        # Reset tiles that are marked as resettable
        for y in range(self.height):
            for x in range(self.width):
                tile_props = TileTypes.get_tile_properties(self.tiles[y][x])
                if tile_props.get('resettable', False):
                    self.tiles[y][x] = self.initial_tiles[y][x]
                    # If this was originally a rock, restore its data
                    if (x, y) in self.initial_rock_data:
                        TileTypes.rock_data[(x, y)] = self.initial_rock_data[(x, y)]
        
        # COMPLETELY RECREATE ALL INITIAL ITEMS
        # First, clear all current items
        self.items.clear()
        # Then spawn new instances of all initial items
        for pos, item_name in self.initial_items.items():
            new_item = ItemRegistry.create_item(item_name)
            self.items[pos] = new_item
            print(f"Respawned {item_name} at position {pos}")  # Debug print
        
        print("Current items after reset:", self.items)  # Debug print
        return True 