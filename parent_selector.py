"""
Base class for parent selectors.
"""
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import List

DEFAULT_FITNESS = [{"metric_name": "score", "maximize": True}]


class ParentSelector(ABC):
    """
    Base class for parent selection algorithms.
    """

    def __init__(self, experiment_params: Dict[str, Any]):
        """
        Constructs a new ParentSelector
        :param experiment_params: the experiment parameters dictionary
        """
        self.experiment_params = experiment_params

    @abstractmethod
    def sort_individuals(self, individuals: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Sorts the passed list of individuals. Implementation is left to subclasses.
        :param individuals: a list of individuals to sort. Note: this list will be modified (sorted)
        :return: the passed individuals list, sorted
        """

    @abstractmethod
    def select_couple(self, sorted_parents: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Select two individuals for reproduction. Implementation is left to subclasses.
        :param sorted_parents: a list of individuals to choose from, sorted, best first
        :return: a list of 2 potentially identical individuals.
        """

    def get_objectives(self) -> List[Dict]:
        """
        Get the objectives for this experiment. Based on previously supplied experiment params. For backwards
        compatibility, if no fitness is specified by the client, `DEFAULT_FITNESS` is used.
        DEF: For the future, leaf-common has a whole series of classes that get
        FitnessObjective information from the config in a consolidated manner
        :return: A list of dicts, where each item in the list is a fitness metric to be optimized.
        """
        if not self.experiment_params or 'evolution' not in self.experiment_params \
                or 'fitness' not in self.experiment_params['evolution']:
            return DEFAULT_FITNESS

        return self.experiment_params['evolution']['fitness']
