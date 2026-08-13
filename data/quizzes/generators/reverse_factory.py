"""Fabrică pentru exercițiile interactive ale metodei mersului invers."""


def exercise(text, mode, answers, explanation, **data):
    return {"text": text, "type": "reverse_method", "format": "interactive", "points": 10,
            "explanation": explanation, "interactive": {"mode": mode, "answers": answers, **data}}


def op(symbol, value):
    return {"op": symbol, "value": value}


def apply(value, operation):
    symbol, amount = operation["op"], operation["value"]
    if symbol == "+": return value + amount
    if symbol == "-": return value - amount
    if symbol == "*": return value * amount
    if symbol == "/":
        assert value % amount == 0
        return value // amount
    raise ValueError(symbol)


def inverse(operation):
    return op({"+":"-", "-":"+", "*":"/", "/":"*"}[operation["op"]], operation["value"])


def chain(start, operations):
    nodes = [start]
    for operation in operations:
        nodes.append(apply(nodes[-1], operation))
    inverse_operations = [inverse(operation) for operation in reversed(operations)]
    reverse_nodes = [nodes[-1]]
    for operation in inverse_operations:
        reverse_nodes.append(apply(reverse_nodes[-1], operation))
    return {"start": start, "end": nodes[-1], "operations": operations, "nodes": nodes,
            "inverse_operations": inverse_operations, "reverse_nodes": reverse_nodes}


def values_for_reverse(data):
    return {f"node:{i}": value for i, value in enumerate(data["reverse_nodes"][1:])}


def operations_for_reverse(data):
    return {f"op:{i}": f'{operation["op"]}{operation["value"]}'.replace("*", "×").replace("/", ":") for i, operation in enumerate(data["inverse_operations"])}
