"""
HU-40 — Configuración por video (RF-02, RF-03, CU-02).

Casos sintéticos para el ROI y la separación en dos equipos (corren
siempre). El de calibración completa corre sobre el clip definitivo
y se salta si el video no está.
"""

from pathlib import Path
import sys

import numpy as np
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from calibrate_video import (  # noqa: E402
    calibrate,
    detect_pitch_roi,
    ring_median_v,
    split_two_teams,
)

DEFINITIVE_VIDEO = PROJECT / "videos" / "2026-09-22 18-50-52.mp4"


# ==================================================
# detect_pitch_roi — casos sintéticos
# ==================================================

def frame_with_pitch(size=(400, 600), pitch_box=(50, 40, 500, 320)):
    """Frame oscuro (UI) con un rectángulo verde de pasto adentro."""

    frame = np.full((*size, 3), (25, 20, 15), dtype=np.uint8)  # UI oscura
    x, y, w, h = pitch_box
    frame[y:y + h, x:x + w] = (40, 160, 70)  # BGR verde de pasto
    return frame


def test_detecta_el_rectangulo_de_pasto():
    x, y, w, h = 50, 40, 500, 320
    frame = frame_with_pitch(pitch_box=(x, y, w, h))
    roi = detect_pitch_roi(frame)
    assert roi is not None
    rx, ry, rw, rh = roi
    # tolerancia de un par de píxeles por el umbral de fila/columna
    assert abs(rx - x) <= 2 and abs(ry - y) <= 2
    assert abs(rw - w) <= 2 and abs(rh - h) <= 2


def test_sin_pasto_no_hay_roi():
    frame = np.full((300, 400, 3), (25, 20, 15), dtype=np.uint8)  # todo UI oscura
    assert detect_pitch_roi(frame) is None


# ==================================================
# ring_median_v — caso sintético
# ==================================================

def test_ring_median_v_ignora_el_centro():
    # un cuadrado con centro oscuro (dorsal) y anillo claro (camiseta)
    value_channel = np.full((30, 30), 40, dtype=np.uint8)  # todo oscuro
    value_channel[10:20, 10:20] = 220  # anillo claro alrededor del centro (15,15)
    value_channel[13:17, 13:17] = 40  # centro oscuro (el "dorsal")

    v = ring_median_v(value_channel, cx=15, cy=15, inner=3, outer=6)
    assert v > 150  # tiene que leer el anillo claro, no el centro oscuro


# ==================================================
# split_two_teams — casos sintéticos
# ==================================================

def test_separa_dos_grupos_bien_distinguibles():
    rng = np.random.default_rng(0)
    dark = rng.normal(90, 5, 50)
    light = rng.normal(220, 5, 50)
    result = split_two_teams(list(dark) + list(light))

    assert result["group_a"]["mean_v"] < result["threshold"] < result["group_b"]["mean_v"]
    assert result["group_a"]["n"] == 50
    assert result["group_b"]["n"] == 50
    assert 90 < result["threshold"] < 220


def test_split_falla_con_muy_pocas_muestras():
    with pytest.raises(ValueError):
        split_two_teams([100, 200])


# ==================================================
# Sobre el clip definitivo (se salta si falta el video)
# ==================================================

@pytest.mark.skipif(not DEFINITIVE_VIDEO.exists(), reason="Falta el video (no se versiona)")
def test_calibracion_sobre_el_clip_definitivo():
    config = calibrate(DEFINITIVE_VIDEO)

    # cancha grande dentro de un frame 1920x1080
    assert config["roi"]["width"] > 900
    assert config["roi"]["height"] > 600

    # fichas más grandes que en los clips de zoom chico (HU-40, T-03)
    assert config["token_radius_px"]["median"] >= 6.5

    # dos equipos bien separados en color
    split = config["team_split"]
    assert split["group_b"]["mean_v"] - split["group_a"]["mean_v"] >= 80
