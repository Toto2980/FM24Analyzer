from pathlib import Path
import json

import numpy as np
import pandas as pd


# ==================================================
# RUTAS
# ==================================================

project_path = Path(__file__).resolve().parent.parent

tokens_path = (
    project_path
    / "output"
    / "classified_tokens.csv"
)

labels_path = (
    project_path
    / "output"
    / "token_labels.csv"
)

output_path = (
    project_path
    / "output"
    / "match"
    / "frame_0000.json"
)


output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# CARGAR DATOS
# ==================================================

tokens = pd.read_csv(
    tokens_path
)

labels = pd.read_csv(
    labels_path,
    dtype={"dorsal": str}
)


# ==================================================
# UNIR DORSAL + DETECCIÓN
# ==================================================

df = tokens.merge(
    labels[
        ["id", "dorsal"]
    ],
    on="id",
    how="left"
)


# ==================================================
# VALIDACIÓN
# ==================================================

if len(df) != 22:

    raise ValueError(
        f"Se esperaban 22 jugadores, "
        f"pero encontramos {len(df)}."
    )


# ==================================================
# VOTACIÓN DEL EQUIPO DEL ARQUERO
# ==================================================

field_players = df[
    df["team"] != "ARQUERO"
].copy()

goalkeepers = df[
    df["team"] == "ARQUERO"
].copy()


def infer_goalkeeper_team(
    goalkeeper,
    field_players
):

    gx = goalkeeper["x"]
    gy = goalkeeper["y"]


    # ----------------------------------------------
    # Distancia a todos los jugadores de campo
    # ----------------------------------------------

    candidates = []

    for _, player in field_players.iterrows():

        px = player["x"]
        py = player["y"]

        distance = np.sqrt(
            (gx - px) ** 2
            +
            (gy - py) ** 2
        )

        candidates.append(
            {
                "team": player["team"],
                "distance": distance
            }
        )


    candidates.sort(
        key=lambda item:
        item["distance"]
    )


    # ----------------------------------------------
    # Tomamos los 5 más cercanos
    # ----------------------------------------------

    nearest = candidates[:5]


    votes = {}

    for candidate in nearest:

        team = candidate["team"]

        # Los más cercanos pesan más.
        weight = 1 / (
            candidate["distance"] + 1
        )

        votes[team] = (
            votes.get(team, 0)
            + weight
        )


    # ----------------------------------------------
    # Ganador
    # ----------------------------------------------

    if votes:

        inferred_team = max(
            votes,
            key=votes.get
        )

        total = sum(
            votes.values()
        )

        confidence = (
            votes[inferred_team]
            / total
        )

        if confidence >= 0.55:

            return (
                inferred_team,
                "PROXIMITY",
                confidence
            )


    # ----------------------------------------------
    # Fallback por lado
    # ----------------------------------------------

    field_width = (
        tokens["x"].max()
    )

    midpoint = field_width / 2

    if gx < midpoint:

        return (
            "RACING",
            "SIDE_FALLBACK",
            0.5
        )

    return (
        "RIVAL",
        "SIDE_FALLBACK",
        0.5
    )


# ==================================================
# ASIGNAR EQUIPO A LOS ARQUEROS
# ==================================================

goalkeeper_teams = {}


for _, goalkeeper in goalkeepers.iterrows():

    team, method, confidence = (
        infer_goalkeeper_team(
            goalkeeper,
            field_players
        )
    )

    goalkeeper_teams[
        int(goalkeeper["id"])
    ] = {
        "team": team,
        "method": method,
        "confidence": confidence
    }


# ==================================================
# CONSTRUIR JUGADORES
# ==================================================

players = []


for _, row in df.iterrows():

    token_id = int(
        row["id"]
    )

    is_goalkeeper = (
        row["team"] == "ARQUERO"
    )


    # ----------------------------------------------
    # Equipo
    # ----------------------------------------------

    if is_goalkeeper:

        goalkeeper_info = (
            goalkeeper_teams[token_id]
        )

        team = goalkeeper_info[
            "team"
        ]

        role = "GK"

        team_method = (
            goalkeeper_info[
                "method"
            ]
        )

        team_confidence = (
            goalkeeper_info[
                "confidence"
            ]
        )

    else:

        team = row["team"]

        role = "PLAYER"

        team_method = "COLOR"

        team_confidence = 1.0


    # ----------------------------------------------
    # Dorsal
    # ----------------------------------------------

    dorsal = str(
        row["dorsal"]
    )


    # ----------------------------------------------
    # Track ID
    # ----------------------------------------------

    track_id = token_id


    # ----------------------------------------------
    # Objeto
    # ----------------------------------------------

    player = {

        "track_id": track_id,

        "identity": {

            "team": team,

            "role": role,

            "number": int(dorsal),

            "confidence": {

                "score": None,

                "gap": None,

                "status": "KNOWN"

            }

        },

        "state": {

            "frame": 0,

            "timestamp_ms": 0,

            "x": int(row["x"]),

            "y": int(row["y"]),

            "radius": int(row["radius"])

        },

        "detection": {

            "team_method": team_method,

            "team_confidence":
                round(
                    float(
                        team_confidence
                    ),
                    3
                ),

            "detector":
                row["source"]

        }

    }


    players.append(
        player
    )


# ==================================================
# ORDENAR POR TRACK ID
# ==================================================

players.sort(
    key=lambda player:
    player["track_id"]
)


# ==================================================
# VALIDACIONES
# ==================================================

racing = [
    p for p in players
    if p["identity"]["team"]
    == "RACING"
]

rival = [
    p for p in players
    if p["identity"]["team"]
    == "RIVAL"
]

goalkeepers_json = [
    p for p in players
    if p["identity"]["role"]
    == "GK"
]


if len(racing) != 11:

    raise ValueError(
        f"RACING tiene {len(racing)} "
        "jugadores en vez de 11."
    )

if len(rival) != 11:

    raise ValueError(
        f"RIVAL tiene {len(rival)} "
        "jugadores en vez de 11."
    )

if len(goalkeepers_json) != 2:

    raise ValueError(
        "La cantidad de arqueros "
        "no es 2."
    )


# ==================================================
# JSON FINAL
# ==================================================

match = {

    "match": {

        "frame": 0,

        "timestamp_ms": 0,

        "resolution": {

            "width": 1280,

            "height": 720

        }

    },

    "players": players

}


# ==================================================
# GUARDAR
# ==================================================

with open(
    output_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        match,
        file,
        indent=4,
        ensure_ascii=False
    )


print("=== FRAME 0000 ===")

print(
    f"Jugadores: {len(players)}"
)

print(
    f"Racing:    {len(racing)}"
)

print(
    f"Rival:     {len(rival)}"
)

print(
    f"Arqueros:  {len(goalkeepers_json)}"
)

print(
    f"\nJSON generado:"
)

print(
    output_path
)


print("\n=== ARQUEROS ===")

for goalkeeper in goalkeepers_json:

    print(
        f"track_id="
        f"{goalkeeper['track_id']} | "
        f"team="
        f"{goalkeeper['identity']['team']} | "
        f"number="
        f"{goalkeeper['identity']['number']} | "
        f"method="
        f"{goalkeeper['detection']['team_method']} | "
        f"confidence="
        f"{goalkeeper['detection']['team_confidence']}"
    )