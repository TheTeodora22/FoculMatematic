"""Fabrică pentru exercițiile interactive ale metodei figurative."""


def scheme(small, large, difference=0, total=None, small_label="numărul mic", large_label="numărul mare"):
    return {"small_parts": small, "large_parts": large, "difference": difference, "total": total,
            "small_label": small_label, "large_label": large_label}


def exercise(text, mode, answers, explanation, *, scheme_data=None, schemes=None, format_tag="interactive", **data):
    payload = {"mode": mode, "answers": answers, **data}
    if scheme_data is not None:
        payload["scheme"] = scheme_data
    if schemes is not None:
        payload["schemes"] = schemes
    return {"text": text, "type": "figurative_method", "format": format_tag, "points": 10,
            "explanation": explanation, "interactive": payload}


def choose_scheme(text, schemes, correct, explanation):
    return exercise(text, "choose_scheme", {"scheme": correct}, explanation, schemes=schemes)


def build_segments(text, target, answers, explanation):
    return exercise(text, "build_segments", answers, explanation, scheme_data=target)


def divide_segments(text, target, parts, explanation):
    return exercise(text, "divide_segments", {"parts": parts}, explanation, scheme_data=target, maximum=max(parts + 3, 8))


def order_steps(text, target, steps, explanation):
    return exercise(text, "order_steps", {f"position:{i}": i for i in range(len(steps))}, explanation,
                    scheme_data=target, steps=steps, display_order=list(reversed(range(len(steps)))))


def animate_difference(text, target, remaining, explanation):
    return exercise(text, "animate_difference", {"removed": target["difference"], "remaining": remaining}, explanation,
                    scheme_data=target)


def repair_scheme(text, broken, choices, correct, explanation):
    return exercise(text, "repair_scheme", {"repair": correct}, explanation, scheme_data=broken, choices=choices)


def true_false(text, target, statement, answer, explanation):
    return exercise(text, "figurative_true_false", {"answer": "true" if answer else "false"}, explanation,
                    scheme_data=target, statement=statement, format_tag="true_false")


def remainder_slider(text, target, maximum, remainder, explanation):
    return exercise(text, "remainder_slider", {"remainder": remainder}, explanation, scheme_data=target, maximum=maximum)


def no_solution(text, target, possible, explanation):
    return exercise(text, "no_solution", {"possible": "yes" if possible else "no"}, explanation,
                    scheme_data=target, note="O parte trebuie să fie număr natural.")


def benches(text, occupied, free, students_per_bench, answers, explanation):
    target = scheme(occupied, occupied, free, occupied * students_per_bench + free,
                    "bănci ocupate", "elevi")
    return exercise(text, "benches", answers, explanation, scheme_data=target, occupied=occupied, free=free,
                    students_per_bench=students_per_bench)


def equivalent_schemes(text, schemes, first, second, explanation):
    return exercise(text, "equivalent_schemes", {"first": first, "second": second}, explanation, schemes=schemes)


def full_puzzle(text, target, answers, explanation):
    return exercise(text, "full_puzzle", answers, explanation, scheme_data=target)
