#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *
g = Grammar()


"""Adapted from Ruby's TreeTop parsing gem

Parses a Lisp-like syntax
"""

Body            = g.Rec( lambda : g.Node("Body", g.OneOrMore( g.Choice([Expr, Ident, Integer, String, Ws]) )) )
Ws              = g.Node("WS", g.Opt(g.Pattern(r'\s')))
Signs           = g.Node("Sign", g.Opt(g.CharSet("+-")))
Integer         = g.Node("Int", g.Seq([Signs, g.Pattern(r'\d+')]))
String          = g.Node("Str", g.Pattern(r'".*?"') )
Ident           = g.Node("Identifier", g.Pattern(r'[a-zA-Z\=\*][a-zA-Z0-9_\=\*]*'))

Expr            = g.Node("Expr", g.Seq([Ws, g.MatchString("("), Body, g.MatchString(")"), Ws]))
#Body.set( ) 

res = Body.parse(' ( 12 56 +10) ')

for el in res:
    print el