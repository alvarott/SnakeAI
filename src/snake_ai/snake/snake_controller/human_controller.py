# This module contains the class that implement the necessary tools for human interaction with the game

# Author: Álvaro Torralba
# Date: 16/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_controller.controller_abc import GameController
from snake_ai.snake.enums import GameDirection
import contextlib
with contextlib.redirect_stdout(None):
    import pygame


class HumanController(GameController):
    """
    Implements the responses to the human interaction with the game
    """

    def action(self, current_dir: GameDirection, events: list) -> GameDirection:
        """
        Checks the current direction of the snake and the keyboard input, it returns the new direction where to turn
        :param current_dir: current snake head direction
        :param events: registered keyboard events within a loop
        :return direction: the new direction to take
        """
        keys = [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN]
        key: pygame.constants = None
        direction = current_dir
        for event in events:
            # Key down event
            if event.type == pygame.KEYDOWN:
                key = event.key
        # Update the direction base on the game state
        if key is not None:
            if current_dir in (GameDirection.UP, GameDirection.DOWN) and key in keys:
                if key == pygame.K_RIGHT:
                    direction = GameDirection.RIGHT
                elif key == pygame.K_LEFT:
                    direction = GameDirection.LEFT
            elif current_dir in (GameDirection.LEFT, GameDirection.RIGHT):
                if key == pygame.K_UP:
                    direction = GameDirection.UP
                elif key == pygame.K_DOWN:
                    direction = GameDirection.DOWN
        return direction
