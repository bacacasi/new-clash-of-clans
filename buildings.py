# buildings.py

class Building:
    def __init__(self, x_grid, y_grid, building_type_key, owner="Player", health=100, max_health=100):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.building_type_key = building_type_key
        self.owner = owner
        self.health = health
        self.max_health = max_health
        self.selected = False

    def get_sprite_key(self):
        return self.building_type_key

    @property
    def grid_pos(self):
        return (self.x_grid, self.y_grid)

    def take_damage(self, amount):
        if amount <= 0: return
        self.health -= amount
        # print(f"{self.owner}'s {self.building_type_key} took {amount} damage, HP: {self.health}/{self.max_health}") # Debug
        if self.health <= 0:
            self.health = 0
            # print(f"{self.owner}'s {self.building_type_key} has been destroyed.") # Debug
            # Actual removal from game lists will be handled by the Game class

    def is_destroyed(self):
        return self.health <= 0

    def __str__(self):
        return f"{self.owner}'s {self.building_type_key} at ({self.x_grid},{self.y_grid}) HP: {self.health}/{self.max_health}"

if __name__ == '__main__':
    b = Building(5,5, "test_b", health=100, max_health=100)
    print(b)
    b.take_damage(30)
    assert b.health == 70
    print(b)
    assert not b.is_destroyed()
    b.take_damage(80)
    assert b.health == 0
    assert b.is_destroyed()
    print(b)
    print("Building class tests with damage passed.")

class Ruin:
    def __init__(self, x_grid, y_grid, building_type_key):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.building_type_key = building_type_key
