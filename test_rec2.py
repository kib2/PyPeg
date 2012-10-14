#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *

"""
Parsing Pascal-like nested comments:
http://en.wikipedia.org/wiki/Parsing_expression_grammar

Begin ← "(*"
End   ← "*)"
C     ← Begin N* End
N     ← C / (!Begin !End Z)
Z     ← any single character
"""


g = Grammar()

C      = g.Rec()
Begin  = g.MatchString("(*")
End    = g.MatchString("*)")
Z      = g.AnyChar()
N      = g.Choice([C , g.Seq([g.Not(Begin), g.Not(End), Z])])
newC   = g.Node("Comment", g.Seq([Begin, g.ZeroOrMore(N), End]) )
C.set( lambda : newC  )

res = C.parse('(*A new (* Pascal (* A  third level *) comment *) like this *)')

for el in res:
    print el
    for sub_el in el.nodes:
        print "-->%s" %(sub_el)
        for sub2_el in sub_el.nodes:
            print "---->%s" %(sub2_el)