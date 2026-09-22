# FM24Analyzer
## Auditoría de pérdidas de tracking — 31 frames / 30 transiciones

**Fecha:** 22/09/2026
**Scripts:** `src/audit_transitions.py`, `src/probe_token_color.py`, `src/probe_ring_vs_center.py`
**Salidas:** `output/audit_31f/` (JSON, CSV, una imagen por transición imperfecta, `evidencia/`)

---

# 1. Qué se hizo

1. **Extracción sin cambio de comportamiento.** `detect_players` y `assign_tracks` pasaron de `batch_tracker.py` a `src/tracking_core.py`, copiadas tal cual.
   - Se guardó una línea base en `output/baseline_31f/` y se volvió a correr el tracker.
   - Los 30 JSON, la salida de consola y `trajectory_30frames.jpg` quedaron **idénticos byte a byte**.
2. **Auditoría.** `audit_transitions.py` reproduce el mismo loop y, en cada transición con `matches < 22`, registra:
   - el track sin match;
   - el candidato más cercano de su bloque y de cualquier bloque;
   - las detecciones libres;
   - un diagnóstico tentativo.
3. **Validación de la auditoría.** Reproduce exactamente la distribución del informe:

```text
22 matches → 12 transiciones
21 matches → 13 transiciones
20 matches →  5 transiciones
Pérdidas totales: 13×1 + 5×2 = 23   ✔
```

---

# 2. Resultado

Las 23 pérdidas se explican por **solo dos tracks**:

| Track | Bloque | Pérdidas | Frames | Diagnóstico |
|---|---|---|---|---|
| T21 | RIVAL #10 | 16 | 10, 13–18, 20–28 | `WRONG_BLOCK` |
| T06 | RACING #10 | 7 | 24–30 | `NO_DETECTION` |

Los otros 20 tracks no perdieron ninguna asociación. El Hungarian y el gating no causaron **ninguna** pérdida: no hay casos `GATING` ni `CONTESTED`.

---

# 3. Pérdida 1 — T21 (Rival #10): clasificación de equipo inestable

## Evidencia

La detección está **en la misma posición exacta** que el track (distancia 0,00 px), pero sale como RACING. Por eso el Hungarian no la puede asignar.

`probe_token_color.py` muestra que el cambio de equipo coincide con el cambio de radio de Hough:

```text
radio 8 → medV ≈ 200 → RIVAL   (correcto)
radio 7 → medV ≈ 162 → RACING  (incorrecto)
medS    ≈ 144 en ambos casos
```

## Causa

El clasificador toma la mediana de un cuadrado central de ±r/2 px. En FM24, ese centro es **el dorsal**, no la camiseta.

El "10" es azul oscuro sobre una ficha celeste. Cuando el radio baja a 7, el parche queda casi entero sobre los dígitos y V cae por debajo de 180. Ver `evidencia/t21_f09_f10.png`.

Con dos cifras se tapa más superficie que con una, lo que explica por qué el caso aparece con el #10.

## Medición de la alternativa (frame 10, 20 jugadores de campo)

| Zona muestreada | V Racing | V Rival | Margen |
|---|---|---|---|
| Cuadrado central (actual) | 78 – **152** | **164** – 232 | 12 |
| Anillo 4,5–6,5 px | 82 – 88 | 231 – 244 | **143** |

- **Con el anillo:** clasifica 20/20 correctamente, con un margen 12 veces mayor.
- **Con el centro:** falla 1/20 en este frame (justamente T21).

Otro detalle: el centro de un jugador de Racing da S=37, V=152. Ese es el caso que el informe §4.4 había descrito como umbrales de S, y también es producto del dorsal.

---

# 4. Pérdida 2 — T06 (Racing #10): oclusión por la etiqueta de nombre

## Evidencia

Desde el frame 24 no hay **ninguna** detección a menos de 20 px de la última posición del track. La detección más cercana es un Rival a 25,6 px, que ya está asignado a T05.

Visualmente, la ficha **sigue en el mismo lugar**. Encima tiene la etiqueta "Miranda" que FM24 dibuja sobre el portador de la pelota, y la pelota está al lado. Ver `evidencia/t06_f22_23_24.png` y `audit_frame_0024.jpg`.

## Causa

La etiqueta tapa la mitad superior del borde del círculo. Esta ficha ya se detectaba solo con el Hough *sensitive* (param2=12). Con la oclusión, ni siquiera ese pasa.

## Por qué importa

Es un problema **sistemático, no un caso raro**: la ficha que se tapa es siempre la del portador de la pelota, es decir, el jugador más relevante para el análisis táctico.

---

# 5. Hallazgos secundarios (no causan pérdidas)

- **Falso candidato GK** en (948–950, 309–311): es un círculo sobre el **arco del área** derecha. Aparece como detección libre en casi todos los frames. Hoy no roba asociaciones, porque está a 60 px de T11, pero puede hacerlo cuando el arquero se mueva.
- **Falsa detección `sensitive`** en (685, 286) en los frames 22–23: probablemente las letras de la etiqueta "Miranda".
- **Limitación de la muestra:** en esta ventana casi todos los jugadores están quietos (distancia 0 px en la mayoría de las transiciones).
  - Esta prueba **no ejercita** el gating ni la asociación bajo movimiento real.
  - "0 pérdidas por gating" no significa que el gating esté validado.
- **La distancia acumulada del informe (§11)** para RACING #01 (33 px) y RIVAL #01 (16 px) corresponde a los arqueros. Queda pendiente separar si es movimiento real o jitter del detector GK.

---

# 6. Recomendación: una única corrección

**Clasificar el equipo con la mediana de V sobre un anillo (≈ 4,5–6,5 px del centro), en lugar del cuadrado central.**

- Es un cambio acotado a un bloque de `detect_players` en `tracking_core.py` (clasificación de campo).
- No toca el detector, el Hungarian ni el gating.
- Resultado esperado, a verificar:

```text
T21: 16 pérdidas → 0
matches = 22 en todas las transiciones salvo 24–30 (T06)
distribución esperada: 23×22, 7×21
```

## Protocolo de verificación

1. Cambiar solo la clasificación.
2. Correr `batch_tracker.py` y `audit_transitions.py` con exactamente la misma prueba.
3. Comparar contra `output/baseline_31f/`. Solo deberían cambiar los frames donde T21 estaba perdido.

## Lo que queda para después (no mezclar en el mismo cambio)

- La oclusión por etiqueta (T06), en la próxima iteración. Hay dos opciones:
  - reforzar la detección de fichas parcialmente tapadas;
  - aceptar la pérdida y resolverla con *coast mode*.

  La decisión depende de si en un tramo con movimiento la etiqueta aparece seguido.
- El falso GK sobre el arco del área.
- Extender a 100 transiciones **con movimiento real** antes de sacar conclusiones sobre el gating.

---

# 7. Resultado de la corrección HU-05 (22/09/2026)

Se aplicó **solo** la clasificación por anillo (`ring_median_v` en `tracking_core.py`, radios 4,5–6,5 px, umbral V = 180).

| | Antes | Después |
|---|---|---|
| Distribución | 12×22, 13×21, 5×20 | **23×22, 7×21** |
| Pérdidas | 23 (T21 ×16, T06 ×7) | **7** (T06 ×7) |
| `WRONG_BLOCK` | 16 | **0** |
| V en el anillo, Racing (303 fichas) | — | 82 – 89,5 |
| V en el anillo, Rival (310 fichas) | — | 231 – 244,5 |

- La regresión (`tests/test_regression_31f.py`) pasa: ningún match de la línea base se perdió ni cambió de posición.
- Queda la pérdida por la etiqueta de nombre (T06), que se ataca en HU-09 (coast mode).
