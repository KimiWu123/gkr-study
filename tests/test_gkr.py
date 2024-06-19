from typing import List
from src.circuit import Circuit, Layer
from src.sumcheck import eval_multi_linear_poly
from src.gkr import random_challenge, prove, SingleClaim, verify
from src.utils import Field
import random

random.seed(1234)


def test_gkr_1layer():
    #    5       20
    #    +        *
    #  2    3   4   5

    # add(0, 0) and mul(1, 2, 3)
    layer = Layer(2, 2, [(0, 0)], [(1, 2, 3)])
    c = Circuit([layer])
    input = [Field(2), Field(3), Field(4), Field(5)]

    evals = c.eval(input)
    r = random_challenge(2)
    output_claim = eval_multi_linear_poly(evals[-1], r)
    print("output_claim: {output_claim.n}")

    print("== prove ==")
    (_, t) = prove(c, SingleClaim(r=r, eval=output_claim), evals)

    print("== verify ==")
    input_claims = verify(c, SingleClaim(r=r, eval=output_claim), t)
    print(f"input claims: {input_claims[0].eval.n}, {input_claims[1].eval.n}")

    for claim in input_claims:
        assert eval_multi_linear_poly(input, claim.r).n == claim.eval.n


def test_gkr_2layers():
    #      3             8
    #      +             *
    # l[0]   l[1]   l[2]   l[3] # 3, 36, 42, 8
    #   +      *      +      *
    # 3   -  9   4  4   -  1   2

    # r = randrange(4)
    # add(0, 0), add(2, 4) and mul(1, 2, 3), mul(3, 6, 7)
    layer1 = Layer(3, 2, [(0, 0), (2, 4)], [(1, 2, 3), (3, 6, 7)])
    # add(0, 0) and mul(1, 2, 3)
    layer2 = Layer(2, 1, [(0, 0)], [(1, 2, 3)])
    c = Circuit([layer1, layer2])

    input = [
        Field(3),
        Field(5),
        Field(9),
        Field(4),
        Field(4),
        Field(7),
        Field(1),
        Field(2),
    ]

    evals = c.eval(input)
    print("\nlayers evals")
    for l1 in evals:
        for l2 in l1:
            print(" ", l2.n, end="")
        print("")

    r = random_challenge(c.layers[-1].num_outputs)
    # evals[-1] ==> [f0(0), f0(1)], the output claim
    # output_claim ==> sum over [f0(0), f0(1)] to reduce the num of claims
    #                  by Algorithm 1. FunctionEvaluations
    output_claim = eval_multi_linear_poly(evals[-1], r)
    print(f"output claim: {output_claim.n}")

    print("== prove ==")
    (p, t) = prove(c, SingleClaim(r=r, eval=output_claim), evals)

    print("== verify ==")
    input_claims = verify(c, SingleClaim(r=r, eval=output_claim), t)
    print(f"input claims: {input_claims[0].eval.n}, {input_claims[1].eval.n}")

    for claim in input_claims:
        assert eval_multi_linear_poly(input, claim.r).n == claim.eval.n
