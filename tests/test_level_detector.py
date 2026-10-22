"""Tests for junior / middle / senior detection."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "jobhunter_crm"))

from services.level_detector import detect_level, experience_label, required_years


@pytest.mark.parametrize("code, level", [
    ("noExperience", "junior"),
    ("between1And3", "junior"),
    ("between3And6", "middle"),
    ("moreThan6", "senior"),
])
def test_hh_experience_code_wins(code, level):
    assert detect_level("Senior Python Developer", "опыт от 10 лет", code) == level


@pytest.mark.parametrize("title, level", [
    ("Junior Python Developer", "junior"),
    ("Стажёр-аналитик", "junior"),
    ("Помощник руководителя", "junior"),
    ("Junior/Middle Frontend", "junior"),
    ("Middle React Developer", "middle"),
    ("Middle/Senior Data Scientist", "middle"),
    ("Senior Backend Engineer", "senior"),
    ("Team Lead Python", "senior"),
    ("Старший бухгалтер", "senior"),
    ("Руководитель отдела маркетинга", "senior"),
    ("Lead generation manager", "junior"),
    ("Архитектор", "junior"),
])
def test_title_keywords(title, level):
    assert detect_level(title, "") == level


@pytest.mark.parametrize("description, level", [
    ("Опыт работы от 1 года", "junior"),
    ("Требуемый опыт работы: 1–3 года", "junior"),
    ("Опыт 2 года", "junior"),
    ("опыт работы от 3 лет", "middle"),
    ("3+ years of experience with Python", "middle"),
    ("at least 5 years experience", "middle"),
    ("6+ years of commercial experience", "senior"),
    ("опыт от 7 лет", "senior"),
    ("kamida 2 yillik tajriba", "junior"),
    ("Без опыта, обучение на месте", "junior"),
    ("Мы молодая команда, работаем 10 лет на рынке", "junior"),
    ("", "junior"),
])
def test_description_experience(description, level):
    assert detect_level("Python Developer", description) == level


def test_required_years_takes_minimum():
    assert required_years("experience 3-5 years; or 2+ years of experience with Django") == 2


def test_experience_label():
    assert experience_label("Dev", "", "between1And3") == "1–3"
    assert experience_label("Dev", "опыт работы от 3 лет") == "3+"
    assert experience_label("Dev", "без опыта") == "0"
    assert experience_label("Dev", "Python Django") == ""
