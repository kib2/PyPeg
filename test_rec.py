#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *

g = Grammar()

Letter          = g.Pattern('[a-z]')
Integer         = g.Pattern('\d+')
Ws              = g.MatchString(" ")
Digit           = g.Pattern('\d')
Term            = g.Rec1()
Terms           = g.Node("Sym", g.ZeroOrMore(g.Seq([Term, Ws])))
FirstSymbolChar = g.Choice([Letter, g.CharSet("~@#$%^&*-_=+:<>,./")])
NextSymbolChar  = g.Choice([FirstSymbolChar , Digit])
Symbol          = g.Node("Sym", g.Seq([FirstSymbolChar, g.ZeroOrMore(NextSymbolChar)]))
String          = g.Node("Str", g.Pattern('".*?"') )
Atom            = g.Node("Atom", g.Choice([Integer, String, Symbol]))
SExpr           = g.Node("SExpr", g.Seq([g.MatchString("("), Terms, g.MatchString(")")]))

Term.set( lambda : g.Choice([Atom, SExpr]) )

res = SExpr.parse('(~c (^a 12 ) #k )')

for el in res:
    print el
    for sub_el in el.nodes:
        print "...%s" %(sub_el)
        for subsub_el in sub_el.nodes:
        	print "......%s" %(subsub_el)