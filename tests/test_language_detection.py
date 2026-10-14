import pytest

from src.services.language import detect_language

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("text,expected", [
    ("Quelle était la valeur de Audit Compliance Score en 2021-03 ?", "fr"),
    ("Donnez le chiffre enregistré pour Average Lead Time", "fr"),
    ("Que dit le manuel de l'employé ?", "fr"),
    ("Résumé des risques", "fr"),
    ("Combien de clients ?", "fr"),
    ("What was Audit Compliance Score in 2021-03?", "en"),
    ("Show me the revenue forecast", "en"),
    ("Hello", "en"),
])
def test_detect_language(text, expected):
    assert detect_language(text) == expected


def test_empty_uses_default():
    assert detect_language("", default="fr") == "fr"
    assert detect_language("", default="de") == "en"
