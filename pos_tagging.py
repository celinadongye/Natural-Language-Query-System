# File: pos_tagging.py
# Template file for Informatics 2A Assignment 2:
# 'A Natural Language Query System in Python/NLTK'

# John Longley, November 2012
# Revised November 2013 and November 2014 with help from Nikolay Bogoychev
# Revised November 2015 by Toms Bergmanis


# PART B: POS tagging

from statements import *

# The tagset we shall use is:
# P  A  Ns  Np  Is  Ip  Ts  Tp  BEs  BEp  DOs  DOp  AR  AND  WHO  WHICH  ?

# Tags for words playing a special role in the grammar:

function_words_tags = [('a', 'AR'), ('an', 'AR'), ('and', 'AND'),
                       ('is', 'BEs'), ('are', 'BEp'), ('does', 'DOs'), ('do', 'DOp'),
                       ('who', 'WHO'), ('which', 'WHICH'), ('Who', 'WHO'), ('Which', 'WHICH'), ('?', '?')]
# upper or lowercase tolerated at start of question.

function_words = [p[0] for p in function_words_tags]


def unchanging_plurals():
    wordsUnchanged = set()                        # Set for the irregular plural forms
    wordsNN = []                                  # List for singular nouns
    wordsNNS = []                                 # List for plural nouns
    with open("sentences.txt", "r") as f:
        for line in f:
            for words in line.split():            # Default separator is a whitespace
                (word, tag) = words.split('|')    # Separate word and tag
                if tag == "NN":                   # Singular noun
                    wordsNN.append(word)
                elif tag == "NNS":                # Plural noun
                    wordsNNS.append(word)
    
    # Word is unchanging plural if noun appears to be the same in both NN and NNS lists
    for noun in wordsNN:
        if noun in wordsNNS:
            wordsUnchanged.add(noun)

    return wordsUnchanged

unchanging_plurals_list = unchanging_plurals()



def noun_stem(s):
    """extracts the stem from a plural noun, or returns empty string"""
    vowels = "aeiou"
    nounStem = ""

    # Check if noun is an irregular plural form
    if s in unchanging_plurals_list:
        nounStem = s
    # If noun stem ends in "man", replace this by "men"
    elif re.match(r'[A-Za-z]*men\b', s):
        nounStem = s[:-2] + "an"
    # Otherwise apply rules for 3s formation from statements.py
    else:
        if s == "has":
            nounStem = "have"
        elif re.match(r'[A-Za-z]+([^sxyz]|(^ch)|(^sh))s\b', s) and not s[-2:-1] in vowels:
            nounStem = s[:-1]
        elif re.match(r'[A-Za-z]+ys\b', s) and s[-3:-2] in vowels:
            nounStem = s[:-1]
        elif re.match(r'[A-Za-z]+ies\b', s) and not s[-4:-3] in vowels and len(s) >= 5:
            nounStem = s[:-3] + 'y'
        elif re.match(r'[A-Za-z]ies\b', s) and not s[0] in vowels:
            nounStem = s[:-1]
        elif re.match(r'[A-Za-z]+(o|x|ch|sh|ss|zz)es\b', s):
            nounStem = s[:-2]
        elif re.match(r'[A-Za-z]+([^sz](se|ze))s\b', s):
            nounStem = s[:-1]
        elif re.match(r'[A-Za-z]+([^iosxz]|[^cs]h)es\b', s):
            nounStem = s[:-1]
        else:
            nounStem = ""
    
    return nounStem

'''
#TestNounStem
print noun_stem("sheep")
print noun_stem("buffalo")
print noun_stem("fish")
print noun_stem("women")
print noun_stem("firemen")
print noun_stem("dogs")
print noun_stem("countries")
print noun_stem("ashes")
'''

def tag_word(lx, wd):
    """returns a list of all possible tags for wd relative to lx"""
    wordTags = set()
    # Proper names
    for word in lx.getAll('P'):
        if (word == wd):
            wordTags.add('P')
    # Common nouns
    for word in lx.getAll('N'):
        if (word == noun_stem(wd)):
            wordTags.add('Np')
        if (word == wd):
            wordTags.add('Ns')
    # Adjectives
    for word in lx.getAll('A'):
        if (word == wd):
            wordTags.add('A')
    # Intransitive verbs
    for word in lx.getAll('I'):
        if (word == verb_stem(wd)):
            wordTags.add('Is')
        if (word == wd):
            wordTags.add('Ip')
    # Transitive verbs
    for word in lx.getAll('T'):
        if (word == verb_stem(wd)):
            wordTags.add('Ts')
        if (word == wd):
            wordTags.add('Tp')
    
    for (word, tag) in function_words_tags:
        if (word == wd):
            wordTags.add(tag)

    return wordTags

'''
#TestTagWord
lx = Lexicon()
lx.add("John", "P")
lx.add("orange", "N")
lx.add("orange", "A")
lx.add("fish", "N")
lx.add("fish", "I")
lx.add("fish", "T")
lx.add("a", "AR")
print tag_word(lx,"John")
print tag_word(lx,"orange")
print tag_word(lx,"fish")
print tag_word(lx,"a")
print tag_word(lx,"zxghqw")
'''


def tag_words(lx, wds):
    """returns a list of all possible taggings for a list of words"""
    if (wds == []):
        return [[]]
    else:
        tag_first = tag_word(lx, wds[0])
        tag_rest = tag_words(lx, wds[1:])
        return [[fst] + rst for fst in tag_first for rst in tag_rest]

# End of PART B.
