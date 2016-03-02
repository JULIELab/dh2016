import glob
import codecs
import re
import gensim
import os
import time
import collections
import sys
import re
from gensim import matutils, corpora, models, similarities
from gensim.matutils import unitvec
from gensim.models.word2vec import Vocab
from numpy import dot, copy


import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


class Corpus(object):
    # structure of google books 2012 files
    TEXT = 0
    YEAR = 1
    MATCH_COUNT = 2
    VOLUME_COUNT = 3

    def __init__(self, years, corpus_path):
        self.corpus_path = corpus_path
        self.first = {}
        self.years = years

    def __iter__(self):
        if not os.path.exists(os.path.join(self.corpus_path, self.years)):
            logging.info("skipping %s", self.years)
        else:
            for line in open(
                    os.path.join(
                        self.corpus_path,
                        self.years),
                    "r",
                    encoding="utf-8"):
                # one document per line, tokens separated by whitespace, tabs separate
                # year/counts
                parts = line.split("\t")
                parts[self.TEXT] = parts[self.TEXT].lower().split(" ")
                for i in range(int(parts[self.MATCH_COUNT])):
                    for word in parts[self.TEXT]:
                        if not word in self.first:
                            self.first[word] = self.years
                    yield parts[self.TEXT]


def update_vocab(corpus, old_model, model):
    """Like mode.build_vocab(), inserts words/vectors from old model"""
    count = model.min_count + 1
    model.scan_vocab(corpus)  # initial survey
    for word in old_model.vocab:  # insert old
        if word not in model.vocab:
            model.raw_vocab[word] += count
            model.vocab[word] = Vocab(
                count=count, index=len(model.index2word))
            model.index2word.append(word)
    # trim by min_count & precalculate downsampling
    model.scale_vocab()
    model.finalize_vocab()  # build tables & arrays
    for word in old_model.vocab:
        if word in model.vocab:
            model.syn0[model.vocab[word].index] = old_model.syn0[
                old_model.vocab[word].index]


def main():
    """
    Training follows procedure described in Kim et al. (2014), cf. https://www.aclweb.org/anthology/W/W14/W14-2517.pdf
    """
    ALPHA = 0.01
    NET_SIZE = 200

    if len(sys.argv) < 6:
        raise Exception("""Provide 5+ arguments:\n\t1,path to save models\n\t2,path to corpora
            \t3,number of worker processes\n\t4,number of max. epochs\n\t5, minimum count
            \t6, hierarchic (0/1)\n\t7,neg sampling (0-20)\n\t8,downsampling (0-0.00001)
            9+ files to train on (one model per file)""")
    model_path = sys.argv[1]
    corpus_path = sys.argv[2]
    workers = int(sys.argv[3])
    epochs = int(sys.argv[4])
    min_count = int(sys.argv[5])
    hs = int(sys.argv[6])
    negative = int(sys.argv[7])
    sample = float(sys.argv[8])
    files = sys.argv[9:]

    if not os.path.exists(model_path):
        os.makedirs(model_path)
    old_model = None
    for f in files:
        if not os.path.exists(os.path.join(corpus_path, f)):
            logging.info("skipping %s", f)
            continue
        logging.info("processing %s", f)
        model = gensim.models.Word2Vec(
            size=NET_SIZE, window=4, min_count=min_count, workers=workers, alpha=ALPHA, sg=1,
            hs=hs, negative=negative, sample=sample)
        corpus = Corpus(f, corpus_path)

        if old_model:
            update_vocab(corpus, old_model, model)
        else:
            model.build_vocab(corpus)

        # training to convergence
        epoch = 0
        dist = 0
        while epoch < epochs and dist < 0.99:
            epoch += 1
            if epoch > 1:
                old_syn0 = copy(model.syn0)
            model.train(corpus)
            if epoch > 1:
                dist = sum([dot(unitvec(model.syn0[i]), unitvec(
                    old_syn0[i])) for i in range(len(model.vocab))]) / len(model.vocab)
        old_model = model
        model.save(os.path.join(model_path, "model" + f))
        logging.info("finished after %s epochs", epoch)

if __name__ == "__main__":
    main()
