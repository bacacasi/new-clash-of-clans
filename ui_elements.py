# ui_elements.py
import pygame
import config

class Button:
    def __init__(self, x, y, width, height, text, action_key, font,
                 bg_color=config.BUTTON_BG_COLOR, text_color=config.BUTTON_TEXT_COLOR,
                 hover_color=config.BUTTON_HOVER_COLOR, tooltip_text_lines=None): # Added tooltip_text_lines
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_key = action_key
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_active_action = False
        self.tooltip_text_lines = tooltip_text_lines if tooltip_text_lines else [] # Store as list

    def draw(self, surface):
        current_bg_color = self.bg_color
        if self.is_active_action:
            current_bg_color = self.hover_color
        elif self.is_hovered:
            current_bg_color = self.hover_color

        pygame.draw.rect(surface, current_bg_color, self.rect)
        pygame.draw.rect(surface, config.BLACK, self.rect, 2) # Border

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return self.action_key
        return None

    def update_active_state(self, current_game_action):
        """Allows the game to tell the button if its action is the current one."""
        self.is_active_action = (self.action_key == current_game_action)

if __name__ == '__main__':
    pygame.init()
    screen_width = 400
    screen_height = 300 # Increased height for tooltip test
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Button Test with Tooltips")

    font = pygame.font.Font(config.DEFAULT_FONT_NAME, config.DEFAULT_FONT_SIZE)
    tooltip_font = pygame.font.Font(config.DEFAULT_FONT_NAME, 18) # Smaller font for tooltips

    # Button with a tooltip
    button1_tooltips = ["Test Button 1:", " - Does a test action.", " - Costs: Nothing!"]
    button1 = Button(50, 50, 150, 50, "Test Button 1", "test1", font, tooltip_text_lines=button1_tooltips)

    button2 = Button(50, 120, 180, 50, "No Tooltip Btn", "test2", font, bg_color=config.RED)
    buttons = [button1, button2]

    active_tooltip_surface = None
    tooltip_pos = (0,0)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        active_tooltip_surface = None # Reset tooltip surface each frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons:
                action_triggered = btn.handle_event(event)
                if action_triggered:
                    print(f"Button '{btn.text}' clicked, action: {action_triggered}")

        # Simple hover check for tooltip (in a real game, this would have a delay)
        for btn in buttons:
            if btn.is_hovered and btn.tooltip_text_lines:
                if btn.tooltip_text_lines:
                    tooltip_renders = []
                    max_w = 0
                    total_h = 0
                    for line in btn.tooltip_text_lines:
                        line_surf = tooltip_font.render(line, True, config.WHITE)
                        tooltip_renders.append(line_surf)
                        max_w = max(max_w, line_surf.get_width())
                        total_h += line_surf.get_height() + 2 # 2 for spacing

                    active_tooltip_surface = pygame.Surface((max_w + 8, total_h + 4), pygame.SRCALPHA) # Padding
                    active_tooltip_surface.fill((*config.BLACK, 200)) # Semi-transparent black background

                    current_y = 4 # Start Y for text
                    for surf in tooltip_renders:
                        active_tooltip_surface.blit(surf, (4, current_y))
                        current_y += surf.get_height() + 2
                    tooltip_pos = (mouse_pos[0] + 15, mouse_pos[1] + 15)
                break # Show only one tooltip

        screen.fill(config.GREY)
        for btn in buttons:
            btn.draw(screen)

        if active_tooltip_surface:
            screen.blit(active_tooltip_surface, tooltip_pos)

        pygame.display.flip()

    pygame.quit()
