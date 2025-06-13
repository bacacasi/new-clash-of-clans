# ui_elements.py
import pygame
import config

class Button:
    def __init__(self, x, y, width, height, text, action_key, font,
                 bg_color=config.BUTTON_BG_COLOR, text_color=config.BUTTON_TEXT_COLOR,
                 hover_color=config.BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_key = action_key # To identify what button does (e.g., "build_town_hall")
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_active_action = False # If this button's action is currently selected

    def draw(self, surface):
        current_bg_color = self.bg_color
        if self.is_active_action:
            current_bg_color = self.hover_color # Use hover color to show it's active
        elif self.is_hovered:
            current_bg_color = self.hover_color

        pygame.draw.rect(surface, current_bg_color, self.rect)
        pygame.draw.rect(surface, config.BLACK, self.rect, 2) # Border

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        # Reset active state on new event, Game class will manage re-setting it if needed
        # self.is_active_action = False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered: # Left click
                # self.is_active_action = True # Visually mark as active (optional here, Game can manage)
                return self.action_key # Return action when clicked
        return None

    def update_active_state(self, current_game_action):
        """Allows the game to tell the button if its action is the current one."""
        if self.action_key == current_game_action:
            self.is_active_action = True
        else:
            self.is_active_action = False

if __name__ == '__main__':
    pygame.init()
    screen_width = 400
    screen_height = 200
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Button Test")

    font = pygame.font.Font(config.DEFAULT_FONT_NAME, config.DEFAULT_FONT_SIZE)

    button1 = Button(50, 50, 150, 50, "Test Button 1", "test1", font)
    button2 = Button(50, 120, 180, 50, "Another Button", "test2", font, bg_color=config.RED)

    buttons = [button1, button2]
    current_action_from_game = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons:
                action_triggered = btn.handle_event(event)
                if action_triggered:
                    print(f"Button '{btn.text}' clicked, action: {action_triggered}")
                    current_action_from_game = action_triggered # Simulate game selecting an action

        # Update button active states based on game's current action
        for btn in buttons:
            btn.update_active_state(current_action_from_game)

        screen.fill(config.GREY)
        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()

    pygame.quit()
