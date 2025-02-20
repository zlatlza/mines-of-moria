from tile_types import TileTypes

class GameState:
    def __init__(self, map_data):
        self.map_data = map_data
        # Save initial state when game starts
        self.initial_state = {
            'items': {},
            'rocks': {},
            'tiles': []
        }
        self.save_initial_state()
        
    def save_initial_state(self):
        """Save the initial state of all resettable elements"""
        # Save initial items
        for pos, item in self.map_data.items.items():
            self.initial_state['items'][pos] = item.name
            
        # Save initial rock data
        for pos, data in TileTypes.rock_data.items():
            self.initial_state['rocks'][pos] = data.copy()
            
        # Save initial tiles
        self.initial_state['tiles'] = [
            [tile for tile in row] 
            for row in self.map_data.tiles
        ]
        
    def reset_state(self):
        """Reset all resettable elements to their initial state"""
        # Reset rocks and tiles
        for y in range(len(self.map_data.tiles)):
            for x in range(len(self.map_data.tiles[0])):
                tile = self.map_data.tiles[y][x]
                tile_props = TileTypes.get_tile_properties(tile)
                if tile_props.get('resettable', False):
                    self.map_data.tiles[y][x] = self.initial_state['tiles'][y][x]
                    
        # Reset rock data
        TileTypes.rock_data.clear()
        for pos, data in self.initial_state['rocks'].items():
            TileTypes.rock_data[pos] = data.copy()
            
        # Reset items
        self.map_data.items.clear()
        for pos, item_name in self.initial_state['items'].items():
            from items import ItemRegistry
            new_item = ItemRegistry.create_item(item_name)
            self.map_data.items[pos] = new_item 