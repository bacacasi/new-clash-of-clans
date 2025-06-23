# units.py
import math # For vector calculations, distance

class Unit:
    def __init__(self, x_pixel, y_pixel, unit_type_key, owner="Player",
                 health=50, attack_power=10, speed=2, attack_rate=60):
        self.x = float(x_pixel)
        self.y = float(y_pixel)
        self.unit_type_key = unit_type_key
        self.owner = owner
        self.health = health
        self.max_health = health
        self.attack_power = attack_power

        self.speed = float(speed)
        self.target_x = None
        self.target_y = None
        self.is_moving = False
        self.selected = False

        self.attack_target_building = None
        self.attack_cooldown = 0
        self.attack_rate = attack_rate
        # Attack range: A unit will stop moving towards its attack_target_building
        # if distance is less than tile_size (e.g. it's on an adjacent tile to the building's center tile)
        # This means it doesn't have to be exactly on the building's center pixel to stop and attack.
        self.effective_attack_range_check = config.TILE_SIZE * 0.8 # Stop a bit before the center

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

    def update_movement(self):
        if not self.is_moving or self.target_x is None or self.target_y is None:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        # If unit has an attack target, check if it's close enough to stop moving and start attacking
        if self.attack_target_building:
            # Consider a slightly larger range for stopping than for attacking, to prevent jittering
            # Or use a fixed range like one tile_size.
            # If the target is the building's center, effective_attack_range_check should be small.
            # If target is building edge, then range check is different.
            # For now, target is building center, stop if within ~0.8 of a tile.
            if distance < self.effective_attack_range_check:
                self.is_moving = False
                # Keep target_x, target_y as they point to the building center for attack orientation (if needed later)
                return

        if distance < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
            if not self.attack_target_building: # Clear non-attack targets
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

    def perform_attack(self, target_building):
        # This method is called by Game class after checking if unit.can_attack() is true
        # and if target_building is still valid.
        if not target_building or target_building.is_destroyed(): # Double check
            self.attack_target_building = None # Clear invalid target
            return False # No attack made

        # print(f"{self.owner}'s {self.unit_type_key} attacks {target_building.owner}'s {target_building.building_type_key}!") # Debug
        target_building.take_damage(self.attack_power)
        self.attack_cooldown = self.attack_rate # Reset cooldown

        if target_building.is_destroyed():
            # print(f"{target_building.building_type_key} destroyed by {self.unit_type_key}") # Debug
            self.attack_target_building = None
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

    unit = Unit(0, 0, "test_unit", speed=5, attack_power=10, attack_rate=60)
    # Target building's center is effectively (16,16) if its grid (0,0) and TILE_SIZE is 32
    # Let's place building at grid (0,0) for simplicity, so its center is (16,16)
    # Unit starts at (0,0) pixel.
    target_building_center_x = config.TILE_SIZE / 2
    target_building_center_y = config.TILE_SIZE / 2
    target_building = DummyBuilding(0,0, health=50)

    print("--- Movement to Attack Target Test ---")
    unit.attack_target_building = target_building
    unit.set_target(target_building_center_x, target_building_center_y, is_attack_move=True)

    attacked_once = False
    for i in range(10): # Simulate game loop
        unit.update_movement()
        print(f"Update {i+1}: Unit at ({unit.x:.1f},{unit.y:.1f}), Moving: {unit.is_moving}, CD: {unit.attack_cooldown}")

        if not unit.is_moving and unit.attack_target_building:
            print("Unit reached attack position.")
            if unit.can_attack():
                if unit.perform_attack(unit.attack_target_building):
                    attacked_once = True
                    print("Unit performed attack.")
            else:
                unit.attack_cooldown -=1
                print(f"Attack cooling down: {unit.attack_cooldown}")

            if unit.attack_target_building and unit.attack_target_building.is_destroyed():
                print("Target destroyed, unit cleared target.")
                break
            elif not unit.attack_target_building:
                break
        if i > 7 and not unit.is_moving and not unit.attack_target_building : # safety break if something unexpected
             print("Exiting test loop early")
             break

    assert attacked_once, "Unit did not perform an attack"
    assert target_building.health < target_building.max_health, "Unit did not damage building"
    print(f"Target health after attack simulation: {target_building.health}")
    print("\nAll Unit attack-related tests passed conceptually.")
