"""
HU-04 — Dataset de referencia (CU-09, RF-72).

El sistema propone detecciones (posición + equipo) para un conjunto de
frames con movimiento; Toto las confirma o corrige a mano, incluido el
dorsal (que el sistema todavía no lee — no hay OCR implementado).

Usa la configuración medida por HU-40 (`calibrate_video.py`) en vez de
las constantes fijas de `tracking_core.py`, así el dataset queda atado
al clip definitivo (1920x1080) y no al clip viejo de prueba.

Salida por frame en `output/reference_dataset/<video>/`:
  - frame_XXXXX.json  → posiciones propuestas, "dorsal": null, "validated": false
  - frame_XXXXX.jpg   → frame completo con cada detección numerada, para
                         que Toto mire el dorsal en pantalla y lo complete
                         a mano en el JSON.
"""

from pathlib import Path
import argparse
import json

import cv2
import numpy as np

from calibrate_video import ring_median_v


def pick_timestamps(video_path, n, margin_s=10.0):
    """N timestamps espaciados, evitando los primeros/últimos segundos."""

    video = cv2.VideoCapture(str(video_path))
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video.release()

    duration_s = total_frames / fps
    return list(np.linspace(margin_s, duration_s - margin_s, n)), fps


def detect_tokens(frame, config):
    """Detecta fichas dentro del ROI calibrado y las clasifica por color."""

    roi = config["roi"]
    x, y, w, h = roi["x"], roi["y"], roi["width"], roi["height"]
    field = frame[y:y + h, x:x + w]

    gray = cv2.GaussianBlur(cv2.cvtColor(field, cv2.COLOR_BGR2GRAY), (5, 5), 1)
    value_channel = cv2.cvtColor(field, cv2.COLOR_BGR2HSV)[:, :, 2]

    radius = config["token_radius_px"]
    min_r = max(2, int(radius["p25"] * 0.7))
    max_r = int(radius["p75"] * 1.4) + 1
    inner, outer = config["ring"]["inner_px"], config["ring"]["outer_px"]

    threshold = config["team_split"]["threshold"]
    racing_is = config["racing_is"]
    if racing_is not in ("group_a", "group_b"):
        raise ValueError("config['racing_is'] debe ser 'group_a' o 'group_b' (confirmado por Toto)")

    # El ROI (perfil de pasto) incluye un margen de un par de filas de
    # pasto arriba/abajo de la cancha real, donde caen el marcador y la
    # barra de gritos (íconos redondos que Hough confunde con fichas).
    # Los arqueros sí pueden estar cerca del borde IZQUIERDO/DERECHO, así
    # que el margen se aplica solo en Y.
    edge_margin_y = int(radius["median"] * 6)

    detections = []
    seen = []

    for param2, source in ((18, "normal"), (12, "sensitive")):
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1, minDist=int(min_r * 1.4) + 6,
            param1=80, param2=param2, minRadius=min_r, maxRadius=max_r
        )
        if circles is None:
            continue

        for cx, cy, r in np.round(circles[0]).astype(int):
            if cy < edge_margin_y or cy > h - edge_margin_y:
                continue

            real_x, real_y = int(cx + x), int(cy + y)

            if any(np.hypot(real_x - sx, real_y - sy) < 16 for sx, sy in seen):
                continue
            seen.append((real_x, real_y))

            v = ring_median_v(value_channel, cx, cy, inner, outer)
            if v is None:
                continue

            group = "group_a" if v < threshold else "group_b"
            team = "RACING" if group == racing_is else "RIVAL"

            detections.append({
                "x": real_x, "y": real_y, "radius": int(r),
                "team_v": round(v, 1), "team": team,
                "dorsal": None, "validated": False,
            })

    detections.sort(key=lambda d: (d["team"], d["x"]))
    for i, d in enumerate(detections, start=1):
        d["index"] = i

    return detections


def draw_frame(frame, detections, roi, out_path):
    vis = frame.copy()
    x, y, w, h = roi["x"], roi["y"], roi["width"], roi["height"]
    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 1)

    for d in detections:
        color = (255, 120, 40) if d["team"] == "RACING" else (40, 180, 255)
        cv2.circle(vis, (d["x"], d["y"]), d["radius"] + 3, color, 2)
        cv2.putText(
            vis, str(d["index"]), (d["x"] - 6, d["y"] - d["radius"] - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2, cv2.LINE_AA
        )
        cv2.putText(
            vis, str(d["index"]), (d["x"] - 6, d["y"] - d["radius"] - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA
        )

    cv2.imwrite(str(out_path), vis)


def build_dataset(video_path, config_path, out_dir, n_frames=5):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))

    timestamps, fps = pick_timestamps(video_path, n_frames)

    video = cv2.VideoCapture(str(video_path))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []

    for t in timestamps:
        frame_number = int(round(t * fps))
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ok, frame = video.read()
        if not ok:
            continue

        detections = detect_tokens(frame, config)

        stem = f"frame_{frame_number:06d}"
        json_path = out_dir / f"{stem}.json"
        jpg_path = out_dir / f"{stem}.jpg"

        json_path.write_text(json.dumps({
            "video": str(video_path),
            "frame": frame_number,
            "timestamp_s": round(t, 2),
            "detections": detections,
        }, indent=2, ensure_ascii=False), encoding="utf-8")

        draw_frame(frame, detections, config["roi"], jpg_path)

        manifest.append({"frame": frame_number, "timestamp_s": round(t, 2), "n_detections": len(detections)})

    video.release()
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Propone el dataset de referencia HU-04 (CU-09) para un video calibrado.")
    parser.add_argument("video", type=Path)
    parser.add_argument("config", type=Path, help="JSON de calibración (salida de calibrate_video.py, con racing_is ya confirmado)")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--n-frames", type=int, default=5)
    args = parser.parse_args()

    out_dir = args.out or Path("output/reference_dataset") / args.video.stem
    manifest = build_dataset(args.video, args.config, out_dir, args.n_frames)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n{len(manifest)} frames propuestos en {out_dir}")


if __name__ == "__main__":
    main()
