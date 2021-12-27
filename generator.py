from parser import ChordParser
from midiutil.MidiFile import MIDIFile
from io import BytesIO


class Generator:

    def __init__(self, chords_str=None, size=1/4):
        self.chords = list()
        if chords_str:
            self.set_chords(chords_str)
        self.tempo = 120
        self.size = size

    def set_tempo(self, tempo):
        self.tempo = int(tempo)

    def set_size(self, size):
        self.size = float(size)

    def set_chords(self, chords_str):
        chords_list = chords_str.split(' ')
        for chord_name in chords_list:
            if not chord_name:
                continue
            try:
                chord = ChordParser.chord(chord_name)
            except TypeError:
                print('No chord for "{}"'.format(chord_name))
            else:
                self.chords.append(chord)

    def parse_melody(self, melody_str):
        melody = dict()
        prev_note = 0
        for i, char in enumerate(melody_str.replace(' ', '')):
            if char in ('_', '-'):
                melody[prev_note][1] += 1
            elif char in ('.',):
                pass
            else:
                chord = self.chords[int(char) - 1]
                notes = chord.notes.values()
                melody[i] = [notes, 1]
                prev_note = i
        return melody

    def build_midi(self, melody):
        mf = MIDIFile(1)
        track = 0
        channel = 0
        velocity = 70

        mf.addTempo(0, 0, self.tempo)
        for start_beat, beat_data in melody.items():
            duration = beat_data[1]
            for inc, note in enumerate(beat_data[0]):
                pitch = note.midi_key
                time = start_beat
                duration = duration
                mf.addNote(track, channel, pitch, time * self.size, duration * self.size, velocity)
        midi = BytesIO()
        mf.writeFile(midi)
        midi.seek(0)
        return midi

    def midi(self, melody_str):
        melody = self.parse_melody(melody_str)
        midi_io = self.build_midi(melody)
        return midi_io


if __name__ == '__main__':
    chords_str = 'Em C G D Em7'
    gen = Generator(chords_str)
    gen.set_tempo(120)
    gen.set_size(1/2)
    melody_str = '1111 2__3 3__3_4 4_4_5'
    melody = gen.parse_melody(melody_str)
    midi_io = gen.build_midi(melody)
    print('saving..')
    with open('midige2n.mid', 'wb') as f:
        f.write(midi_io.read())
    midi_io.close()
    print('ok')
