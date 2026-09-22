from pathlib import Path
import json

import cv2
import numpy as np

from tracking_core import (
    X_FIELD,
    Y_FIELD,
    FIELD_WIDTH,
    FIELD_HEIGHT,
    detect_players,
    assign_tracks
)


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

video_path = (
    project_path
    / "videos"
    / "partido_prueba.mp4"
)

frame0_json_path = (
    project_path
    / "output"
    / "match"
    / "frame_0000.json"
)

match_output = (
    project_path
    / "output"
    / "match"
)

trajectory_output = (
    project_path
    / "output"
    / "trajectory_30frames.jpg"
)


match_output.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# CONFIGURACIÓN
# ==================================================

TOTAL_FRAMES = 30


# ==================================================
# LEER FRAME 0
# ==================================================

with open(
    frame0_json_path,
    "r",
    encoding="utf-8"
) as file:

    frame0_data = json.load(file)


tracks = {}

for player in frame0_data["players"]:

    track_id = player["track_id"]

    tracks[track_id] = {
        "track_id": track_id,
        "identity": player["identity"],
        "state": player["state"],
        "history": [
            {
                "frame": 0,
                "timestamp_ms": 0,
                "x": player["state"]["x"],
                "y": player["state"]["y"]
            }
        ]
    }



# ==================================================
# ABRIR VIDEO
# ==================================================

video = cv2.VideoCapture(
    str(video_path)
)

if not video.isOpened():

    raise RuntimeError(
        "No se pudo abrir el video."
    )


# ==================================================
# IMAGEN PARA TRAYECTORIAS
# ==================================================

success, first_frame = video.read()

if not success:

    raise RuntimeError(
        "No se pudo leer Frame 0."
    )


trajectory_image = first_frame[
    Y_FIELD:
    Y_FIELD + FIELD_HEIGHT,
    X_FIELD:
    X_FIELD + FIELD_WIDTH
].copy()


# ==================================================
# COLORES DE VISUALIZACIÓN
# ==================================================
#
# Solo para la imagen de debug.
#

RACING_COLOR = (
    255,
    120,
    40
)

RIVAL_COLOR = (
    40,
    180,
    255
)

GK_COLOR = (
    180,
    80,
    220
)


# ==================================================
# PROCESAR FRAMES
# ==================================================

print(
    "================================"
)

print(
    "TRACKING 30 FRAMES"
)

print(
    "================================"
)


for frame_number in range(
    1,
    TOTAL_FRAMES + 1
):

    success, frame = video.read()

    if not success:

        print(
            f"Fin del video en frame "
            f"{frame_number}"
        )

        break


    detections = detect_players(
        frame
    )


    matches = assign_tracks(
        tracks,
        detections
    )


    # ----------------------------------------------
    # Guardar estado
    # ----------------------------------------------

    new_frame_players = []


    matched_ids = set()


    for track, detection, distance in matches:

        track_id = track[
            "track_id"
        ]

        previous_x = track[
            "state"
        ]["x"]

        previous_y = track[
            "state"
        ]["y"]

        new_x = detection["x"]
        new_y = detection["y"]


        dx = (
            new_x
            - previous_x
        )

        dy = (
            new_y
            - previous_y
        )


        track["state"] = {

            "frame":
                frame_number,

            "timestamp_ms":
                frame_number
                * 1000 / 30,

            "x":
                int(new_x),

            "y":
                int(new_y),

            "radius":
                int(
                    detection[
                        "radius"
                    ]
                ),

            "dx":
                int(dx),

            "dy":
                int(dy),

            "distance":
                float(distance)

        }


        track["history"].append({

            "frame":
                frame_number,

            "timestamp_ms":
                frame_number
                * 1000 / 30,

            "x":
                int(new_x),

            "y":
                int(new_y)

        })


        matched_ids.add(
            track_id
        )


        new_frame_players.append({

            "track_id":
                track_id,

            "identity":
                track[
                    "identity"
                ],

            "state":
                track[
                    "state"
                ]

        })


    # ----------------------------------------------
    # Guardar JSON
    # ----------------------------------------------

    frame_data = {

        "match": {

            "frame":
                frame_number,

            "timestamp_ms":
                frame_number
                * 1000 / 30

        },

        "players":
            sorted(
                new_frame_players,
                key=lambda p:
                p["track_id"]
            )

    }


    frame_file = (
        match_output
        / f"frame_{frame_number:04d}.json"
    )


    with open(
        frame_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            frame_data,
            file,
            indent=4,
            ensure_ascii=False
        )


    # ----------------------------------------------
    # Log
    # ----------------------------------------------

    total_distance = sum(
        match[2]
        for match in matches
    )


    print(
        f"Frame {frame_number:02d} | "
        f"detecciones={len(detections):2d} | "
        f"matches={len(matches):2d} | "
        f"dist_total={total_distance:.2f}"
    )


video.release()


# ==================================================
# DIBUJAR TRAYECTORIAS
# ==================================================

for track_id, track in tracks.items():

    history = track["history"]

    if len(history) < 2:
        continue


    team = track[
        "identity"
    ]["team"]

    role = track[
        "identity"
    ]["role"]


    if role == "GK":

        line_color = GK_COLOR

    elif team == "RACING":

        line_color = RACING_COLOR

    else:

        line_color = RIVAL_COLOR


    for i in range(
        1,
        len(history)
    ):

        previous = history[
            i - 1
        ]

        current = history[
            i
        ]


        cv2.line(
            trajectory_image,
            (
                previous["x"]
                - X_FIELD,
                previous["y"]
                - Y_FIELD
            ),
            (
                current["x"]
                - X_FIELD,
                current["y"]
                - Y_FIELD
            ),
            line_color,
            2
        )


    # ----------------------------------------------
    # Punto final
    # ----------------------------------------------

    final = history[-1]

    final_x = (
        final["x"]
        - X_FIELD
    )

    final_y = (
        final["y"]
        - Y_FIELD
    )


    cv2.circle(
        trajectory_image,
        (
            final_x,
            final_y
        ),
        4,
        line_color,
        -1
    )


    cv2.putText(
        trajectory_image,
        str(track_id),
        (
            final_x + 5,
            final_y - 5
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        line_color,
        1
    )


# ==================================================
# GUARDAR MAPA
# ==================================================

cv2.imwrite(
    str(trajectory_output),
    trajectory_image
)


# ==================================================
# ESTADÍSTICAS FINALES
# ==================================================

track_lengths = []

for track in tracks.values():

    history = track["history"]

    total = 0

    for i in range(
        1,
        len(history)
    ):

        dx = (
            history[i]["x"]
            - history[i - 1]["x"]
        )

        dy = (
            history[i]["y"]
            - history[i - 1]["y"]
        )

        total += np.hypot(
            dx,
            dy
        )

    track_lengths.append(
        (
            track["track_id"],
            total
        )
    )


print(
    "\n================================"
)

print(
    "RESULTADO"
)

print(
    "================================"
)

print(
    f"Tracks iniciales: "
    f"{len(tracks)}"
)

print(
    f"Mapa generado:"
)

print(
    trajectory_output
)

print(
    "\nDistancia acumulada por track:"
)


for track_id, distance in sorted(
    track_lengths,
    key=lambda item: item[1],
    reverse=True
):

    identity = tracks[
        track_id
    ]["identity"]

    print(
        f"ID {track_id:02d} | "
        f"{identity['team']:6} "
        f"#{identity['number']:02d} | "
        f"{distance:.2f} px"
    )