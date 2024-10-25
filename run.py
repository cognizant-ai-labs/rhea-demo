"""
Script for running RHEA experiments in the Illustrative Domain.
"""

import argparse
import random

import numpy as np

from tqdm import tqdm

from expert_models import expert_model_1, expert_model_2, expert_model_3
from evolutionary_operators import random_candidate, rules_mutate, rules_crossover
from nsga2_parent_selector import Nsga2ParentSelector
from predictor import evaluate_candidate, collect_behavior, compute_oracle_front



parser = argparse.ArgumentParser()
parser.add_argument("--method", help="either rhea or evolution", required=True)
args = parser.parse_args()

method = args.method
assert method in ['rhea', 'evolution']
results_file = f'{method}_results.csv'

selector_params = {'evolution': {'fitness': [{"metric_name": "utility", "maximize": True},
                                             {"metric_name": "cost", "maximize": False}]}}
selector = Nsga2ParentSelector(experiment_params=selector_params)

optimal_front = compute_oracle_front()

pop_size = 20
n_generations = 500
n_trials = 100

for trial in range(n_trials):

    for n_actions in [10, 15, 20, 25, 30, 35, 40, 45, 50]:


        # Initialize population
        if method == 'rhea':
            initial_individuals = [expert_model_1, expert_model_2, expert_model_3]
        else:
            initial_individuals = [random_candidate(n_actions=n_actions) for i in range(3)]

        population = []
        behavior_set = {} # Use to prevent duplicate behaviors
        curr_id = 0

        # Start by evaluating initial individuals and placing them in the population
        for candidate in initial_individuals:
            utility, cost = evaluate_candidate(candidate)
            indy = {'rules': candidate,
                    'metrics': {'utility': utility,
                                'cost': cost},
                    'id': curr_id
                   }
            behavior = collect_behavior(candidate)
            behavior_set[behavior] = curr_id
            indy['behavior'] = behavior
            population.append(indy)
            curr_id += 1

        # Run evolution
        for gen in tqdm(range(n_generations)):

            # Compute closeness to oracle front
            utilities = [indy['metrics']['utility'] for indy in population]
            costs = [indy['metrics']['cost'] for indy in population]
            pop_metrics = set()
            for utility, cost in zip(utilities, costs):
                pop_metrics.add((utility, cost))
            still_to_find = []
            for utility, cost in optimal_front[0]:
                if (utility, cost) not in pop_metrics:
                    still_to_find.append((utility, cost))

            if (len(still_to_find) == 0) or (gen == n_generations - 1):
                print(f"\n# actions: {n_actions}; gens: {gen}\n")
                with open(results_file, 'a') as f:
                    f.write(f"{n_actions},{gen},{still_to_find}\n")
                break

            # Generate new individuals
            generation_size = 10 * pop_size
            new_candidates = []
            while len(population) + len(new_candidates) < generation_size:

                # Select parents
                parent1_idx, parent2_idx = np.random.choice(np.arange(len(population)), 2, replace=False)
                parent1 = population[parent1_idx]
                parent2 = population[parent2_idx]

                # Crossover
                rules1 = parent1['rules']
                rules2 = parent2['rules']
                child = rules_crossover(rules1, rules2)

                # Mutate
                child = rules_mutate(child, n_actions=n_actions)

                # Add to new candidates list if non-trivial and non-duplicate behavior
                if len(child) > 0:
                    behavior = collect_behavior(child)
                    if behavior not in behavior_set:
                        new_candidates.append({'rules': child, 'id': curr_id, 'behavior': behavior})
                        behavior_set[behavior] = curr_id
                        curr_id += 1
                    else:
                        prev_id = behavior_set[behavior]
                        if np.random.random() < 0.5:
                            for i in range(len(population)):
                                if population[i]['id'] == prev_id:
                                    population[i]['rules'] = child

            # Evaluate new individuals
            for candidate in new_candidates:
                utility, cost = evaluate_candidate(candidate['rules'])
                candidate['metrics'] = {'utility': utility,
                                        'cost': cost}

            # Refine population
            population = population + new_candidates
            random.shuffle(population)
            population = selector.sort_individuals(population)
            for indy in population[pop_size:]:
                del behavior_set[indy['behavior']]
            population = population[:pop_size]

            # Add back random or expert solutions
            for candidate in initial_individuals:
                utility, cost = evaluate_candidate(candidate)
                indy = {'rules': candidate,
                        'metrics': {'utility': utility,
                                    'cost': cost},
                        'id': curr_id
                       }
                behavior = collect_behavior(candidate)
                if behavior not in behavior_set:
                    behavior_set[behavior] = curr_id
                    indy['behavior'] = behavior
                    population.append(indy)
                    curr_id += 1

