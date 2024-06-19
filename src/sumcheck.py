from .utils import Field, print_list
from typing import List, Tuple


Coeff_Poly = Tuple[Field, Field, Field]


# Alg. 1 FunctionEvaluations
# A[b] * (1 - ri) + A[b + 2^(l - i)] * ri => (A[b + 2^(l - i)] - A[b]) * r + A[b]
# aka. l_i(x) = (ci - bi)x + bi,
#  reduce two evals at two points to a single eval at some pt
def fix_var(evals: List[Field], r: Field) -> List[Field]:
    ll = int(len(evals) / 2)
    for i in range(ll):
        evals[i] = (evals[2 * i + 1] - evals[2 * i]) * r + evals[2 * i]

    return evals[:ll]


def eval_multi_linear_poly(evals: List[Field], r: List[Field]) -> Field:
    assert len(evals) == (1 << len(r)), "length inconsistent between poly and r"

    # evaluate from input to output
    rl = r.copy()
    e = evals.copy()
    for ri in rl:
        e = fix_var(e, ri)
    return e[0]


# I(g,z) = eq(g,z) = \prod_{i=1}^{l}((1-gi)(1-zi) + gi*zi)
def eq_poly(g: List[Field]) -> List[Field]:
    ll = len(g)
    eq = [Field.ZERO()] * (1 << ll)

    eq[0] = Field.ONE() - g[0]
    eq[1] = g[0]
    for i in range(1, ll):
        for b in range(1 << i):
            prev = eq[b]
            shift = 1 << i
            eq[b + shift] = prev * g[i]
            eq[b] = prev - eq[b + shift]

    return eq


def eval_univar_poly(coeffs: Coeff_Poly, x: Field) -> Field:
    cs = []
    cs.append(coeffs[0])
    cs.append(coeffs[1])
    cs.append(coeffs[2])
    cs.reverse()
    eval = Field.ZERO()
    for coeff in cs:
        eval = eval * x + coeff
    return eval


def prove_sumcheck(
    num_vars: int, claim: Field, f2: List[Field], hg: List[Field], r: List[Field]
) -> (Field, List[Coeff_Poly]):

    assert len(f2) == len(hg)
    assert len(f2) == 1 << len(r)

    (f, g) = (f2.copy(), hg.copy())
    print_list(f, "f")
    print_list(g, "g")

    coeffs_in_layers = []
    for i in range(num_vars):
        sum = Field.ZERO()
        for fi, gi in zip(f, g):
            sum = sum + fi * gi
        assert sum == claim, f"{sum.n} != {claim.n}"

        coeffs = [Field.ZERO()] * 3
        # h2 * hg = (f[b](1 - ri) + f[b+2^(l-i)]) * (g[b](1 - ri) + g[b+2^(l-i)])
        # = (f[b] * g[b]) +
        #   ((f[b+2^(l-i)] - f[b]) * g[b] + (g[b+2^(l-i)] - g[b]) * f[b]) * ri +
        #   (g[b+2^(l-i)] - g[b])(f[b+2^(l-i)] - f[b]) * ri^2
        # just expand all the coefficient naively
        for b in range(int(len(f) / 2)):
            coeffs[0] = coeffs[0] + f[2 * b] * g[2 * b]
            coeffs[1] = (
                coeffs[1]
                + (f[2 * b + 1] - f[2 * b]) * g[2 * b]
                + (g[2 * b + 1] - g[2 * b]) * f[2 * b]
            )
            coeffs[2] = coeffs[2] + (f[2 * b + 1] - f[2 * b]) * (
                g[2 * b + 1] - g[2 * b]
            )
        coeffs_in_layers.append(coeffs)
        print_list(coeffs, "coeffs")

        claim = eval_univar_poly(coeffs, r[i])
        f = fix_var(f, r[i])
        g = fix_var(g, r[i])

        print_list(f, "f")
        print_list(g, "g")
        print(f"claim: {claim.n}")

    return (claim, coeffs_in_layers)


def verify_sumcheck(
    num_vars: int, claim: Field, r: List[Field], coeffs_in_layers: List[Coeff_Poly]
) -> Field:
    for i in range(num_vars):
        uni_poly = coeffs_in_layers[i]
        claim = eval_univar_poly(uni_poly, r[i])

    return claim
