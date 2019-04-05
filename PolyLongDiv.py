# Firstly recall polynomial long division as:
#   a(x) = q(x)b(x) + r(x)
# Where of dividing a(x) by b(x) we get
#   q(x): The quotient
#   r(x): The remainder
# By using n as a modular base, coefficients in the polynomials now may
# be "reduced" into equivalent mod n minimal values.
#
# For example,
# x^3 + 4x^2 + 3x + 2 === x^2 + x^2 + 2 mod 3


from itertools import dropwhile
from copy import copy


# Instances properties:
#   ax: Dividend coefficients
#   bx: Divisor coefficients
#   qx: Quotient coefficients
#   rx: Remainder coefficients
#   n:  Modular base
class PolyModDiv:
    # Drop leading zeros helper
    # @return Pruned list, and number of zeros pruned
    @staticmethod
    def prune(coefs):
        _coefs = list(dropwhile(lambda i: not i, coefs))
        return _coefs, len(coefs)-len(_coefs)

    @staticmethod
    def reduce(coefs, n):
        return [i%n for i in coefs]

    @staticmethod
    def monic(coefs, n):
        # Naive approach!
        m, a = 1, coefs[0]
        while m < n and (a*m)%n != 1:
            m += 1
        return PolyModDiv.reduce([i*m for i in coefs], n)

    @staticmethod
    def clean(coefs, n):
        return PolyModDiv.prune(PolyModDiv.reduce(coefs, n))

    # @param ax The dividend coefficients
    # @param bx The divisor coefficients
    # @param n The modular base
    def __init__(self, ax, bx, n):
        self.original_ax = PolyModDiv.prune(ax)[0]
        self.original_bx = PolyModDiv.prune(bx)[0]
        self.ax = PolyModDiv.reduce(self.original_ax, n)
        self.bx = PolyModDiv.reduce(self.original_bx, n)
        self.n = n
        self.divide()

    def divide(self):
        n = self.n
        ax = copy(self.ax)
        bx = PolyModDiv.monic(self.bx, n)
        qx = [] # Quotient coefficients
        ds = [] # Division steps

        while len(ax) >= len(bx):
            q = ax[0] // bx[0]
            p = len(ax)-len(bx)
            for i, c in enumerate(bx):
                ax[i] -= q*c
            ax, z = PolyModDiv.clean(ax, n)
            # The objective here is not just to find the quotient and remainder
            # but to store each qb(x) and a(x) from each step of long division
            # (note that a(x) in this context is a copy and is being reduced by
            # each step until finished).
            qx += [q] + [0]*(z-1)
            ds += [([q*b for b in bx]+[0]*p, list(ax))]

        self.division_steps = ds
        self.qx = qx
        self.rx = ax

    def toTex(self):
        def coef(c, p):
            return str(c) if p == 0 or c != 1 else ''

        def power(i, p):
            return ('x'+('^'+str(p) if p != 1 else '')) if p != 0 else ''

        def term(c, i, n):
            p = n-i-1
            return coef(c, p)+power(i, p)

        def intersperse(iterable, delim):
            itr = iter(iterable)
            yield next(itr)
            for i in itr:
                yield delim
                yield i

        def convert(coefs):
            # First pass: construct term strings
            s = [(term(a, i, len(coefs)) if a else ' ') for i, a in enumerate(coefs)]
            # Second pass: insert operators (pluck negatives)
            i = 1
            while i < len(s):
                if s[i] != ' ':
                    if s[i][0] == '-':
                        s[i] = s[i][1:]
                        s.insert(i, '-')
                    else:
                        s.insert(i, '+')
                else:
                    s.insert(i, ' ')
                i += 2
            # return list(intersperse(s, '&'))
            return s

        cline = r'\cline{%d-%d}'

        ax, bx, qx, ds = self.ax, self.bx, self.qx, self.division_steps
        order = len(ax)

        lwidth, rwidth = len(bx)*2, len(ax)*2
        pad = '&'*(lwidth-1)
        ncols = lwidth+rwidth
        cbx = convert(bx)
        cax = convert(ax)
        l = len(pad) + 1
        r = l + len(cax) - 1
        sqx = pad + '&'.join(convert(qx)) + r' \\' + (cline%(l, r))
        sbxax = '&'.join(cbx[:-1]) + '&' + (r'\multicolumn{1}{R|}{%s}'%cbx[-1]) + ' & ' + '&'.join(cax) + r' \\'
        print(sqx)
        print(sbxax)
        for qbx, diff in ds:
            qbx_pad = (order-len(qbx))*2
            diff_pad = (order-len(diff))*2
            cqbx = convert(qbx)
            l = len(pad) + qbx_pad + 1
            r = l + len([c for c in cqbx if c != ' ']) - 1
            sqbx = pad + ' ' + '&'*qbx_pad + ' ' + '(-)' + '&'.join(cqbx) + r' \\' + (cline%(l, r))
            sdiff = pad + ' ' + '&'*diff_pad + ' ' + '&'.join(convert(diff)) + r' \\'
            print(sqbx)
            print(sdiff)
            # s = list(intersperse(_s, ' ')) + convert(qbx)
            # s = '& '*lpad + ' & '.join(str(x) for x in qbx)
            # print(s)

    def __str__(self):
        _division_steps = '\n'.join('    '+str(l) for l in self.division_steps)
        if _division_steps:
            _division_steps = '\n' + _division_steps
        return f'''\
original_ax={self.original_ax}
original_bx={self.original_bx}
         ax={self.ax}
         bx={self.bx}
         qx={self.qx}
         rx={self.rx}
division_steps=[{_division_steps}
]
'''


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-a', '--a-coeffs', action='store', type=int, nargs="+",
            help='coefficients of a(x)')
    parser.add_argument(
            '-b', '--b-coeffs', action='store', type=int, nargs="+",
            help='coefficients of b(x)')
    parser.add_argument('-n', action='store', type=int,
            help='modular base')
    args = parser.parse_args()

    _ax, _bx, _n = args.a_coeffs, args.b_coeffs, args.n
    p = PolyModDiv(_ax, _bx, _n)
    print(p)
