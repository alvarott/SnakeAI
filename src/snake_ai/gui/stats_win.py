# This module contains the class that implements the GUI stats window

# Author: Álvaro Torralba
# Date: 22/08/2023
# Version: 0.0.1


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox
from snake_ai.gui.abc_win import WindowABC
from snake_ai.gui._data import FileConfig
from matplotlib.figure import Figure
from snake_ai.data import Folders
import matplotlib.pyplot as plt
import customtkinter as ctk
from snake_ai.IO import IO
import os


class StatsWindow(WindowABC):
    """
    Implements the stats window
    """

    def __init__(self, top_level: ctk.CTk, mediator):
        super().__init__(size=(600, 600), resizeable=False, top_level=top_level, mediator=mediator)
        plt.style.use('bmh')
        # data
        self._data = {}
        self._extension = FileConfig().stats_file
        # Master Frames
        self._master_frame = ctk.CTkFrame(master=self.window)

        # Figures
        self._score_fig = Figure(figsize=(5, 3.5), dpi=100)
        self._efficiency_fig = Figure(figsize=(5, 3.5), dpi=100)

        # Plots
        self._score_plot = self._score_fig.add_subplot()
        self._efficiency_plot = self._efficiency_fig.add_subplot()
        # Plot labels
        self._score_plot.set_title('Score per Game')
        self._efficiency_plot.set_title('Efficiency')

        # Plot Data
        self._avg_fitness = []
        self._avg_score = []
        self._avg_moves = []
        self._avg_turns = []
        self._avg_efficiency = []

        # Canvas
        self._score_canvas = FigureCanvasTkAgg(figure=self._score_fig, master=self._master_frame)
        self._efficiency_canvas = FigureCanvasTkAgg(figure=self._efficiency_fig, master=self._master_frame)

        # Buttons
        self._browse_button = self._NextWinButton(master=self._master_frame, text='Select Stats',
                                                  font=self._buttons_font,
                                                  command=self._browse,
                                                  width=100, height=20)

        self._back_button = self._NextWinButton(master=self._master_frame, text='Back',
                                                font=self._buttons_font,
                                                command=lambda: self._mediator.back_to_main(self.window),
                                                width=100, height=20)

        # Griding
        self._master_frame.grid_propagate(False)
        self._master_frame.columnconfigure(index=0, weight=1, uniform='g')
        self._master_frame.rowconfigure(index=(0, 1), weight=5, uniform='d')
        self._master_frame.rowconfigure(index=2, weight=1, uniform='d')

        # Placements
        self._master_frame.pack(expand=True, fill='both')
        self._score_canvas.get_tk_widget().grid(column=0, row=0, sticky='news', padx=20, pady=10)
        self._efficiency_canvas.get_tk_widget().grid(row=1, sticky='news', padx=20, pady=10)
        self._back_button.place(x=170, y=555)
        self._browse_button.place(x=330, y=555)

    def _browse(self):
        """
        Browse button behavior
        :return:
        """
        data = self._check_files()
        models = []
        scores = []
        efficiencies = []
        colors = ['#33ff00', '#00ffff', '#ccff00', '#ff0099', '#ff9900']
        # Collect data
        if data != -1 and len(data) > 0:
            for item in data.items():
                models.append(item[0] if len(item[0]) < 15 else item[0][:14])
                scores.append(item[1]['scores'])
                efficiencies.append(item[1]['efficiencies'])
            # Plot scores data
            self._score_plot.clear()
            self._score_plot.set_title('Score per Game')
            boxes = self._score_plot.boxplot(scores, vert=True, patch_artist=True)['boxes']
            for i, box in enumerate(boxes):
                box.set_facecolor(colors[i])
            self._score_plot.set_xticklabels(models)
            self._score_canvas.draw()
            # Plot efficiency data
            self._efficiency_plot.clear()
            self._efficiency_plot.set_title('Efficiency per Game')
            boxes = self._efficiency_plot.boxplot(efficiencies, vert=True, patch_artist=True)['boxes']
            for i, box in enumerate(boxes):
                box.set_facecolor(colors[i])
            self._efficiency_plot.set_xticklabels(models)
            self._efficiency_canvas.draw()

    def _check_files(self):
        """
        Check if the selected files contains the right format
        :return:
        """

        def file_error():
            messagebox.showerror('Incorrect dataset',
                                 f'{name} does not contain a supported dataset',
                                 parent=self.window)

        path = filedialog.askopenfilenames(initialdir=Folders.statistics_folder, title="Select files",
                                           filetypes=self._extension, parent=self.window)
        data = {}
        for file in path[:5]:
            name = os.path.basename(file)
            if os.path.isfile(file):
                try:
                    model_data = IO.load(file, dict)
                    if not all(key in model_data.keys() for key in ['scores', 'efficiencies']):
                        file_error()
                        return -1
                    data[name[:name.index('.')]] = model_data
                except Exception:
                    file_error()
            else:
                messagebox.showerror('File not found',
                                     f'The selected file "{name}"has vanished from the specified path',
                                     parent=self.window)
                return -1
        return data
