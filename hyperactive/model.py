# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License

import time
import numbers


def is_numeric(variable):
    return isinstance(variable, numbers.Number)


class Model:
    def __init__(self, model, obj_func_para):
        self.model = model
        self.obj_func_para = obj_func_para

    def eval(self, para_dict):
        para_dict = {**para_dict, **self.obj_func_para}
        results_dict = {}

        start_time = time.time()
        results = self.model(para_dict)
        eval_time = time.time() - start_time

        if isinstance(results, dict):
            if "score" not in results:
                print("Error: model function must return dict with score-keyword")

            results_dict = results
            if "eval_time" not in results_dict:
                results_dict["eval_time"] = eval_time

        else:
            results_dict["score"] = results
            results_dict["eval_time"] = eval_time

        if is_numeric(results_dict["score"]):
            return results_dict
        else:
            print("Error: model function must return numeric variable")
