# Handles the game map
import config

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Initialize an empty map (e.g., a 2D list of characters or None)
        self.grid = [['.' for _ in range(width)] for _ in range(height)]

    def get_map_representation(self): # New version
        return [' '.join(row) for row in self.grid]

    def is_valid_tile(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x, y):
        if self.is_valid_tile(x, y):
            return self.grid[y][x]
        return None

    def set_tile(self, x, y, tile_char):
        if self.is_valid_tile(x, y):
            self.grid[y][x] = tile_char
            return True
        return False

if __name__ == '__main__':
    # Basic test
    test_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)
    test_map.set_tile(5, 5, 'H')
    for row_str in test_map.get_map_representation():
        print(row_str)
