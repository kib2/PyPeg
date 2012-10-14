#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peg import *

g = Grammar()

print "\n---- 1\n"
# Test 1
print g.MatchString("fox").matchTest("g")
print g.MatchString("fox").matchTest("fg")
print g.MatchString("fox").matchTest("flying fox")
print "\n---- 2\n"

# Test 2
print g.Choice([g.MatchString("cat"),g.MatchString("dog")]).matchTest("catfish")
print g.Choice([g.MatchString("cat"),g.MatchString("dog")]).matchTest("doggedly")
print "\n---- 3\n"

# Test 3
print g.Seq([g.MatchString("cat"),g.MatchString("fish")]).matchTest("catnip")  # false
print g.Seq([g.MatchString("cat"),g.MatchString("fish")]).matchTest("dogfish") # false
print g.Seq([g.MatchString("cat"),g.MatchString("fish")]).matchTest("catfish") # true
print "\n---- 4\n"

# Test 4
print g.Seq( [g.Choice( [g.MatchString("cat"),g.MatchString("dog")]), g.MatchString("fish")] ).matchTest("dogfish")   # true
print g.Seq( [g.Choice( [g.MatchString("cat"),g.MatchString("dog")]), g.MatchString("fish")] ).matchTest("catfish")   # true
print g.Seq( [g.Choice( [g.MatchString("cat"),g.MatchString("dog")]), g.MatchString("fish")] ).matchTest("swordfish") # false
print g.Seq( [g.Choice( [g.MatchString("cat"),g.MatchString("dog")]), g.MatchString("fish")] ).matchTest("cat")       # false
print "\n---- 5\n"

# Test 5
print g.Seq( [g.MatchString("cat"), g.Opt([g.MatchString("fish"),g.MatchString("nap")])]).matchTest("cat")     # true
print g.Seq( [g.MatchString("cat"), g.Opt([g.MatchString("fish"),g.MatchString("nap")])]).matchTest("catfish") # true
print "\n---- 6\n"

# Test 6
print g.OneOrMore(g.MatchString("badger")).matchTest("badger badger badgerbadgersnake!") # true
print "\n---- 6 bis\n"

# Test 6 bis
print g.Node("Reg", g.Pattern(r"\d+")).matchTest("1246")
print "\n---- 7\n"

# Test 7
word      = g.Node("word", g.Pattern(r"\w+")) 
ws        = g.Pattern(r"\s+")
eos       = g.CharSet("!.?")
sentence  = g.Node( "sentence", g.Seq([g.ZeroOrMore(g.Choice([word , ws])),  eos]) ) 
sentences = g.OneOrMore(g.Seq([sentence, g.Opt(ws)]))

nod = sentences.parse("Hey! You stole my pen. Hey you stole my pen!")
for el in nod:
    print el
    for sub_el in el.nodes:
        print "...%s" %(sub_el)