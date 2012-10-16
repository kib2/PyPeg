#!/usr/bin/env python
# -*- coding: utf-8 -*-

class FactorEvaluator(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.inner_func = {}
        self.Values     = []
        self.Functions  = {
            "pop"    : "pop",
            "keep"   : "keep",
            "if"     : "if",
            "n"      : "n",
            "bi"     : "bi",
            "bi@"    : "bi_at",
            "even"   : "even",
            "len"    : "len",
            "sum"    : "sum",
            "reduce" : "reduce",
            "count"  : "count",
            "upper"  : "upper",
            "clear"  : "clear",
            "dup"    : "dup",
            "swap"   : "swap",
            "add"    : "add",
            "each"   : "each",
            "+"      : "add",
            "sub"    : "sub",
            "-"      : "sub",
            "mul"    : "mul",
            "*"      : "mul",
            "div"    : "div",
            "/"      : "div",
            "eq?"    : "eq",
            "="      : "eq",
            "times"  : "times",
            "gteq"   : "gteq",
            "lteq"   : "lteq",
            "abs"    : "abs",
            "."      : "println",
            'call'   : "call",
            'list'   : "list",
            'map'    : 'map'
        }

    def fct_add(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append(a + b)

    def fct_sub(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append(b - a)

    def fct_mul(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append(a * b)

    def fct_div(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append(float(b/a))

    def fct_eq(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append(a == b)

    def fct_gteq(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append(b >= a)

    def fct_lteq(self):
        a,b = self.Values.pop(), self.Values.pop()
        self.Values.append( b <= a )

    def fct_abs(self):
        x = self.Values.pop()
        self.Values.append( abs(x) )

    def fct_println(self):
        x = self.Values.pop()
        self.Values.append(x)

    def fct_pop(self):
        self.Values.pop()
    
    def fct_call(self):
        quotation = self.Values.pop()
        #> "Quotation:",quotation.nodes[0]
        self.eval_me( quotation.nodes[0] )

    def fct_clear(self):
        self.Values = []
    
    def fct_dup(self):
        val = self.Values.pop()
        self.Values.append(val)
        self.Values.append(val)
    
    def fct_count(self):
        self.Values.append( len(self.Values) )
   
    def fct_even(self):
        val = self.Values.pop()
        self.Values.append( val % 2 )
   
    def fct_if(self):
        ffalse = self.Values.pop()
        ftrue  = self.Values.pop()
        truth  = self.Values.pop()
        if truth:
            self.Values.append(ftrue)
        else:
            self.Values.append(ffalse)
        self.fct_call()
 
    def fct_n(self):
        n = self.Values.pop()
        self.Values.append(range(n))
   
    def fct_reduce(self):
        func     = self.Values.pop()
        elements = self.Values.pop()
        results = []
        for element in elements:
            newstack = FactorEvaluator()
            newstack.eval_me(Terms.parse(func))
            if newstack.Values.pop():
                results.append(element)
        self.Values.append(results)

    def fct_swap(self):
        a = self.Values.pop()
        b = self.Values.pop()
        self.Values.append(a)
        self.Values.append(b)
    
    def fct_list(self):
        quot = self.Values.pop()
        stk  = self.Values # keep track of the old Stack

        newlist     = []
        self.Values = []

        self.eval_me(quot.nodes[0])
        for el in self.Values:
            newlist.append(el)
        stk.append(newlist)
        self.Values = stk
        stk = None
   
    def fct_map(self):
        quot    = self.Values.pop()
        thelist = self.Values.pop()
        new_list = []
        for el in thelist:
            self.Values.append( el )
            self.Values.append(quot)
            self.fct_call()
            new_list.append(self.Values.pop())
        self.Values.append(new_list)
    
    def fct_keep(self):
        self.fct_swap()
        self.fct_dup()
        last_el = self.Values.pop()
        self.fct_swap()
        self.fct_call()
        self.Values.append( last_el )

    def fct_len(self):
        k = self.Values.pop()
        self.Values.append( len(k) )

    def fct_upper(self):
        k = self.Values.pop()
        self.Values.append( k.upper() )

    def fct_sum(self):
        l = self.Values.pop()
        self.Values.append(l)
        s=0
        for el in l:
            s += el
        self.Values.append( s )

    def fct_each(self):
        # (List quot each)
        quot     = self.Values.pop()
        myList   = self.Values.pop()
        newstack = FactorEvaluator()

        for elem in myList:
            newstack.pushList([elem,quot]) # remember it is backward ?
            newstack.fct_call()
            s = newstack.Values.pop()
            self.append(s)

    def fct_times(self):
        quot   = self.Values.pop()
        ntimes = int(self.Values.pop())
        for i in range(ntimes): #[0:ntimes]:
            self.Values.append( quot )
            self.fct_call()

    def get_last(self):
        if len(self.Values) > 0:
            x = self.Values.pop()
            self.Values.append(x)
        else:
            x = "<<<EMPTY STACK>>>"
        return x

    def push(self,x):
        self.Values.append(x)
    
    def pushList(self,aList):
        for el in aList:
            self.Values.append(el)

    def fct_bi(self):
        #bi ( x p q - )  Apply p to x, then apply q to x
        q   = self.Values.pop()
        p   = self.Values.pop()
        x   = self.Values.pop()

        for elem in [p,q]:
            newstack = FactorEvaluator()
            newstack.pushList([x,elem]) # remember it is backward ?
            newstack.fct_call()
            s = newstack.Values.pop()
            self.push(s)

    def fct_bi_at(self):
        #bi ( x y quot - )  Apply quot to x, then apply quot to y
        q   = self.Values.pop()
        x   = self.Values.pop()
        y   = self.Values.pop()

        for elem in [x,y]:
            newstack = FactorEvaluator()
            newstack.pushList([elem,q]) # remember it is backward ?
            newstack.fct_call()
            s = newstack.Values.pop()
            self.push(s)
    ##  
    ## == EVALUATION == 
    ## 

    def eval_atom_entity(self,n):
        if n.label in ("Int", "Float"):
            return float(n.text())
        elif n.label in ("String"):
            return n.text()[1:-1]
        else:
            return "<<NOT EVALUATED>>"

    def eval_me(self,node):
        n = node
        options = {
            "Int"       :   self.clbck_int_push,
            "Float"     :   self.clbck_float_push,
            "String"    :   self.clbck_str_push,
            "Quotation" :   self.clbck_quot_push,
            "CList"     :   self.clbck_clist,
            "Terms"     :   self.clbck_terms,
            "Atom"      :   self.clbck_terms,
            "Term"      :   self.clbck_term,
            "Symbol"    :   self.clbck_symbol,
            "Define"    :   self.clbck_define,
            "Default"   :   self.clbck_default
            }
        ## Emulate a switch/case with the options dictionnary
        test_value = node.label
        if test_value in options.keys():
            options[node.label](n)
        else:
            options["Default"](n)

    # Callbacks
    def clbck_int_push(self,n):
        self.Values.append( int(n.text()) )

    def clbck_float_push(self,n):
        self.Values.append( float(n.text()) )

    def clbck_str_push(self,n):
        self.Values.append( n.text()[1:-1] )

    def clbck_quot_push(self,n):
        self.Values.append( n )

    def clbck_clist(self,n):
        k = []
        for el in n.getNode("CListTerms").nodes:
            conv = self.eval_atom_entity(el.nodes[0])
            k.append( conv )
        self.Values.append(k)

    def clbck_terms(self,n):
        for t in n.nodes:
            self.eval_me(t)

    def clbck_term(self,n):
        self.eval_me(n.nodes[0])

    def clbck_symbol(self,n):
        to_do = n.text()
        if to_do in self.inner_func.keys():
            self.Values.append( self.inner_func[to_do] )
            self.fct_call()
        else:
            method = getattr(self, "fct_"+ self.Functions[n.text()], None)
            if callable(method):
                return method()

    def clbck_define(self,n):
        z = n.getNode("Quotation")
        self.inner_func[ n.getNode("Symbol").text() ] = z

    def clbck_default(self,n):
        print "Cannot evaluate Node of type " + n.label
