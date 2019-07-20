# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


import numpy as np
import random

from ...base import BaseOptimizer
from ...base import BasePositioner


class EvolutionStrategyOptimizer(BaseOptimizer):
    def __init__(
        self,
        search_config,
        n_iter,
        metric="accuracy",
        n_jobs=1,
        cv=5,
        verbosity=1,
        random_state=None,
        warm_start=False,
        memory=True,
        scatter_init=False,
        individuals=10,
        mutation_rate=0.7,
        crossover_rate=0.3,
    ):
        super().__init__(
            search_config,
            n_iter,
            metric,
            n_jobs,
            cv,
            verbosity,
            random_state,
            warm_start,
            memory,
            scatter_init,
        )

        self.individuals = individuals
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

        self.n_mutations = int(round(self.individuals * mutation_rate))
        self.n_crossovers = int(round(self.individuals * crossover_rate))

        self.initializer = self._init_evo

    def _init_individuals(self, _cand_):
        self.ind_list = [Individual(1) for _ in range(self.individuals)]
        for ind in self.ind_list:
            ind.pos = _cand_._space_.get_random_pos()
            ind.pos_best = ind.pos

    def _mutate_individuals(self, _cand_, mutate_idx):
        self.ind_list = np.array(self.ind_list)
        for ind in self.ind_list[mutate_idx]:
            ind.climb(_cand_)

    def _crossover(self, _cand_, cross_idx, replace_idx):
        self.ind_list = np.array(self.ind_list)
        for i, ind in enumerate(self.ind_list[replace_idx]):
            j = i + 1
            if j == len(cross_idx):
                j = 0

            pos_new = self._cross_two_ind(
                [self.ind_list[cross_idx][i], self.ind_list[cross_idx][j]]
            )

            ind.pos = pos_new

    def _cross_two_ind(self, ind_list):
        pos_new = []

        for pos1, pos2 in zip(ind_list[0].pos, ind_list[1].pos):
            rand = random.randint(0, 1)
            if rand == 0:
                pos_new.append(pos1)
            else:
                pos_new.append(pos2)

        return np.array(pos_new)

    def _new_generation(self, _cand_):

        idx_sorted_ind = self._rank_individuals()
        mutate_idx, cross_idx, replace_idx = self._select_individuals(idx_sorted_ind)

        self._mutate_individuals(_cand_, mutate_idx)
        self._crossover(_cand_, cross_idx, replace_idx)

    def _eval_individuals(self, _cand_, X, y):
        for ind in self.ind_list:
            para = _cand_._space_.pos2para(ind.pos)
            ind.score, _, _ = _cand_._model_.train_model(para, X, y)

            if ind.score > ind.score_best:
                ind.score_best = ind.score
                ind.pos_best = ind.pos

    def _rank_individuals(self):
        scores_list = []
        for ind in self.ind_list:
            scores_list.append(ind.score)

        scores_np = np.array(scores_list)
        idx_sorted_ind = list(scores_np.argsort()[::-1])

        return idx_sorted_ind

    def _select_individuals(self, index_best):
        mutate_idx = index_best[: self.n_mutations]
        cross_idx = index_best[: self.n_crossovers]

        n = self.individuals - max(self.n_mutations, self.n_crossovers)
        replace_idx = index_best[-n:]

        return mutate_idx, cross_idx, replace_idx

    def _find_best_individual(self, _cand_):
        for ind in self.ind_list:
            if ind.score_best > _cand_.score_best:
                _cand_.score_best = ind.score_best
                _cand_.pos_best = ind.pos_best

    def _iterate(self, i, _cand_, X, y):
        self._new_generation(_cand_)
        self._eval_individuals(_cand_, X, y)
        self._find_best_individual(_cand_)

        return _cand_

    def _init_evo(self, _cand_):
        self._init_individuals(_cand_)


class Individual(BasePositioner):
    def __init__(self, eps):
        super().__init__(eps)

        self.pos = None
        self.pos_best = None

        self.score = -1000
        self.score_best = -1000
