"""Fabrică pentru exercițiile metodei falsei ipoteze."""


def scenario(label, count, low, high, total, low_name, high_name, unit="unități", icons=("●","◆")):
    assumed=count*low; mismatch=total-assumed; unit_difference=high-low
    assert unit_difference and mismatch % unit_difference == 0
    high_count=mismatch//unit_difference; low_count=count-high_count
    assert low_count >= 0 and high_count >= 0
    return {"label":label,"count":count,"low":low,"high":high,"total":total,"low_name":low_name,"high_name":high_name,
            "unit":unit,"icons":list(icons),"assumed_total":assumed,"mismatch":mismatch,"unit_difference":unit_difference,
            "high_count":high_count,"low_count":low_count}


def exercise(text, mode, case, answers, explanation, **data):
    return {"text":text,"type":"false_hypothesis_method","format":"interactive","points":10,"explanation":explanation,
            "interactive":{"mode":mode,"scenario":case,"answers":answers,**data}}


def core_answers(case):
    return {key:case[key] for key in ("assumed_total","mismatch","unit_difference","high_count","low_count")}
