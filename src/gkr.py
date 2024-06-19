from .circuit import Circuit
from .utils import Field, print_list
from .sumcheck import (
    eval_multi_linear_poly,
    eq_poly,
    prove_sumcheck,
    verify_sumcheck,
    Coeff_Poly,
)
from typing import List, Tuple
from dataclasses import dataclass
import random


@dataclass
class SingleClaim:
    r: List[Field]
    eval: Field


Claim = Tuple[SingleClaim, SingleClaim]
Coeff_Polys = Tuple[List[Coeff_Poly], List[Coeff_Poly]]


@dataclass
class Transcript:
    r: List[Field]
    claims_in_layers: List[Claim]
    coeffs_in_layers: List[Coeff_Polys]


def random_challenge(num: int) -> List[Field]:
    # random.seed(seed.n)
    randomness = []
    for i in range(num):
        randomness.append(Field(random.randrange(Field.modulus)))
    return randomness


def prove(
    circuit: Circuit, claim: SingleClaim, evals: List[List]
) -> (Claim, Transcript):
    output = evals.pop()
    assert len(circuit.layers) == len(evals)
    assert claim.eval.n == eval_multi_linear_poly(output, claim.r).n

    claims = [claim]
    circuit.layers.reverse()
    evals.reverse()
    claims_in_layers = []
    coeffs_in_layers = []
    r = []
    for layer, input in zip(circuit.layers, evals):
        num_vars = layer.num_inputs

        # reduce the claims
        if len(claims) == 1:
            (claimed_output, eq_r) = (claims[0].eval, eq_poly(claims[0].r))
        else:
            # rlc two claims into one
            challenges = random_challenge(2)
            r.extend(challenges)
            claimed_output = (
                claims[0].eval * challenges[0] + claims[1].eval * challenges[1]
            )
            eq_r0 = eq_poly(claims[0].r)
            eq_r1 = eq_poly(claims[1].r)
            eq_r = []  # [0] * len(eq_r0)
            for eq0, eq1 in zip(eq_r0, eq_r1):
                eq_r.append(eq0 * challenges[0] + eq1 * challenges[1])

        # phase 1
        print("-- phase 1 --")
        print_list(input, "input")
        print_list(eq_r, "eq_r")
        hg_x = layer.phase1_init(eq_r, input)
        rx = random_challenge(num_vars)
        r.extend(rx)
        print_list(rx, "rx")
        (claim_x, coeffs_x_in_layers) = prove_sumcheck(
            num_vars, claimed_output, input, hg_x, rx
        )
        input_x = eval_multi_linear_poly(input, rx)
        print(f"input_x: {input_x.n}")

        eq_x = []
        for eq in eq_poly(rx):
            eq_x.append(input_x * eq)

        # phase 2
        print("-- phase 2 --")
        print_list(eq_x, "eq_x")
        print_list(eq_r, "eq_r")
        hg_y = layer.phase2_init(eq_r, eq_x)

        claim_y = claim_x - layer.phase_1_eval(eq_r, eq_x)
        print("claim_y ", claim_y.n)
        ry = random_challenge(num_vars)
        r.extend(ry)
        (claim, coeffs_y_in_layers) = prove_sumcheck(num_vars, claim_y, input, hg_y, ry)

        input_y = eval_multi_linear_poly(input, ry)
        print("input_y ", input_y.n)

        claims = (SingleClaim(rx, input_x), SingleClaim(ry, input_y))
        claims_in_layers.append(claims)
        coeffs_in_layers.append((coeffs_x_in_layers, coeffs_y_in_layers))

    return (claims, Transcript(r, claims_in_layers, coeffs_in_layers))


def verify(
    circuit: Circuit, output_claim: SingleClaim, transcript: Transcript
) -> Claim:

    transcript.r.reverse()
    claims = [output_claim]
    for layer, claim_in_layer, coeffs_in_layers in zip(
        circuit.layers,
        transcript.claims_in_layers,
        transcript.coeffs_in_layers,
    ):
        num_vars = layer.num_inputs

        # reduce the claims
        if len(claims) == 1:
            (claimed_output, eq_r) = (claims[0].eval, eq_poly(claims[0].r))
        else:
            # rlc two claims into one
            challenges = (transcript.r.pop(), transcript.r.pop())
            claimed_output = (
                claims[0].eval * challenges[0] + claims[1].eval * challenges[1]
            )
            eq_r0 = eq_poly(claims[0].r)
            eq_r1 = eq_poly(claims[1].r)
            eq_r = []  # [0] * len(eq_r0)
            for eq0, eq1 in zip(eq_r0, eq_r1):
                eq_r.append(eq0 * challenges[0] + eq1 * challenges[1])

        # phase 1
        rx = []
        for _ in range(num_vars):
            rx.append(transcript.r.pop())
        verify_sumcheck(num_vars, claimed_output, rx, coeffs_in_layers[0])

        eq_x = []
        input_x = claim_in_layer[0].eval
        for eq in eq_poly(rx):
            eq_x.append(input_x * eq)

        # phase 2
        ry = []
        for _ in range(num_vars):
            ry.append(transcript.r.pop())
        verify_sumcheck(num_vars, claimed_output, ry, coeffs_in_layers[1])

        eq_y = []
        input_y = claim_in_layer[1].eval
        for eq in eq_poly(ry):
            eq_y.append(input_y * eq)

        claims = (SingleClaim(rx, input_x), SingleClaim(ry, input_y))

    return claims
