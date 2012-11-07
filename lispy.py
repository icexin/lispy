#!/usr/bin/env python

import sys
import os
import math
import operator as op


isa = isinstance

def global_init():
    def display(*arg):
        for buffer in arg:
            print to_string(buffer)
    
    builtins = {
        '+':op.add,
        '-':op.sub,
        '*':op.mul,
        '/':op.div,
        '=':op.eq,
        'cons':lambda x, y:[x] + y if isa(y, list) else [x, y],
        'car':lambda x:x[0],
        'cdr':lambda x:x[1:],
        'list':lambda *x:list(x),
        'else':True,
        'null?':lambda x:x == [],
        'display':display
    }
	
    glo = Env()
    glo.update(vars(math))
    glo.update(vars(__builtins__))
    glo.update(builtins)
    return glo


def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

def tokenize(code):
    return code.replace('(', ' ( ').replace(')', ' ) ').split()

def listize(tokens):
    if len(tokens) == 0:
        return []
    token = tokens.pop(0)
    if token == '(':
        l = []
        while tokens[0] != ')':
            l.append(listize(tokens))
        else:
            tokens.pop(0)
            return l
    else:
        return atom(token)
    
def check(tokens):
    i = 0
    stack = 0
    while i < len(tokens):
        token = tokens[i]
        if token == '(':
            stack += 1
        elif token == ')':
            if stack == 0:
                raise SyntaxError('unbalanced left near `%s %s`' %(tokens[i-2], tokens[i-1]))
            else:
                stack -= 1
        else:
            pass
        i += 1
    if stack:
        raise SyntaxError('unbalanced right')

def parse(code):
    tokens = tokenize(code)
    check(tokens)
    
    exps = []
    while tokens:
    	exps.append(listize(tokens))
    return exps



class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer
    def find(self, var):
        if var in self:
            return self[var]
        elif self.outer is None:
            raise ValueError('%s not found' %(var))
        else:
            return self.outer.find(var)
class Exp():
    def __init__(self, env = global_init()):
        self.env = env
        
    def _quote(self, body):
        return body
    
    def _define(self, var, body):
        self.env[var] = self.eval(body)
        
    def _lambda(self, var, body):
        def closure(*arg):
            self.env = Env(var, arg, self.env)
            import pprint
            pprint.pprint(self.env)
            return self.eval(body)
        return closure
    
    def _cond(self, *pairs):
        for pair in pairs:
            (test, exp) = pair
            if self.eval(test):
                return self.eval(exp)
            
    def _if(self, test, do, alt):
        return self._cond((test, do), ('else', alt))
    
    def _delay(self, body):
        return self._lambda([], body)
    
    def _force(self, body):
        proc = self.eval(body)
        return proc()
    
    def proc(self, proc, *args):
        args = [self.eval(arg) for arg in args]
        proc = self.eval(proc)
        return proc(*args)
    
    def eval(self, exp):
        if isa(exp, str):
            return self.env.find(exp)
        if not isa(exp, list):
            return exp
    
        name = '_' + str(exp[0])
        body = exp[1:]
        if hasattr(self, name):
            return  getattr(self, name)(*body)
        else:
            proc = self.eval(exp[0])
            exps = [self.eval(exp) for exp in body]
            return proc(*exps)
        
def to_string(l):
    if isa(l, list):
        inner = [to_string(x) for x in l]
        return '(' + ' '.join(inner) + ')'
    else:
        return str(l)


def repl(prompt = 'lisp> '):
    glo = global_init()
    while True:
        code = raw_input(prompt)
        execute(code, glo)

def execute(code, glo):
    runner = Exp(glo)
    if code:
        exps = parse(code)
        while exps:
            exp = exps.pop(0)
            val = runner.eval(exp)
            if val is not None:
                print to_string(val)
	




def main():
    glo = global_init()
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if os.path.exists(name):
            code = open(name).read()
            execute(code, glo)
    else:
        repl()

if __name__ == '__main__':
    main()


