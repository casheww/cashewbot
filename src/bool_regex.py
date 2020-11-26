import re
from typing import List, Union


"""
Collection of helper functions for evaluating boolean algebra expressions.
"""


def commutative_combinations(exp: str) -> List[str]:
    """
    A.B == B.A
    A+B+C+D == A+B+D+C
    A+B.C+D == B.C+A+D
    """
    equivalents = [exp]
    equivalents.extend()


def double_not(exp: str) -> str:
    """
    A'' == A
    """
    return re.sub(r"['’]{2}", "", exp)


def numeric_not(exp: str) -> str:
    """
    1' == 0;  0' == 1
    """
    def check(match):
        if match.group()[0] == "0":
            return "1"
        else:
            return "0"

    after = re.sub(r"[01]['’]", check, exp)
    return after


def general_and(exp: str) -> str:
    # X.0 == 0;  X.X' == 0
    exp = re.sub(r"[A-Z01]['’]?\.0|0\.[A-Z01]['’]?|"
                 r"([A-Z])['’]\.\1|([A-Z])\.\2['’]",
                 "0",
                 exp)
    # X.1 == X
    exp = re.sub(r"1\.([A-Z])|([A-Z]['’]*)\.1",
                 lambda x: x.groups()[0] if x.groups()[0] else x.groups()[1],
                 exp)
    # X.X == X
    exp = re.sub(r"([A-Z1])\.\1([^'’]|$)",
                 lambda x: x.group()[0],
                 exp)
    # X'.X' == X'
    exp = re.sub(r"([A-Z1]['’])\.\1",
                 lambda x: x.group()[:2],
                 exp)

    return exp


def general_or(exp: str) -> str:
    # 0+0 == 0
    exp = re.sub(r"0\+0", "0", exp)
    # X+X == X
    exp = re.sub(r"([A-Z]['’]?)\+\1([^'’]|$)",
                 lambda x: x.groups()[0],
                 exp)
    # X'+X == 1;  X+1 == 1
    exp = re.sub(r"([A-Z])['’]\+\1|([A-Z])\+\2['’]|"
                 r"[A-Z01]['’]?\+1|1\+[A-Z01]['’]?",
                 "1",
                 exp)
    # X+0 == X
    exp = re.sub(r"([A-Z]['’]?)\+0|0\+([A-Z]['’]?)",
                 lambda x: x.groups()[0] if x.groups()[0] else x.groups()[1],
                 exp)
    return exp


def expansion(exp: str) -> str:
    # X.(X+Y)
    ...


checks = [double_not, numeric_not, general_and, general_or]


def _process_exp(exp: str) -> str:

    while not finished:
        finished = True

        for check in checks:
            after = check(exp)
            if exp != after:
                exp = after
                finished = False  # if one change is made, all checks need be redone

    return exp


def eval_bool_exp(exp: Union[str, re.Match]) -> str:
    if hasattr(exp, "group"):
        exp = exp.group()

    def process_wrap(match):
        contents = match.group().strip("()")
        processed_exp = _process_exp(contents)
        if processed_exp in ["0", "1"]:
            return processed_exp
        else:
            return f"({processed_exp})"

    # deepest bracket pair
    exp = re.sub(r"\([^()]*\)",
                 process_wrap,
                 exp)

    # recursive through bracket depths
    exp = re.sub(r"\(.*(\(.*\)).*\)",
                 lambda x: eval_bool_exp(x.groups()[0]),
                 exp)

    exp = _process_exp(exp)
    return exp
