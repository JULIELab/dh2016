import xml.etree.ElementTree as etree
import sys
import collections


def main():
    """
    Parses DTA corpora and lists most frequent nouns
    """
    wordCount = collections.Counter()

    if len(sys.argv) < 3:
        raise Exception(
            "Please provide 2+ arguments:\n\t1,Number of most frequent words to extract\n\t2+ Files to parse")

    limit = int(sys.argv[1])
    for xml in sys.argv[2:]:
        tree = etree.parse(xml)
        words = {}
        correct_tags = set()
        root = tree.getroot()
        for corpus in root.findall("{http://www.dspin.de/data/textcorpus}TextCorpus"):
            for tokens in corpus.findall("{http://www.dspin.de/data/textcorpus}tokens"):
                for token in tokens.findall("{http://www.dspin.de/data/textcorpus}token"):
                    words[token.attrib["ID"]] = token.text
            for orthography in corpus.findall("{http://www.dspin.de/data/textcorpus}orthography"):
                for correction in orthography.findall("{http://www.dspin.de/data/textcorpus}correction"):
                    if correction.attrib["operation"] == "replace":
                        words[correction.attrib["tokenIDs"]] = correction.text
            for postags in corpus.findall("{http://www.dspin.de/data/textcorpus}POStags"):
                for tag in postags.findall("{http://www.dspin.de/data/textcorpus}tag"):
                    if tag.text == "NN":
                        correct_tags.add(tag.attrib["tokenIDs"])
        for key in words:
            if key in correct_tags:
                wordCount[words[key]] += 1

    print(" ".join([w.lower() for w, c in wordCount.most_common(limit)]))

if __name__ == "__main__":
    main()
