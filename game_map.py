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

            if sprite:
                pixel_x = building.x_grid * tile_size
                pixel_y = building.y_grid * tile_size

                sprite_w, sprite_h = sprite.get_size()
                offset_x = (tile_size - sprite_w) // 2
                offset_y = (tile_size - sprite_h) // 2
                sprite_draw_pos_x = pixel_x + offset_x
                sprite_draw_pos_y = pixel_y + offset_y

                surface.blit(sprite, (sprite_draw_pos_x, sprite_draw_pos_y))

                # Health bar settings
                bar_width = tile_size * 0.8
                bar_height = 6 # pixels
                # Position health bar above the sprite.
                # Use sprite_draw_pos_y as reference, then move further up.
                bar_offset_y = - (bar_height + 3) # Place above the top of the tile by a few pixels

                health_bar_x = pixel_x + (tile_size - bar_width) // 2 # Centered within the tile
                health_bar_y = pixel_y + bar_offset_y # Positioned relative to the top of the tile

                if building.max_health > 0:
                    health_ratio = building.health / building.max_health
                else:
                    health_ratio = 0

                current_health_width = bar_width * health_ratio

                # Draw health bar background (e.g., red or dark grey)
                pygame.draw.rect(surface, config.RED, (health_bar_x, health_bar_y, bar_width, bar_height))
                # Draw current health (e.g., green)
                if current_health_width > 0:
                    pygame.draw.rect(surface, config.GREEN, (health_bar_x, health_bar_y, current_health_width, bar_height))
                # Optional: Draw a border for the health bar
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
    screen_height = config.MAP_HEIGHT * config.TILE_SIZE # Test map only, no UI panel
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("GameMap Draw Test with Health Bars")

    game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)

    sample_buildings = []
    # Player building with full health
    player_th = Building(x_grid=3, y_grid=3, building_type_key="town_hall", owner="Player", health=500, max_health=500)
    sample_buildings.append(player_th)
    # Player building with partial health
    player_mine = Building(x_grid=5, y_grid=2, building_type_key="gold_mine", owner="Player", health=100, max_health=200)
    sample_buildings.append(player_mine)
    # AI building (assuming "ai_town_hall" key exists in assets and has some default health if not specified)
    # For this test, explicitly set health and max_health for AI building too.
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
    print("GameMap draw test with health bars finished.")
