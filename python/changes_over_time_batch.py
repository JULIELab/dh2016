import gensim
import sys
import collections
import codecs
import re


def parse_similar_words(similar_words_file):
    """
    as produced by similar_words_batch.py
    """
    similar_words = {}
    word = ""
    for line in open(similar_words_file, "r"):
        if line == "----------------------------------------------------\n":
            word = ""
        elif word == "":
            word = line.strip()
            similar_words[word] = set()
        else:
            for w, c in eval(line):
                if w not in similar_words[word]:
                    similar_words[word].add(w)
    return similar_words


def longitudinal_changes(similar_words, years):
    """
    similarity between words and a group of similar words
    """
    results = {}
    for word in similar_words:
        results[word] = {}
        for word2 in similar_words[word]:
            results[word][word2] = {}
    for y in years:
        year = re.sub(".*_", "", y)
        model = gensim.models.Word2Vec.load(y)
        for word in similar_words:
            for word2 in similar_words[word]:
                if word2 in model:
                    results[word][word2][year] = model.similarity(word, word2)
                else:
                    results[word][word2][year] = " "
    return results


def store_results(results, years, result_path):
    """
    semicolon separated csv
    """
    files = {}
    for word in results:
        files[word] = codecs.open(result_path + "/" + word, "w", "utf-8")
        files[word].write(
            "year;" + ";".join([word2 for word2 in results[word]]) + "\n")
    for word in results:
        for y in years:
            year = re.sub(".*_", "", y)
            values = [str(results[word][word2][year])
                      for word2 in results[word]]
            files[word].write(year + ";" + ";".join(values) + "\n")
    for f in files:
        files[f].close()


def main():
    """
    Meassures how words changed in relation to other (similar) words, producing csv files
    """
    if len(sys.argv) < 3:
        raise Exception(
            "Provide 3+ arguments:\n\t1,similar_words_file to parse\n\t2,result path\n\t3+,model(s)")
    similar_words_file = sys.argv[1]
    result_path = sys.argv[2]
    years = sys.argv[3:]

    similar_words = parse_similar_words(similar_words_file)
    results = longitudinal_changes(similar_words, years)
    store_results(results, years, result_path)

if __name__ == "__main__":
    main()
