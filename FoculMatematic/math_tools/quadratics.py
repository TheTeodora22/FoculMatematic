"""Trusted generated expressions; user strings are never parsed as code."""
import secrets

import sympy as sp

X = sp.Symbol("x")


def generate_quadratic():
    roots = secrets.SystemRandom().sample(range(-9, 10), 2)
    a = secrets.choice((-3, -2, -1, 1, 2, 3))
    poly = sp.Poly(a * (X - roots[0]) * (X - roots[1]), X)
    return [int(value) for value in poly.all_coeffs()]


def expression(coefficients):
    a, b, c = coefficients
    return sp.Integer(a) * X**2 + sp.Integer(b) * X + sp.Integer(c)


def equation_latex(coefficients):
    return sp.latex(expression(coefficients)) + " = 0"


def check_roots(coefficients, first, second):
    # Called only with bounded integers validated by the Django form.
    expected = sp.solveset(expression(coefficients), X, domain=sp.S.Reals)
    return sp.FiniteSet(sp.Integer(first), sp.Integer(second)) == expected
