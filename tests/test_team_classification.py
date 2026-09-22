"""
HU-05 — Clasificación de equipo por anillo (RF-12, RNF-02).

Sobre los frames 0–30 de partido_prueba.mp4:
- toda ficha de campo se clasifica en su equipo real;
- el margen de V entre Racing y Rival es amplio (≥ 100);
- la distribución de matches es la esperada tras el arreglo.
"""

from pathlib import Path
from collections import Counter
import json
import sys

import cv2
import numpy as np
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from tracking_core import TEAM_V_THRESHOLD, detect_players, run_tracking  # noqa: E402

VIDEO = PROJECT / "videos" / "partido_prueba.mp4"
FRAME0 = PROJECT / "output" / "baseline_31f" / "frame_0000.json"

pytestmark = pytest.mark.skipif(not VIDEO.exists(), reason="Falta videos/partido_prueba.mp4")


@pytest.fixture(scope="module")
def frame0_players():
    with open(FRAME0, encoding="utf-8") as file:
        return json.load(file)["players"]


@pytest.fixture(scope="module")
def team_values(frame0_players):
    truth = [
        ((p["state"]["x"], p["state"]["y"]), p["identity"]["team"])
        for p in frame0_players
        if p["identity"]["role"] == "PLAYER"
    ]
    values = {"RACING": [], "RIVAL": []}
    errors = []
    video = cv2.VideoCapture(str(VIDEO))

    for frame_number in range(31):
        _, frame = video.read()
        for d in detect_players(frame):
            if d.get("role") != "PLAYER":
                continue
            (tx, ty), team = min(truth, key=lambda t: np.hypot(t[0][0] - d["x"], t[0][1] - d["y"]))
            if np.hypot(tx - d["x"], ty - d["y"]) > 5:
                continue
            values[team].append(d["team_v"])
            if d["team"] != team:
                errors.append((frame_number, team, d["x"], d["y"], d["team_v"]))

    video.release()
    return values, errors


def test_ninguna_ficha_mal_clasificada(team_values):
    _, errors = team_values
    assert not errors, errors


def test_margen_de_color_amplio(team_values):
    values, _ = team_values
    racing_max = max(values["RACING"])
    rival_min = min(values["RIVAL"])
    assert rival_min - racing_max >= 100
    assert racing_max < TEAM_V_THRESHOLD < rival_min


def test_distribucion_de_matches(frame0_players):
    results = run_tracking(VIDEO, frame0_players, 30)
    distribution = Counter(len(r["matches"]) for r in results)
    # Solo queda la oclusión por etiqueta de Racing #10 (frames 24–30, HU-09)
    assert distribution == {22: 23, 21: 7}
