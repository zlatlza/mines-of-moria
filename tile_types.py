import pygame

class RockTypes:
    COPPER = {
        'name': 'Copper Rock',
        'color': (184, 115, 51),  # Copper brown
        'mining_level': 1,
        'mining_xp': 10,
        'ore_type': 'copper'
    }
    
    TIN = {
        'name': 'Tin Rock',
        'color': (211, 212, 213),  # Silvery gray
        'mining_level': 1,
        'mining_xp': 10,
        'ore_type': 'tin'
    }
    
    IRON = {
        'name': 'Iron Rock',
        'color': (136, 84, 44),  # Iron brown
        'mining_level': 15,
        'mining_xp': 35,
        'ore_type': 'iron'
    }
    
    @classmethod
    def get_all_rocks(cls):
        return {name: value for name, value in vars(cls).items() 
                if not name.startswith('_') and isinstance(value, dict)}

class TileTypes:
    # Tile type definitions
    FLOOR = 0
    WALL = 1
    ROCK = 2  # Generic rock type
    DEPLETED_ROCK = 3  # New tile type for mined rocks
    FURNACE = 4  # New furnace tile
    BED = 5  # New bed tile
    
    # Dictionary to store rock data for each tile position
    rock_data = {}  # Format: {(x, y): RockType}
    
    # Dictionary to store tile images
    tile_images = {}
    
    @classmethod
    def load_images(cls, tile_size):
        """Load and scale tile images"""
        cls.tile_images = {
            cls.WALL: pygame.transform.scale(
                pygame.image.load('assets/wall.webp').convert_alpha(),
                (tile_size, tile_size)
            )
        }
    
    @staticmethod
    def get_tile_properties(tile_type, position=None):
        """
        Returns a dictionary of properties for each tile type
        """
        base_properties = {
            TileTypes.FLOOR: {
                'name': 'Floor',
                'color': (100, 100, 100),
                'walkable': True,
                'mineable': False,
                'resettable': False  # Floor doesn't reset
            },
            TileTypes.WALL: {
                'name': 'Wall',
                'color': (50, 50, 50),
                'walkable': False,
                'mineable': True,
                'resettable': False,  # Walls stay mined
                'has_image': True  # New property to indicate image availability
            },
            TileTypes.ROCK: {
                'name': 'Rock',
                'color': (128, 128, 128),  # Default gray
                'walkable': False,
                'mineable': True,
                'resettable': True  # Rocks reset when sleeping
            },
            TileTypes.DEPLETED_ROCK: {
                'name': 'Depleted Rock',
                'color': (70, 70, 70),  # Darker gray
                'walkable': False,
                'mineable': False,
                'resettable': True  # Depleted rocks can reset
            },
            TileTypes.FURNACE: {
                'name': 'Furnace',
                'color': (200, 60, 20),  # Orange-red for furnace
                'walkable': False,
                'mineable': False,
                'smeltable': True,
                'resettable': False  # Furnaces don't reset
            },
            TileTypes.BED: {
                'name': 'Bed',
                'color': (150, 50, 150),  # Purple color for bed
                'walkable': False,
                'mineable': False,
                'interactable': True,
                'resettable': False  # Beds don't reset
            }
        }
        
        properties = base_properties.get(tile_type, base_properties[TileTypes.FLOOR]).copy()
        
        # If it's a rock tile and we have position data, update properties with rock-specific data
        if tile_type == TileTypes.ROCK and position in TileTypes.rock_data:
            rock_type = TileTypes.rock_data[position]
            properties.update({
                'name': rock_type['name'],
                'color': rock_type['color'],
                'mining_level': rock_type['mining_level'],
                'mining_xp': rock_type['mining_xp'],
                'ore_type': rock_type['ore_type']
            })
            
        return properties

    @staticmethod
    def set_rock_type(x, y, rock_type):
        """Set the rock type for a specific position"""
        TileTypes.rock_data[(x, y)] = rock_type
    
    @staticmethod
    def clear_rock_type(x, y):
        """Clear rock data when rock is mined"""
        TileTypes.rock_data.pop((x, y), None)

    @staticmethod
    def is_walkable(tile_type):
        """
        Quick helper method to check if a tile type can be walked on
        """
        properties = TileTypes.get_tile_properties(tile_type)
        return properties['walkable'] if properties else False