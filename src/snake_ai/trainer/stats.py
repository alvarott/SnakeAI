# This module contains the class that implements all the logic to process a generates data to be plotted over
# generations performance

# Author: Álvaro Torralba
# Date: 06/09/2023
# Version: 0.0.1


class Stats:
    """
    Generates the plotting data from populations metrics
    """
    def __init__(self, max_score):
        """
        Constructor
        :param max_score: max possible score
        """
        self._limit_score = max_score

    def generation_stats(self, population_stats: list[tuple[int, dict[str, float]]], fitness: dict[int, float]) -> dict:
        """
        Generates the data to be plotted over the last generation
        :param population_stats: last population stats
        :param fitness: last population fitness
        :return:
        """
        scores = []
        moves = []
        efficiencies = []
        for i in population_stats:
            moves.append(i[1]['moves'])
            scores.append(i[1]['score'])
            efficiencies.append(i[1]['efficiency'])
        # Calculate averages
        fitness_avg = sum(list(fitness.values())) / len(fitness)
        score_avg = sum(scores) / len(scores)
        score_max = max(scores)
        total_max_sc = scores.count(self._limit_score)
        moves_avg = sum(moves) / len(moves)
        efficiencies_avg = sum(efficiencies) / len(efficiencies)
        return {'fitness_avg': fitness_avg, 'score_avg': score_avg, 'scores': scores, 'moves_avg': moves_avg,
                'efficiencies_avg': efficiencies_avg, 'score_max': score_max, 'total_max_sc': total_max_sc}
