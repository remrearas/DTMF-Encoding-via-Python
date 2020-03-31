import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.signal
from functools import wraps
from scipy.io.wavfile import write
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2.pdf import PdfFileReader, PdfFileWriter

PLOT_SAMPLE = 100

figures = {}


def signal_figure(f):
    @wraps(f)
    def decor(*args, **kwargs):
        res = f(*args, **kwargs)
        if f.__name__ == 'build_signal':
            if args[1] not in figures:
                fig, ax = plt.subplots()
                ax.plot(scipy.signal.resample(res[0], PLOT_SAMPLE))
                ax.set_title('%s (%s Hz x %s Hz) - Fs=%d Hz - Duration=%f s' % (args[1],
                                                                                res[1],
                                                                                res[2],
                                                                                args[0].Fs,
                                                                                args[0].duration))
                figures[args[1]] = fig

        if f.__name__ == 'encode_raw':
            fig, ax = plt.subplots()
            ax.plot(scipy.signal.resample(res, PLOT_SAMPLE))
            ax.set_title('DTMF Encoded %s' % (args[1]))
            figures[args[1]] = fig
        return res
    return decor


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

    @signal_figure
    def build_signal(self, elem: int or str):
        f1, f2 = self.search(elem)
        return np.sin(2 * np.pi * f1 * self.time) + np.sin(2 * np.pi * f2 * self.time), f1, f2

    @signal_figure
    def encode_raw(self, raw: str):
        return np.concatenate([self.build_signal(x)[0] for x in raw])


if __name__ == "__main__":
    dtmf = DTMF()
    raw_number = '21501322'
    # Generate wave file
    write('./output/%s.wav' % raw_number,
          dtmf.Fs,
          dtmf.encode_raw(raw_number))
    # PDF Reports
    with PdfPages('%s.pdf' % raw_number) as pdf:
        for figure in figures:
            pdf.savefig(figures[figure])
    output = PdfFileWriter()
    pdfOne = PdfFileReader(open("./assets/Cover.pdf", "rb"))
    pdfTwo = PdfFileReader(open('%s.pdf' % raw_number, "rb"))

    output.addPage(pdfOne.getPage(0))
    output.addPage(pdfOne.getPage(1))
    for pageNum in range(pdfTwo.numPages):
        pageObj = pdfTwo.getPage(pageNum)
        output.addPage(pageObj)

    outputStream = open('./output/Chart-%s.pdf' % raw_number, "wb")
    output.write(outputStream)
    outputStream.close()
    os.remove('%s.pdf' % raw_number)

