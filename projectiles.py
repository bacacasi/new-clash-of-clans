import pygame
import math

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, speed=8, color=(255, 255, 0)):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.color = color

        # Calculate direction vector
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.norm_dx = dx / distance
            self.norm_dy = dy / distance
        else:
            self.norm_dx = 0
            self.norm_dy = 0

        # For drawing the tail of the arrow
        self.tail_length = 5

    def update(self):
        """
        Moves the projectile towards its target.
        Returns True if the projectile has reached its target, False otherwise.
        """
        # Move projectile
        self.x += self.norm_dx * self.speed
        self.y += self.norm_dy * self.speed

        # Check if projectile has reached or passed the target
        # A simple way is to check if the distance to target is very small
        distance_to_target = math.hypot(self.x - self.target_x, self.y - self.target_y)
        if distance_to_target < self.speed: # Close enough to be considered "arrived"
            return True
        return False

    def draw(self, screen):
        """
        Draws the projectile on the screen as a line.
        """
        # The end of the line is the projectile's current position
        end_pos = (int(self.x), int(self.y))
        # The start of the line is a short distance behind the end, creating a "tail"
        start_pos = (int(self.x - self.norm_dx * self.tail_length),
                     int(self.y - self.norm_dy * self.tail_length))
        pygame.draw.line(screen, self.color, start_pos, end_pos, 2)
