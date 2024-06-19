from typing import List, Tuple
from .utils import Field


class Layer:
    num_inputs: int
    num_outputs: int
    #  add_i(z, x)
    adds: List[Tuple[int, int]]
    #  mul_i(z, x, y)
    muls: List[Tuple[int, int, int]]

    def __init__(
        self,
        num_inputs: int,
        num_outputs: int,
        adds: List[Tuple[int, int]],
        muls: List[Tuple[int, int, int]],
    ) -> None:
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.adds = adds
        self.muls = muls

    def phase1_init(self, eq_r: List[Field], f3: List[Field]) -> List[Field]:
        f1_g = [Field.ZERO()] * (1 << self.num_inputs)
        for add in self.adds:
            (z, x) = (add[0], add[1])
            f1_g[x] = f1_g[x] + eq_r[z]
        for mul in self.muls:
            (z, x, y) = (mul[0], mul[1], mul[2])
            f1_g[x] = f1_g[x] + eq_r[z] * f3[y]
        return f1_g

    def phase_1_eval(self, eq_r: List[Field], eq_x: List[Field]) -> Field:
        sum = Field.ZERO()
        for add in self.adds:
            (z, x) = (add[0], add[1])
            sum += eq_r[z] * eq_x[x]
        return sum

    def phase2_init(self, eq_r: List[Field], f3: List[Field]) -> List[Field]:
        f1_g = [Field.ZERO()] * (1 << self.num_inputs)
        for mul in self.muls:
            (z, x, y) = (mul[0], mul[1], mul[2])
            f1_g[y] = f1_g[y] + eq_r[z] * f3[x]
        return f1_g


class Circuit:
    layers: List[Layer]

    def __init__(self, layers: List[Layer]) -> None:
        self.layers = layers

    def num_inputs(self) -> int:
        return self.layers[0].num_inputs

    def num_outputs(self) -> int:
        return self.layers[len(self.layers) - 1].num_outputs

    # Eq.2 V_i(g) = sum(add_{i+1}(V{i+1}(x)) + multi_{i+1}(V{i+1}(x) * V{i+1}(y)))
    def eval(self, input: List[Field]) -> List[List]:
        assert len(input) == (1 << self.layers[0].num_inputs), "invalid len of inputs"

        evals = []
        evals.append(input)
        for layer in self.layers:
            # input comes from previous output
            input = evals[-1]
            output = [Field(0)] * (1 << layer.num_outputs)
            for add in layer.adds:
                output[add[0]] = output[add[0]] + input[add[1]]
            for mul in layer.muls:
                output[mul[0]] = output[mul[0]] + input[mul[1]] * input[mul[2]]
            evals.append(output)
        return evals
