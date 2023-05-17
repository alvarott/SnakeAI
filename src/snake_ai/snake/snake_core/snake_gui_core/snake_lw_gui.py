# This module contains a graphic lightweight processing implementation of the Snake game

# Author: Álvaro Torralba
# Date: 15/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_core.snake_gui_core.snake_gui_abc import SnakeGUI
from pygame.surface import Surface


class SnakeLWGUI(SnakeGUI):
    """
    This class implements a graphic lightweight
    """

    # Class constant
    IMAGES = 'lw_gui'

    def __init__(self, size: tuple[int, int], dist_calculator: str, mode: str, show_path: bool = False):
        """
        Constructor
        :param size: grid size
        :param dist_calculator: flag to select the distance calculator to be used
        :param mode: flag to indicate the mode: human controlled or auto controlled
        :param show_path: flag to indicate if the min path must be displayed while rendering
        """
        super().__init__(size=size, img_folder=SnakeLWGUI.IMAGES, dist_calculator=dist_calculator, mode=mode, show_path=show_path)
        self._background: Surface = self._build_background()
        self.render_surface()

    def _build_background(self) -> Surface:
        """
        Produces the background of the game
        :return:
        """
        ref_cell = [0, 0]
        background = Surface(self._dim)
        for i in range(self._rows):
            for j in range(self._cols):
                background.blit(self._images['background'], (ref_cell[0], ref_cell[1]))
                ref_cell[1] += SnakeGUI.BLOCK_SIZE
            ref_cell[0] += SnakeGUI.BLOCK_SIZE
            ref_cell[1] = 0
        return background

    def render_surface(self) -> None:
        """
        Produces all the objects to be rendered in the game board
        :return:
        """
        surface = Surface(self._dim)
        # Render background
        surface.blit(self._background, (0, 0))
        # Render apple
        surface.blit(self._images['apple'], SnakeGUI._cell_to_pixels(self._apple))
        # Render path
        self._render_min_pth(surface)
        # Render Snake
        surface.blit(self._images['head'], SnakeGUI._cell_to_pixels(self.head.pos()))
        current = self.tail
        for _ in range(self._snake.length-1):
            surface.blit(self._images['body'], SnakeGUI._cell_to_pixels(current.pos()))
            current = current.next
        # Render scoreboard
        score = self._fonts['pixel_font'].render(f"Score: {self._stats_data.score}", True, (255, 205, 255))
        surface.blit(score, (self._width - score.get_width(), 0))
        self._surface = surface
