import pygame
import sys
import os # Needed for path joining and existence checks for sounds
import config
from game_map import GameMap
from buildings import Building
from units import Unit
import assets
from ui_elements import Button

SCREEN_WIDTH = config.SCREEN_WIDTH
SCREEN_HEIGHT = config.SCREEN_HEIGHT
FPS = config.FPS

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512) # Initialize mixer first
        pygame.init() # Then Pygame

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Clash of Clans - Graphical WIP")
        self.font = pygame.font.Font(config.DEFAULT_FONT_NAME, config.DEFAULT_FONT_SIZE)
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
            "barracks": {"cost": {"gold": 75, "elixir": 25}, "asset_key": "barracks", "name": "Barracks", "max_health": 300},
            "ai_town_hall": {"cost": {"gold": 0}, "asset_key": "ai_town_hall", "name": "AI Town Hall", "max_health": 500},
            "ai_gold_mine": {"cost": {"gold": 0}, "asset_key": "ai_gold_mine", "name": "AI Gold Mine", "max_health": 200},
            "ai_barracks": {"cost": {"gold": 0}, "asset_key": "ai_barracks", "name": "AI Barracks", "max_health": 300},
        }

        self.ui_buttons = []
        self.current_build_action = None
        self.ghost_sprite = None
        self.feedback_effect = None

        self.sounds = {}
        self._load_sounds()
        self._start_background_music()

        self._setup_ui_buttons()
        self._create_sample_buildings()
        self._create_sample_units()
        print("Pygame initialized with UI, map, sounds, sample buildings/units, and feedback.")

    def _load_sound_safely(self, sound_name, file_path):
        if not os.path.exists(file_path):
            print(f"Sound file not found: {file_path}. Sound '{sound_name}' will not play.")
            self.sounds[sound_name] = None
            return None
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[sound_name] = sound
        except pygame.error as e:
            print(f"Error loading sound {sound_name} from {file_path}: {e}")
            self.sounds[sound_name] = None

    def _load_sounds(self):
        sounds_path = "sounds"
        # The directory was already created by run_in_bash_session in a previous step.
        # if not os.path.exists(sounds_path):
        #     os.makedirs(sounds_path)
        #     print(f"Created directory: {sounds_path}")

        self._load_sound_safely("build_success", os.path.join(sounds_path, "build_success.wav"))
        self._load_sound_safely("build_fail", os.path.join(sounds_path, "build_fail.wav"))
        self._load_sound_safely("action_error", os.path.join(sounds_path, "action_error.wav"))
        # Add more sounds like "unit_trained.wav", "attack.wav" later

    def _play_sound(self, sound_name, loops=0):
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play(loops)
        # else:
            # print(f"Debug: Sound '{sound_name}' not played (either not loaded or None).")


    def _start_background_music(self):
        music_path = "sounds"
        music_file = os.path.join(music_path, "background_music.ogg") # Or .mp3
        if not os.path.exists(music_file):
            print(f"Background music file not found: {music_file}")
            return
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            print(f"Playing background music: {music_file}")
        except pygame.error as e:
            print(f"Error loading or playing background music {music_file}: {e}")

    def _setup_ui_buttons(self):
        button_width = 150
        button_height = config.UI_PANEL_HEIGHT - 2 * 5
        padding = 5
        current_x = padding
        player_buildable_types = ["town_hall", "gold_mine", "barracks"]
        for building_type in player_buildable_types:
            details = self.BUILDING_INFO[building_type]
            action_key = f"build_{building_type}"
            button_text = f"Build {details['name']}"
            btn = Button(current_x, self.ui_panel_y_start + padding, button_width, button_height,
                         button_text, action_key, self.font)
            self.ui_buttons.append(btn)
            current_x += button_width + padding

    def is_tile_empty_for_building(self, grid_x, grid_y):
        if not (0 <= grid_x < config.MAP_WIDTH and 0 <= grid_y < config.MAP_HEIGHT):
            return False
        for b in self.buildings + self.ai_buildings:
            if b.x_grid == grid_x and b.y_grid == grid_y:
                return False
        return True

    def _create_sample_buildings(self):
        self.place_building(3, 3, "town_hall", is_initial_sample=True)
        self.place_building(5, 2, "gold_mine", is_initial_sample=True)
        self.place_building(2, 5, "barracks", is_initial_sample=True)
        self.place_building(config.MAP_WIDTH - 4, config.MAP_HEIGHT - 4, "ai_town_hall", owner="AI", is_initial_sample=True)
        self.place_building(config.MAP_WIDTH - 6, config.MAP_HEIGHT - 3, "ai_gold_mine", owner="AI", is_initial_sample=True)
        self.place_building(config.MAP_WIDTH - 4, config.MAP_HEIGHT - 6, "ai_barracks", owner="AI", is_initial_sample=True)

    def _get_spawn_position(self, owner_str):
        barracks_list = self.buildings if owner_str == "Player" else self.ai_buildings
        owner_barracks = None
        barracks_asset_key_to_find = "barracks" if owner_str == "Player" else "ai_barracks"
        for b in barracks_list:
            if b.building_type_key == barracks_asset_key_to_find and b.owner == owner_str:
                owner_barracks = b; break
        if owner_barracks:
            return (owner_barracks.x_grid * self.tile_size + self.tile_size // 4,
                    owner_barracks.y_grid * self.tile_size + self.tile_size // 4)
        else:
            th_list = self.buildings if owner_str == "Player" else self.ai_buildings
            owner_th = None
            th_asset_key_to_find = "town_hall" if owner_str == "Player" else "ai_town_hall"
            for b in th_list:
                if b.building_type_key == th_asset_key_to_find and b.owner == owner_str:
                    owner_th = b; break
            if owner_th:
                 return (owner_th.x_grid * self.tile_size + self.tile_size // 2,
                        (owner_th.y_grid + 1) * self.tile_size + self.tile_size // 2)
            return (self.tile_size, self.tile_size) if owner_str == "Player" else (config.SCREEN_WIDTH - self.tile_size, self.tile_size)

    def _create_sample_units(self):
        player_spawn_pos = self._get_spawn_position("Player")
        self.units.append(Unit(player_spawn_pos[0], player_spawn_pos[1], "barbarian", "Player"))
        ai_spawn_pos = self._get_spawn_position("AI")
        self.ai_units.append(Unit(ai_spawn_pos[0], ai_spawn_pos[1], "ai_barbarian", "AI"))

    def place_building(self, grid_x, grid_y, building_type_key_from_action, owner="Player", is_initial_sample=False):
        lookup_key = building_type_key_from_action
        if lookup_key not in self.BUILDING_INFO:
            print(f"Error: Building type/key '{lookup_key}' not recognized in BUILDING_INFO.")
            if not is_initial_sample and owner == "Player":
                 self.feedback_effect = {"type": "failure_generic", "pos": (grid_x, grid_y), "timer": config.FPS // 2}
                 self._play_sound("action_error")
            return False

        details = self.BUILDING_INFO[lookup_key]
        cost = details["cost"]
        asset_key_for_sprite = details["asset_key"]
        max_hp = details["max_health"]

        if owner == "Player" and not is_initial_sample:
            for resource, amount in cost.items():
                if self.player_resources.get(resource, 0) < amount:
                    print(f"Error: Not enough {resource}.")
                    self.feedback_effect = {"type": "failure_resource", "pos": (grid_x, grid_y), "timer": config.FPS // 2}
                    self._play_sound("action_error") # Or a specific "not_enough_resources.wav"
                    return False

        if not self.is_tile_empty_for_building(grid_x, grid_y):
            if not is_initial_sample:
                print(f"Error: Tile ({grid_x},{grid_y}) is occupied or invalid.")
                self.feedback_effect = {"type": "failure_placement", "pos": (grid_x, grid_y), "timer": config.FPS // 2}
                self._play_sound("build_fail")
                return False

        if owner == "Player" and not is_initial_sample:
            for resource, amount in cost.items():
                self.player_resources[resource] -= amount

        new_building = Building(grid_x, grid_y, asset_key_for_sprite, owner, health=max_hp, max_health=max_hp)

        if owner == "Player":
            self.buildings.append(new_building)
        else:
            self.ai_buildings.append(new_building)

        print(f"{owner} placed {details['name']} (using asset {asset_key_for_sprite}) at ({grid_x}, {grid_y})")
        if owner == "Player" and not is_initial_sample:
             self.feedback_effect = {"type": "success", "pos": (grid_x, grid_y), "timer": config.FPS // 2}
             self._play_sound("build_success")
        return True

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.mixer.music.stop() # Stop music
        pygame.mixer.quit() # Uninitialize mixer
        pygame.quit()
        sys.exit()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            for btn in self.ui_buttons:
                action_result = btn.handle_event(event)
                if action_result:
                    if action_result.startswith("build_"):
                        building_type_key_from_action = action_result.split("build_")[1]
                        if building_type_key_from_action in self.BUILDING_INFO:
                            if self.current_build_action == action_result:
                                self.current_build_action = None
                                self.ghost_sprite = None
                            else:
                                self.current_build_action = action_result
                                asset_key = self.BUILDING_INFO[building_type_key_from_action]["asset_key"]
                                self.ghost_sprite = assets.get_building_sprite(asset_key, self.tile_size)
                                if self.ghost_sprite:
                                    self.ghost_sprite = self.ghost_sprite.copy()
                            print(f"Build action: {self.current_build_action}")
                        else:
                            print(f"Unknown building type from button: {building_type_key_from_action}")
                            self._play_sound("action_error")
                    break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.current_build_action:
                    grid_x = mouse_pos[0] // self.tile_size
                    grid_y = mouse_pos[1] // self.tile_size
                    if grid_y < config.MAP_HEIGHT:
                        building_type_to_place = self.current_build_action.split("build_")[1]
                        if self.place_building(grid_x, grid_y, building_type_to_place, owner="Player"):
                            pass
                    else: # Click on UI panel while in build mode
                        self._play_sound("action_error")
                elif event.button == 3 and self.current_build_action:
                    print("Build mode cancelled.")
                    self.current_build_action = None
                    self.ghost_sprite = None
                    self._play_sound("action_error") # Sound for cancel?

        for btn in self.ui_buttons:
            btn.update_active_state(self.current_build_action)

    def update(self):
        if self.feedback_effect:
           self.feedback_effect["timer"] -= 1
           if self.feedback_effect["timer"] <= 0:
               self.feedback_effect = None

    def render_text(self, text, x, y, surface_to_draw_on=None, color=None, font=None):
        if surface_to_draw_on is None: surface_to_draw_on = self.screen
        if color is None: color = config.UI_TEXT_COLOR
        if font is None: font = self.font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(topleft=(x,y))
        surface_to_draw_on.blit(text_surface, text_rect)
        return text_rect

    def render(self):
        self.screen.fill(config.GREY)
        all_game_buildings = self.buildings + self.ai_buildings
        self.game_map.draw(self.screen, assets, self.tile_size, all_game_buildings)
        all_game_units = self.units + self.ai_units
        for unit in all_game_units:
            unit_sprite = assets.get_unit_sprite(unit.unit_type_key, self.tile_size)
            if unit_sprite:
                sprite_w, sprite_h = unit_sprite.get_size()
                draw_x = unit.x - sprite_w // 2
                draw_y = unit.y - sprite_h // 2
                self.screen.blit(unit_sprite, (draw_x, draw_y))

        if self.current_build_action and self.ghost_sprite:
            mouse_px, mouse_py = pygame.mouse.get_pos()
            grid_col = mouse_px // self.tile_size
            grid_row = mouse_py // self.tile_size
            show_ghost_on_map = (0 <= grid_col < config.MAP_WIDTH and 0 <= grid_row < config.MAP_HEIGHT)
            if show_ghost_on_map:
                snap_x = grid_col * self.tile_size
                snap_y = grid_row * self.tile_size
                temp_ghost_surf = self.ghost_sprite.copy()
                can_place_visual_check = self.is_tile_empty_for_building(grid_col, grid_row)
                building_type_to_check_cost = self.current_build_action.split("build_")[1]
                cost_info = self.BUILDING_INFO[building_type_to_check_cost]["cost"]
                has_resources = all(self.player_resources.get(res,0) >= amt for res, amt in cost_info.items())
                if can_place_visual_check and has_resources:
                    temp_ghost_surf.set_alpha(config.GHOST_NORMAL_ALPHA)
                else:
                    temp_ghost_surf.set_alpha(config.GHOST_NORMAL_ALPHA // 2)
                    pygame.draw.rect(self.screen, config.RED, (snap_x, snap_y, self.tile_size, self.tile_size), 2)
                sprite_w, sprite_h = temp_ghost_surf.get_size()
                offset_x = (self.tile_size - sprite_w) // 2
                offset_y = (self.tile_size - sprite_h) // 2
                self.screen.blit(temp_ghost_surf, (snap_x + offset_x, snap_y + offset_y))

        if self.feedback_effect:
            effect_gx, effect_gy = self.feedback_effect["pos"]
            effect_px = effect_gx * self.tile_size
            effect_py = effect_gy * self.tile_size
            rect_size = self.tile_size
            feedback_color_rgb = config.GREEN if self.feedback_effect["type"] == "success" else config.RED
            feedback_alpha = 50 + (self.feedback_effect["timer"] * 7)
            feedback_alpha = max(0, min(255, feedback_alpha))
            feedback_surf = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
            feedback_surf.fill((*feedback_color_rgb, feedback_alpha))
            self.screen.blit(feedback_surf, (effect_px, effect_py))

        ui_panel_rect = pygame.Rect(0, self.ui_panel_y_start, config.SCREEN_WIDTH, config.UI_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, config.UI_BG_COLOR, ui_panel_rect)
        for btn in self.ui_buttons:
            btn.draw(self.screen)
        res_text_y = self.ui_panel_y_start + (config.UI_PANEL_HEIGHT - config.DEFAULT_FONT_SIZE) // 2
        player_res_text = f"Gold: {self.player_resources['gold']} | Elixir: {self.player_resources['elixir']}"
        res_display_x = (self.ui_buttons[-1].rect.right + 10) if self.ui_buttons else 10
        if res_display_x + self.font.size(player_res_text)[0] > config.SCREEN_WIDTH - 10 :
            res_display_x = 10
        self.render_text(player_res_text, res_display_x , res_text_y)

        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()
