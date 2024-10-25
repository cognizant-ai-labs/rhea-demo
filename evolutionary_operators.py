"""
Definitions of evolutionary operators for rule-based models.
"""

import numpy as np


def mix_sets(set1, set2):

    mixed_set = set()
    for element in set1:
        if element in set2:
            mixed_set.add(element)
        elif np.random.random() < 0.5:
            mixed_set.add(element)

    for element in set2:
        if element in set1:
            mixed_set.add(element)
        elif np.random.random() < 0.5:
            mixed_set.add(element)

    return tuple(sorted(mixed_set))


def mix_rules(rule1, rule2):
    rule1_cs, rule1_as = rule1
    rule2_cs, rule2_as = rule2

    mixed_cs = mix_sets(rule1_cs, rule2_cs)
    mixed_as = mix_sets(rule1_as, rule2_as)

    mixed_rule = (mixed_cs, mixed_as)

    return mixed_rule


def rules_crossover(parent1, parent2):

    # Probabilities set to have neutral bloat

    child_rules = []
    for rule in parent1:
        random_float = np.random.random()
        if random_float < 1 / 4.: # Keep
            child_rules.append(rule)
        elif random_float < 1 / 2.: # Mix
            n_parent2_rules = len(parent2)
            rule_to_mix_with_idx = np.random.randint(n_parent2_rules)
            rule_to_mix_with = parent2[rule_to_mix_with_idx]
            mixed_rule = mix_rules(rule, rule_to_mix_with)
            child_rules.append(mixed_rule)
        else: # Discard
            pass

    for rule in parent2:
        random_float = np.random.random()
        if random_float < 1 / 4.: # Keep
            child_rules.append(rule)
        elif random_float < 1 / 2.: # Mix
            n_parent1_rules = len(parent1)
            rule_to_mix_with_idx = np.random.randint(n_parent1_rules)
            rule_to_mix_with = parent1[rule_to_mix_with_idx]
            mixed_rule = mix_rules(rule, rule_to_mix_with)
            child_rules.append(mixed_rule)
        else: # Discard
            pass

    return child_rules


def set_mutate(s, p_flip, n_elts):

    for elt in range(n_elts):
        if np.random.random() < p_flip:
            if elt in s:
                s.remove(elt)
            else:
                s.add(elt)
    return s


def rules_mutate(rules, n_contexts=7, n_actions=10):

    # Probabilities set based on classical default rate 1/n

    max_rule_len = n_contexts + n_actions
    effective_n_rules = max(1, len(rules))
    p_flip = 1. / (effective_n_rules * max_rule_len)

    child_rules = []
    for rule in rules:
        rule_cs, rule_as = rule
        c_set = set(rule_cs)
        a_set = set(rule_as)
        child_c_set = set_mutate(c_set, p_flip, n_contexts)
        child_a_set = set_mutate(a_set, p_flip, n_actions)
        child_cs = tuple(sorted(child_c_set))
        child_as = tuple(sorted(child_a_set))
        child_rules.append((child_cs, child_as))

    return child_rules


def random_candidate(n_contexts=7, n_actions=10):
    c_list = []
    for c in range(n_contexts):
        if np.random.random() < 0.5:
            c_list.append(c)
    a_list = []
    for a in range(n_actions):
        if np.random.random() < 0.5:
            a_list.append(a)
    return [(tuple(c_list), tuple(a_list))]
