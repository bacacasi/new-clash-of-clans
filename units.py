# units.py

class Unit:
    def __init__(self, unit_type, health, attack_power):
        self.unit_type = unit_type
        self.health = health
        self.attack_power = attack_power
        # Future attributes: position (x,y), target, state, etc.

    def __str__(self):
        return f"{self.unit_type} (HP: {self.health}, ATK: {self.attack_power})"

UNIT_TYPES = {
    "barbarian": {
        "health": 50,
        "attack_power": 10,
        "cost": {"elixir": 25},
        "training_time": 5, # In game ticks, can be simplified for now
        "required_building": "barracks" # Example, can be simplified
    },
    "archer": {
        "health": 30,
        "attack_power": 7,
        "cost": {"elixir": 50},
        "training_time": 8,
        "required_building": "barracks"
    }
    # Add more unit types as needed
}
