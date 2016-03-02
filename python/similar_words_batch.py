import gensim
import sys
import collections


def get_similar(words, limit, years):
    similar = {}
    for word in words:
        similar[word] = {}

    for year in years:
        model = gensim.models.Word2Vec.load(year)
        for word in words:
            for w, c in model.most_similar(word):
                if w not in similar[word]:
                    similar[word][w] = 0
                similar[word][w] += c
    return similar


def main():
	"""
	Finds <limit> words most similar to other word(s) according to two sets of models
	"""
    if len(sys.argv) != 5:
        raise Exception("Provide 4 arguments:\n\t1,word(s, separated by ;)\n\t2,number of context words (for old and new each)\n\t3, old model(s separated by ;) to query\n\t4, new model(s separated by ;) to query")
    words = sys.argv[1].split(";")
    limit = int(sys.argv[2])
    old = sys.argv[3].split(";")
    new = sys.argv[4].split(";")

    for word in words:
        print(word)
        old_similar = get_similar(words, limit, old)
        new_similar = get_similar(words, limit, new)
        print(sorted([tup for tup in old_similar[word].items()],
                     key=lambda tup: tup[1], reverse=True)[:limit])
        print(sorted([tup for tup in new_similar[word].items()],
                     key=lambda tup: tup[1], reverse=True)[:limit])
        print("----------------------------------------------------")


if __name__ == "__main__":
    main()
