#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *
from factor_eval import *

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

toTest = [
"10 5 div . def neg [0 swap -] 12 neg .",
"def plus5 [5 +] 17 plus5 .",
"5 10 div 50 100 div eq? .",
"3 6 mul 18 eq?",
"-4 16 sub",
"-4 abs",
'"abcd ef" .',
'pop 3 dup',
'5 1 swap',
'clear',
'[3 4 +] call',
'clear',
'def neg [0 swap -]',
'def sq [dup *]',
'clear',
'13 sq .',
'clear',
'8 ["hello" .] times',
'clear',
'1 2 4 [+] keep .',
'[1 2 3] list .',
'clear',
'[1 2 3] list [2 *] map [1 add] map .',
'1 0 lteq ["Yes"] ["No"] if',
'9 5 n 9',
'[1 2 3] list [sum] call .',
'[1 2 3] list [len] call .',
'[1 2 3] list [sum] [len] bi div .',
'clear',
'"john" "John" swap upper swap upper eq? .',
'"john" "John" [ upper ] bi@ eq? .',
'{ 1 2 3 } [2 *] map [1 add] map .'
]

fe = FactorEvaluator()
i=0

for morceau in toTest:
    res      = Terms.parse(morceau)
    computed = fe.eval_me(res[i])
    comp2    = fe.get_last()

    print "Test number:%s\nEval:'%s'\n... ---> Result: %s\n... ---> Stack: %s\n"%(i+1,morceau, comp2, fe.Values)
    i += 1