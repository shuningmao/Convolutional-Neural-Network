import logging
import csv
from collections import defaultdict




class Vocab(object):

    def __init__(self, name = 'n/a', logger=None, fn=None):
        self.logger = logger or logging.getLogger(__name__)

        self.name = name
        self.word_to_index = {}
        self.index_to_word = {}
        self.word_freq = defaultdict(int)

        self.unknown = '<unk>'
        self.eos = '<eos>'

        self.add_word(self.unknown, count=0)
        self.add_word(self.eos, count=0)

        self.unknown_token = self.encode(self.unknown)
        self.eos_token = self.encode(self.eos)

        if fn:
            self.load_vocab(fn)

    def __len__(self):
        return len(self.word_freq)


    def condense(self, threshold=3):
        vocab = Vocab()
        for word, freq in self.word_freq.items():
            if freq >= threshold:
                vocab.add_word(word, count=freq)
        return vocab

    def add_word(self, word, count=1):
        if not isinstance(word, str):
            raise ValueError('word must be string')

        if word not in self.word_to_index:
            index = len(self.word_to_index)
            self.word_to_index[word] = index
            self.index_to_word[index] = word

        self.word_freq[word] += count

    def encode(self, word):
        if word not in self.word_to_index:
            return self.unknown_token
        return self.word_to_index[word]


    def _load_csv_line(self, line):
        line = line.strip().split(' ')
        for word in line:
            if len(word) > 2:
                self.add_word(word)

    def load_csv(self, fn, col=1):
        with open(fn, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                self._load_csv_line(row[col])
        self.logger.info(' vocab loaded from %s', fn)

    def load_vocab(self, fn):
        i = -1
        with open(fn, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                self.add_word(row[0], int(row[1]))
        self.logger.info(' %s vocab loaded from %s', i + 1, fn)

    def save_vocab(self, fn):
        i = -1
        words = self.index_to_word.values()
        with open(fn, 'w') as f:
            writer = csv.writer(f)
            for i, (word, freq) in enumerate(self.word_freq.items()):
                writer.writerow([word, freq])
        self.logger.info(' %s vocab saved to %s', i + 1, fn)
