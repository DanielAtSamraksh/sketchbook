"""
Monadic parser combinators, overloading Python's built-in operators.
Now the value must be a tuple -- I guess this makes it a MonadPlus.
TODO: change cons to deal in tuples instead of lists, now that it's working
TODO: error localization, stream input, memoizing
TODO: for the results use a 'tuple' type with constant-time append
TODO: read http://gbracha.blogspot.com/2007/01/parser-combinators.html
           http://en.wikibooks.org/wiki/Haskell/Understanding_arrows
           http://www.haskell.org/haskellwiki/Arrow#Parser
TODO: see if dropping 'take' can make things simpler/faster

Available operators:
# ~p +p -p p.foo repr(p)
# & / // << >> % * - + ** ^
# __and__ __div__ __floordiv__ __getattribute__ __lshift__ __mod__ __mul__ __neg__ __pos__ __pow__ __repr__ __rshift__ __sub__ __xor__

Glossary:
 s: input string
"""

import re

def parse(peg, s):
    """Return the value from peg parsing (a prefix of) s, or None on failure.
    This function is only for single-value results."""
    for (value,), rest in as_peg(peg)(s):
        return value

def the(T, x):
    assert isinstance(x, T), "%s is not a %s" % (x, T)
    return x

def as_peg(x):
    if isinstance(x, Peg):            return x
    if isinstance(x, (str, unicode)): return match(x)
    if callable(x):                   return Peg(x)
    raise ValueError("Not a peg", x)

def match(regex):
    return Peg(lambda s: [(m.groups(), s[m.end():])
                          for m in [re.match(regex, s)] if m])

class Peg:
    def __init__(self, parse_fn):
        self.__call__ = parse_fn
    def __invert__(self):
        return Peg(lambda s: [] if self(s) else [((), s)])
    def __rshift__(self, f):
        return Peg(lambda s: [[(f(*vals),), s1] for vals, s1 in self(s)])

    def __or__(self, peg):   return alt(self, as_peg(peg))
    def __ror__(self, peg):  return alt(as_peg(peg), self)
    def __add__(self, peg) : return seq(self, as_peg(peg))
    def __radd__(self, peg): return seq(as_peg(peg), self)

    def star(self):  return recur(lambda starred: cons(self, starred) | nil)
    def plus(self):  return cons(self, self.star())
    def maybe(self): return cons(self, nil) | nil

def alt(p, q): return Peg(lambda s: p(s) or q(s))

def seq(p, q):
    return take(p, lambda p_vals: take(q, lambda q_vals: give(p_vals + q_vals)))

def recur(f):
    peg = delay(lambda: f(peg))
    return peg

def delay(thunk):
    def initial_parse_fn(s):
        peg.__call__ = as_peg(thunk())
        return peg(s)
    peg = Peg(initial_parse_fn)
    return peg

# 'give' and 'take' are the monad operators usually named 'return' and 'bind'.
# E.g.: take(give(('hello',)), lambda vals: ...) binds vals to ('hello',)
def give(vals):
    return Peg(lambda s: [(the(tuple, vals), s)])
def take(peg, f):
    return Peg(lambda s: [res for vals, s1 in peg(s) for res in f(the(tuple, vals))(s1)])

def singleton(x): return (x,)

def cons(peg, rest_peg):
    return take(peg, lambda vals: take(rest_peg, lambda (rest,):
             give(singleton(list(the(tuple, vals)) + the(list, rest)))))

nil = give(singleton([]))


# Smoke test

## (as_peg(r'h(e)') + r'(.)')('hello')
#. [(('e', 'l'), 'lo')]
## (~as_peg(r'h(e)') + r'(.)')('xhello')
#. [(('x',), 'hello')]

## parse(match(r'(.)') >> singleton, 'hello')
#. ('h',)

## match(r'(.)').star()('')
#. [(([],), '')]

## parse(match(r'(.)').star(), 'hello')
#. ['h', 'e', 'l', 'l', 'o']


# Example

def make_var(v):      return v
def make_lam(v, e):   return '(lambda (%s) %s)' % (v, e)
def make_app(e1, e2): return '(%s %s)' % (e1, e2)

def test(string):
    _ = match(r'\s*')  # TODO add comments
    identifier = match(r'([A-Za-z_]\w*)\b\s*')

    V     =   identifier +_
    E     = delay(lambda: 
              V                            >> make_var
            | r'\\' +_+ V + '[.]' +_+ E    >> make_lam
            | '[(]' +_+ E + E + '[)]' +_   >> make_app)
    start =   _+ E

    return parse(start, string)

## test('x y')
#. 'x'
## test('\\x.x')
#. '(lambda (x) x)'
## test('(x   x)')
#. '(x x)'
