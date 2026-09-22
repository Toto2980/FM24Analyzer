from pathlib import Path
import json

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

video_path = (
    project_path
    / "videos"
    / "partido_prueba.mp4"
)

frame0_path = (
    project_path
    / "output"
    / "match"
    / "frame_0000.json"
)

output_path = (
    project_path
    / "output"
    / "match"
    / "frame_0001.json"
)

debug_path = (
    project_path
    / "output"
    / "tracking_0000_0001.jpg"
)


# ==================================================
# CONFIGURACIÓN
# ==================================================

X_FIELD = 183
Y_FIELD = 48

FIELD_WIDTH = 913
FIELD_HEIGHT = 623

MAX_DISTANCE = 15.0
LARGE_COST = 10000.0


# ==================================================
# LEER FRAME 0 + FRAME 1
# ==================================================

video = cv2.VideoCapture(
    str(video_path)
)

if not video.isOpened():
    raise RuntimeError(
        "No se pudo abrir el video."
    )

success0, frame0 = video.read()
success1, frame1 = video.read()

video.release()

if not success0 or not success1:
    raise RuntimeError(
        "No se pudieron leer los dos primeros frames."
    )


# ==================================================
# LEER JSON FRAME 0
# ==================================================

with open(
    frame0_path,
    "r",
    encoding="utf-8"
) as file:

    previous_data = json.load(file)


previous_players = (
    previous_data["players"]
)


# ==================================================
# DETECTOR DE FICHAS
# ==================================================

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

    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]


    # --------------------------------------------------
    # Hough normal
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


    normal = []

    if circles is not None:

        circles = np.round(
            circles[0]
        ).astype(int)

        for x, y, radius in circles:

            normal.append({
                "x": x + X_FIELD,
                "y": y + Y_FIELD,
                "radius": radius,
                "source": "normal"
            })


    # --------------------------------------------------
    # Hough sensible
    # --------------------------------------------------

    circles_sensitive = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=80,
        param2=12,
        minRadius=6,
        maxRadius=10
    )


    if circles_sensitive is not None:

        circles_sensitive = np.round(
            circles_sensitive[0]
        ).astype(int)

        for x, y, radius in circles_sensitive:

            duplicate = False

            for token in normal:

                distance = np.hypot(
                    x + X_FIELD - token["x"],
                    y + Y_FIELD - token["y"]
                )

                if distance < 14:
                    duplicate = True
                    break

            if not duplicate:

                normal.append({
                    "x": x + X_FIELD,
                    "y": y + Y_FIELD,
                    "radius": radius,
                    "source": "sensitive"
                })


    # --------------------------------------------------
    # Arqueros
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


    def detect_goalkeeper(region):

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


    for x, y, radius in detect_goalkeeper(
        left_area
    ):

        goalkeeper_candidates.append({
            "x": x + X_FIELD,
            "y": y + Y_FIELD + penalty_y1,
            "radius": radius,
            "source": "goalkeeper"
        })


    for x, y, radius in detect_goalkeeper(
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
            "source": "goalkeeper"
        })


    # --------------------------------------------------
    # Eliminar duplicados de arqueros
    # --------------------------------------------------

    final_tokens = []

    for token in normal:

        is_goalkeeper_duplicate = False

        for goalkeeper in goalkeeper_candidates:

            distance = np.hypot(
                token["x"] - goalkeeper["x"],
                token["y"] - goalkeeper["y"]
            )

            if distance < 14:

                is_goalkeeper_duplicate = True
                break

        if not is_goalkeeper_duplicate:
            final_tokens.append(token)


    final_tokens.extend(
        goalkeeper_candidates
    )


    # --------------------------------------------------
    # Clasificar fichas de campo
    # --------------------------------------------------

    for token in final_tokens:

        if token["source"] == "goalkeeper":

            token["role"] = "GK"
            continue


        local_x = (
            token["x"] - X_FIELD
        )

        local_y = (
            token["y"] - Y_FIELD
        )


        # Pequeña ventana alrededor del centro
        radius = token["radius"]

        x1 = max(
            0,
            int(local_x - radius * 0.5)
        )

        x2 = min(
            FIELD_WIDTH,
            int(local_x + radius * 0.5)
        )

        y1 = max(
            0,
            int(local_y - radius * 0.5)
        )

        y2 = min(
            FIELD_HEIGHT,
            int(local_y + radius * 0.5)
        )


        patch_s = saturation[
            y1:y2,
            x1:x2
        ]

        patch_v = value[
            y1:y2,
            x1:x2
        ]


        median_s = np.median(
            patch_s
        )

        median_v = np.median(
            patch_v
        )


        # Misma lógica que usamos para el frame 0
        if median_v > 180:

            token["team"] = "RIVAL"

        else:

            token["team"] = "RACING"


        token["role"] = "PLAYER"


    return final_tokens


# ==================================================
# DETECTAR FRAME 1
# ==================================================

detections = detect_players(
    frame1
)


print("=== FRAME 1 ===")

print(
    f"Detecciones: {len(detections)}"
)


# ==================================================
# SEPARAR BLOQUES
# ==================================================

racing_tracks = [
    p
    for p in previous_players
    if (
        p["identity"]["team"] == "RACING"
        and p["identity"]["role"] == "PLAYER"
    )
]

rival_tracks = [
    p
    for p in previous_players
    if (
        p["identity"]["team"] == "RIVAL"
        and p["identity"]["role"] == "PLAYER"
    )
]

goalkeeper_tracks = [
    p
    for p in previous_players
    if p["identity"]["role"] == "GK"
]


racing_detections = [
    d
    for d in detections
    if (
        d.get("team") == "RACING"
        and d.get("role") == "PLAYER"
    )
]

rival_detections = [
    d
    for d in detections
    if (
        d.get("team") == "RIVAL"
        and d.get("role") == "PLAYER"
    )
]

goalkeeper_detections = [
    d
    for d in detections
    if d.get("role") == "GK"
]


print(
    f"Racing: "
    f"{len(racing_tracks)} tracks / "
    f"{len(racing_detections)} detecciones"
)

print(
    f"Rival: "
    f"{len(rival_tracks)} tracks / "
    f"{len(rival_detections)} detecciones"
)

print(
    f"GK: "
    f"{len(goalkeeper_tracks)} tracks / "
    f"{len(goalkeeper_detections)} detecciones"
)


# ==================================================
# FUNCIÓN DE ASIGNACIÓN
# ==================================================

def assign_tracks(
    tracks,
    detections
):

    if len(tracks) == 0:
        return [], [], []

    if len(detections) == 0:
        return [], list(
            range(len(tracks))
        ), []


    cost_matrix = np.full(
        (
            len(tracks),
            len(detections)
        ),
        LARGE_COST,
        dtype=float
    )


    for i, track in enumerate(tracks):

        old_x = track[
            "state"
        ]["x"]

        old_y = track[
            "state"
        ]["y"]


        for j, detection in enumerate(
            detections
        ):

            new_x = detection["x"]
            new_y = detection["y"]


            distance = np.hypot(
                old_x - new_x,
                old_y - new_y
            )


            if distance <= MAX_DISTANCE:

                cost_matrix[
                    i,
                    j
                ] = distance


    rows, cols = linear_sum_assignment(
        cost_matrix
    )


    matches = []
    unmatched_tracks = []
    used_detections = set()


    for row, col in zip(
        rows,
        cols
    ):

        cost = cost_matrix[
            row,
            col
        ]


        if cost >= LARGE_COST:

            unmatched_tracks.append(
                row
            )

        else:

            matches.append(
                (
                    row,
                    col,
                    cost
                )
            )

            used_detections.add(
                col
            )


    for i in range(
        len(tracks)
    ):

        if i not in [
            m[0]
            for m in matches
        ] and i not in unmatched_tracks:

            unmatched_tracks.append(
                i
            )


    unmatched_detections = [
        j
        for j in range(
            len(detections)
        )
        if j not in used_detections
    ]


    return (
        matches,
        unmatched_tracks,
        unmatched_detections
    )


# ==================================================
# RESOLVER CADA BLOQUE
# ==================================================

all_matches = []


for block_name, tracks, detections_block in [

    (
        "RACING",
        racing_tracks,
        racing_detections
    ),

    (
        "RIVAL",
        rival_tracks,
        rival_detections
    ),

    (
        "GK",
        goalkeeper_tracks,
        goalkeeper_detections
    )

]:

    matches, unmatched_tracks, unmatched_detections = (
        assign_tracks(
            tracks,
            detections_block
        )
    )


    print(
        f"\n=== {block_name} ==="
    )

    print(
        f"Asociaciones: "
        f"{len(matches)}"
    )

    print(
        f"Sin track: "
        f"{len(unmatched_tracks)}"
    )

    print(
        f"Sin detección: "
        f"{len(unmatched_detections)}"
    )


    for track_index, detection_index, distance in matches:

        track = tracks[
            track_index
        ]

        detection = detections_block[
            detection_index
        ]

        all_matches.append(
            {
                "track": track,
                "detection": detection,
                "distance": distance
            }
        )


# ==================================================
# ESTADÍSTICAS
# ==================================================

distances = [
    match["distance"]
    for match in all_matches
]


mean_distance = (
    np.mean(distances)
    if distances
    else 0
)

max_distance = (
    np.max(distances)
    if distances
    else 0
)


print(
    "\n================================"
)

print(
    "RESULTADO GLOBAL"
)

print(
    "================================"
)

print(
    f"Asociaciones: "
    f"{len(all_matches)}/22"
)

print(
    f"Distancia media: "
    f"{mean_distance:.2f} px"
)

print(
    f"Distancia máxima: "
    f"{max_distance:.2f} px"
)

print(
    f"Gating: "
    f"{MAX_DISTANCE:.2f} px"
)


# ==================================================
# CONSTRUIR FRAME 1
# ==================================================

new_players = []


for match in all_matches:

    previous_player = match[
        "track"
    ]

    detection = match[
        "detection"
    ]

    old_state = previous_player[
        "state"
    ]


    new_x = detection["x"]
    new_y = detection["y"]

    dx = (
        new_x
        - old_state["x"]
    )

    dy = (
        new_y
        - old_state["y"]
    )


    new_player = {

        "track_id":
            previous_player[
                "track_id"
            ],

        "identity":
            previous_player[
                "identity"
            ],

        "state": {

            "frame": 1,

            "timestamp_ms":
                33.33,

            "x": int(new_x),

            "y": int(new_y),

            "radius":
                int(
                    detection[
                        "radius"
                    ]
                ),

            "dx": int(dx),

            "dy": int(dy)

        }

    }


    new_players.append(
        new_player
    )


# ==================================================
# ORDEN
# ==================================================

new_players.sort(
    key=lambda p:
    p["track_id"]
)


# ==================================================
# GUARDAR JSON
# ==================================================

frame1_data = {

    "match": {

        "frame": 1,

        "timestamp_ms": 33.33

    },

    "players":
        new_players
}


with open(
    output_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        frame1_data,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==================================================
# DEBUG VISUAL
# ==================================================

debug = frame1.copy()


for match in all_matches:

    track = match["track"]
    detection = match["detection"]

    old_x = track[
        "state"
    ]["x"]

    old_y = track[
        "state"
    ]["y"]

    new_x = detection["x"]
    new_y = detection["y"]

    track_id = track[
        "track_id"
    ]


    cv2.line(
        debug,
        (old_x, old_y),
        (new_x, new_y),
        (0, 255, 0),
        1
    )

    cv2.circle(
        debug,
        (new_x, new_y),
        5,
        (0, 255, 0),
        2
    )

    cv2.putText(
        debug,
        str(track_id),
        (
            new_x + 5,
            new_y - 5
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 0),
        1
    )


cv2.imwrite(
    str(debug_path),
    debug
)


print(
    f"\nJSON: {output_path}"
)

print(
    f"Debug: {debug_path}"
)