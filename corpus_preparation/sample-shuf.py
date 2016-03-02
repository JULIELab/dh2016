import glob
import gzip
import codecs
import re
import sys
import os
import random
import collections

with_pos = False

targets = {}
my_buffer = {}


def flush(a_buffer, some_targets, a_year):
    for line in a_buffer[a_year]:
        some_targets[a_year].write(line)
    a_buffer[a_year].clear()


class Corpus(object):

    def __init__(self, corpus_path, years):
        self.corpus_path = corpus_path
        self.years = years

    def count(self):
        """
        Provides total number of N-grams (by matche-count) in time span
        """
        n = 0
        for year in self.years:
            year = str(year)
            if not os.path.exists(os.path.join(self.corpus_path, year)):
                raise Exception(os.path.join(
                    self.corpus_path, year) + " does not exist")
            for line in open(os.path.join(self.corpus_path, year), "r", encoding="utf-8"):
                # one document per line, tokens separated by whitespace, tabs
                # separate year/counts
                text, year, match_count, volume_count = line.split("\t")
                n += int(match_count)
        return n

    def select(self, accepted, normalized=None, lower=False):
        """
        Draw a sample according to accepted IDs
        """
        selection = []
        if accepted == None:
            raise Exception("Provide ids of accepted lines")
        if normalized != None:
            normalized = {}
            with codecs.open(normalized, mode="r", encoding="utf-8") as lines:
                for line in lines:
                    word, lemma = line.split(";")
                    normalized[word.strip()] = lemma.strip()
        n = 0
        for year in self.years:
            year = str(year)
            if not os.path.exists(os.path.join(self.corpus_path, year)):
                raise Exception(os.path.join(
                    self.corpus_path, year) + " does not exist")
            for line in open(os.path.join(self.corpus_path, year), "r", encoding="utf-8"):
                # one document per line, tokens separated by whitespace, tabs
                # separate year/counts
                text, year, match_count, volume_count = line.split("\t")
                for i in range(int(match_count)):
                    if accepted[n] > 0:
                        if normalized != None:
                            text = " ".join([normalized[word].lower(
                            ) if word in normalized else word.lower() for word in text.split(" ")])
                        elif lower:
                            text = text.lower()
                        for i in range(accepted[n]):
                            selection.append(text)
                    n += 1
        random.shuffle(selection)
        return selection


if len(sys.argv) != 7:
    raise Exception(
        "Provide: path, target, start (inclusive), end (exclusive), step, sample_size")
raw = sys.argv[1]
target = sys.argv[2]
start = int(sys.argv[3])
end = int(sys.argv[4])
step = int(sys.argv[5])
sample_size = int(sys.argv[6])

if not os.path.exists(target):
    os.makedirs(target)

if (end - start) % step != 0:
    raise Exception("Timespan not divisible by step!")
for x in range(start, end - step + 1, step):
    print("Processing", x)
    c = Corpus(raw, range(x, x + step, 1))
    count = c.count()
    accepted = collections.Counter()
    for i in range(sample_size):
        accepted[random.randint(0, count - 1)] += 1
    selection = c.select(accepted, lower=True)
    with open(os.path.join(target, str(x) + "_" + str(x + step - 1)), "w", 100000, encoding="utf-8") as target_file:
        for text in selection:
            line = text + "\t" + str(x) + "\t1\t0\n"
            target_file.write(line)
