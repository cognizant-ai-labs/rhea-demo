"""
Evaluators for the illustrative domain
"""

from copy import deepcopy

UTILITY_MAP = {
    (0, (0, 1)): 1,
    (0, (0, 1, 2, 3, 4)): 2,
    (0, (0, 1, 2, 3, 4, 5)): 3,
    (1, (0, 1, 2, 3, 4, 5)): 4,
    (1, (0, 1, 2, 3, 5)): 5,
    (1, (2, 3, 4)): 1,
    (0, (6, 7, 8, 9)): 1,
    (1, (6, 7, 8, 9)): 1,
    (2, (6, 7, 8, 9)): 1,
    (3, (6, 7, 8, 9)): 1,
    (4, (6, 7, 8, 9)): 1,
    (5, (6, 7, 8, 9)): 1,
    (6, (6, 7, 8, 9)): 1,
}

KNOWLEDGE_MAP = {
    0: {(): 0,
        (6, 7, 8, 9): 1,
        (0, 1): 1,
        (0, 1, 2, 3, 4): 2,
        (0, 1, 2, 3, 4, 5): 3},
    1: {(): 0,
        (6, 7, 8, 9): 1,
        (2, 3, 4): 1,
        (0, 1, 2, 3, 4, 5): 4,
        (0, 1, 2, 3, 5): 5},
    2: {(): 0,
        (6, 7, 8, 9): 1},
    3: {(): 0,
        (6, 7, 8, 9): 1},
    4: {(): 0,
        (6, 7, 8, 9): 1},
    5: {(): 0,
        (6, 7, 8, 9): 1},
    6: {(): 0,
        (6, 7, 8, 9): 1},
}

N_CONTEXTS = 7

def evaluate_candidate(candidate):
    action_map = collect_action_map(N_CONTEXTS, candidate)
    return evaluate_action_map(UTILITY_MAP, action_map)

def evaluate_action_map(utility_map, action_map):
    total_utility = 0
    total_cost = 0
    for c in action_map:
        a = action_map[c]
        total_cost += len(a)
        if (c, a) in utility_map:
            utility = utility_map[(c, a)]
            total_utility += utility
    return total_utility, total_cost

def collect_action_map(n_contexts, candidate):
    action_map = {}
    for c in range(n_contexts):
        a = get_action(candidate, c)
        action_map[c] = a
    return action_map

def get_action(rules, c):
    for context_set, action_set in rules:
        if c in context_set:
            return tuple(sorted(action_set))
    return tuple()

def collect_behavior(candidate, n_contexts=N_CONTEXTS):
    action_map = collect_action_map(n_contexts, candidate)
    return action_map_to_tuple(action_map, n_contexts)

def action_map_to_tuple(action_map, n_contexts=N_CONTEXTS):
    temp_list = []
    for c in range(n_contexts):
        temp_list.append((c, action_map[c]))
    return tuple(temp_list)

def dominates(u1, c1, u2, c2):
    if (u1 > u2) and (c1 <= c2):
        return True
    elif (u1 >= u2) and (c1 < c2):
        return True
    else:
        return False

def update_front(new_u, new_c, front):

    # Add to empty front
    if len(front) == 0:
        return [(new_u, new_c)]

    # Assume front is list of tuples (u, c) sorted in decreasing order of utility
    for (u, c) in front:
        if dominates(u, c, new_u, new_c):
            return front # Front is unchanged

    # Do not include duplicates
    for (u, c) in front:
        if (u == new_u) and (c == new_c):
            return front

    # If we got here, we add the new point
    new_front = []
    added = False
    prev_u, prev_c = float('inf'), -float('inf')
    for (u, c) in front:
        if (new_u > u) and not added:
            new_front.append((new_u, new_c))
            added = True
        if not dominates(new_u, new_c, u, c):
            new_front.append((u, c))
    return new_front

def compute_oracle_front(knowledge_map=KNOWLEDGE_MAP,
                         context_to_action={},
                         front=[],
                         front_policies={},
                         curr_context=0,
                         n_contexts=N_CONTEXTS):

    useful_actions = knowledge_map[curr_context]
    for action in useful_actions:
        context_to_action[curr_context] = action
        if curr_context == n_contexts - 1:

            # Evaluate solution
            utility = 0
            cost = 0
            for c in range(n_contexts):
                utility += knowledge_map[c][context_to_action[c]]
                cost += len(context_to_action[c])

            # Add to front
            prev_front = deepcopy(front)
            front = update_front(utility, cost, front)
            if front != prev_front:
                front_policies[(utility, cost)] = deepcopy(context_to_action)
        else:

            front, front_policies = compute_oracle_front(knowledge_map,
                                                         context_to_action,
                                                         front,
                                                         front_policies,
                                                         curr_context+1,
                                                         n_contexts)

    return front, front_policies

