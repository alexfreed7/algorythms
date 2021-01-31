import dimod
import dwave_networkx as dnx
import numpy as np

import mingus.core.progressions as progressions
from mingus.containers import NoteContainer
from mingus.midi import midi_file_out
from mingus.containers import Track

import matplotlib.pyplot as plt
import networkx as nx

file = "test.midi"

potentials = {
    ("I", "II"): {
        (0, 0): 10,
        (0, 1): -6,
        (1, 0): -7.5,
        (1, 1): 10},
    ("I", "III"): {
        (0, 0): 10,
        (0, 1): -5,
        (1, 0): 0,
        (1, 1): 10},
    ("I", "IV"): {
        (0, 0): 10,
        (0, 1): -7,
        (1, 0): -7,
        (1, 1): 10},
    ("I", "V"): {
        (0, 0): 10,
        (0, 1): -5.5,
        (1, 0): -5,
        (1, 1): 10},
    ("I", "V7"): {
        (0, 0): 10,
        (0, 1): -7.5,
        (1, 0): -6,
        (1, 1): 10},
    ("I", "VI"): {
        (0, 0): 10,
        (0, 1): -5,
        (1, 0): -5,
        (1, 1): 10},
    ("I", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): 10,
        (1, 0): -5.5,
        (1, 1): 10},
    ("II", "IV"): {
        (0, 0): 10,
        (0, 1): -7,
        (1, 0): -7.5,
        (1, 1): 10},
    ("II", "V"): {
        (0, 0): 10,
        (0, 1): 0,
        (1, 0): -5.5,
        (1, 1): 10},
    ("II", "V7"): {
        (0, 0): 10,
        (0, 1): -7.5,
        (1, 0): -7,
        (1, 1): 10},
    ("II", "VI"): {
        (0, 0): 10,
        (0, 1): -7.5,
        (1, 0): -2,
        (1, 1): 10},
    ("II", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): -7.5,
        (1, 0): -7,
        (1, 1): 10},
    ("III", "IV"): {
        (0, 0): 10,
        (0, 1): -3,
        (1, 0): 0,
        (1, 1): 10},
    ("III", "V"): {
        (0, 0): 10,
        (0, 1): -3,
        (1, 0): -7.5,
        (1, 1): 10},
    ("III", "V7"): {
        (0, 0): 10,
        (0, 1): -6,
        (1, 0): -5.5,
        (1, 1): 10},
    ("III", "VI"): {
        (0, 0): 10,
        (0, 1): -7,
        (1, 0): -5.5,
        (1, 1): 10},
    ("IV", "V"): {
        (0, 0): 10,
        (0, 1): -4,
        (1, 0): -5.5,
        (1, 1): 10},
    ("IV", "V7"): {
        (0, 0): 10,
        (0, 1): -7.5,
        (1, 0): -7,
        (1, 1): 10},
    ("IV", "VI"): {
        (0, 0): 10,
        (0, 1): -5.5,
        (1, 0): -6,
        (1, 1): 10},
    ("V", "V7"): {
        (0, 0): 10,
        (0, 1): -5.5,
        (1, 0): 0,
        (1, 1): 10},
    ("V", "VI"): {
        (0, 0): 10,
        (0, 1): -7.5,
        (1, 0): -7,
        (1, 1): 10},
    ("V7", "VI"): {
        (0, 0): 10,
        (0, 1): 5,
        (1, 0): 0,
        (1, 1): 10},
    ("V7", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): -5.5,
        (1, 0): -7.5,
        (1, 1): 10},
    ("VI", "VIIdim7"): {
        (0, 0): 10,
        (0, 1): 5,
        (1, 0): 0,
        (1, 1): 10},
}

edges = list(potentials.keys())
vertices = list(set([vertex for edge in edges for vertex in edge]))

def plot_chords(potentials):

    graph = nx.Graph()
    graph.add_nodes_from(vertices)
    graph.add_edges_from(edges)
    nx.draw_circular(graph, with_labels=True)

    plt.show()

plot_chords(potentials)


def find_next_state(samples):
    '''
    Find lowest energy state with a single note
    '''
    for sample in samples:
        for k,v in sample.items():
            if v == 1:
                return k


def generate_progression_sequence(potentials, start, length):
    '''
    Generate a sequence of notes

    potentials: dict of potential values for each edge state
    start: the starting note
    length: length of sequence
    '''
    network = dnx.markov_network(potentials)
    sampler = dimod.RandomSampler()#SimulatedAnnealingSampler()#ExactSolver()#
    sequence = [start]

    current = start
    for i in range(length):

        outgoing_edges = [edge for edge in edges if current in edge]
        #print(outgoing_edges)
        # list of neighbors includes current node
        neighbors = list(set([vertex for edge in outgoing_edges for vertex in edge]))
        #print(neighbors)
        non_neighbors = [vertex for vertex in vertices if vertex not in neighbors]
        fixed_variables = {vertex: 0 for vertex in non_neighbors}
        fixed_variables[current] = 0
        #print(fixed_variables)

        samples = dnx.sample_markov_network(
            network,
            sampler,
            fixed_variables
            )
        print(samples)
        current = find_next_state(samples)
        sequence.append(current)

    return sequence

track = generate_progression_sequence(potentials, "VI", 40)

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
