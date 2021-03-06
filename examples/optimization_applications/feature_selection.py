import numpy as np
import itertools
from sklearn.datasets import load_boston
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from hyperactive import Hyperactive, HillClimbingOptimizer

data = load_boston()
X, y = data.data, data.target


def model(opt):
    feature_idx_list = []
    for key in opt.keys():
        if "feature" not in key:
            continue
        if opt[key] is False:
            continue

        nth_feature = int(key.rsplit(".", 1)[1])
        feature_idx_list.append(nth_feature)

    if len(feature_idx_list) == 0:
        return 0

    feature_idx_list = [idx for idx in feature_idx_list if idx is not None]
    x_new = X[:, feature_idx_list]

    knr = KNeighborsRegressor(n_neighbors=opt["n_neighbors"])
    scores = cross_val_score(knr, x_new, y, cv=5)
    score = scores.mean()

    return score


search_space = {
    "n_neighbors": list(range(1, 100)),
    "feature.0": [True, False],
    "feature.1": [True, False],
    "feature.2": [True, False],
    "feature.3": [True, False],
    "feature.4": [True, False],
    "feature.5": [True, False],
    "feature.6": [True, False],
    "feature.7": [True, False],
    "feature.8": [True, False],
    "feature.9": [True, False],
    "feature.10": [True, False],
    "feature.11": [True, False],
    "feature.12": [True, False],
}


hyper = Hyperactive()
hyper.add_search(model, search_space, n_iter=1500)
hyper.run()

