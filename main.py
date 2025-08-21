import pygame
import sys
import os
import config
from game_map import GameMap
from buildings import Building
from units import Unit
from projectiles import Projectile
import assets
from ui_elements import Button

SCREEN_WIDTH = config.SCREEN_WIDTH
SCREEN_HEIGHT = config.SCREEN_HEIGHT
FPS = config.FPS

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Clash of Clans - Graphical WIP")
        self.font = pygame.font.Font(config.DEFAULT_FONT_NAME, config.DEFAULT_FONT_SIZE)
        self.message_font = pygame.font.Font(config.DEFAULT_FONT_NAME, 20)
        self.tooltip_font = pygame.font.Font(config.DEFAULT_FONT_NAME, 18)

        self.ui_panel_y_start = config.MAP_HEIGHT * config.TILE_SIZE
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.tile_size = config.TILE_SIZE
        self.game_map = GameMap(config.MAP_WIDTH, config.MAP_HEIGHT)

        self.buildings = []
        self.ai_buildings = []
        self.units = []
        self.ai_units = []

        self.player_resources = {"gold": 1000, "elixir": 500}
        self.ai_resources = {"gold": 1000, "elixir": 500}

        self.BUILDING_INFO = {
            "town_hall": {"cost": {"gold": 200, "elixir": 0}, "asset_key": "town_hall", "name": "Town Hall", "max_health": 500},
            "gold_mine": {"cost": {"gold": 50, "elixir": 0}, "asset_key": "gold_mine", "name": "Gold Mine", "max_health": 200},
            "barracks": {"cost": {"gold": 75, "elixir": 25}, "asset_key": "barracks", "name": "Barracks", "max_health": 300, "can_train_units": True},
            "ai_town_hall": {"cost": {"gold": 0}, "asset_key": "ai_town_hall", "name": "AI Town Hall", "max_health": 500},
            "ai_gold_mine": {"cost": {"gold": 0}, "asset_key": "ai_gold_mine", "name": "AI Gold Mine", "max_health": 200},
            "ai_barracks": {"cost": {"gold": 0}, "asset_key": "ai_barracks", "name": "AI Barracks", "max_health": 300, "can_train_units": True},
        }
        self.UNIT_TRAINING_INFO = {
            "barbarian": {"cost": {"elixir": 25}, "asset_key": "barbarian", "display_name": "Barbarian", "required_building": "barracks", "health":50, "attack_power":10, "speed": 2.0, "attack_rate": 60, "attack_range": 1.5},
            "archer": {"cost": {"elixir": 50}, "asset_key": "archer", "display_name": "Archer", "required_building": "barracks", "health":30, "attack_power":7, "speed": 1.5, "attack_rate": 45, "attack_range": 4},
            "ai_barbarian": {"cost": {"elixir": 0}, "asset_key": "ai_barbarian", "display_name": "AI Barb", "required_building": "ai_barracks", "health":50, "attack_power":10, "speed": 2.0, "attack_rate": 60, "attack_range": 1.5},
        }

        self.ui_buttons = []
        self.unit_train_buttons = []
        self.selected_building = None
        self.selected_units = []
        self.current_build_action = None
        self.ghost_sprite = None
        self.feedback_effect = None

        self.active_tooltip_surface = None
        self.tooltip_timer = 0
        self.TOOLTIP_DELAY = config.FPS // 2
        self.tooltip_render_pos = (0,0)

        self.game_messages = []
        self.attack_visual_effects = [] # For hit sparks, etc.
        self.projectiles = []


        self.sounds = {}
        self._load_sounds()
        self._start_background_music()

        self._setup_ui_buttons()
        self._create_sample_buildings()
        self._create_sample_units()
        print("Game initialized with attack visual effects framework.")

    def _load_sound_safely(self, sound_name, file_path): # ... (no change)
        if not os.path.exists(file_path): self.sounds[sound_name] = None; return
        try: self.sounds[sound_name] = pygame.mixer.Sound(file_path)
        except pygame.error as e: print(f"Error loading sound {file_path}: {e}"); self.sounds[sound_name] = None
    def _load_sounds(self): # ... (no change)
        sounds_path = "sounds"
        self._load_sound_safely("build_success", os.path.join(sounds_path, "build_success.wav"))
        self._load_sound_safely("build_fail", os.path.join(sounds_path, "build_fail.wav"))
        self._load_sound_safely("action_error", os.path.join(sounds_path, "action_error.wav"))
        self._load_sound_safely("unit_trained", os.path.join(sounds_path, "unit_trained.wav"))
        self._load_sound_safely("unit_attack", os.path.join(sounds_path, "unit_attack.wav"))
    def _play_sound(self, sound_name, loops=0): # ... (no change)
        if self.sounds.get(sound_name): self.sounds[sound_name].play(loops)
    def _start_background_music(self): # ... (no change)
        music_file = os.path.join("sounds", "background_music.ogg")
        if not os.path.exists(music_file): print(f"Music not found: {music_file}"); return
        try: pygame.mixer.music.load(music_file); pygame.mixer.music.set_volume(0.3); pygame.mixer.music.play(-1)
        except pygame.error as e: print(f"Error playing music: {e}")

    def add_game_message(self, text, color=config.WHITE, duration_frames=180, msg_id=None): # ... (no change)
        if msg_id: self.game_messages = [m for m in self.game_messages if m.get("id") != msg_id]
        self.game_messages.append({"text": text, "timer": duration_frames, "color": color, "id": msg_id})
        max_messages = 5
        if len(self.game_messages) > max_messages: self.game_messages = self.game_messages[-max_messages:]

    def _setup_ui_buttons(self): # ... (no change, tooltips added previously)
        self.ui_buttons.clear(); button_width = 120; button_height = config.UI_PANEL_HEIGHT - 10; padding = 5; current_x = padding
        player_buildable_types = ["town_hall", "gold_mine", "barracks"]
        for building_type in player_buildable_types:
            details = self.BUILDING_INFO[building_type]; action_key = f"build_{building_type}"; button_text = f"{details['name']}"
            tt_lines = [f"{details['name']}"];
            for res, amount in details['cost'].items(): tt_lines.append(f"  {res.capitalize()}: {amount}")
            if details.get("max_health"): tt_lines.append(f"  HP: {details['max_health']}")
            btn = Button(current_x, self.ui_panel_y_start + padding, button_width, button_height, button_text, action_key, self.font, tooltip_text_lines=tt_lines)
            self.ui_buttons.append(btn); current_x += button_width + padding

    def _create_unit_train_buttons(self, building): # ... (no change, tooltips added previously)
        self.unit_train_buttons.clear()
        if not building or not self.BUILDING_INFO[building.building_type_key].get("can_train_units"): return
        button_width = 120; button_height = config.UI_PANEL_HEIGHT - 10; padding = 5; current_x = padding
        for unit_type, details in self.UNIT_TRAINING_INFO.items():
            if details["required_building"] == building.building_type_key and not unit_type.startswith("ai_"):
                action_key = f"train_{unit_type}"; button_text = f"Train {details['display_name']}"
                tt_lines = [f"{details['display_name']}"];
                for res, amount in details['cost'].items(): tt_lines.append(f"  {res.capitalize()}: {amount}")
                tt_lines.append(f"  HP: {details['health']}, ATK: {details['attack_power']}, Range: {details.get('attack_range', 1)}")
                btn = Button(current_x, self.ui_panel_y_start + padding, button_width, button_height, button_text, action_key, self.font, tooltip_text_lines=tt_lines)
                self.unit_train_buttons.append(btn); current_x += button_width + padding

    def is_tile_empty_for_building(self, grid_x, grid_y): # ... (no change)
        if not (0 <= grid_x < config.MAP_WIDTH and 0 <= grid_y < config.MAP_HEIGHT): return False
        for b in self.buildings + self.ai_buildings:
            if b.x_grid == grid_x and b.y_grid == grid_y: return False
        return True
    def _create_sample_buildings(self): # ... (no change)
        self.place_building(3, 3, "town_hall", is_initial_sample=True)
        self.place_building(5, 2, "gold_mine", is_initial_sample=True)
        self.place_building(2, 5, "barracks", is_initial_sample=True)
        self.place_building(config.MAP_WIDTH - 4, config.MAP_HEIGHT - 4, "ai_town_hall", owner="AI", is_initial_sample=True)
        self.place_building(config.MAP_WIDTH - 6, config.MAP_HEIGHT - 3, "ai_gold_mine", owner="AI", is_initial_sample=True)
        self.place_building(config.MAP_WIDTH - 4, config.MAP_HEIGHT - 6, "ai_barracks", owner="AI", is_initial_sample=True)
    def _get_spawn_position(self, owner_str, base_building=None): # ... (no change)
        if base_building:
             return (base_building.x_grid * self.tile_size + self.tile_size + self.tile_size // 4,
                    base_building.y_grid * self.tile_size + self.tile_size // 4)
        relevant_buildings = self.buildings if owner_str == "Player" else self.ai_buildings; spawn_source = None
        barracks_key = "barracks" if owner_str == "Player" else "ai_barracks"; th_key = "town_hall" if owner_str == "Player" else "ai_town_hall"
        for b_type_key in [barracks_key, th_key]:
            for b in relevant_buildings:
                if b.building_type_key == b_type_key: spawn_source = b; break
            if spawn_source: break
        if spawn_source: return (spawn_source.x_grid * self.tile_size + self.tile_size // 2, (spawn_source.y_grid + 1) * self.tile_size + self.tile_size // 2)
        return (self.tile_size, self.tile_size)
    def _create_sample_units(self): # ... (no change)
        player_barracks = next((b for b in self.buildings if b.building_type_key == "barracks"), None)
        player_spawn_pos = self._get_spawn_position("Player", player_barracks)
        p_barb_stats = self.UNIT_TRAINING_INFO["barbarian"]
        self.units.append(Unit(player_spawn_pos[0], player_spawn_pos[1], p_barb_stats["asset_key"], "Player", health=p_barb_stats["health"], attack_power=p_barb_stats["attack_power"], speed=p_barb_stats["speed"], attack_rate=p_barb_stats["attack_rate"], attack_range=p_barb_stats["attack_range"]))
        ai_barracks = next((b for b in self.ai_buildings if b.building_type_key == "ai_barracks"), None)
        ai_spawn_pos = self._get_spawn_position("AI", ai_barracks)
        ai_barb_stats = self.UNIT_TRAINING_INFO["ai_barbarian"]
        self.ai_units.append(Unit(ai_spawn_pos[0], ai_spawn_pos[1], ai_barb_stats["asset_key"], "AI", health=ai_barb_stats["health"], attack_power=ai_barb_stats["attack_power"], speed=ai_barb_stats["speed"], attack_rate=ai_barb_stats["attack_rate"], attack_range=ai_barb_stats["attack_range"]))

    def place_building(self, grid_x, grid_y, building_type_key_from_action, owner="Player", is_initial_sample=False): # ... (no change from previous step where messages were added)
        lookup_key = building_type_key_from_action
        if lookup_key not in self.BUILDING_INFO:
            if not is_initial_sample and owner=="Player": self._play_sound("action_error"); self.add_game_message(f"Cannot build: Unknown type '{lookup_key}'", config.RED, msg_id="build_error")
            return False
        details = self.BUILDING_INFO[lookup_key]; cost = details["cost"]; asset_key = details["asset_key"]; max_hp = details["max_health"]
        if owner == "Player" and not is_initial_sample:
            for res, amt in cost.items():
                if self.player_resources.get(res, 0) < amt:
                    self._play_sound("action_error"); self.add_game_message(f"Not enough {res} for {details['name']}", config.RED, msg_id="resource_error")
                    return False
        if not self.is_tile_empty_for_building(grid_x, grid_y) and not is_initial_sample:
            self._play_sound("build_fail"); self.add_game_message("Tile occupied or invalid", config.RED, msg_id="placement_error")
            return False
        if owner == "Player" and not is_initial_sample:
            for res, amt in cost.items(): self.player_resources[res] -= amt
        new_b = Building(grid_x, grid_y, asset_key, owner, health=max_hp, max_health=max_hp)
        if owner == "Player": self.buildings.append(new_b)
        else: self.ai_buildings.append(new_b)
        if owner == "Player" and not is_initial_sample: self._play_sound("build_success"); self.add_game_message(f"{details['name']} placed!", config.GREEN)
        return True

    def train_unit(self, unit_type_key): # ... (no change from previous step where messages were added)
        if not self.selected_building or not self.BUILDING_INFO[self.selected_building.building_type_key].get("can_train_units"):
            self._play_sound("action_error"); self.add_game_message("Select a training building first.", config.RED); return
        if unit_type_key not in self.UNIT_TRAINING_INFO:
            self._play_sound("action_error"); self.add_game_message(f"Unknown unit: {unit_type_key}", config.RED); return
        details = self.UNIT_TRAINING_INFO[unit_type_key]; cost = details["cost"]
        for res, amt in cost.items():
            if self.player_resources.get(res, 0) < amt: self._play_sound("action_error"); self.add_game_message(f"Not enough {res} for {details['display_name']}", config.RED, msg_id="resource_error"); return
        for res, amt in cost.items(): self.player_resources[res] -= amt
        spawn_pos = self._get_spawn_position("Player", self.selected_building)
        new_unit = Unit(spawn_pos[0], spawn_pos[1], details["asset_key"], "Player", health=details["health"], attack_power=details["attack_power"], speed=details["speed"], attack_rate=details["attack_rate"], attack_range=details["attack_range"])
        self.units.append(new_unit); self._play_sound("unit_trained"); self.add_game_message(f"{details['display_name']} trained!", config.GREEN)

    def run(self): # ... (no change)
        while self.is_running: self.handle_events(); self.update(); self.render(); self.clock.tick(FPS)
        pygame.mixer.music.stop(); pygame.mixer.quit(); pygame.quit(); sys.exit()

    def handle_events(self): # ... (no change from previous step, tooltip logic exists)
        mouse_pos = pygame.mouse.get_pos()
        grid_x_mouse, grid_y_mouse = mouse_pos[0] // self.tile_size, mouse_pos[1] // self.tile_size
        keys_pressed = pygame.key.get_pressed(); shift_held = keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]
        current_hovered_button = None
        active_buttons = self.unit_train_buttons if self.selected_building and self.BUILDING_INFO[self.selected_building.building_type_key].get("can_train_units") else self.ui_buttons
        for btn in active_buttons:
            if btn.rect.collidepoint(mouse_pos): current_hovered_button = btn; break
        if current_hovered_button and current_hovered_button.tooltip_text_lines:
            self.tooltip_timer += 1
            if self.tooltip_timer >= self.TOOLTIP_DELAY:
                if not self.active_tooltip_surface:
                    self.tooltip_render_pos = (mouse_pos[0] + 15, mouse_pos[1] + 15)
                    tt_renders = [self.tooltip_font.render(line, True, config.WHITE) for line in current_hovered_button.tooltip_text_lines]
                    max_w = max(s.get_width() for s in tt_renders) if tt_renders else 0; total_h = sum(s.get_height() for s in tt_renders) + (len(tt_renders) -1) * 2 if tt_renders else 0
                    self.active_tooltip_surface = pygame.Surface((max_w + 8, total_h + 4), pygame.SRCALPHA); self.active_tooltip_surface.fill((*config.BLACK, 220))
                    current_y_tt = 4
                    for surf in tt_renders: self.active_tooltip_surface.blit(surf, (4, current_y_tt)); current_y_tt += surf.get_height() + 2
        else: self.tooltip_timer = 0; self.active_tooltip_surface = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.is_running = False; return
            for btn in active_buttons:
                action_result = btn.handle_event(event)
                if action_result:
                    if action_result.startswith("build_"):
                        b_type = action_result.split("build_")[1]
                        if self.current_build_action == action_result: self.current_build_action = None; self.ghost_sprite = None
                        else:
                            if b_type in self.BUILDING_INFO:
                                self.current_build_action = action_result; self.selected_building = None; self.selected_units.clear(); self.unit_train_buttons.clear()
                                for u in self.units: u.selected = False
                                asset_key = self.BUILDING_INFO[b_type]["asset_key"]
                                self.ghost_sprite = assets.get_building_sprite(asset_key, self.tile_size); self.ghost_sprite.set_alpha(config.GHOST_NORMAL_ALPHA)
                    elif action_result.startswith("train_"): self.train_unit(action_result.split("train_")[1])
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_on_ui_button = False
                for btn in self.ui_buttons + self.unit_train_buttons:
                    if btn.rect.collidepoint(mouse_pos): clicked_on_ui_button = True; break
                if clicked_on_ui_button: continue
                if event.button == 1:
                    if self.current_build_action:
                        if grid_y_mouse < config.MAP_HEIGHT:
                            b_type_to_place = self.current_build_action.split("build_")[1]
                            if self.place_building(grid_x_mouse, grid_y_mouse, b_type_to_place, owner="Player"):
                                if not shift_held: self.current_build_action = None; self.ghost_sprite = None
                        else: self._play_sound("action_error"); self.add_game_message("Cannot build on UI panel", config.RED)
                    else:
                        if grid_y_mouse < config.MAP_HEIGHT:
                            newly_selected_building = None
                            for b in self.buildings:
                                if b.x_grid == grid_x_mouse and b.y_grid == grid_y_mouse: newly_selected_building = b; break
                            if newly_selected_building:
                                if self.selected_building: self.selected_building.selected = False
                                for u in self.selected_units: u.selected = False; self.selected_units.clear()
                                self.selected_building = newly_selected_building; self.selected_building.selected = True
                                if self.BUILDING_INFO[self.selected_building.building_type_key].get("can_train_units"): self._create_unit_train_buttons(self.selected_building)
                                else: self.unit_train_buttons.clear()
                            else:
                                if self.selected_building: self.selected_building.selected = False; self.selected_building = None
                                self.unit_train_buttons.clear()
                                clicked_unit = None
                                for unit in self.units:
                                    unit_sprite = assets.get_unit_sprite(unit.unit_type_key, self.tile_size)
                                    if unit_sprite:
                                        sprite_w, sprite_h = unit_sprite.get_size()
                                        unit_rect = pygame.Rect(unit.x - sprite_w//2, unit.y - sprite_h//2, sprite_w, sprite_h)
                                        if unit_rect.collidepoint(mouse_pos): clicked_unit = unit; break
                                if not shift_held:
                                    for u in self.selected_units: u.selected = False; self.selected_units.clear()
                                if clicked_unit:
                                    if clicked_unit in self.selected_units: clicked_unit.selected = False; self.selected_units.remove(clicked_unit)
                                    else: clicked_unit.selected = True; self.selected_units.append(clicked_unit)
                                elif not shift_held :
                                     for u in self.selected_units: u.selected = False; self.selected_units.clear()
                elif event.button == 3:
                    if self.current_build_action: self.current_build_action = None; self.ghost_sprite = None; self._play_sound("action_error")
                    elif self.selected_units:
                        target_building = None
                        if grid_y_mouse < config.MAP_HEIGHT:
                            for b in self.ai_buildings:
                                if b.x_grid == grid_x_mouse and b.y_grid == grid_y_mouse: target_building = b; break
                        for unit in self.selected_units:
                            if target_building:
                                unit.attack_target_building = target_building
                                unit.set_target(target_building.x_grid * self.tile_size + self.tile_size // 2, target_building.y_grid * self.tile_size + self.tile_size // 2, is_attack_move=True)
                            else:
                                unit.attack_target_building = None
                                unit.set_target(mouse_pos[0], mouse_pos[1], is_attack_move=False)
                    elif self.selected_building: self.selected_building.selected = False; self.selected_building = None; self.unit_train_buttons.clear()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_build_action: self.current_build_action = None; self.ghost_sprite = None
                    elif self.selected_building: self.selected_building.selected = False; self.selected_building = None; self.unit_train_buttons.clear()
                    elif self.selected_units:
                        for u in self.selected_units: u.selected = False; self.selected_units.clear()
        for btn in self.ui_buttons + self.unit_train_buttons:
            if not btn.rect.collidepoint(mouse_pos): btn.is_hovered = False
            btn.update_active_state(self.current_build_action)

    def update(self):
        if self.feedback_effect: self.feedback_effect["timer"] -= 1
        if self.feedback_effect and self.feedback_effect["timer"] <= 0: self.feedback_effect = None
        new_messages = []
        for msg in self.game_messages:
            msg["timer"] -= 1
            if msg["timer"] > 0: new_messages.append(msg)
        self.game_messages = new_messages

        for unit in self.units: # Player units
            # Target validity check
            if unit.attack_target_building and unit.attack_target_building not in self.ai_buildings:
                unit.attack_target_building = None # Target was destroyed or removed
                unit.is_moving = False # Stop unit
                unit.target_x, unit.target_y = None, None


            unit.update_movement() # Update position based on target

            if unit.attack_target_building and not unit.is_moving: # If has target and is in range (not moving)
                if unit.can_attack():
                    if unit.perform_attack(unit.attack_target_building): # perform_attack returns True if attack happened
                        self._play_sound("unit_attack")
                        target_b = unit.attack_target_building
                        target_pos_x = target_b.x_grid * self.tile_size + self.tile_size // 2
                        target_pos_y = target_b.y_grid * self.tile_size + self.tile_size // 2

                        # If archer, create a projectile. Otherwise, create a hit spark.
                        if unit.unit_type_key == 'archer':
                            # Arrow color can be customized, e.g. brown
                            arrow_color = (139, 69, 19)
                            self.projectiles.append(Projectile(unit.x, unit.y, target_pos_x, target_pos_y, color=arrow_color))
                        else:
                            # Melee units get the instant hit spark effect
                            self.attack_visual_effects.append({
                                "pos": (target_pos_x, target_pos_y),
                                "timer": config.FPS // 6, # Short duration (e.g., 10 frames)
                                "color": config.YELLOW # Or a specific attack color
                            })

                        if target_b.is_destroyed(): # Check again after attack
                            self.add_game_message(f"AI's {target_b.building_type_key} destroyed!", config.GREEN)
                            # Unit's perform_attack already clears its own target if building is destroyed
                else:
                    unit.attack_cooldown -= 1

        for unit in self.ai_units: unit.update_movement()

        # Update attack visual effects
        self.attack_visual_effects = [effect for effect in self.attack_visual_effects if effect["timer"] > 0]
        for effect in self.attack_visual_effects:
            effect["timer"] -= 1

        # Update projectiles
        for p in self.projectiles[:]:
            if p.update():
                self.projectiles.remove(p)

        self.ai_buildings = [b for b in self.ai_buildings if not b.is_destroyed()]


    def render_text(self, text, x, y, surf=None, color=None, font=None): # ... (no change)
        surf = surf or self.screen; color = color or config.UI_TEXT_COLOR; font = font or self.font
        text_surf = font.render(text, True, color); text_rect = text_surf.get_rect(topleft=(x,y))
        surf.blit(text_surf, text_rect); return text_rect

    def render(self):
        self.screen.fill(config.GREY)
        self.game_map.draw(self.screen, assets, self.tile_size, self.buildings + self.ai_buildings)

        for unit in self.units + self.ai_units:
            unit_sprite = assets.get_unit_sprite(unit.unit_type_key, self.tile_size)
            if unit_sprite:
                sprite_w, sprite_h = unit_sprite.get_size()
                draw_pos = (int(unit.x - sprite_w // 2), int(unit.y - sprite_h // 2))
                self.screen.blit(unit_sprite, draw_pos)
                if unit.selected:
                    selection_radius = max(sprite_w, sprite_h) // 2 + 4
                    pygame.draw.circle(self.screen, config.WHITE, (int(unit.x), int(unit.y)), selection_radius, 2)

        if self.current_build_action and self.ghost_sprite: # ... (ghost sprite logic no change)
            mx, my = pygame.mouse.get_pos(); gx, gy = mx // self.tile_size, my // self.tile_size
            if 0 <= gx < config.MAP_WIDTH and 0 <= gy < config.MAP_HEIGHT:
                sx, sy = gx * self.tile_size, gy * self.tile_size; temp_ghost = self.ghost_sprite.copy()
                valid_place = self.is_tile_empty_for_building(gx, gy)
                b_type_cost = self.current_build_action.split("build_")[1]
                has_res = all(self.player_resources.get(r,0) >= amount for r, amount in self.BUILDING_INFO[b_type_cost]["cost"].items())
                if valid_place and has_res: temp_ghost.set_alpha(config.GHOST_NORMAL_ALPHA)
                else: temp_ghost.set_alpha(config.GHOST_NORMAL_ALPHA // 2); pygame.draw.rect(self.screen, config.RED, (sx, sy, self.tile_size, self.tile_size), 2)
                sw, sh = temp_ghost.get_size(); ox, oy = (self.tile_size - sw)//2, (self.tile_size - sh)//2
                self.screen.blit(temp_ghost, (sx + ox, sy + oy))

        if self.feedback_effect: # ... (feedback effect logic no change)
            gx, gy = self.feedback_effect["pos"]; px, py = gx * self.tile_size, gy * self.tile_size
            col_rgb = config.GREEN if self.feedback_effect["type"] == "success" else config.RED
            alpha = 50 + (self.feedback_effect["timer"] * 7); alpha = max(0, min(255, alpha))
            f_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA); f_surf.fill((*col_rgb, alpha))
            self.screen.blit(f_surf, (px, py))

        # Render attack visual effects
        for effect in self.attack_visual_effects:
            radius = effect["timer"] * 1.5 # Radius shrinks as timer goes down, make it a bit larger
            if radius > 1: # Only draw if radius is somewhat visible
                pygame.draw.circle(self.screen, effect["color"], (int(effect["pos"][0]), int(effect["pos"][1])), int(radius))

        # Render projectiles
        for p in self.projectiles:
            p.draw(self.screen)

        # UI Panel ... (no change)
        pygame.draw.rect(self.screen, config.UI_BG_COLOR, (0, self.ui_panel_y_start, config.SCREEN_WIDTH, config.UI_PANEL_HEIGHT))
        active_buttons = self.unit_train_buttons if self.selected_building and self.BUILDING_INFO[self.selected_building.building_type_key].get("can_train_units") else self.ui_buttons
        for btn in active_buttons: btn.draw(self.screen)
        res_y = self.ui_panel_y_start + (config.UI_PANEL_HEIGHT - config.DEFAULT_FONT_SIZE) // 2
        player_res_str = f"Gold: {self.player_resources['gold']} | Elixir: {self.player_resources['elixir']}"
        last_btn_right = active_buttons[-1].rect.right if active_buttons else 0; res_x = last_btn_right + 20
        if not active_buttons or res_x + self.font.size(player_res_str)[0] > config.SCREEN_WIDTH -10: res_x = 10
        self.render_text(player_res_str, res_x , res_y)
        message_y_offset = 10
        for i, msg_data in enumerate(self.game_messages):
            msg_surface = self.message_font.render(msg_data["text"], True, msg_data["color"])
            msg_rect = msg_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, top=message_y_offset)
            bg_rect = msg_rect.inflate(6, 4); s = pygame.Surface(bg_rect.size, pygame.SRCALPHA); s.fill((*config.BLACK, 180))
            self.screen.blit(s, bg_rect); self.screen.blit(msg_surface, msg_rect)
            message_y_offset += msg_surface.get_height() + 4
        if self.active_tooltip_surface:
            tooltip_rect = self.active_tooltip_surface.get_rect(topleft=self.tooltip_render_pos)
            tooltip_rect.clamp_ip(self.screen.get_rect())
            self.screen.blit(self.active_tooltip_surface, tooltip_rect)
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()
