"""
Implementation of a parent selector inspired by NSGA-II
For more information, readers are encouraged to refer to this paper:
K. Deb, A. Pratap, S. Agarwal, and T. Meyarivan. 2002. A fast and elitist
multiobjective genetic algorithm: NSGA-II. Trans. Evol. Comp 6, 2 (April
2002), 182-197. DOI=http://dx.doi.org/10.1109/4235.996017
Or http://www.dmi.unict.it/mpavone/nc-cs/materiale/NSGA-II.pdf
"""
import math

from typing import Dict
from typing import List

import numpy as np

from parent_selector import ParentSelector



class Nsga2ParentSelector(ParentSelector):
    """
    This class implements a parent selection method inspired by the NSGA-II algorithm
    """

    def prepare_fronts(self, individuals: List[Dict[str, object]]) -> Dict[int, List[Dict[str, object]]]:
        """
        Exposed only for testing purporses
        """

        fronts = self._fast_non_dominated_sort(individuals)
        # Compute the crowding distances of each front
        for front in fronts.values():
            self._crowding_distance_assignment(front)

        return fronts

    def _fast_non_dominated_sort(self, individuals):
        """
        Implementation of the NSGA-II fast-non-dominated-sort algorithm.
        :param individuals: a list of evaluated individuals (i.e. with metrics)
        :return: a dictionary of fronts containing their respective individuals: front[1] contains the list of
        individuals composing the pareto-optimal front.
        """
        fronts = {1: []}
        for indy in individuals:
            # Sp: a set of indies that indy dominates
            indy["dominated"] = []
            # nb: domination count: number of indies that dominate indy
            indy["nb_dominators"] = 0
            for other in individuals:
                if self._dominates(indy, other, self.get_objectives()):
                    indy["dominated"].append(other)
                elif self._dominates(other, indy, self.get_objectives()):
                    indy["nb_dominators"] += 1
            if indy["nb_dominators"] == 0:
                indy["metrics"]["NSGA-II_rank"] = 1  # First front
                fronts[1].append(indy)
        i = 1
        while fronts[i]:
            # Q: Used to store the members of the next front
            next_front = []
            for indy in fronts[i]:
                for dominated in indy["dominated"]:
                    dominated["nb_dominators"] -= 1
                    if dominated["nb_dominators"] == 0:
                        dominated["metrics"]["NSGA-II_rank"] = i + 1
                        next_front.append(dominated)
            i += 1
            fronts[i] = next_front
        return fronts

    @staticmethod
    def _dominates(indy_1, indy_2, objectives):
        """
        Dominance Test:
        (According to page 5 of https://engineering.purdue.edu/~sudhoff/ee630/Lecture09.pdf)
        indy_1 dominates indy_2 if:
          - indy_1 is no worse than indy_2 in all objectives
          - indy_1 is strictly better than indy_2 in at least one objective
        indy_1 dominates indy_2 is equivalent to indy_2 is dominated by indy_1.
        :param indy_1: an individual with metrics
        :param indy_2: an individual with metrics
        :param objectives: a list of objectives. For instance:
                [
                    {"metric_name": "score", "maximize": True},
                    {"metric_name": "steps", "maximize": False}
                 ]
        :return: True if indy_1 dominates indy_2, False otherwise
        """
        # An individual can't be better than itself
        if indy_1["id"] == indy_2["id"]:
            return False

        # indy_1 is no worse than indy_2 in all objectives
        for objective in objectives:
            if Nsga2ParentSelector.is_worse(indy_1, indy_2, objective):
                return False

        # indy_1 is strictly better than indy_2 in at least one objective
        for objective in objectives:
            # Return true is indy_1 is better than indy_2 in at least one objective
            if Nsga2ParentSelector.is_strictly_better(indy_1, indy_2, objective):
                return True

        return False

    @staticmethod
    def is_worse(indy_1: Dict[str, object], indy_2: Dict[str, object],
                 objective: Dict[str, object]) -> bool:
        """
        Returns True if indy_1 is worse than indy_2 for the passed objective
        :param indy_1: an individual with metrics
        :param indy_2: an individual with metrics
        :param objective: an objective dictionary in the form {"metric_name": "score", "maximize": True}
        :return: True is indy_1 is worse than indy_2, False otherwise
        """
        metric_name = objective["metric_name"]
        if objective["maximize"]:
            # Maximize: higher is better. So indy_1 is worse if it's lower than indy_2
            is_worse = indy_1["metrics"][metric_name] < indy_2["metrics"][metric_name]
        else:
            # Minimize: lower is better. So indy_1 is worse if it's bigger than indy_2
            is_worse = indy_1["metrics"][metric_name] > indy_2["metrics"][metric_name]
        return is_worse

    @staticmethod
    def is_strictly_better(indy_1: Dict[str, object], indy_2: Dict[str, object],
                           objective: Dict[str, object]) -> bool:
        """
        Returns True if indy_1 is strictly better than indy_2 for the passed objective
        :param indy_1: an individual with metrics
        :param indy_2: an individual with metrics
        :param objective: an objective dictionary in the form {"metric_name": "score", "maximize": True}
        :return: True is indy_1 is strictly better than indy_2, False otherwise
        """
        metric_name = objective["metric_name"]
        if objective["maximize"]:
            # Maximize: higher is better. So indy_1 is strictly better if it's higher than indy_2
            is_strictly_better = indy_1["metrics"][metric_name] > indy_2["metrics"][metric_name]
        else:
            # Minimize: lower is better. So indy_1 is better if it's lower than indy_2
            is_strictly_better = indy_1["metrics"][metric_name] < indy_2["metrics"][metric_name]
        return is_strictly_better

    def _crowding_distance_assignment(self, front):
        """
        Computes the crowding distance and sets it for each individual in the passed front.
        :param front: a list of individuals belonging to the same front
        :return: nothing, sets a 'NSGA-II_crowding_distance' variable for each individual in the front
        """
        # Special cases for fronts of 2 or less individuals
        if not front:
            return

        if len(front) == 1:
            front[0]["metrics"]["NSGA-II_crowding_distance"] = math.inf
            return

        if len(front) == 2:
            front[0]["metrics"]["NSGA-II_crowding_distance"] = math.inf
            front[1]["metrics"]["NSGA-II_crowding_distance"] = math.inf
            return

        # Initialize the distances to 0
        for indy in front:
            indy["metrics"]["NSGA-II_crowding_distance"] = 0

        # For each objective
        for objective in self.get_objectives():
            metric_name = objective["metric_name"]
            # Sort using each objective value
            # We're measuring distances, so whether we minimize or maximize the objective does not matter.
            # Sort the individuals according to the objective value in ascending order
            # Equivalent to:
            # sorted_individuals = sorted(front, key=lambda k: k["metrics"][metric_name])
            # But Pylint "W0640: Cell variable metric_name defined in loop (cell-var-from-loop)"
            # made me use a "default value of a parameter to the lambda":
            sorted_individuals = sorted(front, key=lambda k, sk=metric_name: k["metrics"][sk])
            objective_min = sorted_individuals[0]["metrics"][metric_name]
            objective_max = sorted_individuals[-1]["metrics"][metric_name]
            norm = objective_max - objective_min
            # set crowding_distance to infinity for the boundaries
            sorted_individuals[0]["metrics"]["NSGA-II_crowding_distance"] = math.inf
            sorted_individuals[-1]["metrics"]["NSGA-II_crowding_distance"] = math.inf
            # If norm is 0 it means all the metrics are the same (e.g. ties). Skip this metric, there is no distance.
            if norm != 0:
                # For all the individuals between the first one and the last one
                for i in range(1, len(sorted_individuals) - 1):
                    objective_distance = (sorted_individuals[i + 1]["metrics"][metric_name] -
                                          sorted_individuals[i - 1]["metrics"][metric_name])
                    normalized_objective_distance = objective_distance / norm
                    distance = \
                        sorted_individuals[i]["metrics"]["NSGA-II_crowding_distance"] + normalized_objective_distance
                    sorted_individuals[i]["metrics"]["NSGA-II_crowding_distance"] = distance

    def sort_individuals(self, individuals: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        # Prepares the fronts,
        # Sorts the passed individuals by rank first, where lower is better
        # Then by crowding_distance, where higher is better. Note: using the negative value to flip the
        crowding_distance ordering
        :param individuals: a list of individuals to sort. Note: this list will be modified (sorted)
        :return: the passed individuals list, sorted
        """
        _ = self.prepare_fronts(individuals)
        self.internal_sort_individuals(individuals)
        return individuals

    def internal_sort_individuals(self, individuals: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        # Sorts the passed individuals by rank first, where lower is better
        # Then by crowding_distance, where higher is better. Note: using the negative value to flip the
        crowding_distance ordering
        :param individuals: a list of individuals to sort. Note: this list will be modified (sorted)
        :return: the passed individuals list, sorted
        """
        individuals.sort(key=lambda indy: (indy["metrics"]["NSGA-II_rank"],
                                           -indy["metrics"]["NSGA-II_crowding_distance"]))
        return individuals

    def select_couple(self, sorted_parents: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Tournament Selection with replacement. The 2 parents can be the same, effectively allowing cloning.
        Selects 2 individuals from the passed list. Compares them and keeps the one with the highest fitness.
        Selects 2 individuals again from the same list. Compares them and keeps the one with the highest fitness.
        :param sorted_parents: a list of individuals to choose from, sorted, best first
        :return: a list of 2 potentially identical individuals.
        """
        # Pick 2 individuals' index randomly. Could be the same one twice. Keep the lowest index, as it means the
        # individual as a better rank or crowding_distance
        chosen_index = min(np.random.choice(np.arange(len(sorted_parents)), 2, replace=True))
        parent1 = sorted_parents[chosen_index]

        # Do the same thing for parent1
        chosen_index = min(np.random.choice(np.arange(len(sorted_parents)), 2, replace=True))
        parent2 = sorted_parents[chosen_index]
        return [parent1, parent2]

    def select_to_remove(self, sorted_parents: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Tournament Selection with replacement. The 2 parents can be the same, effectively allowing cloning.
        Selects 2 individuals from the passed list. Compares them and keeps the one with the highest fitness.
        Selects 2 individuals again from the same list. Compares them and keeps the one with the highest fitness.
        :param sorted_parents: a list of individuals to choose from, sorted, best first
        :return: a list of 2 potentially identical individuals.
        """
        # Pick 2 individuals' index randomly. Could be the same one twice. Keep the lowest index, as it means the
        # individual as a better rank or crowding_distance
        chosen_index = max(np.random.choice(np.arange(len(sorted_parents)), 2, replace=True))
        idx_to_remove = sorted_parents[chosen_index]


