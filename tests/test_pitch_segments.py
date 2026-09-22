"""
HU-41 / RF-15 — Detección de tramos sin cancha.

Los tests sintéticos (frames y muestras armadas a mano) corren siempre,
sin depender de ningún video. El test sobre el clip real verifica que
el detector reproduce los tramos medidos a mano el 22/09/2026 y se
salta si el video no está (no se versiona).
"""

from pathlib import Path
import sys

import numpy as np
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from detect_pitch_segments import (  # noqa: E402
    classify_frame,
    detect_pitch_segments,
    samples_to_segments,
)

VIDEO_WITH_MENU = PROJECT / "videos" / "2026-09-22 17-27-45.mp4"


def solid_color_frame(bgr, size=(200, 300)):
    frame = np.zeros((*size, 3), dtype=np.uint8)
    frame[:, :] = bgr
    return frame


# ==================================================
# classify_frame — casos sintéticos
# ==================================================

def test_frame_verde_de_pasto_se_clasifica_como_cancha():
    green = solid_color_frame((40, 160, 70))  # BGR: verde de pasto
    result = classify_frame(green)
    assert result["pitch_visible"] is True
    assert result["grass_fraction"] > 0.9


def test_frame_oscuro_de_menu_no_se_clasifica_como_cancha():
    dark_ui = solid_color_frame((30, 25, 20))  # gris/azul oscuro típico de menú
    result = classify_frame(dark_ui)
    assert result["pitch_visible"] is False
    assert result["grass_fraction"] < 0.05


def test_frame_mitad_pasto_mitad_menu():
    frame = solid_color_frame((30, 25, 20), size=(200, 300))
    frame[:, :150] = (40, 160, 70)  # mitad izquierda con pasto
    result = classify_frame(frame)
    assert 0.4 < result["grass_fraction"] < 0.6
    assert result["pitch_visible"] is True  # 0.5 > umbral 0.30


# ==================================================
# samples_to_segments — casos sintéticos
# ==================================================

def make_samples(flags, step=0.5):
    return [{"t": round(i * step, 3), "pitch_visible": f} for i, f in enumerate(flags)]


def test_un_solo_tramo_si_no_hay_menu():
    samples = make_samples([True] * 10)
    segments = samples_to_segments(samples, min_segment_s=1.0)
    assert len(segments) == 1
    assert segments[0]["status"] == "PITCH"


def test_detecta_un_tramo_excluido_en_el_medio():
    # 5s cancha, 3s menu, 5s cancha (paso 0.5s)
    samples = make_samples([True] * 10 + [False] * 6 + [True] * 10)
    segments = samples_to_segments(samples, min_segment_s=1.0)
    assert [s["status"] for s in segments] == ["PITCH", "EXCLUDED", "PITCH"]
    assert segments[1]["start_s"] == pytest.approx(5.0)
    assert segments[1]["end_s"] == pytest.approx(8.0)


def test_parpadeo_corto_se_funde_con_el_vecino():
    # una sola muestra "sin cancha" en medio de un tramo con cancha
    samples = make_samples([True] * 10 + [False] + [True] * 10)
    segments = samples_to_segments(samples, min_segment_s=1.0)
    assert len(segments) == 1
    assert segments[0]["status"] == "PITCH"


def test_tramos_no_se_solapan_y_cubren_todo():
    samples = make_samples([True] * 4 + [False] * 4 + [True] * 4 + [False] * 4)
    segments = samples_to_segments(samples, min_segment_s=1.0)
    assert segments[0]["start_s"] == 0.0
    assert segments[-1]["end_s"] == pytest.approx(len(samples) * 0.5)
    for a, b in zip(segments, segments[1:]):
        assert a["end_s"] == b["start_s"]


# ==================================================
# Sobre el clip real (se salta si falta el video)
# ==================================================

@pytest.mark.skipif(not VIDEO_WITH_MENU.exists(), reason="Falta el video (no se versiona)")
def test_detecta_el_menu_de_preferencias_del_clip_real():
    segments, _ = detect_pitch_segments(VIDEO_WITH_MENU)
    excluded = [s for s in segments if s["status"] == "EXCLUDED"]

    # Medido a mano el 22/09/2026: panel de cámara ~0:31-0:40,
    # menú de Preferencias ~1:14-2:05.
    camera_panel = next(s for s in excluded if 25 <= s["start_s"] <= 35)
    assert 35 <= camera_panel["end_s"] <= 45

    preferences_menu = next(s for s in excluded if 70 <= s["start_s"] <= 80)
    assert 120 <= preferences_menu["end_s"] <= 130
