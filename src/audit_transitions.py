"""
Auditoría de transiciones con matches < 22.

Reproduce exactamente el loop de batch_tracker.py (mismo detector,
misma asignación, mismo estado de tracks) y, en cada transición
imperfecta, registra qué track quedó sin match, qué detección quedó
libre y a qué distancia estaba el candidato más cercano.

Solo mide. No escribe nada en output/match.
"""

from pathlib import Path
from collections import Counter
import copy
import csv
import json

import cv2
import numpy as np

from tracking_core import (
    X_FIELD,
    Y_FIELD,
    FIELD_WIDTH,
    FIELD_HEIGHT,
    MAX_DISTANCE,
    detect_players,
    assign_tracks
)


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

video_path = project_path / "videos" / "partido_prueba.mp4"

frame0_json_path = (
    project_path / "output" / "match" / "frame_0000.json"
)

audit_output = project_path / "output" / "audit_31f"

audit_output.mkdir(parents=True, exist_ok=True)


# ==================================================
# CONFIGURACIÓN
# ==================================================

TOTAL_FRAMES = 30

# Radio hasta el que se considera "gating" una pérdida:
# el candidato del mismo bloque existe, pero fuera de MAX_DISTANCE.
GATING_RADIUS = 2 * MAX_DISTANCE

# Solo para dibujar
LOST_COLOR = (0, 0, 255)
FREE_COLOR = (0, 255, 255)
MATCH_COLOR = (0, 200, 0)


# ==================================================
# HELPERS
# ==================================================

def block_of(identity_or_detection):

    if identity_or_detection.get("role") == "GK":
        return "GK"

    return identity_or_detection.get("team")


def same_block(track, detection):

    role = track["identity"]["role"]

    if detection.get("role") != role:
        return False

    if role == "PLAYER":
        return detection.get("team") == track["identity"]["team"]

    return True


def describe_detection(detection, index, distance):

    return {
        "det_index": index,
        "x": int(detection["x"]),
        "y": int(detection["y"]),
        "radius": int(detection["radius"]),
        "source": detection["source"],
        "role": detection.get("role"),
        "team": detection.get("team"),
        "block": block_of(detection),
        "distance": round(float(distance), 2)
    }


def diagnose(track_block, nearest_same, nearest_any, same_taken):

    # Candidato válido dentro del gate, pero asignado a otro track
    if (
        nearest_same is not None
        and nearest_same["distance"] <= MAX_DISTANCE
        and same_taken
    ):
        return "CONTESTED"

    # Hay algo dentro del gate, pero de otro rol / equipo
    if (
        nearest_any is not None
        and nearest_any["distance"] <= MAX_DISTANCE
        and nearest_any["block"] != track_block
    ):
        return "WRONG_BLOCK"

    # El mismo bloque existe, pero fuera del gate
    if (
        nearest_same is not None
        and nearest_same["distance"] <= GATING_RADIUS
    ):
        return "GATING"

    return "NO_DETECTION"


# ==================================================
# ESTADO INICIAL (idéntico a batch_tracker.py)
# ==================================================

with open(frame0_json_path, "r", encoding="utf-8") as file:
    frame0_data = json.load(file)


tracks = {}

for player in frame0_data["players"]:

    track_id = player["track_id"]

    tracks[track_id] = {
        "track_id": track_id,
        "identity": player["identity"],
        "state": copy.deepcopy(player["state"])
    }


missed_streak = {track_id: 0 for track_id in tracks}


# ==================================================
# LOOP
# ==================================================

video = cv2.VideoCapture(str(video_path))

if not video.isOpened():
    raise RuntimeError("No se pudo abrir el video.")

success, _ = video.read()

if not success:
    raise RuntimeError("No se pudo leer Frame 0.")


transitions = []
loss_rows = []
match_histogram = Counter()


for frame_number in range(1, TOTAL_FRAMES + 1):

    success, frame = video.read()

    if not success:
        print(f"Fin del video en frame {frame_number}")
        break

    detections = detect_players(frame)

    # Posiciones previas: las que usó assign_tracks
    previous_state = {
        track_id: (track["state"]["x"], track["state"]["y"])
        for track_id, track in tracks.items()
    }

    matches = assign_tracks(tracks, detections)

    match_histogram[len(matches)] += 1

    matched_track_ids = set()
    taken_det = {}

    for track, detection, distance in matches:

        for j, candidate in enumerate(detections):
            if candidate is detection:
                taken_det[j] = track["track_id"]
                break

        matched_track_ids.add(track["track_id"])

    # ----------------------------------------------
    # Auditar ANTES de actualizar el estado
    # ----------------------------------------------

    lost_tracks = [
        tracks[track_id]
        for track_id in sorted(tracks)
        if track_id not in matched_track_ids
    ]

    free_indices = [
        j for j in range(len(detections)) if j not in taken_det
    ]

    if lost_tracks:

        lost_report = []

        for track in lost_tracks:

            track_id = track["track_id"]
            old_x, old_y = previous_state[track_id]

            distances = [
                float(np.hypot(old_x - d["x"], old_y - d["y"]))
                for d in detections
            ]

            nearest_any = None
            nearest_same = None
            nearest_same_index = None

            for j, detection in enumerate(detections):

                if (
                    nearest_any is None
                    or distances[j] < nearest_any["distance"]
                ):
                    nearest_any = describe_detection(
                        detection, j, distances[j]
                    )

                if same_block(track, detection) and (
                    nearest_same is None
                    or distances[j] < nearest_same["distance"]
                ):
                    nearest_same = describe_detection(
                        detection, j, distances[j]
                    )
                    nearest_same_index = j

            same_taken_by = (
                taken_det.get(nearest_same_index)
                if nearest_same_index is not None
                else None
            )

            if nearest_same is not None:
                nearest_same["taken_by_track"] = same_taken_by

            if nearest_any is not None:
                nearest_any["taken_by_track"] = taken_det.get(
                    nearest_any["det_index"]
                )

            track_block = block_of(track["identity"])

            diagnosis = diagnose(
                track_block,
                nearest_same,
                nearest_any,
                same_taken_by is not None
            )

            missed_streak[track_id] += 1

            entry = {
                "track_id": track_id,
                "team": track["identity"]["team"],
                "role": track["identity"]["role"],
                "number": track["identity"]["number"],
                "block": track_block,
                "last_x": int(old_x),
                "last_y": int(old_y),
                "missed_streak": missed_streak[track_id],
                "nearest_same_block": nearest_same,
                "nearest_any_block": nearest_any,
                "diagnosis": diagnosis
            }

            lost_report.append(entry)

            loss_rows.append({
                "frame": frame_number,
                "track_id": track_id,
                "block": track_block,
                "number": track["identity"]["number"],
                "missed_streak": missed_streak[track_id],
                "last_x": int(old_x),
                "last_y": int(old_y),
                "same_dist": (
                    nearest_same["distance"] if nearest_same else ""
                ),
                "same_source": (
                    nearest_same["source"] if nearest_same else ""
                ),
                "same_taken_by": (
                    "" if same_taken_by is None else same_taken_by
                ),
                "any_dist": (
                    nearest_any["distance"] if nearest_any else ""
                ),
                "any_block": (
                    nearest_any["block"] if nearest_any else ""
                ),
                "any_source": (
                    nearest_any["source"] if nearest_any else ""
                ),
                "diagnosis": diagnosis
            })

        # ------------------------------------------
        # Detecciones libres
        # ------------------------------------------

        free_report = []

        for j in free_indices:

            detection = detections[j]

            best_track = None
            best_distance = None

            for track_id, (tx, ty) in previous_state.items():

                distance = float(
                    np.hypot(tx - detection["x"], ty - detection["y"])
                )

                if best_distance is None or distance < best_distance:
                    best_track = track_id
                    best_distance = distance

            item = describe_detection(detection, j, best_distance)
            item["nearest_track"] = best_track
            item["nearest_track_block"] = block_of(
                tracks[best_track]["identity"]
            )
            free_report.append(item)

        transitions.append({
            "frame": frame_number,
            "detections": len(detections),
            "matches": len(matches),
            "lost_tracks": lost_report,
            "free_detections": free_report
        })

        # ------------------------------------------
        # Imagen de auditoría
        # ------------------------------------------

        image = frame[
            Y_FIELD:Y_FIELD + FIELD_HEIGHT,
            X_FIELD:X_FIELD + FIELD_WIDTH
        ].copy()

        for track, detection, _ in matches:

            cv2.circle(
                image,
                (int(detection["x"]) - X_FIELD,
                 int(detection["y"]) - Y_FIELD),
                int(detection["radius"]) + 2,
                MATCH_COLOR,
                1
            )

        for entry in lost_report:

            center = (
                entry["last_x"] - X_FIELD,
                entry["last_y"] - Y_FIELD
            )

            cv2.circle(image, center, int(MAX_DISTANCE), LOST_COLOR, 1)
            cv2.drawMarker(
                image, center, LOST_COLOR, cv2.MARKER_CROSS, 8, 2
            )
            cv2.putText(
                image,
                f"T{entry['track_id']} {entry['block']}"
                f"#{entry['number']} {entry['diagnosis']}",
                (center[0] + 10, center[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                LOST_COLOR,
                1
            )

        for item in free_report:

            center = (item["x"] - X_FIELD, item["y"] - Y_FIELD)

            cv2.circle(
                image, center, item["radius"] + 3, FREE_COLOR, 2
            )
            cv2.putText(
                image,
                f"free {item['source']} {item['block']}",
                (center[0] + 10, center[1] + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                FREE_COLOR,
                1
            )

        cv2.putText(
            image,
            f"frame {frame_number}  det={len(detections)}  "
            f"matches={len(matches)}",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )

        cv2.imwrite(
            str(audit_output / f"audit_frame_{frame_number:04d}.jpg"),
            image
        )

    # ----------------------------------------------
    # Actualizar estado (igual que batch_tracker.py)
    # ----------------------------------------------

    for track, detection, distance in matches:

        track["state"] = {
            "x": int(detection["x"]),
            "y": int(detection["y"])
        }

        missed_streak[track["track_id"]] = 0


video.release()


# ==================================================
# GUARDAR
# ==================================================

with open(
    audit_output / "audit_transitions.json", "w", encoding="utf-8"
) as file:
    json.dump(transitions, file, indent=4, ensure_ascii=False)


fields = [
    "frame", "track_id", "block", "number", "missed_streak",
    "last_x", "last_y",
    "same_dist", "same_source", "same_taken_by",
    "any_dist", "any_block", "any_source",
    "diagnosis"
]

with open(
    audit_output / "audit_summary.csv", "w", encoding="utf-8", newline=""
) as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(loss_rows)


# ==================================================
# RESUMEN
# ==================================================

print("================================")
print("AUDITORÍA 30 TRANSICIONES")
print("================================")

print("\nDistribución de matches:")
for matches_count in sorted(match_histogram, reverse=True):
    print(
        f"  {matches_count} matches → "
        f"{match_histogram[matches_count]} transiciones"
    )

print(f"\nPérdidas totales: {len(loss_rows)}")

print("\nPor bloque:")
for block, count in Counter(r["block"] for r in loss_rows).most_common():
    print(f"  {block:7} {count}")

print("\nPor diagnóstico:")
for diagnosis, count in Counter(
    r["diagnosis"] for r in loss_rows
).most_common():
    print(f"  {diagnosis:13} {count}")

print("\nPor track:")
for track_id, count in Counter(
    r["track_id"] for r in loss_rows
).most_common():
    identity = tracks[track_id]["identity"]
    frames = [r["frame"] for r in loss_rows if r["track_id"] == track_id]
    print(
        f"  T{track_id:02d} {block_of(identity):6} "
        f"#{identity['number']:02d} → {count} "
        f"(frames {frames})"
    )

print(f"\nSalida: {audit_output}")
