#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *
g = Grammar()


"""Adapted from C.Diggins's Jigsaw SExpressions-like syntax file
"""

Letter          = g.Pattern('[a-z]')
Integer         = g.Pattern('\d+')
Ws              = g.Pattern('\s*')
Digit           = g.Pattern('\d')

Term            = g.Rec2( lambda : g.Choice([Atom, SExpr]) )
Terms           = g.Node("Sym", g.ZeroOrMore(g.Seq([Term, Ws])))
FirstSymbolChar = g.Choice([Letter, g.CharSet("~@#$%^&*-_=+:<>,./")])
NextSymbolChar  = g.Choice([FirstSymbolChar , Digit])
Symbol          = g.Node("Sym", g.Seq([FirstSymbolChar, g.ZeroOrMore(NextSymbolChar)]))
String          = g.Node("Str", g.Pattern('".*?"') )
Atom            = g.Node("Atom", g.Choice([Integer, String, Symbol]))
SExpr           = g.Node("SExpr", g.Seq([g.MatchString("("), Terms, g.MatchString(")")]))

test_strings = ('a)', '()', '(a)', '(c (a 12) "hello")')

for ts in test_strings:
    pass

res= SExpr.parse('(c (a 12 (a 12)) "hello")')

for el in res:
    print el
    for sel in el.nodes:
        print "---SUB: ",sel
        for ssel in sel.nodes:
            print "---SUBSUB: ",ssel
print "RESULT:  ", res , "\n"

