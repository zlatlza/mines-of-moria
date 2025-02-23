class MenuManager:
    def __init__(self):
        self.active_menus = []
        
    def open_menu(self, menu):
        self.active_menus.append(menu)
        menu.is_open = True
        
    def close_all_menus(self):
        for menu in self.active_menus:
            menu.is_open = False
        self.active_menus.clear()
        
    def close_menu(self, menu):
        if menu in self.active_menus:
            self.active_menus.remove(menu)
            menu.is_open = False 