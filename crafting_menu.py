import pygame
from items import ItemRegistry

class CraftingRecipe:
    def __init__(self, name, level, material, bars_required):
        self.name = name
        self.level = level
        self.material = material
        self.bars_required = bars_required
        self.rect = None  # Store rectangle for hover detection

class CraftingMenu:
    def __init__(self):
        self.is_open = False
        self.hovered_recipe = None
        self.recipes = {
            "bronze": [
                CraftingRecipe("Bronze Dagger", 1, "bronze", 1),
                CraftingRecipe("Bronze Med Helm", 2, "bronze", 1),
                CraftingRecipe("Bronze Sword", 3, "bronze", 1),
                CraftingRecipe("Bronze Shield", 4, "bronze", 1),
                CraftingRecipe("Bronze Full Helm", 5, "bronze", 2),
                CraftingRecipe("Bronze Plate Legs", 6, "bronze", 3),
                CraftingRecipe("Bronze Long Sword", 7, "bronze", 2),
                CraftingRecipe("Bronze Scimitar", 8, "bronze", 2),
                CraftingRecipe("Bronze Plate Body", 9, "bronze", 5),
            ],
            "iron": [
                CraftingRecipe("Iron Dagger", 10, "iron", 1),
                # Add more iron recipes following the same pattern
            ]
        }
        
    def draw(self, screen, smithing_level):
        if not self.is_open:
            return
            
        padding = 10
        width = 400
        height = 300
        x = (screen.get_width() - width) // 2
        y = (screen.get_height() - height) // 2
        
        # Draw background
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        
        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_recipe = None
        
        # Draw available recipes
        font = pygame.font.Font(None, 24)
        y_offset = y + padding
        
        for material, recipes in self.recipes.items():
            for recipe in recipes:
                if smithing_level >= recipe.level:
                    # Create rectangle for hover detection
                    recipe.rect = pygame.Rect(x + padding, y_offset, width - (padding * 2), 25)
                    
                    # Check if mouse is hovering over this recipe
                    if recipe.rect.collidepoint(mouse_pos):
                        self.hovered_recipe = recipe
                        # Draw hover highlight
                        pygame.draw.rect(screen, (150, 150, 150), recipe.rect)
                    
                    text = f"{recipe.name} (Level {recipe.level}, {recipe.bars_required} bars)"
                    text_surface = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surface, (x + padding, y_offset))
                    y_offset += 30

    def handle_click(self, pos, player):
        if not self.is_open:
            return False
        
        # If we have a hovered recipe, craft it
        if self.hovered_recipe and player.skills.smithing_level >= self.hovered_recipe.level:
            self.craft_item(self.hovered_recipe, player)
            return True
            
        return False

    def craft_item(self, recipe, player):
        # Check if player has enough bars
        bars_found = 0
        bar_slots = []
        bar_name = f"{recipe.material.title()} Bar"
        
        for i, item in enumerate(player.inventory.items):
            if item and item.name == bar_name:
                bars_found += 1
                bar_slots.append(i)
                if bars_found >= recipe.bars_required:
                    break
        
        if bars_found >= recipe.bars_required:
            # Remove the bars
            for i in range(recipe.bars_required):
                player.inventory.items[bar_slots[i]] = None
            
            # Create the new item
            new_item = ItemRegistry.create_item(recipe.name.lower().replace(" ", "_"))
            if player.inventory.add_item(new_item):
                player.game.add_message(f"Successfully crafted {recipe.name}!")
                # Award smithing XP (10 * bars used)
                player.skills.add_smithing_xp(10 * recipe.bars_required)
            else:
                player.game.add_message("Inventory full! Cannot craft item.")
                # Return the bars
                for i in range(recipe.bars_required):
                    player.inventory.items[bar_slots[i]] = ItemRegistry.create_item(bar_name.lower().replace(" ", "_"))
        else:
            player.game.add_message(f"Need {recipe.bars_required} {bar_name}s to craft {recipe.name}")

    def close(self):
        self.is_open = False
        self.hovered_recipe = None 