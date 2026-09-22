"""
HU-41 / RF-15 — Detección de tramos sin cancha.

FM24 muestra menús (Preferencias, panel de cámara, sustituciones, etc.)
sobre o en lugar de la vista de partido. Esos tramos no tienen jugadores
que trackear y hay que excluirlos del análisis, no tratarlos como
pérdidas de detección.

Método: la cancha es la única superficie grande y continua de color
verde de pasto en toda la pantalla. Un menú tapa esa superficie (fondo
oscuro de la UI) o la reduce a fragmentos chicos. Se mide, cada
`sample_every_s` segundos, qué fracción del frame es pasto; si supera
un umbral, se considera que la cancha está visible.

Es deliberadamente agnóstico a resolución y ROI: mide sobre el frame
completo, así que no depende de la calibración de HU-40. Cuando la
cancha SÍ está visible pero en otra escala, la fracción de pasto varía
poco (el pasto ocupa la mayor parte del frame en cualquiera de los
clips medidos), así que el mismo umbral sirvió en 1280×720 con y sin
panel inferior.
"""

from pathlib import Path
import argparse
import json

import cv2
import numpy as np


# Rango HSV de pasto, medido sobre partido_prueba.mp4 y los clips del
# 22/09 (con y sin panel inferior, con y sin menús). H no cambia con
# la resolución ni con el zoom; V sí varía algo con el brillo del
# stream, por eso el rango es generoso.
GRASS_HSV_LOW = (28, 90, 60)
GRASS_HSV_HIGH = (55, 255, 255)

# Fracción mínima del frame que tiene que ser pasto para considerar
# la cancha visible. Medido: con cancha, la fracción está siempre
# > 0.45; sobre un menú (fondo oscuro), < 0.05. 0.30 deja margen de
# sobra a ambos lados.
PITCH_FRACTION_THRESHOLD = 0.30

DEFAULT_SAMPLE_EVERY_S = 0.5

# Una racha de menos de esta duración no se reporta como un tramo
# propio: se funde con el vecino más largo. Evita "parpadeos" de un
# par de frames (una transición de cámara, un ícono grande en la
# esquina) que no son un menú real.
MIN_SEGMENT_S = 1.0


def classify_frame(frame):
    """Devuelve {"pitch_visible": bool, "grass_fraction": float}."""

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GRASS_HSV_LOW, GRASS_HSV_HIGH)
    fraction = float(mask.mean()) / 255

    return {
        "pitch_visible": fraction >= PITCH_FRACTION_THRESHOLD,
        "grass_fraction": round(fraction, 4)
    }


def sample_video(video_path, sample_every_s=DEFAULT_SAMPLE_EVERY_S):
    """Devuelve una lista de muestras [{"t": segundos, "pitch_visible": bool, "grass_fraction": float}]."""

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise RuntimeError(f"No se pudo abrir el video: {video_path}")

    fps = video.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(sample_every_s * fps))

    samples = []
    frame_number = 0

    while True:
        grabbed = video.grab()

        if not grabbed:
            break

        if frame_number % step == 0:
            ok, frame = video.retrieve()
            if not ok:
                break

            result = classify_frame(frame)
            samples.append({
                "t": round(frame_number / fps, 3),
                **result
            })

        frame_number += 1

    video.release()

    return samples


def samples_to_segments(samples, min_segment_s=MIN_SEGMENT_S):
    """
    Convierte muestras puntuales en tramos contiguos.

    Devuelve una lista de tramos ordenados por tiempo:
    [{"start_s", "end_s", "status": "PITCH" | "EXCLUDED"}]

    Un tramo más corto que `min_segment_s` se funde con el tramo
    anterior (mismo estado que el que venía sosteniéndose), para no
    reportar parpadeos de una o dos muestras como un tramo real.
    """

    if not samples:
        return []

    step = samples[1]["t"] - samples[0]["t"] if len(samples) > 1 else 1.0

    raw = []
    current_status = "PITCH" if samples[0]["pitch_visible"] else "EXCLUDED"
    start = samples[0]["t"]

    for sample in samples[1:]:
        status = "PITCH" if sample["pitch_visible"] else "EXCLUDED"
        if status != current_status:
            raw.append({"start_s": start, "end_s": sample["t"], "status": current_status})
            current_status = status
            start = sample["t"]

    raw.append({
        "start_s": start,
        "end_s": samples[-1]["t"] + step,
        "status": current_status
    })

    # Fundir tramos cortos con el anterior (o con el siguiente si son
    # el primero de todos).
    merged = []
    for segment in raw:
        duration = segment["end_s"] - segment["start_s"]
        if duration < min_segment_s and merged:
            merged[-1]["end_s"] = segment["end_s"]
        else:
            merged.append(dict(segment))

    # Si tras la fusión quedan dos tramos consecutivos con el mismo
    # estado (pudo pasar al absorber uno corto en el medio), unirlos.
    collapsed = [merged[0]]
    for segment in merged[1:]:
        if segment["status"] == collapsed[-1]["status"]:
            collapsed[-1]["end_s"] = segment["end_s"]
        else:
            collapsed.append(segment)

    return collapsed


def detect_pitch_segments(video_path, sample_every_s=DEFAULT_SAMPLE_EVERY_S, min_segment_s=MIN_SEGMENT_S):
    """API principal: video -> tramos PITCH/EXCLUDED."""

    samples = sample_video(video_path, sample_every_s=sample_every_s)
    segments = samples_to_segments(samples, min_segment_s=min_segment_s)

    return segments, samples


def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes}:{secs:05.2f}"


def main():
    parser = argparse.ArgumentParser(description="Detecta tramos sin cancha en un video de FM24 (HU-41 / RF-15).")
    parser.add_argument("video", type=Path)
    parser.add_argument("--sample-every", type=float, default=DEFAULT_SAMPLE_EVERY_S)
    parser.add_argument("--min-segment", type=float, default=MIN_SEGMENT_S)
    parser.add_argument("--out", type=Path, default=None, help="Ruta del JSON de salida")
    args = parser.parse_args()

    segments, samples = detect_pitch_segments(
        args.video,
        sample_every_s=args.sample_every,
        min_segment_s=args.min_segment
    )

    print(f"{args.video.name}")
    print("=" * 60)
    total = segments[-1]["end_s"] if segments else 0
    excluded_total = sum(s["end_s"] - s["start_s"] for s in segments if s["status"] == "EXCLUDED")

    for segment in segments:
        duration = segment["end_s"] - segment["start_s"]
        print(
            f"  {format_timestamp(segment['start_s'])} - {format_timestamp(segment['end_s'])} "
            f"({duration:5.1f}s)  {segment['status']}"
        )

    print("-" * 60)
    print(f"Total: {format_timestamp(total)} | Excluido: {excluded_total:.1f}s "
          f"({100 * excluded_total / total:.1f}% del video)" if total else "Sin muestras")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as file:
            json.dump({
                "video": str(args.video),
                "sample_every_s": args.sample_every,
                "min_segment_s": args.min_segment,
                "segments": segments
            }, file, indent=2, ensure_ascii=False)
        print(f"\nGuardado: {args.out}")


if __name__ == "__main__":
    main()
