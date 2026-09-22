"""
HU-04 — Dataset de referencia (CU-09, RF-72).

Caso sintético para detect_tokens (corre siempre). La construcción real
del dataset se corre a mano con build_reference_dataset.py: no es un
proceso automático repetible frame a frame, es una propuesta puntual
que Toto valida, así que no tiene sentido un test de regresión sobre
el video real.
"""

from pathlib import Path
import sys

import cv2
import numpy as np
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from build_reference_dataset import detect_tokens  # noqa: E402


def make_config():
    return {
        "roi": {"x": 0, "y": 0, "width": 300, "height": 200},
        "token_radius_px": {"median": 7.0, "p25": 6.0, "p75": 8.0, "n": 10},
        "ring": {"inner_px": 4.2, "outer_px": 6.3},
        "team_split": {"threshold": 150.0, "group_a": {"mean_v": 90.0, "n": 1}, "group_b": {"mean_v": 220.0, "n": 1}},
        "racing_is": "group_b",
    }


def draw_token(frame, cx, cy, v):
    # Ficha: círculo del valor V pedido, con un "dorsal" oscuro en el
    # centro que ring_median_v tiene que ignorar (igual que HU-05).
    # cv2.circle (no un cuadrado relleno) para que HoughCircles tenga
    # un borde circular real que detectar.
    cv2.circle(frame, (cx, cy), 7, (int(v), int(v), int(v)), -1)
    cv2.circle(frame, (cx, cy), 2, (20, 20, 20), -1)


def test_detect_tokens_clasifica_racing_y_rival():
    frame = np.full((200, 300, 3), (20, 60, 25), dtype=np.uint8)  # fondo tipo pasto (V=60)

    draw_token(frame, 60, 100, 90)     # oscuro -> group_a -> RIVAL (racing_is = group_b)
    draw_token(frame, 200, 100, 220)   # claro -> group_b -> RACING

    detections = detect_tokens(frame, make_config())
    teams = sorted(d["team"] for d in detections)

    assert teams == ["RACING", "RIVAL"]
    assert all(d["dorsal"] is None and d["validated"] is False for d in detections)


def test_detect_tokens_ignora_bordes_superior_e_inferior():
    frame = np.full((200, 300, 3), (30, 90, 40), dtype=np.uint8)

    draw_token(frame, 150, 5, 220)     # pegado al borde de arriba (marcador / gritos)
    draw_token(frame, 150, 195, 220)   # pegado al borde de abajo
    draw_token(frame, 150, 100, 220)   # en el medio: sí debe aparecer

    detections = detect_tokens(frame, make_config())

    assert len(detections) == 1
    assert detections[0]["y"] == pytest.approx(100, abs=3)
