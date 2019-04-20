from itertools import dropwhile
from copy import copy

# PolyModDiv class
#
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
        self.bx = PolyModDiv.monic(self.original_bx, n)
        self.n = n
        self.divide()

    def divide(self):
        n = self.n
        ax = copy(self.ax)
        bx = self.bx
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
        ds = ds if ds else [0]

        self.division_steps = ds
        self.qx = qx
        self.rx = ax

    def toTex(self):
        def coef(c, p):
            return str(c) if p == 0 or c != 1 else ''
        def power(i, p):
            return ('x'+('^'+str(p) if p != 1 else '')) if p != 0 else ''
        def term(c, i, n):
            if not c:
                return ' '
            p = n-i-1
            return coef(c, p)+power(i, p)
        def convert(coefs):
            if all(x == 0 for x in coefs):
                return ['0']
            # First pass: construct term strings
            s = [term(a, i, len(coefs)) for i, a in enumerate(coefs)]
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
            return s

        ax, bx, qx, ds = self.ax, self.bx, self.qx, self.division_steps
        order = len(ax)-1
        c_ax, c_bx, c_qx = convert(ax), convert(bx), convert(qx)
        c_bx = c_bx[:-1] + [r'\multicolumn{1}{R|}{%s}' % c_bx[-1]]
        lcols, rcols = len(c_bx), len(c_ax)
        ncols = lcols + rcols
        lpad = '&'*lcols

        def cols(sx):
            return lcols+1+(order-len(sx)+1)*2
        def pad(sx):
            return '&'*(cols(sx)-1)
        def cline(sx):
            return r'\cline{%d-%d}' % (cols(sx), ncols)

        out = lpad + '&'.join(c_qx) + r'\\' + cline(ax) + '\n'
        out += '&'.join(c_bx) + '&' + '&'.join(c_ax) + r'\\' + '\n'
        for qbx, diff in ds:
            c_qbx = convert(qbx)
            c_qbx = ['(-)' + c_qbx[0]] + c_qbx[1:]
            out += pad(qbx) + '&'.join(c_qbx) + r'\\' + cline(qbx) + '\n'
            out += pad(diff) + '&'.join(convert(diff)) + r'\\' + '\n'
        pre = r'\begin{tabular}{*{%d}{R}}' % ncols + '\n'
        post = r'\end{tabular}' + '\n'
        return pre + out + post

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
    pre = '''\
\\documentclass{standalone}
\\usepackage{amsmath}
\\usepackage{array}
\\newcolumntype{R}{>{$}r<{$}} 
\\setlength{\\tabcolsep}{2pt}
\\renewcommand{\\arraystretch}{1.5} 
\\begin{document}'''
    post = '''\
\\end{document}'''
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
    parser.add_argument('-t', '--latex', action='store_true',
            help='output formatted LaTeX')
    parser.add_argument('-T', '--standalone', action='store_true',
            help='output formatted LaTeX (standalone document)')
    args = parser.parse_args()

    _ax, _bx, _n = args.a_coeffs, args.b_coeffs, args.n
    p = PolyModDiv(_ax, _bx, _n)
    if args.latex:
        print(p.toTex())
    elif args.standalone:
        print(pre+p.toTex()+post)
    else:
        print(p)

