import dimod
import dwave_networkx as dnx

potentials = {
    ('a', 'b'): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ('b', 'c'): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ('c', 'd'): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ('d', 'a'): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
}

def find_next_state(samples):
    '''
    Find lowest energy state with a single note
    '''
    for sample in samples:
        total_sum = 0
        keys = []
        for k,v in sample.items():
            total_sum += v
            if v == 1:
                keys.append(k)

        if total_sum == 1:
            return keys[0]

def generate_note_sequence(potentials, start, length):
    '''
    Generate a sequence of notes

    potentials: dict of potential values for each edge state
    start: the starting note
    length: length of sequence
    '''
    network = dnx.markov_network(potentials)
    sampler = dimod.RandomSampler() #dimod.ExactSolver()

    sequence = [start]

    current = start
    for i in range(length):
        samples = dnx.sample_markov_network(network, sampler, fixed_variables={current: 0})
        current = find_next_state(samples)
        sequence.append(current)

    return sequence

print(generate_note_sequence(potentials, 'b', 10))
