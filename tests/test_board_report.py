"""Board-ready PDF export produces a valid PDF."""
import pytest

pytest.importorskip("reportlab")


def test_board_pdf_is_a_valid_pdf():
    from src.services.board_report import generate_board_pdf
    pdf = generate_board_pdf()
    assert isinstance(pdf, (bytes, bytearray))
    assert pdf[:4] == b"%PDF"           # valid PDF header
    assert len(pdf) > 1500               # non-trivial, multi-section document
