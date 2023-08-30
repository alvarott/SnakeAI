# This module contains the class that displays a snake game with a player controlled snake

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from snake_ai.snake.game_process.snake_human_process import SnakeHuman
from snake_ai.snake.game_process.snake_ai_gui_process import SnakeAIGUI
from snake_ai.snake.game_displayer.game_displayer_abc import GameDisplayerABC
from snake_ai.neural.nn import NN
import pygame


BLOCK_SIZE = 30
X_EXTRA_BLOCKS = 3 * BLOCK_SIZE
Y_EXTRA_BLOCKS = 2 * BLOCK_SIZE
FONT_COLOR = (255, 255, 255)


class GameVSAIDisplayer(GameDisplayerABC):
    """
    API for displayer classes
    """
    def __init__(self, size: tuple[int, int], speed: int, show_path: bool, graphics: str, brain: NN, vision: str):
        """
        Constructor
        :param size: grid game size
        :param speed: integer that controls pygame clock
        :param show_path: boolean flag to control A* rendering
        :param graphics: selected graphics
        :param brain: instance of the NN that controls the game
        :param vision: defines the data type of that is going to feed NN supported options[binary, real]
        @TODO improve the menu interaction
        """
        super().__init__(show_path)
        super().init_pygame(((size[0] * BLOCK_SIZE) * 2 + X_EXTRA_BLOCKS, size[1] * BLOCK_SIZE + Y_EXTRA_BLOCKS))
        pygame.display.set_caption('Player vs AI')
        self._size = size
        self._speed = speed
        self._graphics = graphics
        self._model = brain
        self._vision = vision
        self._player = SnakeHuman(size=(size[0], size[1]), core=graphics, show_path=show_path)
        self._ai = SnakeAIGUI(size=(size[0], size[1]), core=graphics, show_path=show_path,
                              brain=brain, vision=vision, mode='autoP')
        self._load_resources()
        self._player_str = self._fonts['pixel_font'].render(f"Player", True, FONT_COLOR)
        self._player_str_rect = self._player_str.get_rect(bottomleft=(BLOCK_SIZE * 2, BLOCK_SIZE))
        self._ai_str = self._fonts['pixel_font'].render(f"AI", True, FONT_COLOR)
        self._ai_str_rect = self._ai_str.get_rect(bottomleft=(3 * BLOCK_SIZE + self._ai.surface.get_width(),
                                                              BLOCK_SIZE))
        self._ai_anchor = (2 * BLOCK_SIZE + self._ai.surface.get_width(), BLOCK_SIZE)
        self._player_anchor = (BLOCK_SIZE, BLOCK_SIZE)
        self._background = pygame.transform.scale(self._images['background'],
                                                  (self._game_width, self._game_height))
        self._player_init_surface = self._player.surface.copy()
        self._ai_init_surface = self._ai.surface.copy()
        self._start_transition = True
        self._count_down_size = 90
        self._counts = 3
        self._count_speed = 24

    def _init_surface(self) -> None:
        """
        Creates the initial surface
        :return:
        """
        # Place and render key-arrows image
        i_width, i_height = self._images['arrows'].get_size()
        image = pygame.transform.scale(self._images['arrows'], (i_width/3, i_height/3))
        image_rect = image.get_rect(center=(self._game_width/2, self._game_height / 2))
        self._screen.blit(image, image_rect)
        # Place and render phrase 1
        phrase = self._fonts['pixel_font'].render(f"Controlled with", True, FONT_COLOR)
        phrase_rect = phrase.get_rect(center=(self._game_width / 2, (self._game_height / 2) - 150))
        self._screen.blit(phrase, phrase_rect)
        # Place and render phrase 2
        phrase2 = self._fonts['pixel_font'].render(f"Press any key to start", True, FONT_COLOR)
        rect3 = phrase2.get_rect(center=(self._game_width / 2, (self._game_height / 2) + 150))
        self._screen.blit(phrase2, rect3)

    def _final_surface(self) -> None:
        """
        Creates de final surface
        :return:
        """
        # Erase current surface
        self._screen.fill((0, 0, 0))
        # Phrases
        player = self._fonts['pixel_font'].render(f"Player Score: {self._player.stats['score']}", True, FONT_COLOR)
        ai = self._fonts['pixel_font'].render(f"AI Score: {self._ai.stats['score']}", True, FONT_COLOR)
        exit = self._fonts['pixel_font'].render(f"Press Esc-Exit Enter-Retry", True, FONT_COLOR)
        # Rectangles
        player_rect = player.get_rect(center=(self._game_width / 2, (self._game_height / 2) - 100))
        ai_rect = ai.get_rect(center=(self._game_width / 2, (self._game_height / 2) - 50))
        exit_rect = exit.get_rect(center=(self._game_width / 2, (self._game_height / 2) + 100))
        # Render
        self._screen.blit(player, player_rect)
        self._screen.blit(ai, ai_rect)
        self._screen.blit(exit, exit_rect)

    def _scoreboard(self) -> None:
        """
        Generates the scoreboard
        :return:
        """
        # Ai Score and name
        ai_score = self._fonts['pixel_font'].render(f"Score: {self._ai.stats['score']}", True, FONT_COLOR)
        ai_rect = ai_score.get_rect(bottomright=(self._game_width - BLOCK_SIZE * 2, BLOCK_SIZE))
        pl_score = self._fonts['pixel_font'].render(f"Score: {self._player.stats['score']}", True, FONT_COLOR)
        pl_rect = pl_score.get_rect(bottomright=(self._player.surface.get_width(), BLOCK_SIZE))
        self._screen.blit(pl_score, pl_rect)
        self._screen.blit(ai_score, ai_rect)
        self._screen.blit(self._ai_str, self._ai_str_rect)
        self._screen.blit(self._player_str, self._player_str_rect)

    def _reset(self) -> None:
        """
        Resets the state of the game
        :return:
        """
        self._ai = SnakeAIGUI(size=self._size, core=self._graphics, show_path=self._a_star, brain=self._model,
                              vision=self._vision, mode='autoP')
        self._player = SnakeHuman(size=self._size, core=self._graphics, show_path=self._a_star)
        self._player_init_surface = self._player.surface.copy()
        self._ai_init_surface = self._ai.surface.copy()

    def _restart(self) -> None:
        """
        Restarts the game
        :return:
        """
        self._reset()
        self._start_transition = True
        self._screen.fill((0, 0, 0))
        self._init_surface()
        self._initializing = True
        self._running = False
        self._ended = False
        pygame.display.flip()

    def run(self):
        """
        Game main loop logic
        :return:
        """
        timer_size = self._count_down_size
        ticks_left = self._counts
        speed = self._count_speed
        clock = pygame.time.Clock()
        self._init_surface()
        pygame.display.flip()
        while self._alive:
            events = pygame.event.get()
            for event in events:
                # Exit Game event
                if event.type == pygame.QUIT:
                    self._alive = False
                    self._running = False
                    self._ended = False
                    pygame.quit()
                # Initialize game event
                elif event.type == pygame.KEYDOWN and self._initializing:
                    self._running = True
                    self._initializing = False
                # Exit or retry event
                elif event.type == pygame.KEYDOWN and self._ended:
                    key = event.key
                    if key == pygame.K_ESCAPE:
                        self._alive = False
                        self._ended = False
                        pygame.quit()
                    elif key == pygame.K_RETURN:
                        speed = self._count_speed
                        self._restart()
                elif event.type == pygame.KEYDOWN and not self._player.running:
                    key = event.key
                    if key == pygame.K_ESCAPE:
                        self._running = False
                        self._ended = True
                    elif key == pygame.K_r:
                        speed = self._count_speed
                        self._restart()
            # Main event
            if self._running:
                # Refresh background
                self._screen.blit(self._background, (0, 0))
                # Player init count down
                if self._start_transition:
                    if ticks_left ==  0:
                        self._start_transition = False
                        speed = self._speed
                        ticks_left = self._counts
                    else:
                        if timer_size > 4:
                            timer = (pygame.font.Font(self._timer_font_path.open('br'), timer_size)
                                     .render(f"{ticks_left}", True, FONT_COLOR))
                            timer_rect_player = timer.get_rect(center=(self._player.surface.get_width() / 2,
                                                               self._player.surface.get_height() / 2 - 90))
                            timer_rect_ai = timer.get_rect(center=(self._ai.surface.get_width() / 2,
                                                                   self._ai.surface.get_height() / 2 - 90))
                            self._player.surface.blit(self._player_init_surface, (0,0))
                            self._ai.surface.blit(self._ai_init_surface, (0,0))
                            self._player.surface.blit(timer, timer_rect_player)
                            self._ai.surface.blit(timer, timer_rect_ai)
                            timer_size -= 3
                        else:
                            timer_size = self._count_down_size
                            ticks_left -= 1
                else:
                # Player main loop
                    if self._player.running and not self._start_transition:
                        self._player.step(current_dir=self._player.core.direction, events=events)
                    else:
                        game_over = self._fonts['pixel_font'].render(f"GAME OVER!!", True, FONT_COLOR)
                        retry = self._fonts_m['pixel_font'].render(f"Press Esc-Exit R-Retry", True, FONT_COLOR)
                        game_over_rec = game_over.get_rect(center=(self._player.surface.get_width() / 2,
                                                           self._player.surface.get_height() / 2 - 30))
                        retry_rec = retry.get_rect(center=(self._player.surface.get_width() / 2,
                                                           self._player.surface.get_height() / 2 + 20))
                        self._player.surface.blit(game_over, game_over_rec)
                        self._player.surface.blit(retry, retry_rec)
                    # AI step
                    if self._ai.running:
                        self._ai.step(current_dir=self._ai.core.direction, vision=self._ai.core.vision)
                    else:
                        ai_over = self._fonts['pixel_font'].render(f"GAME OVER!!", True, FONT_COLOR)
                        ai_over_rec = ai_over.get_rect(center=(self._ai.surface.get_width() / 2,
                                                               self._ai.surface.get_height() / 2))
                        self._ai.surface.blit(ai_over, ai_over_rec)
                # Render game state
                pygame.draw.rect(self._player.surface, (0, 0, 0), self._player.surface.get_rect(), 4)
                pygame.draw.rect(self._ai.surface, (0, 0, 0), self._ai.surface.get_rect(), 4)
                self._screen.blit(self._player.surface, self._player_anchor)
                self._screen.blit(self._ai.surface, self._ai_anchor)
                self._scoreboard()
                pygame.display.flip()
                clock.tick(speed)
                if not self._player.running and not self._ai.running:
                    self._running = False
                    self._ended = True
            if self._ended:
                self._final_surface()
                pygame.display.flip()
