import dimod
import dwave_networkx as dnx
import numpy as np

import mingus.core.progressions as progressions
from mingus.containers import NoteContainer
from mingus.midi import midi_file_out
from mingus.containers import Track

file = "test.midi"

potentials = {
    ("I", "II"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0},
    ("I", "III"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("I", "IV"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("I", "V"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    # ("I", "V7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    ("I", "VI"): {
        (0, 0): -1,
        (0, 1): 10,
        (1, 0): 4,
        (1, 1): 2,
    },
    # ("I", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("II", "IV"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("II", "V"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("II", "V7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("II", "VI"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("II", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("III", "IV"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("III", "V"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("III", "V7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("III", "VI"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("III", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("IV", "V"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("IV", "V7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("IV", "VI"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("IV", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("V", "V7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("V", "VI"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("V", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("V7", "VI"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("V7", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # },
    # ("VI", "VIIdim7"): {
    #     (0, 0): 0,
    #     (0, 1): 1,
    #     (1, 0): 1,
    #     (1, 1): 0,
    # }
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

def generate_progression_sequence(potentials, start, length):
    '''
    Generate a sequence of notes

    potentials: dict of potential values for each edge state
    start: the starting note
    length: length of sequence
    '''
    network = dnx.markov_network(potentials)
    sampler = dimod.RandomSampler() #dimod.ExactSolver()

    print(network)

    sequence = [start]

    current = start
    for i in range(length):
        samples = dnx.sample_markov_network(network, sampler, fixed_variables={current: 0})
        current = find_next_state(samples)
        sequence.append(current)

    return sequence

track = generate_progression_sequence(potentials, "II", 10)

print("TRACK: ", track)

def play_track(track, channel=8, velocity=100):
    song = Track()
    for progression in track:
        p = progressions.to_chords(progression, "C")
        print('progression: ', p)
        chord = NoteContainer()
        chord.add_notes(progressions.to_chords(progression, "C")[0])
        print('chord: ', chord)
        song.add_notes(chord)
    midi_file_out.write_Track(file, song, bpm=120)

play_track(track)
