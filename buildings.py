# Defines building types and their properties

class Building:
    def __init__(self, x, y, building_type="unknown", symbol="B", health=100):
        self.x = x
        self.y = y
        self.building_type = building_type
        self.symbol = symbol # Character to represent building on map
        self.health = health

    def __str__(self):
        return f"{self.building_type} at ({self.x}, {self.y}) with {self.health} HP"

    def take_damage(self, amount):
        self.health -= amount
        print(f"{self.building_type} at ({self.x}, {self.y}) took {amount} damage, remaining HP: {self.health}")
        if self.is_destroyed():
            print(f"{self.building_type} at ({self.x}, {self.y}) has been destroyed!")

    def is_destroyed(self):
        return self.health <= 0

# Define specific building types (can be expanded later)
BUILDING_TYPES = {
    "town_hall": {
        "symbol": "H",
        "health": 500,
        "cost": {"gold": 0}, # Free for the first one
        "generates": {"gold": 5} # Generates 5 gold per update cycle
    },
    "gold_mine": {
        "symbol": "G",
        "health": 200,
        "cost": {"gold": 50},
        "generates": {"gold": 20} # Generates 20 gold per update cycle
    },
    # Add other building types here if needed, e.g., for Elixir
    "elixir_collector": {
        "symbol": "E",
        "health": 150,
        "cost": {"gold": 75}, # Example cost
        "generates": {"elixir": 10}
    },
    "barracks": {
        "symbol": "B",
        "health": 300,
        "cost": {"gold": 100, "elixir": 50} # Example cost
        # Does not generate resources, but enables unit training
    }
}
