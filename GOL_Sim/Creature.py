from GOL_Sim.DNA import DNA


class Creature(object):

    def __init__(self, width, height):
        self.dna = DNA(width * height)
        self.width = width
        self.height = height
        self.score = 0

    def set_dna(self, new_dna):
        del self.dna
        self.dna = new_dna

    def gen_coords_from_dna(self):
        alive_cells = []

        for index in range(len(self.dna)):
            if self.dna[index]:
                alive_cells.append([index % self.width,
                                    int(index / self.height)])

        return alive_cells

    def mate(self, other, mutation_chance):
        if self.width != other.width or self.height != other.height:
            print('tried mating the following creature sizes\'s:')
            print(str(self.width) + ' by ' + str(self.height))
            print(str(other.width) + ' by ' + str(other.height))
            return

        new_dna = self.dna.splice(other.dna)
        new_dna.mutate(mutation_chance)

        child = Creature(self.width, self.height)
        child.set_dna(new_dna)

        return child
