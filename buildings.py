# buildings.py (simplified for graphical integration)

class Building:
    def __init__(self, x_grid, y_grid, building_type_key, owner="Player", health=100, max_health=100):
        self.x_grid = x_grid  # Grid X
        self.y_grid = y_grid  # Grid Y
        self.building_type_key = building_type_key  # e.g., "town_hall", "ai_gold_mine"
        self.owner = owner
        self.health = health
        self.max_health = max_health
        # The actual sprite will be fetched using building_type_key from assets.py.
        # The `symbol` attribute from the text-based version is not explicitly needed here
        # if rendering relies on `building_type_key` and `owner` to fetch sprites.
        # However, if GameMap uses symbols for quick checks, it could be re-added.

    def get_sprite_key(self):
        """
        Determines the key to use for fetching the sprite from assets.
        This version assumes that if a building is AI-owned, its
        building_type_key is already prefixed e.g., "ai_town_hall".
        If assets.py's get_building_sprite handles owner distinction
        more directly, this method might be simplified or removed.
        """
        return self.building_type_key

    @property
    def grid_pos(self):
        return (self.x_grid, self.y_grid)

    def __str__(self):
        return f"{self.owner}'s {self.building_type_key} at ({self.x_grid},{self.y_grid}) HP: {self.health}/{self.max_health}"

# Full BUILDING_TYPES dictionary (like in the text-based version) is not strictly needed here
# if assets.py (TEMP_BUILDING_GRAPHICS_INFO) and config.py handle all static properties
# required for graphics and basic gameplay.
# For gameplay logic (cost, generation rates), we'll need to reintegrate the full version later.

# Example usage (for testing this file independently, if needed):
if __name__ == '__main__':
    # This test won't show graphics but can test the class structure.
    # For graphical tests, assets.py and a pygame loop are needed.
    player_th = Building(x_grid=5, y_grid=5, building_type_key="town_hall", owner="Player", health=500, max_health=500)
    ai_mine = Building(x_grid=10, y_grid=10, building_type_key="ai_gold_mine", owner="AI", health=150, max_health=200)

    print(player_th)
    print(f"Player TH sprite key: {player_th.get_sprite_key()}")
    print(ai_mine)
    print(f"AI Mine sprite key: {ai_mine.get_sprite_key()}")

    # Verify that building_type_key directly reflects AI ownership for sprites
    # This means when creating an AI building, its type_key should be e.g. "ai_town_hall"
    # if assets.py uses such keys.
    assert player_th.get_sprite_key() == "town_hall"
    assert ai_mine.get_sprite_key() == "ai_gold_mine"
    print("Basic Building class tests passed.")
