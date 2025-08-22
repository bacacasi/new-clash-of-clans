# game_map.py
import pygame
import config # For TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, colors

class GameMap:
    def __init__(self, map_width_tiles, map_height_tiles):
        self.width_tiles = map_width_tiles
        self.height_tiles = map_height_tiles
        self.grid = [['.' for _ in range(map_width_tiles)] for _ in range(map_height_tiles)]

    def draw(self, surface, assets_module, tile_size, all_buildings):
        for x_idx in range(self.width_tiles + 1):
            px = x_idx * tile_size
            pygame.draw.line(surface, config.BLACK, (px, 0), (px, self.height_tiles * tile_size))
        for y_idx in range(self.height_tiles + 1):
            py = y_idx * tile_size
            pygame.draw.line(surface, config.BLACK, (0, py), (self.width_tiles * tile_size, py))

        for building in all_buildings:
            sprite_key = building.building_type_key
            sprite = assets_module.get_building_sprite(sprite_key, tile_size)

            pixel_x = building.x_grid * tile_size
            pixel_y = building.y_grid * tile_size

            if sprite:
                sprite_w, sprite_h = sprite.get_size()
                offset_x = (tile_size - sprite_w) // 2
                offset_y = (tile_size - sprite_h) // 2
                sprite_draw_pos_x = pixel_x + offset_x
                sprite_draw_pos_y = pixel_y + offset_y

                surface.blit(sprite, (sprite_draw_pos_x, sprite_draw_pos_y))

            # Selection Highlight
            if building.selected:
                selection_rect = pygame.Rect(pixel_x, pixel_y, tile_size, tile_size)
                pygame.draw.rect(surface, config.CYAN, selection_rect, 3) # Cyan border, 3px thick

            # Health bar for damaged buildings
            if hasattr(building, 'health') and hasattr(building, 'max_health') and building.health < building.max_health:
                bar_width = tile_size * 0.8
                bar_height = 6
                bar_offset_y = - (bar_height + 3)

                health_bar_x = pixel_x + (tile_size - bar_width) // 2
                health_bar_y = pixel_y + bar_offset_y

                if building.max_health > 0:
                    health_ratio = max(0, min(1, building.health / building.max_health))
                else:
                    health_ratio = 0

                current_health_width = bar_width * health_ratio

                # Background (red)
                pygame.draw.rect(surface, config.RED, (health_bar_x, health_bar_y, bar_width, bar_height))
                # Foreground (green)
                if current_health_width > 0:
                    pygame.draw.rect(surface, config.GREEN, (health_bar_x, health_bar_y, current_health_width, bar_height))
                # Border
                pygame.draw.rect(surface, config.BLACK, (health_bar_x, health_bar_y, bar_width, bar_height), 1)


    def is_valid_grid_pos(self, x_grid, y_grid):
        return 0 <= x_grid < self.width_tiles and 0 <= y_grid < self.height_tiles

    def get_tile_symbol(self, x_grid, y_grid):
        if self.is_valid_grid_pos(x_grid, y_grid):
            return self.grid[y_grid][x_grid]
        return None

    def set_tile_symbol(self, x_grid, y_grid, symbol):
        if self.is_valid_grid_pos(x_grid, y_grid):
            self.grid[y_grid][x_grid] = symbol
            return True
        return False

if __name__ == '__main__':
    pygame.init()
    import assets
    from buildings import Building

    screen_width = config.MAP_WIDTH * config.TILE_SIZE
    screen_height = config.MAP_HEIGHT * config.TILE_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("GameMap Draw Test with Selection & Health Bars")

    game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)

    sample_buildings = []
    player_th = Building(x_grid=3, y_grid=3, building_type_key="town_hall", owner="Player", health=500, max_health=500)
    player_th.selected = True # Test selection
    sample_buildings.append(player_th)

    player_mine = Building(x_grid=5, y_grid=2, building_type_key="gold_mine", owner="Player", health=100, max_health=200)
    sample_buildings.append(player_mine)

    ai_th = Building(x_grid=config.MAP_WIDTH - 4, y_grid=config.MAP_HEIGHT - 4,
                     building_type_key="ai_town_hall", owner="AI", health=300, max_health=600)
    sample_buildings.append(ai_th)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(config.GREY)
        game_map.draw(screen, assets, config.TILE_SIZE, sample_buildings)
        pygame.display.flip()

    pygame.quit()
    print("GameMap draw test with selection and health bars finished.")
