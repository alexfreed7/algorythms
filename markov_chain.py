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
        (0, 0): 10,
        (0, 1): .9,
        (1, 0): .95,
        (1, 1): 10},
    ("I", "III"): {
        (0, 0): 10,
        (0, 1): .9,
        (1, 0): 10,
        (1, 1): 10},
    ("I", "IV"): {
        (0, 0): 10,
        (0, 1): .75,
        (1, 0): .75,
        (1, 1): 10},
    ("I", "V"): {
        (0, 0): 10,
        (0, 1): .85,
        (1, 0): .7,
        (1, 1): 10},
    ("I", "V7"): {
        (0, 0): 10,
        (0, 1): .95,
        (1, 0): .7,
        (1, 1): 10},
    ("I", "VI"): {
        (0, 0): 10,
        (0, 1): .8,
        (1, 0): .8,
        (1, 1): 10},
    ("I", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): 10,
        (1, 0): .85,
        (1, 1): 10},
    ("II", "IV"): {
        (0, 0): 10,
        (0, 1): .7,
        (1, 0): .9,
        (1, 1): 10},
    ("II", "V"): {
        (0, 0): 10,
        (0, 1): .5,
        (1, 0): .9,
        (1, 1): 10},
    ("II", "V7"): {
        (0, 0): 10,
        (0, 1): .95,
        (1, 0): .9,
        (1, 1): 10},
    ("II", "VI"): {
        (0, 0): 10,
        (0, 1): .95,
        (1, 0): .6,
        (1, 1): 10},
    ("II", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): .95,
        (1, 0): .9,
        (1, 1): 10},
    ("III", "IV"): {
        (0, 0): 10,
        (0, 1): .75,
        (1, 0): 10,
        (1, 1): 10},
    ("III", "V"): {
        (0, 0): 10,
        (0, 1): .75,
        (1, 0): .95,
        (1, 1): 10},
    ("III", "V7"): {
        (0, 0): 10,
        (0, 1): .8,
        (1, 0): .9,
        (1, 1): 10},
    ("III", "VI"): {
        (0, 0): 10,
        (0, 1): .85,
        (1, 0): .9,
        (1, 1): 10},
    ("IV", "V"): {
        (0, 0): 10,
        (0, 1): .7,
        (1, 0): .9,
        (1, 1): 10},
    ("IV", "V7"): {
        (0, 0): 10,
        (0, 1): .95,
        (1, 0):.9,
        (1, 1): 10},
    ("IV", "VI"): {
        (0, 0): 10,
        (0, 1): .9,
        (1, 0): .8,
        (1, 1): 10},
    ("V", "V7"): {
        (0, 0): 10,
        (0, 1): 0.9,
        (1, 0): 10,
        (1, 1): 10},
    ("V", "VI"): {
        (0, 0): 10,
        (0, 1): .95,
        (1, 0): .9,
        (1, 1): 10},
    ("V7", "VI"): {
        (0, 0): 10,
        (0, 1): 10,
        (1, 0): 1,
        (1, 1): 10},
    ("V7", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): 0.9,
        (1, 0): .95,
        (1, 1): 10},
    ("VI", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): 1,
        (1, 0): 10,
        (1, 1): 10},
}


def find_next_state(samples):
    '''
    Find lowest energy state with a single note
    '''

    for sample in samples:
        for k,v in sample.items():
            if v == 0:
                return k


def generate_progression_sequence(potentials, start, length):
    '''
    Generate a sequence of notes

    potentials: dict of potential values for each edge state
    start: the starting note
    length: length of sequence
    '''
    network = dnx.markov_network(potentials)
    sampler = dimod.RandomSampler()
    sequence = [start]

    current = start
    for i in range(length):
        samples = dnx.sample_markov_network(
            network,
            sampler,
            fixed_variables={current: 1}
            )
        current = find_next_state(samples)
        sequence.append(current)

    return sequence

track = generate_progression_sequence(potentials, "VIIdim7", 30)

print("TRACK: ", track)

def play_track(track, channel=8, velocity=100):
    song = Track()
    for progression in track:
        p = progressions.to_chords(progression, "C")
        #print('progression: ', p)
        chord = NoteContainer()
        chord.add_notes(progressions.to_chords(progression, "C")[0])
        #print('chord: ', chord)
        song.add_notes(chord)
    midi_file_out.write_Track(file, song, bpm=120)

play_track(track)
