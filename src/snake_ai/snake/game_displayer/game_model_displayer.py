# This module contains the class that displays a snake game together with a representation of the NN

# Author: Álvaro Torralba
# Date: 24/06/2023
# Version: 0.0.1

from snake_ai.snake.game_displayer.game_displayer_abc import GameDisplayerABC
from snake_ai.snake.game_process.snake_ai_gui_process import SnakeAIGUI
from snake_ai.neural.nn_graphics import NNGraph
from snake_ai.neural.nn import NN
from snake_ai.data import Folders
from snake_ai.IO import IO
import pygame

BLOCK_SIZE = 30
FONT_COLOR = (255, 255, 255)
SCREEN = (1590, 810)
BINARY_MAP = ["wall_s", "wall_e", "wall_n", "wall_w",
              "body_s", "body_e", "body_n", "body_w",
              "apple_s", "apple_e", "apple_n", "apple_w",
              "head_s", "head_e", "head_n", "head_w",
              "tail_s", "tail_e", "tail_n", "tail_w",
              "free_s", "snake_s"]
REAL_MAP = ["wall_n", "wall_w", "wall_s", "wall_e",
            "body_n", "body_w", "body_s", "body_e",
            "apple_n", "apple_w", "apple_s", "apple_e",
            "head_s", "head_e", "head_n", "head_w",
            "tail_s", "tail_e", "tail_n", "tail_w",
            "free_s", "snake_s"]


class GameModelDisplayer(GameDisplayerABC):
    """
    API for displayer classes
    """

    def __init__(self, size: tuple[int, int], speed: int, show_path: bool, graphics: str,
                 brain: NN, vision: str, mediator=None, name: str = None, reload: bool = False):
        """
        Constructor
        :param size: grid game size
        :param speed: integer that controls pygame clock
        :param show_path: boolean flag to control A* rendering
        :param graphics: selected graphics
        :param brain: instance of the NN that controls the game
        :param vision: defines the data type of that is going to feed NN supported options[binary, real]
        :param name: used as flag and name file to produce output statistics
        :param mediator: app mediator instance
        :param reload: flag to indicate if the model must be reloaded, used to update the training displayer
        """
        super().__init__(show_path)
        super().init_pygame(SCREEN)
        pygame.display.set_caption('Model Display')
        self._name = name
        self._size = size
        self._speed = speed
        self._graphics = graphics
        self._model = brain
        self._vision = vision
        self._accuracy = []
        self._efficiency = []
        self._scores = []
        self._completed_games = 0
        self._best_score = 0
        self._input_lb = BINARY_MAP if vision == 'binary' else REAL_MAP
        self._output_lb = ["left", "straight", "right"]
        self._max_score = size[0] * size[1] - 3
        self._mediator = mediator
        self._reload = reload
        self._games = 0
        self._ai = SnakeAIGUI(size=(size[0], size[1]), core=graphics, show_path=show_path, brain=self._model,
                              vision=vision, mode='autoP')
        self._nn_graph = NNGraph(self._ai.controller.layers, self._input_lb, self._output_lb)
        self._ai_rect = self._ai.surface.get_rect(center=((self._game_width / 4) * 3, self._game_height / 2))
        self._nn_graph_rect = self._nn_graph.surface.get_rect(center=(self._game_width / 4, self._game_height / 2))
        self._load_resources()
        self._background = pygame.transform.scale(self._images['background'], (self._game_width, self._game_height))

    def force_init(self):
        """
        Skips the initial dialog window
        :return:
        """
        self._initializing = False
        self._running = True

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

    def _stats_board(self, update: bool) -> None:
        """
        Produces the current stats render
        """
        # Update stats and make holder strings
        if update:
            if len(self._scores) < 20000:
                self._scores.append(self._ai.stats['score'])
                self._accuracy.append(self._ai.stats['accuracy'])
                self._efficiency.append(self._ai.stats['efficiency'])
            self._best_score = self._best_score if self._best_score > self._ai.stats['score'] \
                else self._ai.stats['score']
            self._completed_games = self._completed_games if self._ai.stats['score'] != self._max_score \
                else self._completed_games + 1
        if len(self._accuracy) > 0:
            accu = (sum(self._accuracy) / len(self._accuracy)) * 100
            effi = (sum(self._efficiency) / len(self._efficiency)) * 100
        else:
            accu = 0
            effi = 0
        # Phrases to render
        best_str = self._fonts_s['pixel_font'].render(f"Best: {self._best_score}/{self._max_score}", True, FONT_COLOR)
        accu_str = self._fonts_s['pixel_font'].render(f"Accuracy: {accu:.2f}%", True, FONT_COLOR)
        effi_str = self._fonts_s['pixel_font'].render(f"Efficiency: {effi:.2f}%", True, FONT_COLOR)
        games_str = self._fonts_s['pixel_font'].render(f"C.games: {self._completed_games}/{len(self._accuracy)}",
                                                       True, FONT_COLOR)
        # Create rectangles
        space = 20
        effi_rect = accu_str.get_rect(topright=(self._ai_rect.centerx - space, self._ai_rect.bottom + 3))
        accu_rect = effi_str.get_rect(topleft=(self._ai_rect.centerx + space, self._ai_rect.bottom + 3))
        best_rect = best_str.get_rect(topleft=(accu_rect.right + space, self._ai_rect.bottom + 3))
        c_rect = games_str.get_rect(topright=(effi_rect.left - space, self._ai_rect.bottom + 3))

        # Rendering
        self._screen.blit(best_str, best_rect)
        self._screen.blit(effi_str, effi_rect)
        self._screen.blit(accu_str, accu_rect)
        self._screen.blit(games_str, c_rect)

    def _reset(self) -> None:
        """
        Resets the state of the game
        :return:
        """
        if self._games == 5 and self._reload:
            self._games = 0
            new_model = self._mediator.reload_model()
            self._model = new_model if isinstance(new_model, NN) else self._model
        self._ai = SnakeAIGUI(size=self._size, core=self._graphics, show_path=self._a_star, brain=self._model,
                              vision=self._vision, mode='autoP')

    def run(self):
        """
        Game main loop logic
        :return:
        """
        clock = pygame.time.Clock()
        if self._initializing and not self._running:
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
                    self._screen.blit(self._nn_graph.draw_nn(self._ai.core.vision.tolist(),
                                                             self._ai.controller.nn_activation), self._nn_graph_rect)
                    # Render game state
                    pygame.draw.rect(self._ai.surface, (255, 255, 255), self._ai.surface.get_rect(), 3)
                    self._screen.blit(self._ai.surface, self._ai_rect)
                    self._scoreboard()
                    self._stats_board(False)
                    pygame.display.flip()
                    clock.tick(self._speed)
                else:
                    if self._reload:
                        self._games += 1
                    self._stats_board(True)
                    self._reset()
        # Save statistics
        if len(self._scores) > 0 and self._name is not None:
            try:
                IO.save(Folders.statistics_folder, self._name,
                        {'scores': self._scores, 'efficiencies': self._efficiency})
            except:
                pass
