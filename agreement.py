# File: agreement.py
# Template file for Informatics 2A Assignment 2:
# 'A Natural Language Query System in Python/NLTK'

# John Longley, November 2012
# Revised November 2013 and November 2014 with help from Nikolay Bogoychev
# Revised November 2015 by Toms Bergmanis
# Revised October 2017 by Chunchuan Lyu with help from Kiniorski Filip


# PART C: Syntax and agreement checking

from statements import *
from pos_tagging import *

# Grammar for the query language (with POS tokens as terminals):

from nltk import CFG
from nltk import parse
from nltk import Tree



grammar = CFG.fromstring('''
   S     -> WHO QP QM | WHICH Nom QP QM
   QP    -> VP | DO NP T
   VP    -> I | T NP | BE A | BE NP | VP AND VP
   NP    -> P | AR Nom | Nom
   Nom   -> AN | AN Rel
   AN    -> N | A AN
   Rel   -> WHO VP | NP T
   N     -> "Ns" | "Np"
   I    -> "Is" | "Ip"
   T    -> "Ts" | "Tp"
   A     -> "A"
   P     -> "P"
   BE    -> "BEs" | "BEp"
   DO    -> "DOs" | "DOp"
   AR    -> "AR"
   WHO   -> "WHO"
   WHICH -> "WHICH"
   AND   -> "AND"
   QM    -> "?"
   ''')

chartpsr = parse.ChartParser(grammar)

def all_parses(wlist,lx):
    """returns all possible parse trees for all possible taggings of wlist"""
    allp = []
    for tagging in tag_words(lx, wlist):
        allp = allp + [t for t in chartpsr.parse(tagging)]
    return allp


# This produces parse trees of type Tree.
# Available operations on trees:  tr.label(), tr[i],  len(tr)


# Singular/plural agreement checking.

# For convenience, we reproduce the parameterized rules from the handout here:

#    S      -> WHO QP[y] QM | WHICH Nom[y] QP[y] QM
#    QP[x]  -> VP[x] | DO[y] NP[y] T[p]
#    VP[x]  -> I[x] | T[x] NP | BE[x] A | BE[x] NP[x] | VP[x] AND VP[x]
#    NP[s]  -> P | AR Nom[s]
#    NP[p]  -> Nom[p]
#    Nom[x] -> AN[x] | AN[x] Rel[x]
#    AN[x]  -> N[x] | A AN[x]
#    Rel[x] -> WHO VP[x] | NP[y] T[y]
#    N[s]   -> "Ns"  etc.

def label(t):
    if (isinstance(t,str)):
        return t
    elif (isinstance(t,tuple)):
        return t[1]
    else:
        return t.label()

def top_level_rule(tr):
    if (isinstance(tr,str)):
        return ''
    else:
        rule = tr.label() + ' ->'
        for t in tr:
            rule = rule + ' ' + label(t)
        return rule
        
def N_phrase_num(tr):
    """returns the number attribute of a noun-like tree, based on its head noun"""
    if (tr.label() == 'N'):
        return tr[0][1]  # the s or p from Ns or Np
    elif (tr.label() == 'Nom'):
        return N_phrase_num(tr[0])
    elif (tr.label() == 'AN'):
        if (len(tr) == 1):
            return N_phrase_num(tr[0])
        else:
            return N_phrase_num(tr[1])
    elif (tr.label() == 'NP'):
        if (tr[0].label == 'P'):
            return 's'
        elif (tr[0].label == 'Nom'):
            return N_phrase_num(tr[0])
        else:
            return N_phrase_num(tr[1])
    else:
        return ""

def V_phrase_num(tr):
    """returns the number attribute of a verb-like tree, based on its head verb,
       or '' if this is undetermined."""
    if (tr.label() == 'T' or tr.label() == 'I'):
        return tr[0][1]  # the s or p from Is,Ts or Ip,Tp
    elif (tr.label() == 'VP'):
        return V_phrase_num(tr[0])
    elif (tr.label() == 'BE' or tr.label() == 'DO'):
        return tr[0][2]
    elif (tr.label() == 'Rel'):
        return V_phrase_num(tr[1])
    elif (tr.label() == 'QP'):
        if (len(tr) == 1):
            return V_phrase_num(tr[0])
        elif (V_phrase_num(tr[0]) == V_phrase_num(tr[2])):
            return V_phrase_num(tr[0])
        else:
            return ""
    else:
        return ""

def matches(n1,n2):
    return (n1==n2 or n1=='' or n2=='')

def check_node(tr):
    """checks agreement constraints at the root of tr"""
    rule = top_level_rule(tr)
    if (rule == 'S -> WHICH Nom QP QM'):
        return (matches (N_phrase_num(tr[1]), V_phrase_num(tr[2])))
    elif (rule == 'NP -> AR Nom'):
        return (N_phrase_num(tr[1]) == 's')
    elif (rule == 'NP -> Nom'):
        return (N_phrase_num(tr[0]) == 'p')
    elif (rule == 'QP -> DO NP T'):
        return (matches (V_phrase_num(tr[0]), N_phrase_num(tr[1]))) and (V_phrase_num(tr[2]) == 'p')
    elif (rule == 'VP -> BE NP'):
        return (matches (V_phrase_num(tr[0]), N_phrase_num(tr[1])))
    elif (rule == 'VP -> VP AND VP'):
        return (matches (V_phrase_num(tr[0]), V_phrase_num(tr[2])))
    elif (rule == 'Nom -> AN Rel'):
        return (matches (N_phrase_num(tr[0]), V_phrase_num(tr[1])))
    elif (rule == 'Rel -> NP T'):
        return (matches (N_phrase_num(tr[0]), V_phrase_num(tr[1])))
    else:
        return True

def check_all_nodes(tr):
    """checks agreement constraints everywhere in tr"""
    if (isinstance(tr,str)):
        return True
    elif (not check_node(tr)):
        return False
    else:
        for subtr in tr:
            if (not check_all_nodes(subtr)):
                return False
        return True

def all_valid_parses(lx, wlist):
    """returns all possible parse trees for all possible taggings of wlist
       that satisfy agreement constraints"""
    return [t for t in all_parses(wlist,lx) if check_all_nodes(t)]

            
# Converter to add words back into trees.
# Strips singular verbs and plural nouns down to their stem.

def restore_words_aux(tr,wds):
    if (isinstance(tr,str)):
        wd = wds.pop()
        if (tr=='Is'):
            return ('I_' + verb_stem(wd), tr)
        elif (tr=='Ts'):
            return ('T_' + verb_stem(wd), tr)
        elif (tr=='Np'):
            return ('N_' + noun_stem(wd), tr)
        elif (tr=='Ip' or tr=='Tp' or tr=='Ns' or tr=='A'):
            return (tr[0] + '_' + wd, tr)
        else:
            return (wd, tr)
    else:
        return Tree(tr.label(), [restore_words_aux(t,wds) for t in tr])

def restore_words(tr,wds):
    """adds words back into syntax tree, sometimes tagged with POS prefixes"""
    wdscopy = wds+[]
    wdscopy.reverse()
    return restore_words_aux(tr,wdscopy)

# Example:

if __name__ == "__main__":
    #code for a simple testing, feel free to modify
    lx = Lexicon()
    lx.add('John','P')
    lx.add('like','T')
    tr0 = all_valid_parses(lx, ['Who','likes','John','?'])[0]
    tr = restore_words(tr0,['Who','likes','John','?'])
    tr.draw()

# End of PART C.

