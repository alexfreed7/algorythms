import dimod
import dwave_networkx as dnx
import numpy as np
import mingus 
import mingus.core.progressions as progressions
from mingus.containers import NoteContainer
from mingus.midi import fluidsynth

SF2 = ""#"Nice-Steinway-v3.8.sf2"

potentials = {
    ("I", "II"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
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
    ("I", "V7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("I", "VI"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("I", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },


    ("II", "IV"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("II", "V"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("II", "V7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("II", "VI"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("II", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },



    ("III", "IV"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("III", "V"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("III", "V7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("III", "VI"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("III", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("IV", "V"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("IV", "V7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("IV", "VI"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("IV", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },

    ("V", "V7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("V", "VI"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },("V", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },

    ("V7", "VI"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
    ("V7", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },

    ("VI", "VIIdim7"): {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    },
}

progression = ["I", "IV", "V7"]
c = progressions.to_chords(progression, "C")

if not fluidsynth.init(SF2):
    print("Couldn't load soundfont", SF2)


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

    sequence = [start]

    current = start
    for i in range(length):
        samples = dnx.sample_markov_network(network, sampler, fixed_variables={current: 0})
        current = find_next_state(samples)
        sequence.append(current)

    return sequence

track = generate_progression_sequence(potentials, "I", 10)

print("TRACK: ", track)

def play_track(track, channel=8, velocity=50):
    for progression in track:
        chord = NoteContainer(progressions.to_chords(progression, "C"))
        fluidsynth.play_NoteContainer(chord, channel, velocity)
