class Semitone:

    def __init__(self, name, enharmonic=False):
        self.name = name
        self.is_note = enharmonic



class Note:

    MAJOR = {
        'C': Semitone('C'),
        'C#': Semitone('C#', enharmonic=True),
        'D': Semitone('D'),
        'D#': Semitone('D#', enharmonic=True),
        'E': Semitone('E'),
        'F': Semitone('F'),
        'F#': Semitone('F#', enharmonic=True),
        'G': Semitone('G'),
        'G#': Semitone('G#', enharmonic=True),
        'A': Semitone('A'),
        'A#': Semitone('A#', enharmonic=True),
        'B': Semitone('B'),
    }

    MINOR = {
        'C': Semitone('C'),
        'Db': Semitone('Db', enharmonic=True),
        'D': Semitone('D'),
        'Eb': Semitone('Eb', enharmonic=True),
        'E': Semitone('E'),
        'F': Semitone('F'),
        'Gb': Semitone('Gb', enharmonic=True),
        'G': Semitone('G'),
        'Ab': Semitone('Ab', enharmonic=True),
        'A': Semitone('A'),
        'Bb': Semitone('Bb', enharmonic=True),
        'B': Semitone('B'),
    }

    def __init__(self, key, octave=1, gamma=None):
        self.key = str(key).strip()[:2].capitalize()
        self.octave = octave
        if gamma is None:
            self.gamma = self.get_gamma()
        else:
            self.gamma = gamma

    def get_gamma(self):
        if self.key in self.MAJOR:
            gamma = self.MAJOR
        else:
            gamma = self.MINOR
        return gamma

    def set_gamma(self, gamma):
        self.key = gamma[list(gamma)[list(self.gamma).index(self.key)]].name
        self.gamma = gamma

    @property
    def minor(self):
        gamma = self.MINOR
        key = gamma[list(gamma)[list(self.gamma).index(self.key)]]
        return Note(key.name, octave=self.octave)

    @property
    def major(self):
        gamma = self.MAJOR
        key = gamma[list(gamma)[list(self.gamma).index(self.key)]]
        return Note(key.name, octave=self.octave)

    @property
    def frequency(self):
        n = self - Note('A')
        f0 = 440 * 2 ** (n / 12)
        return f0

    @property
    def midi_key(self):
        n = Note('A') - self + 49
        return n

    def __add__(self, other):
        assert isinstance(other, int)
        octave, semitones = divmod(other, 12)
        keys = self.gamma
        key = list(keys).index(self.key)
        key += semitones
        inc_octave, clean_key = divmod(key, 12)
        octave += inc_octave + self.octave
        key = clean_key - inc_octave * 12
        key_char = keys[list(keys)[key]]
        return Note(key_char.name, octave=octave, gamma=self.gamma)

    def __sub__(self, other):
        if isinstance(other, Note):
            keys = self.MAJOR
            key0 = list(keys).index(self.major.key)
            key = list(keys).index(other.major.key)
            diff = (self.octave - other.octave) * 12 - (key - key0)
            return diff

        elif isinstance(other, int):
            return self.__add__(-other)

    def __str__(self):
        return '{}{}'.format(self.key, self.octave)

    def __repr__(self):
        return '{}'.format(self.key)








