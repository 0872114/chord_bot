from note import Note
from copy import copy


class Tuning:

    DEFAULT_OCTAVE_ORDER = 2, 1, 1, 1, 0
    DEFAULT_TUNING_NAME = 'EBGDAE'

    def __init__(self, name=DEFAULT_TUNING_NAME, octave_order=DEFAULT_OCTAVE_ORDER):
        self.name = name
        self.octave_order = octave_order
        self.strings = list()
        for string in name:
            if string == '#':
                self.strings[len(self.strings) - 1] += 1
            else:
                self.add_string(string)

    def get_string_octave(self, n):
        if len(self.octave_order) <= n:
            octave = self.octave_order[len(self.octave_order) - 1]
        else:
            octave = self.octave_order[n]
        return octave

    def add_string(self, key, octave=None):
        if octave is None:
            octave = self.get_string_octave(len(self.strings))
        self.strings.append(Note(key, octave=octave))

    def __str__(self):
        return str(self.strings)

    def __iter__(self):
        for n in self.strings:
            yield n

    def __getitem__(self, item):
        assert isinstance(item, int)
        if item >= len(self.strings):
            return IndexError('No string with order number {} in tuning "{}"'.format(item, self.name))

        return self.strings[item]


class Fretboard:

    def __init__(self, tuning=None, frets=22):
        self.frets = frets
        if tuning is None:
            self.tuning = Tuning()
        else:
            self.tuning = tuning
        assert isinstance(self.tuning, Tuning)

    def note(self, n, fret=None):
        if n > len(self.tuning.name):
            raise IndexError('No string {} on {}-string guitar'.format(n, len(self.tuning.name)))

        start_note = self.tuning[n-1]
        return start_note + int(fret)

    def find_note(self, note):
        for n in self.tuning:
            print(note - n, end=' ')

    def draw_note(self, notes, start=0, end=None):
        if end is None:
            end = self.frets + 1
        fretboard = list()
        for n in reversed(list(self.tuning)):
            string = list()
            for i in range(start, end + 1):
                if (n + i).major.key in notes:
                    symb = (n + i).major
                elif (n + i).minor.key in notes:
                    symb = (n + i).minor
                else:
                    symb = '  '
                string.append(' {}'.format(symb).rjust(4))
            print('|'.join(string))
        string = list()
        for i in range(start, end + 1):
            string.append('{}'.format(i).rjust(4))
        print(' '.join(string))

    def __getitem__(self, item):
        return self.note(*item)


class ChordBuilder:
    """
    1. get steps amount, set steps in major
    2. modify tonic if minor
    3. alternate chord (sus, add, remove, reduce, enlarge)
    4. modify all if dim
    5. modify last(?) if aug :todo
    6.(?) find lowest, then add bass note :todo

    #todo:
    parser to class
    :symbol bank (in)
    comparsion for Note
    change H to B ?
    tonic tone - to note
    : do not change
    ? is_minor
    ...
    fretboard find_note()
    : order is first, last, third, seventh, others; can drop 5, 9 ,11
    ...
    draw fretboard
    ...
    next: harmony
    """

    NATURAL_MAJOR_STEPS = 'CDEFGAB'

    def __init__(self, tonic: Note):
        assert isinstance(tonic, Note)
        self.steps = dict()
        self.steps[1] = tonic
        self.is_minor = False
        print(' 1 {} tonic'.format(self.tonic))

    @property
    def tonic(self):
        return self.steps[1]

    @classmethod
    def step_interval(cls, step):
        steps = cls.NATURAL_MAJOR_STEPS * (step // 7 + 1)
        octave = (step - 1) // 7
        interval = Note(steps[step - 1], octave=octave) - Note('C', octave=0)
        return interval

    def add_natural_major_step(self, step):
        interval = self.step_interval(step)
        self.steps[step] = self.tonic + interval
        self.steps[step].set_gamma(self.tonic.gamma)
        print(' {} {} added'.format(step, self.steps[step]))

    def enlarge(self, step):
        if self.steps.get(step) is None:
            print('no step {} to enlarge'.format(step))
            return
        print('♯{} {} enlarged'.format(step, self.steps[step]))
        self.steps[step] += 1
        self.steps[step].set_gamma(Note.MAJOR)

    def reduce(self, step):
        if self.steps.get(step) is None:
            print('no step {} to reduce'.format(step))
            return
        print('♭{} {} reduced'.format(step, self.steps[step]))
        self.steps[step] -= 1
        self.steps[step].set_gamma(Note.MINOR)

    def expand_to(self, target_step, maj=False):
        for step in range(3, target_step+1, 2):
            if self.steps.get(step) is None:
                self.add_natural_major_step(step)
                if not maj and step in (7, ):
                    self.reduce(step)
        if not target_step % 2 and self.steps.get(target_step) is None:
            self.add_natural_major_step(target_step)

    def maj(self, target_step=5):
        self.expand_to(target_step)

    def min(self, target_step=5):
        self.expand_to(target_step)
        self.reduce(3)
        self.is_minor = True

    def maj7(self):
        self.maj(7)

    def hitchcock7(self):
        self.expand_to(7)
        self.reduce(7)
        self.is_minor = True

    def min_maj7(self):
        self.min(7)
        self.is_minor = True

    def dominant7(self):
        self.maj(7)
        self.reduce(7)
        self.is_minor = True

    def sus(self, target=4, base=3):
        """ suspended 3 or base
            r"sus[249]"
            as last
        """
        print(' {} {} suspended to {}'.format(base,  self.steps[base], target))
        if base in self.steps:
            del self.steps[base]

        self.add_natural_major_step(target)

    def add(self, step):
        self.add_natural_major_step(step)

    def dim(self):
        """ reduce all
            r"dim"
            as last
        """
        self.is_minor = True
        for k, step in self.steps.items():
            if k != 1:
                self.reduce(k)

    def aug(self):
        """ enlarge the last step
            r"\+$" - + at the end
            as last
        """
        # todo: theory
        self.enlarge(max(self.steps))

    def add_bass(self, key):
        """ add a bass note
        """
        i = 0
        while self.steps.get(i):
            i -= 1
        self.steps[i] = Note(key, octave=self.tonic.octave-1)

    def omit(self, step):
        print(' {} {} omitted'.format(step, self.steps[step]))
        if self.steps.get(step) is not None:
            del self.steps[step]

    def next(self, step):
        next_note = self.tonic + self.step_interval(step)
        return ChordBuilder(next_note)

    @property
    def notes(self):
        return self.steps

    def __iter__(self):
        note_names = list()
        for key in sorted(self.steps.keys()):
            note_names.append(self.steps[key].key)
        for note in note_names:
            yield note

    def __str__(self):
        note_names = list()
        for key in sorted(self.steps.keys()):
            note_names.append(self.steps[key].key)
        return ' '.join(note_names)

