"""
HU-40 — Configuración por video (RF-02, RF-03, CU-02).

Hasta ahora `tracking_core.py` tenía el ROI, el radio de ficha y el
umbral de color de Racing/Rival fijos en el código, medidos sobre
`partido_prueba.mp4`. Cada video nuevo (otro zoom, otra resolución,
otros colores de camiseta) rompía esos valores.

Este módulo mide esos parámetros automáticamente a partir del propio
video y los guarda en un archivo de configuración (JSON) que
`tracking_core.py` puede leer en lugar de usar constantes fijas.

No decide solo cuál de los dos colores es el equipo propio (Racing):
eso requiere que el usuario lo confirme una vez por video (RF-03,
CU-02), porque el mismo club puede jugar con la camiseta titular o la
alternativa según el partido.
"""

from pathlib import Path
import argparse
import json

import cv2
import numpy as np


GRASS_HSV_LOW = (28, 90, 60)
GRASS_HSV_HIGH = (55, 255, 255)

# Fracción mínima de pasto en una fila/columna para considerarla
# "dentro de la cancha". 0.5 separa bien el pasto de la UI en los
# cuatro clips medidos (720p y 1080p, con y sin panel inferior).
ROI_ROW_COL_THRESHOLD = 0.5

# Radios de anillo como fracción del radio de la ficha (HU-05). Los
# valores absolutos que funcionaron en partido_prueba.mp4 (radio
# ~7.26 px) fueron 4.5–6.5 px, es decir, ~62 %–90 % del radio.
RING_INNER_FRACTION = 0.60
RING_OUTER_FRACTION = 0.90


# ==================================================
# ROI: rectángulo de la cancha
# ==================================================

def detect_pitch_roi(frame, low=GRASS_HSV_LOW, high=GRASS_HSV_HIGH, threshold=ROI_ROW_COL_THRESHOLD):
    """
    ROI de un solo frame a partir del perfil de pasto por fila/columna.

    Más robusto que un bounding box de contornos: una franja de pasto
    angosta que se cuela desde el marcador (via el contorno) no pasa
    el umbral de "más de la mitad de la fila/columna es pasto".

    Devuelve (x, y, w, h) o None si no encuentra cancha en el frame
    (por ejemplo, un menú de FM24 de pantalla completa).
    """

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)

    row_fraction = mask.mean(axis=1) / 255
    col_fraction = mask.mean(axis=0) / 255

    def bounds(fraction):
        indices = np.where(fraction > threshold)[0]
        if indices.size == 0:
            return None
        return int(indices.min()), int(indices.max())

    y_bounds = bounds(row_fraction)
    x_bounds = bounds(col_fraction)

    if y_bounds is None or x_bounds is None:
        return None

    x1, x2 = x_bounds
    y1, y2 = y_bounds

    return (x1, y1, x2 - x1, y2 - y1)


def detect_pitch_roi_robust(video_path, num_samples=15):
    """
    ROI robusto a lo largo de todo el video: mediana de varias
    muestras espaciadas. Descarta las muestras donde no hay cancha
    (menú) o donde el ROI detectado es anormalmente chico (una
    pantalla de sustitución, una repetición con zoom) antes de tomar
    la mediana final.
    """

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise RuntimeError(f"No se pudo abrir el video: {video_path}")

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    positions = np.linspace(0, total_frames - 1, num_samples, dtype=int)

    candidates = []

    for position in positions:
        video.set(cv2.CAP_PROP_POS_FRAMES, int(position))
        ok, frame = video.read()
        if not ok:
            continue
        roi = detect_pitch_roi(frame)
        if roi is not None:
            candidates.append(roi)

    video.release()

    if not candidates:
        raise RuntimeError("No se detectó cancha en ninguna de las muestras.")

    widths = np.array([c[2] for c in candidates])
    heights = np.array([c[3] for c in candidates])
    median_w, median_h = np.median(widths), np.median(heights)

    # Descartar outliers (< 70% de la mediana): frames con la cancha
    # tapada u ocluida a medias.
    keep = [
        c for c, w, h in zip(candidates, widths, heights)
        if w >= 0.7 * median_w and h >= 0.7 * median_h
    ]

    if not keep:
        keep = candidates

    x = int(np.median([c[0] for c in keep]))
    y = int(np.median([c[1] for c in keep]))
    w = int(np.median([c[2] for c in keep]))
    h = int(np.median([c[3] for c in keep]))

    return {
        "x": x, "y": y, "width": w, "height": h,
        "samples_used": len(keep), "samples_total": len(candidates)
    }


# ==================================================
# RADIO DE FICHA
# ==================================================

def detect_token_radius(frame, roi, min_radius=3, max_radius=15):
    """Mediana del radio de Hough dentro del ROI, para calibrar minRadius/maxRadius."""

    x, y, w, h = roi["x"], roi["y"], roi["width"], roi["height"]
    field = frame[y:y + h, x:x + w]
    gray = cv2.GaussianBlur(cv2.cvtColor(field, cv2.COLOR_BGR2GRAY), (5, 5), 1)

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=int(0.7 * min_radius) + 6,
        param1=80, param2=14, minRadius=min_radius, maxRadius=max_radius
    )

    if circles is None:
        return None

    radii = circles[0][:, 2]

    return {
        "median": float(np.median(radii)),
        "p25": float(np.percentile(radii, 25)),
        "p75": float(np.percentile(radii, 75)),
        "n": int(len(radii))
    }


# ==================================================
# COLOR DE EQUIPO: separación en dos grupos
# ==================================================

def ring_median_v(value_channel, cx, cy, inner, outer):
    reach = int(np.ceil(outer))
    height, width = value_channel.shape

    x1, x2 = max(0, int(cx) - reach), min(width, int(cx) + reach + 1)
    y1, y2 = max(0, int(cy) - reach), min(height, int(cy) + reach + 1)

    if x2 <= x1 or y2 <= y1:
        return None

    ys, xs = np.mgrid[y1:y2, x1:x2]
    dist = np.hypot(xs - cx, ys - cy)
    ring = (dist >= inner) & (dist <= outer)

    if not ring.any():
        return None

    return float(np.median(value_channel[y1:y2, x1:x2][ring]))


def collect_token_v_values(video_path, roi, radius, num_frames=6):
    """Recorre varios frames, detecta círculos y mide su V de anillo."""

    x, y, w, h = roi["x"], roi["y"], roi["width"], roi["height"]
    min_r = max(2, int(radius["p25"] * 0.7))
    max_r = int(radius["p75"] * 1.4) + 1
    inner = radius["median"] * RING_INNER_FRACTION
    outer = radius["median"] * RING_OUTER_FRACTION

    video = cv2.VideoCapture(str(video_path))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    positions = np.linspace(total_frames * 0.1, total_frames * 0.9, num_frames, dtype=int)

    values = []
    debug_tokens = []

    for position in positions:
        video.set(cv2.CAP_PROP_POS_FRAMES, int(position))
        ok, frame = video.read()
        if not ok:
            continue

        field = frame[y:y + h, x:x + w]
        gray = cv2.GaussianBlur(cv2.cvtColor(field, cv2.COLOR_BGR2GRAY), (5, 5), 1)
        value_channel = cv2.cvtColor(field, cv2.COLOR_BGR2HSV)[:, :, 2]

        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1, minDist=int(min_r * 1.4) + 4,
            param1=80, param2=14, minRadius=min_r, maxRadius=max_r
        )

        if circles is None:
            continue

        for cx, cy, r in np.round(circles[0]).astype(int):
            v = ring_median_v(value_channel, cx, cy, inner, outer)
            if v is not None:
                values.append(v)
                if position == positions[0]:
                    debug_tokens.append({"x": int(cx + x), "y": int(cy + y), "r": int(r), "v": v})

    video.release()

    return values, debug_tokens


def split_two_teams(values, iterations=25):
    """
    1D k-means con k=2 sobre los valores de V. Reemplaza al umbral
    fijo (180) que HU-05 usó para partido_prueba.mp4: cada video
    puede tener sus propios dos colores de camiseta.

    Devuelve {threshold, group_a: {mean, n}, group_b: {mean, n}}.
    group_a es el de menor V (más oscuro).
    """

    values = np.array(sorted(values))

    if len(values) < 4:
        raise ValueError("Muy pocas muestras para separar dos equipos.")

    centers = np.array([np.percentile(values, 25), np.percentile(values, 75)])

    for _ in range(iterations):
        distances = np.abs(values[:, None] - centers[None, :])
        labels = distances.argmin(axis=1)
        new_centers = np.array([
            values[labels == k].mean() if np.any(labels == k) else centers[k]
            for k in (0, 1)
        ])
        if np.allclose(new_centers, centers):
            break
        centers = new_centers

    order = np.argsort(centers)
    centers = centers[order]
    labels = np.array([list(order).index(label) for label in labels])

    threshold = float((centers[0] + centers[1]) / 2)

    return {
        "threshold": threshold,
        "group_a": {"mean_v": float(centers[0]), "n": int((labels == 0).sum())},
        "group_b": {"mean_v": float(centers[1]), "n": int((labels == 1).sum())},
    }


# ==================================================
# CLI
# ==================================================

def calibrate(video_path, num_roi_samples=15, num_color_frames=6):
    roi = detect_pitch_roi_robust(video_path, num_samples=num_roi_samples)

    video = cv2.VideoCapture(str(video_path))
    mid_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT) * 0.5)
    video.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
    ok, frame = video.read()
    video.release()

    if not ok:
        raise RuntimeError("No se pudo leer un frame central para medir el radio.")

    radius = detect_token_radius(frame, roi)
    if radius is None:
        raise RuntimeError("No se detectaron fichas para medir el radio.")

    values, debug_tokens = collect_token_v_values(video_path, roi, radius, num_frames=num_color_frames)
    split = split_two_teams(values)

    return {
        "video": str(video_path),
        "roi": roi,
        "token_radius_px": radius,
        "ring": {
            "inner_px": round(radius["median"] * RING_INNER_FRACTION, 2),
            "outer_px": round(radius["median"] * RING_OUTER_FRACTION, 2)
        },
        "team_split": split,
        "racing_is": None,  # RF-03: lo confirma el usuario (ver --debug-image)
        "_debug_tokens_sample": debug_tokens
    }


def draw_debug_image(video_path, config, out_path):
    video = cv2.VideoCapture(str(video_path))
    mid_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT) * 0.5)
    video.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
    ok, frame = video.read()
    video.release()

    if not ok:
        return

    roi = config["roi"]
    threshold = config["team_split"]["threshold"]
    x, y, w, h = roi["x"], roi["y"], roi["width"], roi["height"]

    vis = frame.copy()
    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 2)

    field = frame[y:y + h, x:x + w]
    gray = cv2.GaussianBlur(cv2.cvtColor(field, cv2.COLOR_BGR2GRAY), (5, 5), 1)
    value_channel = cv2.cvtColor(field, cv2.COLOR_BGR2HSV)[:, :, 2]
    r = config["token_radius_px"]
    inner, outer = config["ring"]["inner_px"], config["ring"]["outer_px"]
    min_r = max(2, int(r["p25"] * 0.7))
    max_r = int(r["p75"] * 1.4) + 1

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=int(min_r * 1.4) + 4,
        param1=80, param2=14, minRadius=min_r, maxRadius=max_r
    )

    if circles is not None:
        for cx, cy, rr in np.round(circles[0]).astype(int):
            v = ring_median_v(value_channel, cx, cy, inner, outer)
            if v is None:
                continue
            color = (255, 120, 40) if v < threshold else (40, 180, 255)
            cv2.circle(vis, (cx + x, cy + y), rr + 2, color, 2)

    cv2.imwrite(str(out_path), vis)


def main():
    parser = argparse.ArgumentParser(description="Calibra ROI, radio de ficha y color de equipo para un video (HU-40).")
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--debug-image", type=Path, default=None)
    args = parser.parse_args()

    config = calibrate(args.video)
    config.pop("_debug_tokens_sample", None)

    print(json.dumps(config, indent=2, ensure_ascii=False))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2, ensure_ascii=False)
        print(f"\nGuardado: {args.out}")

    if args.debug_image:
        args.debug_image.parent.mkdir(parents=True, exist_ok=True)
        draw_debug_image(args.video, config, args.debug_image)
        print(f"Imagen de verificación: {args.debug_image}")


if __name__ == "__main__":
    main()
