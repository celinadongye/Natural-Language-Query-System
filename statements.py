# File: statements.py
# Template file for Informatics 2A Assignment 2:
# 'A Natural Language Query System in Python/NLTK'

# John Longley, November 2012
# Revised November 2013 and November 2014 with help from Nikolay Bogoychev
# Revised November 2015 by Toms Bergmanis
# Revised October 2017 by Chunchuan Lyu


# PART A: Processing statements
import nltk

def add(lst,item):
    if (item not in lst):
        lst.insert(len(lst),item)

class Lexicon:
    """stores known word stems of various part-of-speech categories"""
    # Word stems is the list of tuples where each tuple is the word stem and its POS category
    global wordStems
    wordStems = []

    # Method adds a word stem with a given POS category
    def add(self, stem, cat):
        # Adds word stem and category as a list to the end of wordStems list
        wordStems.append((stem, cat))
    
    # Returns all known word stems of a given category
    def getAll(self, cat):
        # List with no repeated word stems
        stems = []
        # Each element in wordStems list is a pair of stem and cat
        # If the cat in the pair, which is the second element, matches
        # the cat argument, then we add it to stems list
        for pair in wordStems:
            if (pair[1] == cat):
                add(stems, pair[0])
        return stems

'''
#TestLexicon
lx = Lexicon()
lx.add("John","P")
lx.add("Mary","P")
lx.add("like","T")
lx.add("likes","T")
lx.add("fish","T")

print lx.getAll("P")                             #returns ['John', 'Mary']
'''


class FactBase:
    """stores unary and binary relational facts"""
    global unaryFacts
    global binaryFacts
    unaryFacts = []
    binaryFacts = []

    def addUnary(self, pred, e1):
        add(unaryFacts, (pred, e1))
    
    def addBinary(self, pred, e1, e2):
        add(binaryFacts, (pred, e1, e2))
    
    def queryUnary(self, pred, e1):
        uTuple = (pred, e1)
        if (uTuple in unaryFacts):
            return True
        else:
            return False
    
    def queryBinary(self, pred, e1, e2):
        bTuple = (pred, e1, e2)
        if (bTuple in binaryFacts):
            return True
        else:
            return False


'''
#TestFactBase
fb = FactBase()
fb.addUnary("duck","John")
fb.addBinary("love","John","Mary")
print fb.queryUnary("duck","John")               # returns True  
print fb.queryBinary("love","Mary","John")       # returns False
print fb.queryBinary("Mary", "love", "duck")     # returns False
'''


import re
from nltk.corpus import brown 

# Retrieve all tagged word in Brown corpus
words = brown.tagged_words()
# Get all verbs tagged VB or VBZ
global verbs
verbs = set()
for (word, tag) in words:
    if (tag == "VB" or "VBZ"):
        verbs.add(word)

def verb_stem(s):
    """extracts the stem from the 3sg form of a verb, or returns empty string"""
    vowels = "aeiou"
    verbStem = ""

    # 3s form of verb have is has
    if s == "has":
        verbStem = "have"
    # Stem ends in anything except s,x,y,z,ch,sh or a vowel
    elif re.match(r'[A-Za-z]+([^sxyz]|(^ch)|(^sh))s\b', s) and not s[-2:-1] in vowels:
        verbStem = s[:-1]
    # Stem ends in y preceded by a vowel
    elif re.match(r'[A-Za-z]+ys\b', s) and s[-3:-2] in vowels:
        verbStem = s[:-1]
    # Stem ends in y preceded by a non-vowel and contains at least three letters
    elif re.match(r'[A-Za-z]+ies\b', s) and not s[-4:-3] in vowels and len(s) >= 5:    # minimum length of input string s is 5
        verbStem = s[:-3] + 'y'
    # Stem is of the form Xie where X is a single letter other than a vowel
    elif re.match(r'[A-Za-z]ies\b', s) and not s[0] in vowels:
        verbStem = s[:-1]
    # Stem ends in o,x,ch,sh,ss or zz
    elif re.match(r'[A-Za-z]+(o|x|ch|sh|ss|zz)es\b', s):
        verbStem = s[:-2]
    # Stem ends in se or ze but not in sse or zze
    elif re.match(r'[A-Za-z]+([^sz](se|ze))s\b', s):
        verbStem = s[:-1]
    # Stem ends in e not preceded by i,o,s,x,z,ch,sh
    elif re.match(r'[A-Za-z]+([^iosxz]|[^cs]h)es\b', s):
        verbStem = s[:-1]
    # If string s cannot be generated by the rules, empty string is returned
    else:
        verbStem = ""

    #return verbStem

    # Check if word is a verb according to Brown corpus
    if (s == "has" or s == "does"):
        return verbStem
    if verbStem in verbs:
        return verbStem
    else:
        return ""


'''
#TestVerbStem
print (verb_stem("laptops"))         # returns "" because it is a noun
print (verb_stem("has"))
print (verb_stem("does"))
print (verb_stem("eats"))
print (verb_stem("tells"))
print (verb_stem("shows"))
print (verb_stem("pays"))
print (verb_stem("buys"))
print (verb_stem("flies"))
print (verb_stem("tries"))
print (verb_stem("unifies"))
print (verb_stem("dies"))
print (verb_stem("lies"))
print (verb_stem("ties"))
print (verb_stem("goes"))
print (verb_stem("boxes"))
print (verb_stem("attaches"))
print (verb_stem("washes"))
print (verb_stem("dresses"))
print (verb_stem("fizzes"))          # returns ""         
print (verb_stem("loses"))
print (verb_stem("dazes"))           # returns ""  
print (verb_stem("lapses"))
print (verb_stem("analyses"))        # returns ""
''' 



def add_proper_name (w,lx):
    """adds a name to a lexicon, checking if first letter is uppercase"""
    if ('A' <= w[0] and w[0] <= 'Z'):
        lx.add(w,'P')
        return ''
    else:
        return (w + " isn't a proper name")

def process_statement (lx,wlist,fb):
    """analyses a statement and updates lexicon and fact base accordingly;
       returns '' if successful, or error message if not."""
    # Grammar for the statement language is:
    #   S  -> P is AR Ns | P is A | P Is | P Ts P
    #   AR -> a | an
    # We parse this in an ad hoc way.
    msg = add_proper_name (wlist[0],lx)
    if (msg == ''):
        if (wlist[1] == 'is'):
            if (wlist[2] in ['a','an']):
                lx.add (wlist[3],'N')
                fb.addUnary ('N_'+wlist[3],wlist[0])
            else:
                lx.add (wlist[2],'A')
                fb.addUnary ('A_'+wlist[2],wlist[0])
        else:
            stem = verb_stem(wlist[1])
            if (len(wlist) == 2):
                lx.add (stem,'I')
                fb.addUnary ('I_'+stem,wlist[0])
            else:
                msg = add_proper_name (wlist[2],lx)
                if (msg == ''):
                    lx.add (stem,'T')
                    fb.addBinary ('T_'+stem,wlist[0],wlist[2])
    return msg
                        
# End of PART A.
