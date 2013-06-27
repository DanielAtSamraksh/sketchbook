"""
Generic 2-pass assembler.
"""

from collections import defaultdict

def assemble(assemble1, lines, env, origin=0):
    lines = list(lines)
    forward_refs = defaultdict(int)
    both = UnionDict(env, forward_refs)
    for tokens in assembler_pass(lines, both, origin):
        assemble1(tokens, both)
    unresolved = set(forward_refs) - set(env)
    if unresolved:
        raise Exception("Unresolved refs", ' '.join(sorted(unresolved)))
    return [assemble1(tokens, env) 
            for tokens in assembler_pass(lines, env, origin)]

class UnionDict(object):        # XXX rename
    def __init__(self, dict1, dict2):
        self.dict1, self.dict2 = dict1, dict2
    def __getitem__(self, key):
        try:
            return self.dict1[key]
        except KeyError:
            return self.dict2[key]
    def __setitem__(self, key, value):
        self.dict1[key] = value
    def get(self, key, default=None):
        return self.dict1.get(key, default)

def assembler_pass(lines, env, origin):
    here = origin
    for line in lines:
        label, tokens = tokenize(line)
        if label:
            if env.get(label, here) != here:
                raise Exception("Multiply-defined", label, env[label], here)
            env[label] = here
        if not tokens:
            continue
        env['__here__'] = here
        yield tokens
        here += 1

def starts_comment(string):
    return string.startswith(';')

def tokenize(line):
    tokens = line.split()
    if line[:1].isspace() or starts_comment(line):
        label = ''
    else:
        label = tokens.pop(0)
    for i, token in enumerate(tokens):
        if starts_comment(token):
            tokens = tokens[:i]
            break
    return label, tokens
