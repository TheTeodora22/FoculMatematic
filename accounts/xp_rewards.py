"""Acordare XP după quiz: xp_câștigat = xp_maxim_quiz × (scor / scor_maxim)."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser

from .models import Profile


def compute_quiz_xp_reward(score: int, max_score: int, quiz_max_xp: int) -> int:
    """
    Returnează XP rotunjit (întreg, ≥ 0).
    Dacă quiz_max_xp sau max_score sunt 0, returnează 0.
    """
    if quiz_max_xp <= 0 or max_score <= 0:
        return 0
    if score <= 0:
        return 0
    if score > max_score:
        score = max_score
    return int(round(quiz_max_xp * score / max_score))


def award_quiz_xp(user: AbstractUser, score: int, max_score: int, quiz_max_xp: int) -> int:
    """
    Adaugă XP la profilul utilizatorului. Returnează cantitatea acordată (0 dacă nimic).
    Apelantul trebuie să fie deja în interiorul transaction.atomic() dacă vrei consistență cu alte scrieri.
    """
    gain = compute_quiz_xp_reward(score, max_score, quiz_max_xp)
    if gain <= 0:
        return 0
    profile = Profile.objects.select_for_update().get(user=user)
    profile.xp += gain
    profile.save()
    return gain
