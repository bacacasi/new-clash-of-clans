# Main game file
import time
import config
import random # For AI
import json # For saving/loading
import os # For checking file existence

from game_map import GameMap
from buildings import Building, BUILDING_TYPES
from units import Unit, UNIT_TYPES

class Game:
    def __init__(self):
        self.game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)
        self.is_running = True
        self.player_resources = {"gold": 100, "elixir": 50} # Example resources
        self.buildings = []
        self.units = []
        self.place_building("town_hall", config.MAP_WIDTH // 2, config.MAP_HEIGHT // 2, is_initial=True)

        # AI opponent initialization
        self.ai_resources = {"gold": 100, "elixir": 50}
        self.ai_buildings = []
        self.ai_units = []

        # AI starting position (e.g., opposite side of player)
        ai_start_x = config.MAP_WIDTH - 1 - (config.MAP_WIDTH // 2)
        ai_start_y = config.MAP_HEIGHT // 2
        self.place_ai_building("town_hall", ai_start_x, ai_start_y, is_initial=True)
        self.place_ai_building("gold_mine", ai_start_x, ai_start_y - 2, is_initial=True) # Place it nearby
        self.place_ai_building("barracks", ai_start_x, ai_start_y + 2, is_initial=True)


    def run(self):
        print("Starting Clash of Clans (Local Version)...")
        # Try to load game at start, if you want to auto-load
        # if os.path.exists("clash_save.json"):
        #    self.load_game("clash_save.json")

        while self.is_running:
            self.update()
            self.render()
            self.handle_input()
            time.sleep(1 / config.GAME_SPEED)

    def update(self):
        # Player Resource Generation
        for building in self.buildings:
            building_details = BUILDING_TYPES.get(building.building_type)
            if building_details and "generates" in building_details:
                generation_info = building_details["generates"]
                for resource, amount in generation_info.items():
                    self.player_resources[resource] = self.player_resources.get(resource, 0) + amount

        # AI Resource Generation
        for building in list(self.ai_buildings):
            building_details = BUILDING_TYPES.get(building.building_type)
            if building_details and "generates" in building_details:
                generation_info = building_details["generates"]
                for resource, amount in generation_info.items():
                    self.ai_resources[resource] = self.ai_resources.get(resource, 0) + amount

        # AI Build Logic: Gold Mine
        num_ai_gold_mines = sum(1 for b in self.ai_buildings if b.building_type == "gold_mine")
        ai_th = next((b for b in self.ai_buildings if b.building_type == "town_hall" and b.owner == "AI"), None)
        if ai_th and num_ai_gold_mines < 2 and self.ai_resources.get("gold", 0) >= BUILDING_TYPES["gold_mine"]["cost"].get("gold", 50):
            placed_second_mine = False
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0: continue
                    check_x, check_y = ai_th.x + dx, ai_th.y + dy
                    if self.game_map.is_valid_tile(check_x, check_y) and self.game_map.get_tile(check_x, check_y) == '.':
                        if self.place_ai_building("gold_mine", check_x, check_y):
                            placed_second_mine = True; break
                if placed_second_mine: break

        # AI Train Logic: Barbarian
        num_ai_barbarians = sum(1 for u in self.ai_units if u.unit_type == "barbarian")
        if num_ai_barbarians < 10 and any(b.building_type == "barracks" for b in self.ai_buildings):
            if self.ai_resources.get("elixir", 0) >= UNIT_TYPES["barbarian"]["cost"].get("elixir", 25):
                self.train_ai_unit("barbarian")

        # AI Attack Logic
        if sum(1 for u in self.ai_units if u.unit_type == "barbarian" and u.owner == "AI") >= 3:
            player_buildings_alive = [b for b in self.buildings if b.owner == "Player" and not b.is_destroyed()]
            if player_buildings_alive:
                target_player_building = random.choice(player_buildings_alive)
                self.ai_execute_attack("barbarian", target_player_building)
        pass

    def _building_to_dict(self, building):
        return {
            "type": building.building_type, "x": building.x, "y": building.y,
            "health": building.health, "symbol": building.symbol, "owner": building.owner
        }

    def _unit_to_dict(self, unit):
        return {
            "type": unit.unit_type, "health": unit.health,
            "attack_power": unit.attack_power, "owner": unit.owner
        }

    def save_game(self, filename="clash_save.json"):
        game_state = {
            "player_resources": self.player_resources,
            "player_buildings": [self._building_to_dict(b) for b in self.buildings],
            "player_units": [self._unit_to_dict(u) for u in self.units],
            "ai_resources": self.ai_resources,
            "ai_buildings": [self._building_to_dict(b) for b in self.ai_buildings],
            "ai_units": [self._unit_to_dict(u) for u in self.ai_units],
        }
        try:
            with open(filename, 'w') as f:
                json.dump(game_state, f, indent=4)
            print(f"Game saved to {filename}")
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_game(self, filename="clash_save.json"):
        if not os.path.exists(filename):
            print(f"Save file {filename} not found.")
            return False
        try:
            with open(filename, 'r') as f:
                game_state = json.load(f)

            self.game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)
            self.buildings = []
            self.units = []
            self.ai_buildings = []
            self.ai_units = []

            self.player_resources = game_state.get("player_resources", {"gold": 100, "elixir": 50})
            for b_data in game_state.get("player_buildings", []):
                b = Building(b_data["x"], b_data["y"], b_data["type"], b_data["symbol"], b_data["health"])
                b.owner = b_data.get("owner", "Player")
                self.buildings.append(b)
                self.game_map.set_tile(b.x, b.y, b.symbol)

            for u_data in game_state.get("player_units", []):
                u = Unit(u_data["type"], u_data["health"], u_data["attack_power"])
                u.owner = u_data.get("owner", "Player")
                self.units.append(u)

            self.ai_resources = game_state.get("ai_resources", {"gold": 100, "elixir": 50})
            for b_data in game_state.get("ai_buildings", []):
                b = Building(b_data["x"], b_data["y"], b_data["type"], b_data["symbol"], b_data["health"])
                b.owner = b_data.get("owner", "AI")
                self.ai_buildings.append(b)
                self.game_map.set_tile(b.x, b.y, b.symbol)

            for u_data in game_state.get("ai_units", []):
                u = Unit(u_data["type"], u_data["health"], u_data["attack_power"])
                u.owner = u_data.get("owner", "AI")
                self.ai_units.append(u)

            print(f"Game loaded from {filename}")
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def render(self):
        print("\n" * 50)
        output_lines = []
        output_lines.append("--- MAP " + "-" * (config.MAP_WIDTH * 2 - 6))
        map_repr = self.game_map.get_map_representation()
        output_lines.extend(map_repr)
        output_lines.append("-" * (config.MAP_WIDTH * 2))

        output_lines.append("--- RESOURCES ---")
        resource_strings = []
        for res, amount in self.player_resources.items():
            resource_strings.append(f"{res.capitalize()}: {amount}")
        output_lines.append(" | ".join(resource_strings))

        output_lines.append("--- YOUR BUILDINGS ---")
        player_b_sorted = sorted([b for b in self.buildings if b.owner == "Player"], key=lambda build: build.building_type)
        if not player_b_sorted: output_lines.append("  No buildings constructed.")
        else:
            for b in player_b_sorted: output_lines.append(f"  - {b.building_type} ({b.x},{b.y}) HP: {b.health}/{BUILDING_TYPES[b.building_type]['health']}")

        output_lines.append("--- AI BUILDINGS ---")
        ai_b_sorted = sorted([b for b in self.ai_buildings if b.owner == "AI"], key=lambda build: build.building_type)
        if not ai_b_sorted: output_lines.append("  AI has no buildings.")
        else:
            for b in ai_b_sorted: output_lines.append(f"  - {b.building_type} ({b.x},{b.y}) HP: {b.health}/{BUILDING_TYPES[b.building_type]['health']} (Symbol: {b.symbol})")

        output_lines.append("--- YOUR UNITS ---")
        player_unit_counts = {}
        for unit in [u for u in self.units if u.owner == "Player"]: player_unit_counts[unit.unit_type] = player_unit_counts.get(unit.unit_type, 0) + 1
        if not player_unit_counts: output_lines.append("  No units trained.")
        else:
            for unit_type, count in player_unit_counts.items():
                details = UNIT_TYPES[unit_type]
                output_lines.append(f"  - {unit_type.capitalize()}: {count} (HP: {details['health']}, ATK: {details['attack_power']})")

        output_lines.append("--- AI UNITS ---")
        ai_unit_counts = {}
        for unit in [u for u in self.ai_units if u.owner == "AI"]: ai_unit_counts[unit.unit_type] = ai_unit_counts.get(unit.unit_type, 0) + 1
        if not ai_unit_counts: output_lines.append("  AI has no units.")
        else:
            for unit_type, count in ai_unit_counts.items():
                details = UNIT_TYPES[unit_type]
                output_lines.append(f"  - {unit_type.capitalize()}: {count} (HP: {details['health']}, ATK: {details['attack_power']})")
        output_lines.append("=" * (config.MAP_WIDTH * 2))
        for line in output_lines: print(line)

    def place_ai_building(self, building_type_name, x, y, is_initial=False):
        if not self.game_map.is_valid_tile(x, y): return False
        if self.game_map.get_tile(x, y) != '.': return False
        if building_type_name not in BUILDING_TYPES: return False
        details = BUILDING_TYPES[building_type_name]
        cost = details.get("cost", {})
        if not is_initial:
            for resource, amount in cost.items():
                if self.ai_resources.get(resource, 0) < amount: return False
            for resource, amount in cost.items(): self.ai_resources[resource] -= amount
        ai_symbol = details["symbol"].lower()
        new_building = Building(x, y, building_type_name, ai_symbol, details["health"])
        new_building.owner = "AI"
        self.ai_buildings.append(new_building)
        self.game_map.set_tile(x, y, new_building.symbol)
        print(f"AI placed {building_type_name} at ({x}, {y}).")
        return True

    def train_ai_unit(self, unit_type_name):
        if unit_type_name not in UNIT_TYPES: return False
        unit_details = UNIT_TYPES[unit_type_name]
        required_building_type = unit_details.get("required_building")
        if required_building_type:
            if not any(b.building_type == required_building_type for b in self.ai_buildings): return False
        cost = unit_details.get("cost", {})
        for resource, amount in cost.items():
            if self.ai_resources.get(resource, 0) < amount: return False
        for resource, amount in cost.items(): self.ai_resources[resource] -= amount
        new_unit = Unit(unit_type_name, unit_details["health"], unit_details["attack_power"])
        new_unit.owner = "AI"
        self.ai_units.append(new_unit)
        print(f"AI trained a {unit_type_name}.")
        return True

    def ai_execute_attack(self, attacking_unit_type, target_player_building):
        if not target_player_building or target_player_building.is_destroyed(): return
        attacking_ai_units = [u for u in self.ai_units if u.unit_type == attacking_unit_type]
        if not attacking_ai_units: return
        total_damage = sum(u.attack_power for u in attacking_ai_units)
        if total_damage == 0: return
        print(f"AI's {len(attacking_ai_units)} {attacking_unit_type}(s) are attacking your {target_player_building.building_type} at ({target_player_building.x}, {target_player_building.y}) for {total_damage} damage.")
        target_player_building.take_damage(total_damage)
        if target_player_building.is_destroyed():
            self.game_map.set_tile(target_player_building.x, target_player_building.y, '.')
            self.buildings.remove(target_player_building)
            print(f"Your {target_player_building.building_type} at ({target_player_building.x}, {target_player_building.y}) was destroyed by the AI!")

    def place_building(self, building_type_name, x, y, is_initial=False):
        if not self.game_map.is_valid_tile(x, y):
            print(f"Error: Cannot place building at ({x},{y}). Invalid location."); return False
        if self.game_map.get_tile(x, y) != '.':
            print(f"Error: Cannot place building at ({x},{y}). Tile not empty."); return False
        if building_type_name not in BUILDING_TYPES:
            print(f"Error: Unknown building type '{building_type_name}'."); return False
        details = BUILDING_TYPES[building_type_name]
        if not is_initial:
            cost = details.get("cost", {})
            for resource, amount in cost.items():
                if self.player_resources.get(resource, 0) < amount:
                    print(f"Error: Not enough {resource} to build {building_type_name}. Need {amount}, have {self.player_resources.get(resource, 0)}."); return False
            for resource, amount in cost.items(): self.player_resources[resource] -= amount
        new_building = Building(x, y, building_type_name, details["symbol"], details["health"])
        new_building.owner = "Player"
        self.buildings.append(new_building)
        self.game_map.set_tile(x, y, new_building.symbol)
        print(f"Placed {building_type_name} at ({x}, {y}).")
        return True

    def handle_input(self):
        command = input("Cmd (build <t> x y, train <t>, attack <t> x y, save, load, wait, quit): ").strip()
        if not command: return
        parts = command.split()
        action = parts[0].lower()

        if action == 'quit': self.is_running = False
        elif action == 'build' and len(parts) == 4:
            try: self.place_building(parts[1], int(parts[2]), int(parts[3]))
            except ValueError: print("Invalid build command.")
            except Exception as e: print(f"Error: {e}")
        elif action == 'train' and len(parts) == 2: self.train_unit(parts[1].lower())
        elif action == 'attack' and len(parts) == 4:
            try:
                unit_type = parts[1].lower()
                if unit_type not in UNIT_TYPES: print(f"Unknown unit: {unit_type}"); return
                self.execute_attack(unit_type, int(parts[2]), int(parts[3]))
            except ValueError: print("Invalid attack command.")
            except Exception as e: print(f"Error: {e}")
        elif action == 'save':
            filename = parts[1] if len(parts) > 1 else "clash_save.json"
            self.save_game(filename)
        elif action == 'load':
            filename = parts[1] if len(parts) > 1 else "clash_save.json"
            self.load_game(filename) # Render will show the new state
        elif action == 'wait': pass
        else: print(f"Unknown command: {command}")

    def execute_attack(self, attacking_unit_type, target_x, target_y):
        target_building = None
        # Ensure we only target AI buildings if player is attacking
        for b in self.ai_buildings: # Player attacks AI buildings
            if b.x == target_x and b.y == target_y and b.owner == "AI":
                target_building = b; break
        if not target_building: # Or if it's a player building by mistake / general structure
            for b in self.buildings:
                 if b.x == target_x and b.y == target_y and b.owner == "AI": # Check again (though redundant if lists are separate)
                    target_building = b; break

        if not target_building: print(f"Error: No AI building found at ({target_x}, {target_y})."); return
        if target_building.is_destroyed(): print(f"Error: Building at ({target_x}, {target_y}) is already destroyed."); return

        attacking_units_of_type = [u for u in self.units if u.unit_type == attacking_unit_type and u.owner == "Player"]
        if not attacking_units_of_type: print(f"No {attacking_unit_type}s available to attack."); return
        total_damage = sum(u.attack_power for u in attacking_units_of_type)
        if total_damage == 0: print(f"{attacking_unit_type}s have no attack power."); return

        print(f"Your {len(attacking_units_of_type)} {attacking_unit_type}(s) are attacking AI's {target_building.building_type} at ({target_x}, {target_y}) for {total_damage} total damage.")
        target_building.take_damage(total_damage)
        if target_building.is_destroyed():
            self.game_map.set_tile(target_building.x, target_building.y, '.')
            self.ai_buildings.remove(target_building) # Remove from AI's buildings
            print(f"AI's {target_building.building_type} at ({target_x}, {target_y}) was destroyed!")

    def train_unit(self, unit_type_name):
        if unit_type_name not in UNIT_TYPES:
            print(f"Error: Unknown unit type '{unit_type_name}'."); return False
        unit_details = UNIT_TYPES[unit_type_name]
        required_building_type = unit_details.get("required_building")
        if required_building_type:
            if not any(b.building_type == required_building_type for b in self.buildings if b.owner == "Player"):
                print(f"Error: Need a {required_building_type} to train {unit_type_name}."); return False
        cost = unit_details.get("cost", {})
        for resource, amount in cost.items():
            if self.player_resources.get(resource, 0) < amount:
                print(f"Error: Not enough {resource} to train {unit_type_name}. Need {amount}, have {self.player_resources.get(resource, 0)}."); return False
        for resource, amount in cost.items(): self.player_resources[resource] -= amount
        new_unit = Unit(unit_type_name, unit_details["health"], unit_details["attack_power"])
        new_unit.owner = "Player"
        self.units.append(new_unit)
        print(f"Trained a {unit_type_name}. Total {unit_type_name}s: {sum(1 for u in self.units if u.unit_type == unit_type_name and u.owner == 'Player')}")
        return True

if __name__ == '__main__':
    game = Game()
    game.run()
