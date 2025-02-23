import pygame

class CraftingRecipe:
    def __init__(self, name, level, material, bars_required):
        self.name = name
        self.level = level
        self.material = material
        self.bars_required = bars_required

class CraftingMenu:
    def __init__(self):
        self.is_open = False
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
        
        # Draw available recipes
        font = pygame.font.Font(None, 24)
        y_offset = y + padding
        
        for material, recipes in self.recipes.items():
            for recipe in recipes:
                if smithing_level >= recipe.level:
                    text = f"{recipe.name} (Level {recipe.level}, {recipe.bars_required} bars)"
                    text_surface = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surface, (x + padding, y_offset))
                    y_offset += 30 

    def handle_click(self, pos, player):
        if not self.is_open:
            return False
        
        x, y = pos
        padding = 10
        width = 400
        height = 300
        menu_x = (pygame.display.get_surface().get_width() - width) // 2
        menu_y = (pygame.display.get_surface().get_height() - height) // 2
        
        # Check if click is within menu bounds
        if not (menu_x <= x <= menu_x + width and menu_y <= y <= menu_y + height):
            return False
        
        # Calculate which recipe was clicked
        y_offset = menu_y + padding
        click_index = (y - y_offset) // 30
        
        current_index = 0
        for material, recipes in self.recipes.items():
            for recipe in recipes:
                if player.skills.smithing_level >= recipe.level:
                    if current_index == click_index:
                        self.craft_item(recipe, player)
                        return True
                    current_index += 1
        
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