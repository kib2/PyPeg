#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
    A port of Christopher Diggin's Jigsaw C# 4.0 project:
    

    Christopher Diggin's nice article explaining how to build a grammar 
    is on the CodeProject's site:
    http:#www.codeproject.com/KB/recipes/programminglanguagetoools.aspx

    Kibleur Christophe, December 2011.

    Note:
    =====

    Using cache is set inside the NodeRule.__init__ method

"""

import re


"""
================================================================================
                            GRAMMAR CLASS
            A class handling all the possible parsers
================================================================================
"""

class Grammar(object):
    # Operator overloading
    def __add__(self, other):
        return self.Seq([self, other ])

    def __radd__(self, other):
        return self.Seq([other,self])

    def __div__(self, other):
        return self.Choice([self, other])

    def __rdiv__(self, other):
        return self.Choice([self, other])

    def __or__(self, other):
        return self.Choice([other, self])

    def __ror__(self, other):
        return self.Choice([other, self])

    ## CLASSMETHODS
    @classmethod
    def Node(self, name, rule):
        n = NodeRule(rule)
        n.SetName(name)
        return n
    
    @classmethod
    def At(self, rule):
        return AtRule(rule)
    
    @classmethod
    def Not(self, rule):
        return NotRule(rule)
    
    @classmethod
    def Choice(self, rules):
        return ChoiceRule(rules)
    
    @classmethod
    def Seq(self, rules):
        return SeqRule(rules)
    
    @classmethod
    def Opt(self, rules):
        return OptRule(rules)
    
    @classmethod
    def ZeroOrMore(self, s):
        return ZeroOrMoreRule(s)
    
    @classmethod
    def OneOrMore(self, r):
        return PlusRule(r)
   
    @classmethod
    def MatchString(self, s):
        return StringRule(s)
    
    @classmethod  
    def Delay(self):
        return DelayRule()

    @classmethod
    def Char(self, c):
        if isinstance(c, basestring):
            return CharRule(lambda v: v == c )
        else:
            return CharRule(c)
    
    @classmethod
    def CharSet(self, s):
        if s == "":
            print "Charset is empty"
        return self.Char(lambda c: c in s)
    
    @classmethod
    def CharRange(self, a,b):
        return self.Char(lambda c: (c == a) and (c == b))
    
    @classmethod
    def Regex(self, re):
        return RegexRule(re)
    
   
    @classmethod
    def AnyChar(self):
        return self.Char(lambda c: True)

    @classmethod
    def AdvanceWhileNot(self,r):
        if (r is None):
            print "Cannot build this AdvanceWhileNot rule without any parser"
        return ZeroOrMoreRule(self.Seq([self.Not(r), self.AnyChar()]))
    
"""
================================================================================
                            NODE CLASS
            The grammar nodes are used by your ParserState instance
================================================================================
"""

class Node(object):
    def __init__(self, begin, label, inputs):
        self.inputs  = inputs         # Input string used to create AST node.
        self.begin  = begin         # Index where AST content starts within Input.
        self.theend = len(inputs)   # Index where AST content ends within Input.
        self.label  = label         # The name of the associated rule.
        self.nodes  = []            # List of child nodes.  

    def lenght(self):
        # Length of associated text.
        diff = self.theend - self.begin
        if diff > 0:
            return diff
        else:
            return 0

    def isLeaf(self):
        # Indicates whether there are any children nodes or not. 
        return len(self.nodes) == 0

    def text(self):
        # Text associated with the parse result.
        return self.inputs[self.begin: self.begin + self.lenght()]

    def withLabel(self,label):
        return self.getNode(label)
    
    def nthChild(self,n):
        # Returns the nth child node.
        return self.nodes[n]
    

    def getNodes(self,label):
        # Returns all child nodes with the given label
        res = []
        for el in self.nodes:
            if el.label == label:
                res.append(el)
        return res

    def getNode(self,label):
        # Returns the first child node with the given label.
        return self.getNodes(label)[0]
    

    def count(self):
        return len(self.nodes)
    

    def descendants(self):
        res = []
        for n in self.nodes:
            for d in n.descendants():
                res.append(n)
        return res

    def __str__(self):
        t = self.text()
        #return "Nodes %s Text: '%s'" % (self.label,t)
        return "%s->'%s'" % (self.label,t)

    def __repr__(self):
        t = self.text()
        return "Node %s Text: '%s'" % (self.label,t)

"""
================================================================================
                            PARSERSTATE CLASS
        The ParserState is used inside the NodeRule class, it keeps an array
        of nodes (ParserState.nodes).
================================================================================
"""

class ParserState(object):

    def __init__(self, inputs, pos, nodes=[]):
        self.inputs = inputs
        self.pos    = pos
        self.nodes = nodes
        self.cache  = {}

    def current(self):
        return self.inputs[self.pos:]
    
    def assign(self,thestate):
        self.inputs = thestate.inputs
        self.pos    = thestate.pos
        self.nodes  = thestate.nodes
        return
    
    def clone(self):
        return ParserState(self.inputs, self.pos, self.nodes)
    
    def restoreAfter(self,action):
        old_state = self.clone()
        action()
        self.assign(old_state)
    
    def cacheResult(self,rule, pos, node):
        if (pos not in self.cache):
            self.cache[pos] = {}
        if (rule not in self.cache[pos]):
            self.cache[pos][rule] = node

    def getCachedResult(self,rule):
        node = None
        n = self.pos
        if (n not in self.cache):
            return [False, None]
        
        if rule in self.cache[n]:
            node = self.cache[n][rule]
            return [True, node]
        return [False, None]
    
    def __str__(self):
        k = len(self.inputs)
        return "ParserState pos: %s , len: %s" % (self.pos, k)
    
"""
================================================================================
                            RULES CLASS
        All the following classes derive from the Rule base class.
        Each one should implement the internalMatch method.
================================================================================
"""

class Rule(object):

    def __init__(self, rules = None):
        self.children = []
        self._name = 'no_name'
        self.is_reccursive = False

        if rules is None:
            self.children = []    
        elif isinstance(rules, (list, tuple)):
            self.children = rules
        else:
            self.children.append(rules)

    # Operator overloading
    def __add__(self, other):
        return Grammar.Seq([self, other ])

    def __radd__(self, other):
        return Grammar.Seq([self,other])

    def __div__(self, other):
        return Grammar.Seq([self, other ])

    def __or__(self, other):
        return Grammar.Choice([self, other])

    def __ror__(self, other):
        return Grammar.Choice([self,other ])

    # Getters & Setters  
    @property
    def name(self):
        return self._name
 
    @name.setter
    def name(self,nom):
        self._name = nom
    
    def SetName(self,nom):
        self._name = nom
        return self

    @property
    def child(self):
        if len(self.children) > 0:
            return self.children[0]
        else:
            return None
    
    def callAction(self,param):
        if self.action:
            self.action.match(param)
        else:
            return

    def childInString(self):
        res = ''
        for c in self.children:
            res += "%s, "%c
        return res
    
    def internalMatch(self,something):
        # to be overwritten
        print "internalMatch To Be implemented"
    
    def matchTest(self,something):
        res  = self.match(something)
        truc = self #children[0]
        return "Matching %s against '%s' ===> %s" % (truc, something,res)

    def match(self,something):
        # Determine wether something is a state or an input string
        if isinstance(something, basestring):
            # It is a string so we build a ParserState from it
            # and then call match again with it
            #print "Something is a string : '%s'" %(something)
            thestate = ParserState(something,0)
            return self.match(thestate)
        else:
            # Assumed something is a state
            #print "Something is %s" %(something)
            return self.internalMatch(something)

    def parse(self,input):
        thestate = ParserState(input,0)
        res = self.match(thestate)

        #print "RESULT IS '%s'"  % (res)

        if (not res):
            print "Rule %s failed to match" % (self.name)
        
        return thestate.nodes

    # def __add__(self,other):
    #     return Grammar().Seq(other)
    
    # def __div__(self,other):
    #     return Grammar().Choice(other)
    
    def __str__(self):
        return 'Rule Generic'

    def __repr__(self):
        return "%s" % (self.name)

"""
================================================================================
                            DERIVED RULES CLASSES
================================================================================
"""

class AtRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        old = thestate.clone()
        result = self.child.match(thestate)
        thestate.assign(old)
        return result
    
    def __str__(self):
        return "At: %s"%(self.name)
    
class NotRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        old = thestate.clone()
        if self.child.match(thestate):
            thestate.assign(old)
            return False
        
        return True
    
    def __str__(self):
        child = self.child
        return "Not: %s"%(child)
    
class NodeRule(Rule):

    def __init__(self, rules):
        Rule.__init__(self, rules)
        self._name = 'NodeRule'
        self.useCache = True #False #True

    def internalMatch(self,thestate):
        if self.useCache:
            return self.internalMatchWithCaching(thestate)
        else:
            return self.internalMatchWithoutCaching(thestate)       
    
    def internalMatchWithCaching(self,thestate):
        start = thestate.pos
        # Remember getCachedResult returns a tuple [a,b]
        # a is a bool, b is a Node (or None)
        res, node  = thestate.getCachedResult(self)

        # Check if the result has been cached to eventually retrieve it
        if res:
            if node == None:
                return False
            thestate.pos = node.theend
            thestate.nodes.append(node)
            return True
        
        # Result has not been cached
        node = Node(thestate.pos, self.name, thestate.inputs)
        oldNodes = thestate.nodes
        thestate.nodes = []

        res = self.child.match(thestate)

        if res:
            node.theend = thestate.pos
            node.nodes  = thestate.nodes
            oldNodes.append(node)
            thestate.cacheResult(self, start, node)
            thestate.nodes = oldNodes
            return True
        else:
            thestate.nodes = oldNodes
            thestate.cacheResult(self, start, None)
            return False
   
    def internalMatchWithoutCaching(self,thestate):
        node = Node(thestate.pos, self.name, thestate.inputs)
        oldNodes = thestate.nodes
        thestate.nodes = []

        res = self.child.match(thestate)

        if res:
            node.theend = thestate.pos
            node.nodes  = thestate.nodes
            oldNodes.append(node)
            thestate.nodes = oldNodes
            return True
        else:
            thestate.nodes = oldNodes
            return False

    def __str__(self):
        c = self.child
        return "Node: %s"%(c)

class StringRule(Rule):

    def __init__(self, s):
        self.s = s
    def internalMatch(self,thestate):

        if (not thestate.inputs[thestate.pos:].startswith(self.s)):
            return False
        
        thestate.pos += len(self.s)
        return True
    
    def __str__(self):
        return "String: '%s'"%(self.s)

class ChoiceRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        old = thestate.clone()
        for r in self.children:
            if r.match(thestate):
                return True
            thestate.assign(old)
        return False

    def __str__(self):
        res = self.childInString()
        return "Choice: %s"%(res)

class SeqRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        old = thestate.clone()
        for r in self.children:
            if not r.match(thestate):
                thestate.assign(old)
                return False
        return True

    def __str__(self):
        c = self.childInString()
        return "Sequence: %s"%(c)

class OptRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        self.child.match(thestate)
        return True
    
    def __str__(self):
        c = self.childInString()
        return "Opt: %s"%(c)

class ZeroOrMoreRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        while self.child.match(thestate):
            pass
        return True

    def __str__(self):
        return "ZeroOrMore: %s"%(self.children)

class PlusRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    # Used for OneOrMore
    def internalMatch(self,thestate):
        res = self.child.match(thestate)
        if not res:
            return False
        while self.child.match(thestate):
            pass
        return True

    def __str__(self):
        c = self.childInString()
        return "Plus: %s"%(c)

class EndRule(Rule):
    def __init__(self, rules):
        Rule.__init__(self, rules)

    def internalMatch(self,thestate):
        return thestate.pos == len(thestate.inputs)
    
    def __str__(self):
        return "EndRule"

class CharRule(Rule):      
    def __init__(self, fct):
        Rule.__init__(self)
        self.predicate = fct

    def internalMatch(self,thestate):
        if thestate.pos >= len(thestate.inputs):
            return False

        a = thestate.inputs[thestate.pos]

        if not self.predicate(thestate.inputs[thestate.pos]):
            return False
        
        thestate.pos += 1
        return True  

    def __str__(self):
        return "Char: %s"%(self.predicate)

class RegexRule(Rule):
    def __init__(self, reg):
        Rule.__init__(self)
        self.reg = re.compile(reg)
        self.pat = self.reg.pattern

    def internalMatch(self,thestate):
        # try to find the given pattern at the beginning of the input
        m = self.reg.match(thestate.inputs, thestate.pos)
        #print "Regexp search gave %s" %(m)
        #if (m is None or m.start() != thestate.pos):
        if m is None or m is False: # or m.start() != thestate.pos:
            return False
        else:
            decal = len(thestate.inputs[m.start(0):m.end(0)])
            thestate.pos += decal #len(thestate.inputs[m.start(0):m.end(0)])
            return True

    def __str__(self):
        return "Regexp: %s"%(self.pat)
    
class DelayRule(Rule):
    def __init__(self):
        self.my_rule = None
        self.children = []
        self.name = "Delayed"

    def set(self,p):
        self.my_rule  = p

    def internalMatch(self,parser_state):
        if len(self.children) == 0:
            self.children.append(self.my_rule)
        return self.child.match(parser_state)

    def __str__(self):
        return "RecursiveRule2"