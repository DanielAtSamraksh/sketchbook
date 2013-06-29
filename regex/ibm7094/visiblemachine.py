"""
A virtual machine meant to share enough of the IBM 7094's character to
run Thompson's code in an obvious direct translation, but to be easier
to quickly explain and visually animate. So the 'machine words' are
fixed-length strings with fields holding instruction mnemonics and
decimal numbers.
"""

from assembler import assemble

## toplevel('thompson.vm.s')
#.  0 set   7 0  0   20 fetch 7 0 11   40 ifne  1 A 19   60                80             
#.  1 fetch 3 7 46   21 set   6 0  0   41 jump  4 0 11   61                81             
#.  2 store 3 7 47   22 ifeq  7 0  0   42 noop  0 0  0   62                82             
#.  3 set   3 4  0   23 jump  0 0 29   43 ifne  1 B 19   63                83             
#.  4 fetch 5 0 10   24 add   7 7 -1   44 jump  4 0 11   64                84             
#.  5 add   3 5  0   25 fetch 3 7 66   45 found 0 0  0   65                85             
#.  6 store 3 7 46   26 store 3 6 46   46                66                86             
#.  7 add   7 7  1   27 add   6 6  1   47                67                87             
#.  8 smash 7 0  0   28 jump  0 0 22   48                68                88             
#.  9 jump  0 4  2   29 fetch 3 0 36   49                69                89             
#. 10 jump  2 0  0   30 store 3 6 46   50                70                90             
#. 11 set   7 0  0   31 smash 7 0  0   51                71                91             
#. 12 set   3 4  0   32 smash 0 0 11   52                72                92             
#. 13 fetch 5 0 10   33 getch 0 0  0   53                73                93             
#. 14 add   3 5  0   34 jump  2 0 39   54                74                94             
#. 15 store 3 7 66   35 jump  0 0 46   55                75                95             
#. 16 add   7 7  1   36 jump  0 0 20   56                76                96             
#. 17 smash 7 0 11   37 smash 0 0 11   57                77                97             
#. 18 jump  0 2  1   38 jump  0 0 20   58                78                98             
#. 19 jump  0 2  1   39 noop  0 0  0   59                79                99             
#. 

def toplevel(filename):
    env = dict(('r%d'%i, i) for i in range(1, 10))
    words = assemble(assemble1, open(filename), env)
    vm = VM(words, '')
    vm.show()

def show(words):
    lines = ['%2d %s %s %s %s' % (addr, word[:5], word[5], word[6], word[7:])
             for addr, word in enumerate(words)]
    print '\n'.join(format_columns(lines, 5))

def format_columns(lines, ncols, sep='   '):
    assert lines 
    assert all(len(line) == len(lines[0]) for line in lines)
    nrows = (len(lines) + ncols-1) // ncols
    lines = list(lines)
    while len(lines) % nrows != 0:
        lines.append('')
    columns = [lines[i:i+nrows] for i in range(0, len(lines), nrows)]
    return map(sep.join, zip(*columns))

## for row in format_columns(map(str, range(10)), 3): print row
#. 0   4   8
#. 1   5   9
#. 2   6   
#. 3   7   
#. 

def assemble1(tokens, env):
    mnemonic, rest = tokens[0].lower(), ' '.join(tokens[1:])
    fields = [field.strip() or '0' for field in rest.split(',')]
    args = [eval(operand, {}, env) for operand in fields]
    if mnemonic == 'zeroes':
        assert len(args) == 1
        return [' '*9] * args[0]
    else:
        while len(args) < 3:
            args.append('0')
        assert len(args) == 3
        return ['%-5s%s%s%02s' % (mnemonic, args[0], args[1], int(args[2]))]

def put_number(vh, vn):
    vl = '%2d' % vn
    assert len(vl) == 2
    return vh + vl

def get_number(v):
    vh, vl = v[:7], v[7:]
    assert len(vl) == 2
    return vh, int(vl)

def add(u, v):
    uh, un = get_number(u)
    vh, vn = get_number(v)
    rn = (un + vn + 100) % 100
    if not uh.strip(): return put_number(vh, rl)
    if not vh.strip(): return put_number(uh, rl)
    assert False

class VM(object):

    def __init__(self, program, input_chars):
        self.pc = put_number(' '*7, 0)
        self.M = [' '*9] * 100
        self.R = [' '*9] * 10
        self.input_chars = iter(input_chars)
        for addr, value in enumerate(program):
            assert len(value) == 9
            self.store(put_number(' '*7, addr), value)

    def show(self):
        return show(self.M)

    def fetch(self, addr):
        return self.M[get_number(addr)]

    def store(self, addr, value):
        ah, an = get_number(addr)
        self.M[an] = value

    def get(self, r):
        return self.R[int(r)]

    def set(self, r, value):
        if int(r) != 0:
            self.R[int(r)] = value

    def step(self):
        insn = self.fetch(self.pc)
        self.pc = add(self.pc, put_number(' '*7, 1))
        op, r1, r2, addr = insn[:5], insn[5], insn[6], insn[7:]

        def ea():
            return add(self.get(r2), addr)

        if   op == 'fetch':
            self.set(r1, self.fetch(ea()))
        elif op == 'store':
            self.store(ea(), self.get(r1))
        elif op == 'set  ':
            self.set(r1, ea())
        elif op == 'add  ':
            self.set(r1, add(self.get(r1), ea()))
        elif op == 'jump ':
            self.set(r1, self.pc)
            self.pc = ea()
        elif op == 'ifeq ':
            value = ' '*8 + r2
            if self.get(r1) == value:
                self.pc = ' '*7 + addr
        elif op == 'ifne ':
            value = ' '*8 + r2
            if self.get(r1) != value:
                self.pc = ' '*7 + addr
        elif op == 'getch':
            ch = next(self.input_chars, None)
            if ch is None:
                assert False
            self.set(r1, ' '*8 + ch)
        elif op == 'found':
            assert False
        else:
            assert False


if __name__ == '__main__':
    import sys
    toplevel(sys.argv[1])
