import re
from chord import ChordBuilder
from note import Note


chords = """
A Am A+ Adim A7 A7+5 Am7 Am7+ Am7-5 Adim7 A6 Am6 A7-5 A6/9 A9 A7-9 Amaj9 A11 Am11 A13 Amaj13 Asus Am6/9 A5 A7+9 A7+11 A7-5(+9) A7sus4 A9-5 A9+11 A9sus4 A13-9 A13sus4 Aadd9 Am-6 Am9 Am9-5 Am9+7 Am13 Am(add9) Amaj7 Amaj7-5 Amaj7+11 Asus2 A+7+9 A+7-9 A+9
Db Dbm Db+ Dbdim Db7 Db7+5 Dbm7 Dbm7+ Dbm7-5 Dbdim7 Db6 Dbm6 Db7-5 Db6/9 Db9 Db7-9 Dbmaj9 Db11 Dbm11 Db13 Dbmaj13 Dbm6/9 Db5 Db7+9 Db7+11 Db7-5(+9) Db7sus4 Db9-5 Db9+11 Db9sus4 Db13-9 Db13sus4 Dbadd9 Dbm-6 Dbm9 Dbm9-5 Dbm9+7 Dbm13 Dbm(add9) Dbmaj7 Dbmaj7-5 Dbmaj7+11 Dbsus2 Db+7+9 Db+7-9 Db+9 Dbsus Db
C#-maj7, C#m#7, C#m+7, C#m/maj7, C#m7+, C#min/maj7, C#mmaj7, Db-maj7, Dbm#7, Dbm+7, Dbm/maj7, Dbm7+, Dbmin/maj7, Dbmmaj7 CM7, CΔ, CΔ7
Am/G# Amaj Amin AM7 AM Amaug Aaug G/H/A#
""".split(' ')


class ChordParser:

    BASE_PATTERS = re.compile(r"^([A-H][b#]?)(sus(?!\d)|m(?!aj)|maj(?!\d)||[+-])(dim|aug|)")
    ALTERATIONS_PATTERN = re.compile(r"((?:[#b+-/]|add|sus|no|omit|maj|))(\d+)")
    BASS_PATTERN = re.compile(r"/([A-H][b#+-]?)")

    @classmethod
    def parse(cls, chord):
        print(chord)
        to_replace = {
            'H': 'B',
            'Ø': 'm7b5',
            '°7': 'dim7',
            '°': 'dim7',
            'o7': 'dim7',
            'Δ7': 'maj7',
            'Δ': 'maj7',
            'M': 'maj',
        }
        for pattern, replace in to_replace.items():
            if pattern in chord:
                prev = chord
                chord = chord.replace(pattern, replace)
                print('Pattern "{}": Replaced {} to {}'.format(pattern, prev, chord))
        is_bms = chord.endswith('+')
        if is_bms:
            chord = chord[:-1]

        main = re.search(cls.BASE_PATTERS, chord)
        chord = chord[len(main[1]):]
        alterations = re.findall(cls.ALTERATIONS_PATTERN, chord)
        add_bass = re.findall(cls.BASS_PATTERN, chord)

        return dict(
            tonic=main[1],
            character=main[2],
            modifier=main[3],
            alterations=alterations,
            bass_to_add=add_bass,
            is_bms=is_bms
        )

    @staticmethod
    def build(data):
        """
        1. get steps amount, set steps in major
        2. modify tonic if minor
        3. alternate chord (sus, add, remove, reduce, enlarge)
        4. modify all if dim
        5. modify last(?) if aug :todo
        6.(?) find lowest, then add bass note :todo
        """
        # set tonic
        tonic = data['tonic']
        chord = ChordBuilder(Note(tonic))
        # set character
        character = data['character']
        major = 'maj', ''
        minor = 'm', 'min'
        sus4 = 'sus',
        if character in major:
            chord.maj()
            chord.tonic.set_gamma(Note.MAJOR)
        elif character in minor:
            chord.min()
            chord.tonic.set_gamma(Note.MINOR)
        elif character in sus4:
            chord.maj()
            chord.sus(4)
        # add additional steps
        major = 'maj',
        minor = '',
        add = '/', 'add'
        for cmd, attr in data['alterations']:
            step = int(attr)
            if cmd in major:
                chord.expand_to(step, maj=True)
            elif cmd in minor:
                chord.expand_to(step)
                # Special A5
                if step == 5:
                    chord.omit(3)
            elif cmd in add:
                chord.add_natural_major_step(step)

        # modify steps
        reduce = 'b', '-'
        enlarge = '#', '+'
        sus = 'sus',
        for cmd, attr in data['alterations']:
            step = int(attr)
            if cmd in reduce:
                chord.expand_to(step)
                chord.reduce(step)
            elif cmd in enlarge:
                chord.expand_to(step)
                chord.enlarge(step)
            elif cmd in sus:
                chord.sus(step)
        # omit notes
        omit = 'no', 'omit'
        for cmd, attr in data['alterations']:
            step = int(attr)
            if cmd in omit:
                chord.omit(step)
        # modify result
        dim = 'dim',
        aug = 'aug',
        cmd = data['modifier']
        if cmd in dim:
            chord.dim()
        elif cmd in aug or data['is_bms']:
            chord.aug()
        # add bass
        for note in data['bass_to_add']:
            chord.add_bass(note)
        return chord

    @classmethod
    def chord(cls, chord_name):
        chord_data = cls.parse(chord_name)
        chord_obj = cls.build(chord_data)
        print('→', chord_obj)
        return chord_obj


if __name__ == '__main__':
    accords = dict()
    for chord in 'Am/G,  Bbmaj13/11 ,Cm7b5 ,C°7 ,CØ, C-7 (b5)'.split(','): # + ['Am9+7', 'A5', 'Am', 'Am-6', 'Am6/9', 'A5', 'A7-5(+9)', 'Asus2', 'A13sus4', 'Aadd9', 'Am-6', 'Amaj13', 'Amaj7', 'A13', 'A11', 'A9', 'A7', 'A7+']:
        chord = chord.strip()
        parsed = ChordParser.parse(chord)
        print(parsed)
        accords[chord] = ChordParser.build(parsed)

    for key, val in accords.items():
        print('"{}": {}'.format(key, val))

