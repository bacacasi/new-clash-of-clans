import pygame
import config
import os # For checking file paths

IMAGE_PATH = "images" # Directory for sprites

_sprite_cache = {} # Cache for generated sprites (both image-based and procedural)

def _load_image_safely(path, size=None):
    if not os.path.exists(path):
        # print(f"Image not found: {path}") # Optional debug for missing files
        return None
    try:
        image = pygame.image.load(path)
        # Use convert_alpha() for images with transparency, convert() for opaque images for performance.
        # Assuming most sprites might have transparency (e.g. PNGs)
        if image.get_alpha() is not None or path.lower().endswith(".png"):
            image = image.convert_alpha()
        else:
            image = image.convert()

        if size:
            image = pygame.transform.smoothscale(image, size) # smoothscale for better quality
        return image
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        return None

# Simplified type definitions for graphical placeholders (fallbacks)
TEMP_BUILDING_GRAPHICS_INFO = {
    "town_hall": {"color": config.BLUE, "size_factor": 0.9, "shape": "rect"},
    "gold_mine": {"color": config.YELLOW, "size_factor": 0.7, "shape": "rect"},
    "elixir_collector": {"color": config.PURPLE, "size_factor": 0.7, "shape": "rect"},
    "barracks": {"color": config.RED, "size_factor": 0.8, "shape": "rect"},
    "ai_town_hall": {"color": (0,0,139), "size_factor": 0.9, "shape": "rect"},
    "ai_gold_mine": {"color": (204,204,0), "size_factor": 0.7, "shape": "rect"},
    "ai_barracks": {"color": (139,0,0), "size_factor": 0.8, "shape": "rect"},
}

TEMP_UNIT_GRAPHICS_INFO = {
    "barbarian": {"color": config.GREEN, "radius_factor": 0.3, "shape": "circle"},
    "archer": {"color": config.ORANGE, "radius_factor": 0.25, "shape": "circle"},
    "ai_barbarian": {"color": (0,100,0), "radius_factor": 0.3, "shape": "circle"},
}


def get_building_sprite(building_type_key, tile_size):
    # Try image cache first
    image_cache_key = (building_type_key, tile_size, "image")
    if image_cache_key in _sprite_cache:
        return _sprite_cache[image_cache_key]

    # Determine correct size factor from fallback info first
    # This handles cases where building_type_key might not be in TEMP_BUILDING_GRAPHICS_INFO
    # (e.g. if we add new buildings but forget to update TEMP dicts, though ideally they are kept in sync or merged)
    fallback_info = TEMP_BUILDING_GRAPHICS_INFO.get(building_type_key)
    if not fallback_info: # Try generic version if specific (e.g. ai_) not found
        generic_key = building_type_key.replace("ai_", "")
        fallback_info = TEMP_BUILDING_GRAPHICS_INFO.get(generic_key,
                            {"color": config.GREY, "size_factor": 0.6, "shape": "rect"}) # Absolute default

    sprite_render_size = int(tile_size * fallback_info.get("size_factor", 0.9))

    # Attempt to load image
    image_name = f"{building_type_key}.png"
    full_image_path = os.path.join(IMAGE_PATH, image_name)
    loaded_image = _load_image_safely(full_image_path, (sprite_render_size, sprite_render_size))

    if loaded_image:
        _sprite_cache[image_cache_key] = loaded_image
        return loaded_image

    # Fallback to procedural generation if image loading failed
    procedural_cache_key = (building_type_key, tile_size, "procedural")
    if procedural_cache_key in _sprite_cache:
        return _sprite_cache[procedural_cache_key]

    # Use the fallback_info determined earlier for procedural generation
    size = sprite_render_size
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)

    if fallback_info["shape"] == "rect":
        pygame.draw.rect(sprite, fallback_info["color"], (0, 0, size, size))
        pygame.draw.rect(sprite, config.BLACK, (0, 0, size, size), 1)
    # Add other shapes if needed for procedural fallback

    _sprite_cache[procedural_cache_key] = sprite
    return sprite


def get_unit_sprite(unit_type_key, tile_size):
    image_cache_key = (unit_type_key, tile_size, "image")
    if image_cache_key in _sprite_cache:
        return _sprite_cache[image_cache_key]

    fallback_info = TEMP_UNIT_GRAPHICS_INFO.get(unit_type_key)
    if not fallback_info: # Try generic version
        generic_key = unit_type_key.replace("ai_", "")
        fallback_info = TEMP_UNIT_GRAPHICS_INFO.get(generic_key,
                            {"color": config.WHITE, "radius_factor": 0.2, "shape": "circle"})

    radius = int(tile_size * fallback_info.get("radius_factor", 0.3))
    sprite_render_diameter = radius * 2

    image_name = f"{unit_type_key}.png"
    full_image_path = os.path.join(IMAGE_PATH, image_name)
    loaded_image = _load_image_safely(full_image_path, (sprite_render_diameter, sprite_render_diameter))

    if loaded_image:
        _sprite_cache[image_cache_key] = loaded_image
        return loaded_image

    procedural_cache_key = (unit_type_key, tile_size, "procedural")
    if procedural_cache_key in _sprite_cache:
        return _sprite_cache[procedural_cache_key]

    sprite_size = sprite_render_diameter
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)

    if fallback_info["shape"] == "circle":
        pygame.draw.circle(sprite, fallback_info["color"], (radius, radius), radius)
        pygame.draw.circle(sprite, config.BLACK, (radius, radius), radius, 1)

    _sprite_cache[procedural_cache_key] = sprite
    return sprite

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((300, 200)) # Adjusted screen size for more sprites
    pygame.display.set_caption("Asset Test - Images & Fallbacks")

    # Create dummy image files for testing fallbacks vs. loads
    # This part would typically be manual, but we can simulate for the test
    if not os.path.exists(IMAGE_PATH): os.makedirs(IMAGE_PATH)

    # Create a dummy town_hall.png
    dummy_th_surf = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
    dummy_th_surf.fill(config.CYAN) # Distinct color to show it's the loaded image
    pygame.draw.rect(dummy_th_surf, config.BLACK, (2,2,config.TILE_SIZE-4, config.TILE_SIZE-4), 3)
    pygame.image.save(dummy_th_surf, os.path.join(IMAGE_PATH, "town_hall.png"))

    # Test cases
    sprite_keys_to_test = [
        ("town_hall", config.TILE_SIZE),      # Should load dummy image
        ("gold_mine", config.TILE_SIZE),      # Should use procedural fallback
        ("ai_barracks", config.TILE_SIZE),    # Should use procedural fallback (ai_barracks)
        ("barbarian", config.TILE_SIZE),      # Should use procedural fallback
        ("ai_barbarian", config.TILE_SIZE),   # Should use procedural fallback (ai_barbarian)
        ("non_existent_building", config.TILE_SIZE) # Should use default procedural
    ]

    x_offset, y_offset = 10, 10
    max_x = screen.get_width() - (config.TILE_SIZE + 10)

    for key, size in sprite_keys_to_test:
        print(f"Attempting to get sprite for: {key}")
        if key.startswith("non_existent"): # Test building or unit default
            if "building" in key:
                 sprite = get_building_sprite(key, size)
            else:
                 sprite = get_unit_sprite(key,size)
        elif "barbarian" in key: # It's a unit
            sprite = get_unit_sprite(key, size)
        else: # It's a building
            sprite = get_building_sprite(key, size)

        if sprite:
            screen.blit(sprite, (x_offset, y_offset))
            sprite_w = sprite.get_width()
            x_offset += sprite_w + 10
            if x_offset > max_x:
                x_offset = 10
                y_offset += config.TILE_SIZE + 10 # Move to next row
        else:
            print(f"Sprite for {key} could not be generated/loaded.")

    pygame.display.flip()
    print("Asset test: Displaying sprites. town_hall should be a cyan square (loaded image). Others procedural.")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

    # Clean up dummy image
    if os.path.exists(os.path.join(IMAGE_PATH, "town_hall.png")):
        os.remove(os.path.join(IMAGE_PATH, "town_hall.png"))
    print("Asset test finished.")
