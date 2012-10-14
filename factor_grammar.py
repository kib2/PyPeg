#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *
g = Grammar()

WS              = g.Regex('\s*')
Digit           = g.Regex('\d')
Letter          = g.Regex('[a-zA-Z]')
FirstSymbolChar = Letter | g.CharSet("~@#?$%^&*-_=+:<>,./")
NextSymbolChar  = FirstSymbolChar | Digit
Symbol          = g.Node("Symbol", FirstSymbolChar + g.ZeroOrMore(NextSymbolChar))
AString         = g.Node("String", g.Char('"') + g.AdvanceWhileNot(g.Char('"')) + g.Char('"'))
Float           = g.Node("Float", g.Regex('\-?\d+?\.\d+'))
Integ           = g.Node("Int", g.Regex('-?\d+'))
Atom            = g.Node("Atom", Integ | Float | AString | Symbol)
Term            = g.Delay()
Terms           = g.Node("Terms", g.ZeroOrMore(Term)) #  Our Entry Point
CListTerm       = g.Delay()
CListTerms      = g.Node("CListTerms", g.ZeroOrMore(CListTerm))
Quotation       = g.Node("Quotation", g.Char('[') + WS + Terms + WS + g.Char(']'))
CList           = g.Node("CList", g.Char('{') + WS + CListTerms + WS + g.Char('}'))
Define          = g.Node("Define",g.MatchString("def") + WS + Symbol + WS + Quotation )

CListTerm.set( (Define | Atom | Quotation) + WS)
Term.set( (Define | Atom | Quotation | CList) + WS)

res= Terms.parse('52 def toto [1 [1 2 3] 3] list [2 *] map [1 add] map .')

for el in res:
    print el
    for sel in el.nodes:
        print "--SUB: ",sel
        for ssel in sel.nodes:
            print "----SUBSUB: ",ssel
            for sssel in ssel.nodes:
            	print "------SUBSUB: ",sssel
print "RESULT:  ", res , "\n"

