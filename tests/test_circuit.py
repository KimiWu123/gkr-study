from src.circuit import Circuit, Layer
from src.utils import Field


def test_circuit_1layer():
    #    5       20
    #    +        *
    #  2    3   4   5
    # r = randrange(4)

    # add(0, 0) and mul(1, 2, 3)
    layer = Layer(2, 1, [(0, 0)], [(1, 2, 3)])
    c = Circuit([layer])

    input = [Field(2), Field(3), Field(4), Field(5)]
    eval = c.eval(input)
    assert eval[0] == input
    assert eval[1] == [Field(2), Field(20)]
