from typing import List
from src.circuit import Circuit, Layer
from src.sumcheck import eval_multi_linear_poly
from src.gkr import random_challenge, prove, SingleClaim, verify, Transcript
from src.utils import Field


class Prover:
    circuit: Circuit

    def __init__(self, c: Circuit) -> None:
        self.circuit = c

    def prove(self, intputs: List[Field]) -> (SingleClaim, Transcript):
        c = self.circuit

        evals = c.eval(intputs)
        print("\nlayers evals")
        for l1 in evals:
            for l2 in l1:
                print(" ", l2.n, end="")
            print("")

        r = random_challenge(c.layers[-1].num_outputs)
        # evals[-1] ==> [f0(0), f0(1)], the output claim
        # output_claim ==> sum over [f0(0), f0(1)] to reduce the num of claims
        #                  by Algorithm 1. FunctionEvaluations
        output_claim_value = eval_multi_linear_poly(evals[-1], r)
        print(f"output claim: {output_claim_value.n}")
        output_claim = SingleClaim(r=r, eval=output_claim_value)

        print("== prove ==")
        (p, t) = prove(c, output_claim, evals)

        return (output_claim, t)


class Verifier:
    circuit: Circuit

    def __init__(self, c: Circuit) -> None:
        self.circuit = c

    def verify(self, inputs: List[Field], output_claim: SingleClaim, t: Transcript):
        c = self.circuit

        input_claims = verify(c, output_claim, t)
        print(f"input claims: {input_claims[0].eval.n}, {input_claims[1].eval.n}")

        for claim in input_claims:
            assert eval_multi_linear_poly(inputs, claim.r).n == claim.eval.n

        return True


def test_gkr_1layer():
    #    5       20
    #    +        *
    #  2    3   4   5

    # add(0, 0) and mul(1, 2, 3)
    layer = Layer(2, 2, [(0, 0), (0, 1)], [(1, 2, 3)])
    c = Circuit([layer])
    input = [Field(2), Field(3), Field(4), Field(5)]

    p = Prover(c)
    (claim, transcript) = p.prove(input)

    v = Verifier(c)
    v.verify(input, claim, transcript)


def test_gkr_2layers():
    #     44            22          # output claims
    #      +             *
    # l[0]   l[1]   l[2]   l[3]     # 3, 36, 42, 8
    #   +      *      +      *
    # 3  5   9   4   4   7  1  2    # input

    # add(0, 0), add(0, 1), add(2, 4), add(2, 5) and mul(1, 2, 3), mul(3, 6, 7)
    layer1 = Layer(3, 2, [(0, 0), (0, 1), (2, 4), (2, 5)], [(1, 2, 3), (3, 6, 7)])
    # add(0, 0), add(0, 1) and mul(1, 2, 3)
    layer2 = Layer(2, 1, [(0, 0), (0, 1)], [(1, 2, 3)])
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

    p = Prover(c)
    (claim, transcript) = p.prove(input)

    v = Verifier(c)
    v.verify(input, claim, transcript)
