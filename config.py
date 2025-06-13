# Configuration for the game
MAP_WIDTH = 20  # Grid cells, not pixels
MAP_HEIGHT = 15 # Grid cells, not pixels
GAME_SPEED = 1  # Ticks per second for text game logic (may or may not be used directly with FPS)
TILE_SIZE = 32 # Size of a single map tile in pixels

# Screen and UI
FPS = 30
UI_PANEL_HEIGHT = 60 # Height for the UI panel
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE # Should be 20*32 = 640
SCREEN_HEIGHT = (MAP_HEIGHT * TILE_SIZE) + UI_PANEL_HEIGHT # Should be (15*32) + 60 = 480 + 60 = 540

# Fonts
DEFAULT_FONT_NAME = None # Pygame will use a default system font
DEFAULT_FONT_SIZE = 24
UI_TEXT_COLOR = (255, 255, 255) # White
UI_BG_COLOR = (0, 0, 0) # Black

# Button Colors
BUTTON_BG_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255) # White
BUTTON_HOVER_COLOR = (150, 150, 150)

# Ghost Sprite Feedback Colors
GHOST_VALID_COLOR = (0, 255, 0, 150) # Green, semi-transparent
GHOST_INVALID_COLOR = (255, 0, 0, 150) # Red, semi-transparent
GHOST_NORMAL_ALPHA = 150 # Default alpha for normal state (can be different from valid/invalid if needed)


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
GREEN = (0, 255, 0) # Solid Green for success feedback, GHOST_VALID_COLOR for ghost
BLUE = (0, 0, 255)
RED = (255, 0, 0) # Solid Red for failure feedback, GHOST_INVALID_COLOR for ghost
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
