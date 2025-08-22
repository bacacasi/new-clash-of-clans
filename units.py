# units.py
import math # For vector calculations, distance
import config

class Unit:
    def __init__(self, x_pixel, y_pixel, unit_type_key, owner="Player",
                 health=50, attack_power=10, speed=2, attack_rate=60, attack_range=1.5):
        self.x = float(x_pixel)
        self.y = float(y_pixel)
        self.unit_type_key = unit_type_key
        self.owner = owner
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.attack_range = float(attack_range)

        self.speed = float(speed)
        self.target_x = None
        self.target_y = None
        self.is_moving = False
        self.selected = False

        self.attack_target_building = None
        self.attack_target_unit = None
        self.attack_cooldown = 0
        self.attack_rate = attack_rate
        # Attack range, in tiles. Unit stops when distance to target is less than this.
        # The range is specified in tiles (e.g. 4 tiles) and converted to pixels here.
        self.effective_attack_range_check = self.attack_range * config.TILE_SIZE

    def get_sprite_key(self):
        return self.unit_type_key

    @property
    def pos(self):
        return (self.x, self.y)

    def set_target(self, target_x, target_y, is_attack_move=False):
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.is_moving = True
        if not is_attack_move:
            self.attack_target_building = None
            self.attack_target_unit = None

    def update_movement(self):
        # If unit is attacking a dynamic target (a unit), update target coordinates
        if self.attack_target_unit:
            self.target_x = self.attack_target_unit.x
            self.target_y = self.attack_target_unit.y

        if not self.is_moving or self.target_x is None or self.target_y is None:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        # If unit has an attack target, check if it's close enough to stop moving and start attacking
        attack_target = self.attack_target_building or self.attack_target_unit
        if attack_target:
            if distance < self.effective_attack_range_check:
                self.is_moving = False
                # Keep target_x, target_y as they point to the target for attack orientation
                return

        if distance < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
            # Clear non-attack move targets upon arrival
            if not (self.attack_target_building or self.attack_target_unit):
                self.target_x = None
                self.target_y = None
        else:
            if distance > 0:
                norm_dx = dx / distance
                norm_dy = dy / distance
                self.x += norm_dx * self.speed
                self.y += norm_dy * self.speed

    def can_attack(self):
        return self.attack_cooldown <= 0

    def take_damage(self, amount):
        if amount <= 0: return
        self.health -= amount
        if self.health <= 0:
            self.health = 0

    def is_destroyed(self):
        return self.health <= 0

    def perform_attack(self, target):
        # This method is called by Game class after checking if unit.can_attack() is true
        # and if the target is still valid.
        if not target or target.is_destroyed(): # Double check
            self.attack_target_building = None
            self.attack_target_unit = None
            return False # No attack made

        # print(f"{self.owner}'s {self.unit_type_key} attacks target!") # Debug
        target.take_damage(self.attack_power)
        self.attack_cooldown = self.attack_rate # Reset cooldown

        if target.is_destroyed():
            # print(f"Target destroyed by {self.unit_type_key}") # Debug
            self.attack_target_building = None
            self.attack_target_unit = None
            self.is_moving = False
            self.target_x = None
            self.target_y = None
        return True # Attack was made

    def __str__(self):
        return f"{self.owner}'s {self.unit_type_key} at ({self.x:.1f},{self.y:.1f}) HP: {self.health} ATK: {self.attack_power}"

# Example usage (for testing this file independently):
if __name__ == '__main__':
    import config # Required for TILE_SIZE in Unit class

    class DummyBuilding:
        def __init__(self, x, y, owner="AI", health=100, type_key="dummy_barracks"):
            self.x_grid = x; self.y_grid = y; self.owner = owner
            self.health = health; self.max_health = health; self.building_type_key = type_key
        def take_damage(self, amount): self.health -= amount; print(f"DUMMY: {self.building_type_key} took {amount} dmg, HP: {self.health}")
        def is_destroyed(self): return self.health <= 0

    # --- Test Melee Unit ---
    print("--- Melee Unit Test ---")
    melee_unit = Unit(0, 0, "test_melee", speed=10, attack_range=1.5)
    target_building = DummyBuilding(0,0, health=50) # at grid (0,0) -> center pixel (16,16)
    target_pixel_x = target_building.x_grid * config.TILE_SIZE + config.TILE_SIZE / 2
    target_pixel_y = target_building.y_grid * config.TILE_SIZE + config.TILE_SIZE / 2

    melee_unit.attack_target_building = target_building
    melee_unit.set_target(target_pixel_x, target_pixel_y, is_attack_move=True)

    stopped_in_range = False
    for _ in range(20):
        melee_unit.update_movement()
        if not melee_unit.is_moving:
            dist = math.hypot(target_pixel_x - melee_unit.x, target_pixel_y - melee_unit.y)
            print(f"Melee unit stopped at distance: {dist:.1f}. Target range: {melee_unit.effective_attack_range_check:.1f}")
            if dist < melee_unit.effective_attack_range_check:
                stopped_in_range = True
            break
    assert stopped_in_range, "Melee unit did not stop within its attack range."
    print("Melee unit test passed.")

    # --- Test Ranged Unit ---
    print("\n--- Ranged Unit Test ---")
    archer = Unit(0, 0, "test_archer", speed=10, attack_range=4) # Archer with 4 tile range
    target_building_ranged = DummyBuilding(5, 0, health=50) # at grid (5,0) -> center pixel (176, 16)
    target_pixel_x_ranged = target_building_ranged.x_grid * config.TILE_SIZE + config.TILE_SIZE / 2
    target_pixel_y_ranged = target_building_ranged.y_grid * config.TILE_SIZE + config.TILE_SIZE / 2

    archer.attack_target_building = target_building_ranged
    archer.set_target(target_pixel_x_ranged, target_pixel_y_ranged, is_attack_move=True)

    stopped_in_range_ranged = False
    for _ in range(30):
        archer.update_movement()
        if not archer.is_moving:
            dist = math.hypot(target_pixel_x_ranged - archer.x, target_pixel_y_ranged - archer.y)
            print(f"Ranged unit stopped at distance: {dist:.1f}. Target range: {archer.effective_attack_range_check:.1f}")
            if dist < archer.effective_attack_range_check:
                stopped_in_range_ranged = True
            break
    assert stopped_in_range_ranged, "Ranged unit did not stop within its attack range."
    print("Ranged unit test passed.")
