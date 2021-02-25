#!/usr/bin/env python
from dimod import ExactSolver
import dwave_networkx as dnx
from dwave.system import LeapHybridSampler

import numpy as np
import random

import mingus.core.progressions as progressions
from mingus.containers import NoteContainer, Track, Note, Bar, Composition
import mingus.core.notes as mingus_notes
from mingus.midi import midi_file_out

import matplotlib.pyplot as plt
import networkx as nx

from pyfiglet import Figlet
from PyInquirer import style_from_dict, Token, prompt

chord_edges = [('I', 'II'), ('I', 'III'), ('I', 'IV'), ('I', 'V'), ('I', 'V'), ('I', 'VI'), ('I', 'VIIdim'), ('II', 'IV'), ('II', 'V'), ('II', 'V'), ('II', 'VI'), ('II', 'VIIdim'), ('III', 'IV'), ('III', 'V'), ('III', 'V'), ('III', 'VI'), ('IV', 'V'), ('IV', 'V'), ('IV', 'VI'), ('V', 'VI'), ('V', 'VI'), ('V', 'VIIdim'), ('VI', 'VIIdim')]
chord_edges_minor = [('i', 'iidim'), ('i', 'III'), ('i', 'iv'), ('i', 'v'), ('i', 'VI'), ('i', 'VII'), ('iidim', 'iv'), ('iidim', 'v'), ('ii', 'v'), ('ii', 'VI'), ('ii', 'VII'), ('III', 'iv'), ('III', 'v'), ('III', 'VI'), ('iv', 'v'), ('iv', 'VI'), ('v', 'VI'), ('v', 'VII'), ('VI', 'VII')]
## [(pair[0].lower(),pair[1].lower()) for pair in chord_edges]

note_edges = [('0','2'), ('0', '4'), ('0', '7'), ('0', '9'), ('2', '7'), ('2', '9'),  ('4', '7'),  ('4', '9'),  ('7', '9')]
note_edges_minor = [ ('0', '3'), ('0', '5'), ('0', '7'), ('0', '7'),  ('0', '10'),   ('3', '5'), ('3', '7'), ('3', '7'),  ('5', '7'), ('5', '7'),('7', '10')]

def cli():
    style = style_from_dict({
        Token.QuestionMark: '#E91E63 bold',
        Token.Selected: '#673AB7 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#2196f3 bold',
        Token.Question: '',
    })


    f = Figlet(font='slant')
    print(f.renderText('Algorhythms'))

    print('Generate music with a quantum computer!\n')
    print('Your song will be coming straight from D-Wave quantum processing units!\n')

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
        },
        {
        'type': 'rawlist',
        'name': 'sampler',
        'message': 'Which solver do you want to use?',
        'choices': ['Local', 'Leap']
        },
        {
        'type': 'rawlist',
        'name': 'scale',
        'message': 'Happy or Sad?',
        'choices': ['Happy', 'Sad']
    },
    ]

    answers = prompt(questions, style=style)

    title = str(answers['title'])
    file = title + ".midi"
    duration = int(answers['duration'])

    scales = {
        'Happy':chord_edges,
        'Sad': chord_edges_minor
    }
    scale = scales[answers['scale']]

    melodys = {
        'Happy':note_edges,
        'Sad':note_edges_minor
    }
    melody = melodys[answers['scale']]

    samplers = {
        'Local': ExactSolver,
        'Leap': LeapHybridSampler
    }
    sampler = samplers[answers['sampler']]

    tempo = {
        'Happy': 100,
        'Sad': 60
    }

    bpm = tempo[answers['scale']]
    number_notes = int(bpm * 1/60 * duration)    # beats per second

    chord_potentials = generate_potentials(scale)
    melody_potentials = generate_potentials(melody)

    print('Sending to sampler...')
    chord_sequence = generate_note_sequence(chord_potentials, number_notes, sampler)
    melody_sequence = generate_note_sequence(melody_potentials, number_notes * 2, sampler)

    save_track(chord_sequence, melody_sequence, file, bpm, title)

    print('Done! Your quantum song can be found in "' + file + '"\n')
    print('You can open it in MuseScore to listen to it and see the score!')

def generate_potentials(graph_edges):
    return {
        edge: {
            (0, 0): 10,
            (0, 1): random_number(),
            (1, 0): random_number(),
            (1, 1): 10
        } for edge in graph_edges
    }

def find_next_state(samples):
    '''
    Find lowest energy state with a single note
    '''
    for sample in samples:
        low_energy_states = [k for k,v in sample.items() if v == 1]
        return random.choice(low_energy_states)


def generate_note_sequence(potentials, length, solver):
    '''
    Generate a sequence of notes

    potentials: dict of potential values for each edge state
    start: the starting note
    length: length of sequence
    '''
    edges = list(potentials.keys())
    vertices = list(set([vertex for edge in edges for vertex in edge]))

    start = random.choice(vertices)

    network = dnx.markov_network(potentials)
    sampler = solver()
    sequence = [start]

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
        # progress = int(i/length * 100)
        # if progress != 0:
        #     print(str(progress) + "%")
        current = find_next_state(samples)
        sequence.append(current)
    #print('100%')

    return sequence


def save_track(chords, melody, file, bpm, title):
    chords += "V"
    chords += "I"
    left_hand = Track()
    right_hand = Track()

    melody = [mingus_notes.int_to_note(int(n)) for n in melody]

    print('melody: ', melody)
    print('chords: ', chords)


    for i in range(len(chords)-2):
        left_bar = Bar()
        right_bar = Bar()
        bar_chords = chords[i:i+2]  # 2 chords per bar
        bar_notes = melody[i:i+4]

        # add 4 notes to bar
        for note in bar_notes:
            n = NoteContainer()
            n.add_note(note, dynamics={'velocity': np.random.randint(127)})
            right_bar.place_notes(n, 4)

        # add 2 chords to bar
        for progression in bar_chords:
            chord = NoteContainer()
            p = progressions.to_chords(progression, "C")[0] # ex:['C', 'E', 'G']
            for note in p:
                note += '-3'
                chord.add_note(note)
            left_bar.place_notes(chord, 2)
        left_hand.add_bar(left_bar)
        right_hand.add_bar(right_bar)

    c = Composition()
    c.set_author('P. Dirac')
    c.set_title(title)
    c.add_track(right_hand)
    c.add_track(left_hand)

    midi_file_out.write_Composition(file, c, bpm)

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
