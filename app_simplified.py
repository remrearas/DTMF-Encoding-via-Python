import numpy as np
from scipy.io.wavfile import write


class DTMF:
    Columns = [1209, 1336, 1477, 1633]
    Index = [697,
             770,
             852,
             941]
    Matrix = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']
    ]
    Fs = 44100
    duration = 0.4

    def get(self, index: int, col: int) -> int or str:
        return self.Matrix[self.Index.index(index)][self.Columns.index(col)]

    def search(self, keyword: int or str) -> tuple or None:
        for idxRow, column in enumerate(self.Matrix):
            for idxColumn, element in enumerate(column):
                if element == keyword:
                    return self.Index[idxRow], self.Columns[idxColumn]

    @property
    def time(self):
        return np.arange(self.Fs * self.duration) * (1 / self.Fs)

    def build_signal(self, elem: int or str):
        f1, f2 = self.search(elem)
        return np.sin(2 * np.pi * f1 * self.time) + np.sin(2 * np.pi * f2 * self.time), f1, f2

    def encode_raw(self, raw: str):
        return np.concatenate([self.build_signal(x)[0] for x in raw])


if __name__ == "__main__":
    dtmf = DTMF()
    raw_number = '21501322'
    # Generate wave file
    write('./output/%s.wav' % raw_number,
          dtmf.Fs,
          dtmf.encode_raw(raw_number))

