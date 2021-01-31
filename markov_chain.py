import dimod
import dwave_networkx as dnx
import numpy as np
import random

import mingus.core.progressions as progressions
from mingus.containers import NoteContainer, Track, Note
from mingus.midi import midi_file_out

import matplotlib.pyplot as plt
import networkx as nx

from pyfiglet import Figlet
from PyInquirer import style_from_dict, Token, prompt

graph_edges = [('I', 'II'), ('I', 'III'), ('I', 'IV'), ('I', 'V'), ('I', 'V'), ('I', 'VI'), ('I', 'VIIdim'), ('II', 'IV'), ('II', 'V'), ('II', 'V'), ('II', 'VI'), ('II', 'VIIdim'), ('III', 'IV'), ('III', 'V'), ('III', 'V'), ('III', 'VI'), ('IV', 'V'), ('IV', 'V'), ('IV', 'VI'), ('V', 'VI'), ('V', 'VI'), ('V', 'VIIdim'), ('VI', 'VIIdim')]

def cli():
    style = style_from_dict({
        Token.QuestionMark: '#E91E63 bold',
        Token.Selected: '#673AB7 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#2196f3 bold',
        Token.Question: '',
    })


    f = Figlet(font='slant')
    print(f.renderText('Algorythms'))

    print('Generate music with a quantum computer!\n')
    print('Your song will be coming straight from d-wave quantum processing units!\n')

    questions = [
        {
            'type': 'input',
            'name': 'title',
            'message': 'What should the song be called?',
            'default': 'My first quantum song!'
        },
        {
            'type': 'input',
            'name': 'duration',
            'message': 'Song duration (in seconds)?',
            'default': '30'
        }
    ]

    answers = prompt(questions, style=style)

    file = str(answers['title']) + ".midi"
    duration = int(answers['duration'])

    bpm = 90
    number_notes = int(bpm * 1/60 * duration)    # beats per second

    potentials = {
        edge: {
            (0, 0): 10,
            (0, 1): random_number(),
            (1, 0): random_number(),
            (1, 1): 10
        } for edge in graph_edges
    }

    edges = list(potentials.keys())
    vertices = list(set([vertex for edge in edges for vertex in edge]))

    start = random.choice(vertices)

    track = generate_progression_sequence(potentials, start, number_notes)

    play_track(track, file, bpm)

    print('Done! Your quantum song can be found in "' + file + '"\n')
    print('You can open it in MuseScore to listen to it and see the score!')


def find_next_state(samples):
    '''
    Find lowest energy state with a single note
    '''
    for sample in samples:
        low_energy_states = [k for k,v in sample.items() if v == 1]
        return random.choice(low_energy_states)


def generate_progression_sequence(potentials, start, length):
    '''
    Generate a sequence of notes

    potentials: dict of potential values for each edge state
    start: the starting note
    length: length of sequence
    '''
    network = dnx.markov_network(potentials)
    sampler = dimod.ExactSolver()
    sequence = [start]

    edges = list(potentials.keys())
    vertices = list(set([vertex for edge in edges for vertex in edge]))

    current = start
    for i in range(length):
        outgoing_edges = [edge for edge in edges if current in edge]
        neighbors = list(set([vertex for edge in outgoing_edges for vertex in edge]))
        non_neighbors = [vertex for vertex in vertices if vertex not in neighbors]
        fixed_variables = {vertex: 0 for vertex in non_neighbors}
        fixed_variables[current] = 0

        samples = dnx.sample_markov_network(
            network,
            sampler,
            fixed_variables
            )
        current = find_next_state(samples)
        sequence.append(current)

    return sequence


def play_track(track, file, bpm):
    track += "V"
    track += "I"
    song = Track()
    for progression in track:
        p = progressions.to_chords(progression, "C")
        chord = NoteContainer()
        p = progressions.to_chords(progression, "C")[0]
        for note in p:
            chord.add_note(note, dynamics={'velocity': np.random.randint(127)})
        chord.add_note(note, dynamics={'velocity': np.random.randint(127)})
        song.add_notes(chord)
    midi_file_out.write_Track(file, song, bpm)

def random_number():
    return -1**np.random.randint(10) * np.random.rand() * 10

def plot_chords(potentials):

    graph = nx.Graph()
    graph.add_nodes_from(vertices)
    graph.add_edges_from(edges)
    nx.draw_circular(graph, with_labels=True)

    plt.show()


if __name__ == "__main__":
    cli()
