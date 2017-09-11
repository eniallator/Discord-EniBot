from random import random
from GOL_Sim.Creature import Creature


class Population(object):

    def __init__(self, size, width, height, mutation_chance, creatures_to_remain):
        self._population = []
        self._width = width
        self._height = height
        self._mutation_chance = mutation_chance
        self._creatures_to_remain = creatures_to_remain

        for _ in range(size):
            self.add_creature(Creature(width, height))

    def __iter__(self):
        return iter(self._population)

    def __len__(self):
        return len(self._population)

    def __setitem__(self, index, val):
        self._population[index] = val

    def __getitem__(self, index):
        return self._population[index]

    def add_creature(self, creature):
        self._population.append(creature)

    def _make_choice(self, scores, index, choice):
        mod_scores = lambda index: index % len(scores)
        accumulator = scores[mod_scores(index)]

        while accumulator < choice:
            index = mod_scores(index + 1)
            accumulator += scores[index]

        return mod_scores(index)

    def _choose_mates(self, population):
        scores = [creature.score for creature in population]
        total = sum(scores)
        chosen_creatures = []

        first_index = self._make_choice(scores, 0, random() * total)
        chosen_creatures.append(population[first_index])
        total -= scores[first_index]

        second_index = self._make_choice(scores, first_index + 1, random() * total)
        chosen_creatures.append(population[second_index])

        return chosen_creatures

    def _add_creatures_to_remain(self, new_population):
        remain_creatures = sorted(self, key=lambda creature: creature.score, reverse=True)[:self._creatures_to_remain]

        for creature_to_add in remain_creatures:
            new_population.add_creature(creature_to_add)

    def evolve(self):
        new_population = Population(0, self._width, self._height, self._mutation_chance, self._creatures_to_remain)
        self._add_creatures_to_remain(new_population)

        for _ in range(len(self) - self._creatures_to_remain):
            mates = self._choose_mates(new_population)
            child = mates[0].mate(mates[1], self._mutation_chance)
            new_population.add_creature(child)

        return new_population
