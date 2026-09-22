"""
HU-03 — Regresión sobre los frames 0–30 de partido_prueba.mp4.

Compara el tracking actual contra la línea base guardada en
output/baseline_31f/ (estado del 22/09/2026, antes de cualquier
corrección). Un cambio puede agregar matches, nunca perderlos ni
mover un jugador que la línea base ya seguía.
"""

from pathlib import Path
import json
import sys

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from tracking_core import run_tracking  # noqa: E402

VIDEO = PROJECT / "videos" / "partido_prueba.mp4"
BASELINE = PROJECT / "output" / "baseline_31f"
TOTAL_FRAMES = 30

pytestmark = pytest.mark.skipif(
    not VIDEO.exists(),
    reason="Falta videos/partido_prueba.mp4 (los videos no se versionan)"
)


def load_baseline(frame_number):
    path = BASELINE / f"frame_{frame_number:04d}.json"
    with open(path, encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture(scope="module")
def results():
    frame0 = load_baseline(0)
    return run_tracking(VIDEO, frame0["players"], TOTAL_FRAMES)


def test_procesa_los_30_frames(results):
    assert len(results) == TOTAL_FRAMES


@pytest.mark.parametrize("frame_number", range(1, TOTAL_FRAMES + 1))
def test_no_pierde_matches_de_la_linea_base(results, frame_number):
    baseline = {
        p["track_id"]: (p["state"]["x"], p["state"]["y"])
        for p in load_baseline(frame_number)["players"]
    }
    current = results[frame_number - 1]["matches"]

    perdidos = sorted(set(baseline) - set(current))
    assert not perdidos, f"frame {frame_number}: se perdieron los tracks {perdidos}"


@pytest.mark.parametrize("frame_number", range(1, TOTAL_FRAMES + 1))
def test_no_mueve_jugadores_de_la_linea_base(results, frame_number):
    baseline = {
        p["track_id"]: (p["state"]["x"], p["state"]["y"])
        for p in load_baseline(frame_number)["players"]
    }
    current = results[frame_number - 1]["matches"]

    movidos = {
        tid: (baseline[tid], current[tid])
        for tid in baseline
        if tid in current and current[tid] != baseline[tid]
    }
    assert not movidos, f"frame {frame_number}: posiciones distintas {movidos}"
