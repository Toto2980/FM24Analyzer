"""
Lógica compartida de detección y asociación.

Extraída tal cual de batch_tracker.py para que otros scripts
(auditoría, pruebas) usen exactamente el mismo comportamiento.
"""

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment


# ==================================================
# CONFIGURACIÓN
# ==================================================

X_FIELD = 183
Y_FIELD = 48

FIELD_WIDTH = 913
FIELD_HEIGHT = 623

MAX_DISTANCE = 15.0
LARGE_COST = 10000.0

# Clasificación de equipo (HU-05). Radios en px, medidos con el
# zoom de partido_prueba.mp4 (fichas de radio 7–8 px).
RING_INNER = 4.5
RING_OUTER = 6.5
TEAM_V_THRESHOLD = 180


# ==================================================
# DETECTOR
# ==================================================

def ring_median_v(value, cx, cy):
    """Mediana de V en el anillo RING_INNER–RING_OUTER alrededor de (cx, cy)."""

    reach = int(np.ceil(RING_OUTER))
    height, width = value.shape

    x1, x2 = max(0, int(cx) - reach), min(width, int(cx) + reach + 1)
    y1, y2 = max(0, int(cy) - reach), min(height, int(cy) + reach + 1)

    ys, xs = np.mgrid[y1:y2, x1:x2]
    dist = np.hypot(xs - cx, ys - cy)
    ring = (dist >= RING_INNER) & (dist <= RING_OUTER)

    return np.median(value[y1:y2, x1:x2][ring])


def detect_players(frame):

    field = frame[
        Y_FIELD:
        Y_FIELD + FIELD_HEIGHT,
        X_FIELD:
        X_FIELD + FIELD_WIDTH
    ]

    gray = cv2.cvtColor(
        field,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (9, 9),
        2
    )

    hsv = cv2.cvtColor(
        field,
        cv2.COLOR_BGR2HSV
    )

    value = hsv[:, :, 2]


    # --------------------------------------------------
    # DETECCIÓN NORMAL
    # --------------------------------------------------

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=80,
        param2=18,
        minRadius=6,
        maxRadius=10
    )

    detections = []


    if circles is not None:

        circles = np.round(
            circles[0]
        ).astype(int)

        for x, y, radius in circles:

            detections.append({
                "x": x + X_FIELD,
                "y": y + Y_FIELD,
                "radius": radius,
                "source": "normal"
            })


    # --------------------------------------------------
    # DETECCIÓN SENSIBLE
    # --------------------------------------------------

    sensitive = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=80,
        param2=12,
        minRadius=6,
        maxRadius=10
    )

    if sensitive is not None:

        sensitive = np.round(
            sensitive[0]
        ).astype(int)

        for x, y, radius in sensitive:

            real_x = x + X_FIELD
            real_y = y + Y_FIELD

            duplicate = False

            for detection in detections:

                distance = np.hypot(
                    real_x - detection["x"],
                    real_y - detection["y"]
                )

                if distance < 14:

                    duplicate = True
                    break

            if not duplicate:

                detections.append({
                    "x": real_x,
                    "y": real_y,
                    "radius": radius,
                    "source": "sensitive"
                })


    # --------------------------------------------------
    # DETECCIÓN DE ARQUEROS
    # --------------------------------------------------

    penalty_width = 170

    penalty_y1 = int(
        FIELD_HEIGHT * 0.25
    )

    penalty_y2 = int(
        FIELD_HEIGHT * 0.75
    )

    left_area = field[
        penalty_y1:penalty_y2,
        0:penalty_width
    ]

    right_area = field[
        penalty_y1:penalty_y2,
        FIELD_WIDTH - penalty_width:
        FIELD_WIDTH
    ]

    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )


    def detect_goalkeepers(region):

        region_gray = cv2.cvtColor(
            region,
            cv2.COLOR_BGR2GRAY
        )

        enhanced = clahe.apply(
            region_gray
        )

        enhanced = cv2.GaussianBlur(
            enhanced,
            (7, 7),
            2
        )

        circles = cv2.HoughCircles(
            enhanced,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=15,
            param1=70,
            param2=10,
            minRadius=5,
            maxRadius=11
        )

        if circles is None:
            return []

        return np.round(
            circles[0]
        ).astype(int)


    goalkeeper_candidates = []


    for x, y, radius in detect_goalkeepers(
        left_area
    ):

        goalkeeper_candidates.append({
            "x": x + X_FIELD,
            "y": y + Y_FIELD + penalty_y1,
            "radius": radius,
            "source": "goalkeeper",
            "role": "GK"
        })


    for x, y, radius in detect_goalkeepers(
        right_area
    ):

        goalkeeper_candidates.append({
            "x": (
                x
                + X_FIELD
                + FIELD_WIDTH
                - penalty_width
            ),
            "y": y + Y_FIELD + penalty_y1,
            "radius": radius,
            "source": "goalkeeper",
            "role": "GK"
        })


    # --------------------------------------------------
    # ELIMINAR DUPLICADOS DE ARQUERO
    # --------------------------------------------------

    field_detections = []

    for detection in detections:

        duplicate = False

        for goalkeeper in goalkeeper_candidates:

            distance = np.hypot(
                detection["x"]
                - goalkeeper["x"],
                detection["y"]
                - goalkeeper["y"]
            )

            if distance < 14:

                duplicate = True
                break


        if not duplicate:

            field_detections.append(
                detection
            )


    field_detections.extend(
        goalkeeper_candidates
    )


    # --------------------------------------------------
    # CLASIFICAR CAMPO
    # --------------------------------------------------

    for detection in field_detections:

        if detection.get("role") == "GK":
            continue


        # HU-05: el color se mide en un anillo que excluye el
        # dorsal. El cuadrado central caía sobre los dígitos y
        # clasificaba mal al Rival #10 (Auditoría 31 frames, §3).
        median_v = ring_median_v(
            value,
            detection["x"] - X_FIELD,
            detection["y"] - Y_FIELD
        )

        detection["team_v"] = float(median_v)

        if median_v > TEAM_V_THRESHOLD:

            detection["team"] = "RIVAL"

        else:

            detection["team"] = "RACING"


        detection["role"] = "PLAYER"


    return field_detections


# ==================================================
# ASIGNACIÓN HÚNGARA
# ==================================================

def assign_tracks(
    current_tracks,
    detections
):

    track_list = list(
        current_tracks.values()
    )


    if not track_list:
        return []


    cost_matrix = np.full(
        (
            len(track_list),
            len(detections)
        ),
        LARGE_COST,
        dtype=float
    )


    for i, track in enumerate(
        track_list
    ):

        old_x = track[
            "state"
        ]["x"]

        old_y = track[
            "state"
        ]["y"]

        team = track[
            "identity"
        ]["team"]

        role = track[
            "identity"
        ]["role"]


        for j, detection in enumerate(
            detections
        ):

            # ------------------------------------------
            # Mismo rol
            # ------------------------------------------

            if detection.get("role") != role:
                continue


            # ------------------------------------------
            # Mismo equipo
            # ------------------------------------------

            if role == "PLAYER":

                if detection.get(
                    "team"
                ) != team:

                    continue


            # ------------------------------------------
            # Distancia
            # ------------------------------------------

            distance = np.hypot(
                old_x - detection["x"],
                old_y - detection["y"]
            )


            if distance <= MAX_DISTANCE:

                cost_matrix[
                    i,
                    j
                ] = distance


    rows, cols = (
        linear_sum_assignment(
            cost_matrix
        )
    )


    matches = []

    for row, col in zip(
        rows,
        cols
    ):

        cost = cost_matrix[
            row,
            col
        ]

        if cost < LARGE_COST:

            matches.append(
                (
                    track_list[row],
                    detections[col],
                    cost
                )
            )


    return matches


# ==================================================
# LOOP DE TRACKING REUTILIZABLE
# ==================================================

def run_tracking(video_path, frame0_players, total_frames):
    """
    Reproduce el loop de batch_tracker.py sin escribir archivos.

    Devuelve una lista, un elemento por frame procesado (1..N):
    {"frame": n, "detections": int, "matches": {track_id: (x, y)}}
    """

    tracks = {
        player["track_id"]: {
            "track_id": player["track_id"],
            "identity": player["identity"],
            "state": {
                "x": player["state"]["x"],
                "y": player["state"]["y"]
            }
        }
        for player in frame0_players
    }

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise RuntimeError(f"No se pudo abrir el video: {video_path}")

    success, _ = video.read()

    if not success:
        raise RuntimeError("No se pudo leer Frame 0.")

    results = []

    for frame_number in range(1, total_frames + 1):

        success, frame = video.read()

        if not success:
            break

        detections = detect_players(frame)
        matches = assign_tracks(tracks, detections)

        frame_matches = {}

        for track, detection, _ in matches:

            track["state"] = {
                "x": int(detection["x"]),
                "y": int(detection["y"])
            }

            frame_matches[track["track_id"]] = (
                int(detection["x"]),
                int(detection["y"])
            )

        results.append({
            "frame": frame_number,
            "detections": len(detections),
            "matches": frame_matches
        })

    video.release()

    return results
