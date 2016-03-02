import gensim
import sys
import collections
import math
from scipy import spatial
from operator import itemgetter
from gensim import matutils
from numpy import dot


def main():
    """
    prints list of words sorted according to their changes between two points of time
    """
    if len(sys.argv) != 4 and len(sys.argv) != 3:
        raise Exception(
            "Provide 2+ arguments:\n\t1,first model\n\t2,second model\n\t3,Optional: number of min occurrences")
    start = sys.argv[1]
    end = sys.argv[2]
    if len(sys.argv) == 4:
        min_occ = int(sys.argv[3])
    else:
        min_occ = 0

    model1 = gensim.models.Word2Vec.load(start)
    model2 = gensim.models.Word2Vec.load(end)

    similarity = {}

    for word in model1.vocab:
        if model1.vocab[word].count >= min_occ and word in model2.vocab and model2.vocab[word].count >= min_occ:
            similarity[word] = dot(matutils.unitvec(
                model1[word]), matutils.unitvec(model2[word]))

    for w, c in sorted(similarity.items(), key=itemgetter(1)):
        print(w, c)


if __name__ == "__main__":
    main()
