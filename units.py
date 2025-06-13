# units.py (simplified for graphical integration)

class Unit:
    def __init__(self, x_pixel, y_pixel, unit_type_key, owner="Player", health=50, attack_power=10):
        self.x = x_pixel # Pixel X coordinate on the map
        self.y = y_pixel # Pixel Y coordinate on the map
        self.unit_type_key = unit_type_key # e.g., "barbarian", "ai_barbarian"
        self.owner = owner
        self.health = health
        self.attack_power = attack_power
        # The actual sprite will be fetched using unit_type_key from assets.py

    def get_sprite_key(self):
        """
        Determines the key for fetching the sprite from assets.py.
        This assumes that if a unit is AI-owned, its unit_type_key is already
        prefixed (e.g., "ai_barbarian") if different sprites are defined in assets.py.
        If assets.py's get_unit_sprite handles owner distinction more directly,
        this method might be simplified or removed.
        """
        return self.unit_type_key

    @property
    def pos(self):
        return (self.x, self.y)

    def __str__(self):
        return f"{self.owner}'s {self.unit_type_key} at ({self.x},{self.y}) HP: {self.health} ATK: {self.attack_power}"

# We'll use TEMP_UNIT_GRAPHICS_INFO in assets.py to get sprite details for now.
# Full UNIT_TYPES dictionary (like in the text-based version) is not strictly needed here
# if assets.py and config.py handle all static properties required for graphics.
# For gameplay logic (cost, training time), we'll need to reintegrate the full version later.

# Example usage (for testing this file independently):
if __name__ == '__main__':
    player_barb = Unit(x_pixel=100, y_pixel=150, unit_type_key="barbarian", owner="Player")
    # For AI units, if assets.py has a specific key like "ai_barbarian", use that.
    ai_barb = Unit(x_pixel=200, y_pixel=250, unit_type_key="ai_barbarian", owner="AI")

    print(player_barb)
    print(f"Player Barbarian sprite key: {player_barb.get_sprite_key()}")
    print(ai_barb)
    print(f"AI Barbarian sprite key: {ai_barb.get_sprite_key()}")

    assert player_barb.get_sprite_key() == "barbarian"
    assert ai_barb.get_sprite_key() == "ai_barbarian" # This assumes assets.py has "ai_barbarian"
    print("Basic Unit class tests passed.")
