from typing import List


class Field:
    n: int
    modulus = (
        # 52435875175126190479447740508185965837690552500527637822603658699938581184513
        8191
    )

    @classmethod
    def ZERO(cls):
        return Field(0)

    @classmethod
    def ONE(cls):
        return Field(1)

    def __init__(self, n: int) -> None:
        self.n = n % Field.modulus

    def __add__(self, b):
        return Field((self.n + b.n) % Field.modulus)

    def __sub__(self, b):
        return Field((self.n - b.n) % Field.modulus)

    def __mul__(self, b):
        return Field((self.n * b.n) % Field.modulus)

    def __eq__(self, b):
        return self.n == b.n


def print_list(list: List[Field], name: str):
    print(name, ": [", end=" ")
    for c in list:
        print(c.n, end=", ")
    print("]")
