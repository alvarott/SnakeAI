# This module contains the class that displays a snake game together with a representation of the NN

# Author: Álvaro Torralba
# Date: 24/06/2023
# Version: 0.0.1

from snake_ai.snake.game_displayer.game_displayer_abc import GameDisplayerABC
from snake_ai.snake.game_process.snake_ai_gui_process import SnakeAIGUI
from snake_ai.neural.nn_graphics import NNGraph
from snake_ai.IO import IO
import pygame


BLOCK_SIZE = 30
FONT_COLOR = (255, 255, 255)
SCREEN = (1590, 810)


class GameModelDisplayer(GameDisplayerABC):
    """
    API for displayer classes
    """
    def __init__(self, size: tuple[int, int], speed: int, dist_calculator: str, show_path: bool, graphics: str,
                 brain_path: str):
        """
        Constructor
        :param size: grid game size
        :param speed: integer that controls pygame clock
        :param dist_calculator:
        :param show_path: boolean flag to control A* rendering
        :param graphics: selected graphics
        :param brain_path: path to the snake brain
        """
        super().__init__(show_path)
        super().init_pygame(SCREEN)
        pygame.display.set_caption('Model Display')
        self._size = size
        self._speed = speed
        self._dist = dist_calculator
        self._graphics = graphics
        self._model = IO.load(brain_path)
        self._ai = SnakeAIGUI(size=(size[0], size[1]), core=graphics,
                              dist_calculator=dist_calculator, show_path=show_path, brain=self._model)
        self._nn_graph = NNGraph(self._ai.layers)
        self._ai_rect = self._ai.surface.get_rect(center=((self._game_width / 4) * 3, self._game_height / 2))
        self._nn_graph_rect = self._nn_graph.surface.get_rect(center=(self._game_width / 4, self._game_height / 2))
        self._load_resources()
        self._background = pygame.transform.scale(self._images['background'], (self._game_width, self._game_height))

    def _init_surface(self) -> None:
        """
        Creates the initial surface
        :return:
        """
        # Place and render phrase 1
        phrase = self._fonts['pixel_font'].render(f"Press any key to start the simulation", True, FONT_COLOR)
        phrase_rect = phrase.get_rect(center=(self._game_width / 2, (self._game_height / 2) - 75))
        self._screen.blit(phrase, phrase_rect)
        # Place and render phrase 2
        phrase2 = self._fonts['pixel_font'].render(f"Press Esc to end it", True, FONT_COLOR)
        rect3 = phrase2.get_rect(center=(self._game_width / 2, (self._game_height / 2) + 75))
        self._screen.blit(phrase2, rect3)

    def _scoreboard(self) -> None:
        """
        Generates the scoreboard
        :return:
        """
        # Ai Score and name
        ai_score = self._fonts['pixel_font'].render(f"Score: {self._ai.stats['score']}", True, FONT_COLOR)
        ai_rect = ai_score.get_rect(bottomright=(self._ai_rect.right - BLOCK_SIZE, self._ai_rect.top))
        self._screen.blit(ai_score, ai_rect)

    def _reset(self) -> None:
        """
        Resets the state of the game
        :return:
        """
        self._ai = SnakeAIGUI(size=self._size, core=self._graphics, dist_calculator=self._dist,
                              show_path=self._a_star, brain=self._model)

    def run(self):
        """
        Game main loop logic
        :return:
        """
        clock = pygame.time.Clock()
        self._init_surface()
        pygame.display.flip()
        while self._alive:
            events = pygame.event.get()
            for event in events:
                # Exit Game event
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self._alive = False
                    self._running = False
                    self._ended = False
                    pygame.quit()
                # Initialize game event
                elif event.type == pygame.KEYDOWN and self._initializing:
                    self._running = True
                    self._initializing = False
            # Main event
            if self._running:
                if self._ai.running:
                    # Refresh background
                    self._screen.blit(self._background, (0, 0))
                    # AI step
                    if self._ai.running:
                        self._ai.step(current_dir=self._ai.core.direction, vision=self._ai.core.vision)
                    # Draw the NN
                    self._screen.blit(self._nn_graph.draw_nn(self._ai.nn_activations), self._nn_graph_rect)
                    # Render game state
                    pygame.draw.rect(self._ai.surface, (0, 0, 0), self._ai.surface.get_rect(), 4)
                    self._screen.blit(self._ai.surface, self._ai_rect)
                    self._scoreboard()
                    pygame.display.flip()
                    clock.tick(self._speed)
                else:
                    self._reset()
