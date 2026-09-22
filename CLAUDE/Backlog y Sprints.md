# FM24Analyzer
## Product Backlog y plan de sprints (Scrum + Kanban)

**Fuente de verdad de los requerimientos:** `SRS - FM24Analyzer.md`. Cada ítem de este backlog referencia los RF/RNF que implementa.
**Última actualización:** 22/09/2026
**Tablero Kanban (fuente viva del estado de cada tarjeta):** https://claude.ai/artifact/JfV8f274KCJVwr146BXiPK

---

# 1. Cómo trabajamos

## 1.1. Tablero Kanban

```text
BACKLOG  →  SPRINT ACTUAL  →  EN CURSO  →  TERMINADO Y TESTEADO  →  ENTREGADO (tag del sprint)
```

| Columna | Qué significa |
|---|---|
| **Backlog** | Todo lo que falta, ordenado por prioridad |
| **Sprint actual** | Lo que se comprometió para este sprint |
| **En curso** | Máximo **2 ítems** a la vez (límite WIP) |
| **Terminado y testeado** | Cumple la Definición de Hecho (§1.3) |
| **Entregado** | Forma parte de un incremento con tag de git |

## 1.2. Cadencia

- **Sprint:** 2 semanas.
- **Capacidad supuesta:** 6–8 h por semana, fuera del horario protegido de estudio. Son unos **12–16 puntos por sprint**, con 1 punto ≈ 1 h. Se ajusta con la velocidad real después del Sprint 1.
- **Al cerrar cada sprint:**
  1. **Demo:** correr el entregable.
  2. **Revisión:** ¿se cumplió el objetivo?
  3. **Retro:** una cosa a mejorar.
  4. **Tag de git:** `v0.N.0`.

## 1.3. Definición de Hecho (DoD)

Un ítem pasa a **Terminado y testeado** solo si cumple todo esto:

1. Cumple el criterio de verificación de su RF/RNF en la SRS.
2. Tiene un test automático o un benchmark repetible que lo demuestra.
3. La regresión (`HU-03`) no empeoró.
4. Los parámetros nuevos están en la configuración, no hardcodeados.
5. Está commiteado en git con un mensaje que referencia el ID (ej. `HU-05: clasificar por anillo`).
6. Si cambia algún resultado, se anotó en el changelog del sprint.

## 1.4. Estimación

Puntos de historia: **1, 2, 3, 5, 8**. Un ítem de más de 8 puntos se divide.

---

# 2. Épicas

| ID | Épica | SRS | Estado |
|---|---|---|---|
| E0 | Fundaciones y proceso | RNF-08, RNF-15 | 🟡 |
| E1 | Percepción | RF-10…RF-15 | 🟡 |
| E2 | Identificación | RF-20…RF-23, RF-100, RF-101 | 🟡 |
| E3 | Tracking robusto | RF-30…RF-34 | 🟡 |
| E4 | Calidad y benchmark | RF-70…RF-73, CU-09 | 🟡 |
| E5 | Reconstrucción espacial | RF-40…RF-42 | ⬜ |
| E6 | Métricas tácticas | RF-50…RF-56 | ⬜ |
| E7 | Salidas, CLI e informe | RF-01…RF-05, RF-60…RF-63, RF-80…RF-81, RNF-20 | ⬜ |
| E8 | Post-MVP: eventos, comparación, UI, lectura de interfaz | RF-57, RF-90…RF-93, RF-102…RF-105, CU-04, CU-08 | ⬜ |

---

# 3. Incremento previo (ya hecho antes del proceso formal)

| Ítem | Estado |
|---|---|
| Entorno, lectura de video, ROI | ✅ |
| Detector Hough normal + sensible + arqueros | ✅ inicial |
| Clasificación de equipo por HSV | ✅ inicial (con falla conocida, ver HU-05) |
| Extracción de dorsales + 21 templates + benchmark (88,46 %) | ✅ inicial |
| Modelo `token_id` / `track_id`, JSON por frame | ✅ |
| Tracking Hungarian + gating, 30 transiciones | ✅ inicial |
| Extracción de `tracking_core.py` (sin cambio de comportamiento) | ✅ 22/09 |
| Auditoría de pérdidas de 31 frames | ✅ 22/09 |

---

# 4. Plan de sprints hasta el MVP

## Cierre del Sprint 0 (22/09/2026)

- **Entregado:** SRS v1.0 aprobada, tablero, repo público en GitHub, tag `v0.0.1`.
- **Decisiones:** equipo propio = Racing; zoom 2D fijo con fichas grandes; la etiqueta de nombre no se puede sacar, así que coast mode (HU-09) pasa a obligatorio; el MVP no separa con / sin pelota.
- **Cambios al plan:**
  - Entran al Sprint 1 HU-40 (configuración por video), HU-41 (excluir menús) y T-03 (clip definitivo).
  - HU-06 y HU-07 pasan al Sprint 2.
  - Se agrega HU-45 (videos largos, RNF-20) al Sprint 3.
- **Retro:** el clip grabado mezcló menús y otro zoom con el partido. Las condiciones de grabación tienen que estar escritas antes de grabar (RNF-10).
- **Desde ahora:** el tablero es la fuente viva del estado. Este archivo guarda el plan y los cierres de sprint.

## Sprint 0 — Proceso y fundaciones (cerrado, `v0.0.1`)

**Objetivo:** que el proyecto tenga plano (SRS), tablero y repositorio.
**Entregable:** SRS v1.0 aprobada, repo git con `v0.0.1`.

| ID | Historia / tarea | SRS | Pts | Estado |
|---|---|---|---|---|
| HU-00 | Escribir la SRS v0.1 | — | 3 | ✅ Entregado |
| HU-01 | Resolver las decisiones D-01…D-09 y aprobar la SRS v1.0 | SRS §12 | 2 | ✅ Entregado |
| HU-02 | Inicializar git, `.gitignore`, `requirements.txt` con versiones fijas, README, subir a GitHub | RNF-08, RNF-15 | 2 | ✅ Entregado — github.com/Toto2980/FM24Analyzer |
| HU-02b | Crear el tablero Kanban y cargar el backlog | — | 1 | ✅ Entregado |
| T-01 | Fijarse si FM24 permite ocultar la etiqueta de nombre | D-03, RF-13 | 1 | ✅ Entregado — no se puede sacar; se resuelve con coast mode (HU-09, ahora obligatoria) |
| T-02 | Grabar clip con juego en movimiento | HU-04, HU-08 | 1 | ✅ Entregado — captura con otro zoom/resolución, ver HU-40 |

## Sprint 1 — Tracking confiable en el clip de prueba (en curso)

**Objetivo:** 0 pérdidas por clasificación y red de seguridad de regresión.
**Entregable `v0.1.0`:** tracker con clasificación por anillo, regresión automática, configuración por video y dataset de referencia inicial.

| ID | Historia | SRS | Pts | Estado / criterio de aceptación |
|---|---|---|---|---|
| HU-03 | **Como** desarrollador **quiero** un test de regresión sobre los frames 0–30 **para** que ningún cambio empeore lo que ya funciona | RF-73, RNF-14 | 3 | ✅ Hecho — `tests/test_regression_31f.py`, 61 casos contra `output/baseline_31f/` |
| HU-05 | **Como** mánager **quiero** que la clasificación de equipo mire la camiseta y no el dorsal **para** que el Rival #10 no se pierda | RF-12, RNF-02 | 2 | ✅ Hecho — clasificación por anillo. Distribución 23×22, 7×21; `WRONG_BLOCK` 16 → 0 |
| HU-41 | Detectar y excluir los tramos del video sin cancha (menús, preferencias) | RF-15 | 2 | ✅ Hecho — `src/detect_pitch_segments.py`, verificado contra el clip con el menú de Preferencias |
| T-03 | Grabar el clip definitivo a 1920×1080 con el zoom fijo (cancha + panel) | D-09, RNF-10 | 1 | ✅ Hecho — `2026-09-22 18-50-52.mp4`, fichas de radio ~7,8 px |
| HU-40 | Configuración por video: ROI de la cancha, radio de ficha y colores de Racing / rival | RF-02, RF-03, CU-02 | 3 | ✅ Entregado — `src/calibrate_video.py` mide ROI (1186×849), radio de ficha (7,3 px) y separa equipos por color (91 vs 215, separación 123). Toto confirmó: Racing = grupo claro |
| HU-04 | **Como** mánager **quiero** etiquetar un dataset de referencia (≥ 5 frames con movimiento) **para** medir la exactitud real | CU-09, RF-72 | 5 | ⬜ Pendiente. Claude propone las marcas, Toto las valida |

**Total:** 16 pts (11 ya entregados).

## Sprint 2 — Tracking con movimiento y oclusiones

**Objetivo:** tracking estable en ≥ 100 transiciones con juego en movimiento.
**Entregable `v0.2.0`.**

| ID | Historia | SRS | Pts | Criterio de aceptación |
|---|---|---|---|---|
| HU-06 | **Como** mánager **quiero** que el falso arquero sobre el arco del área desaparezca **para** que no robe asociaciones | RF-11 | 2 | 0 candidatos GK libres en el clip de prueba, sin perder a ningún arquero real |
| HU-07 | Integrar `audit_transitions` al pipeline como informe de calidad | RF-70 | 3 | Cada corrida genera `quality.json` |
| HU-08 | Ejecutar la auditoría en un clip con movimiento (≥ 100 transiciones) y documentar las causas | RF-70 | 2 | Documento de auditoría con la distribución de causas |
| HU-09 | Coast mode: mantener la posición estimada mientras la etiqueta de nombre tapa la ficha | RF-13, RF-32 | 5 | Obligatoria (D-03: la etiqueta no se puede sacar). Racing #10 (frames 24–30 del clip de prueba) queda `estimated`, sin perderse |
| HU-10 | Ajustar el gating **solo si** HU-08 muestra pérdidas `GATING` | RF-30 | 2 | Pérdidas `GATING` = 0 en el clip de HU-08 |
| HU-11 | Votación del dorsal por track | RF-21, RNF-03 | 3 | Exactitud por track ≥ objetivo D-01 |
| HU-12 | Benchmark contra el dataset de referencia | RF-72 | 3 | `benchmark` reporta RNF-01…RNF-05 |
| HU-47 | Excluir árbitros y asistentes (fichas con «A» y «M») | RF-10 | 2 | En los clips nuevos el árbitro es una ficha casi igual a las de un equipo. No se puede confundir con un jugador |

**Total:** 22 pts. **Sobre la capacidad supuesta (12–16 pts).** Creció al mover HU-06/HU-07 desde el Sprint 1 (por capacidad) y sumar HU-47 (hallazgo nuevo). Candidatos a pasar al Sprint 3 si no llegamos: HU-11 y HU-12 (dependen de HU-04, que puede no estar terminada) — a decidir con Toto al empezar el sprint.

## Sprint 3 — Espacio, configuración y exportación

**Objetivo:** datos en metros, exportables, sin constantes en el código.
**Entregable `v0.3.0`.**

| ID | Historia | SRS | Pts | Criterio de aceptación |
|---|---|---|---|---|
| HU-13 | Configuración centralizada (YAML/JSON) con los nombres de equipo | RF-02, RF-03 | 3 | Ninguna constante fuera de la configuración. Construye sobre `src/calibrate_video.py` de HU-40 |
| HU-14 | Coordenadas normalizadas y en metros | RF-40, RF-41 | 3 | Test de esquinas y de las distancias de las áreas |
| HU-15 | Normalizar la dirección de ataque | RF-42 | 2 | Test con un clip de cada tiempo (Toto graba el 2º tiempo) |
| HU-16 | Carpeta por ejecución + `tracks.csv` + `run.json` versionados | RF-60…RF-63 | 3 | Esquema validado por test |
| HU-17 | Validación de la entrada | RF-01, RNF-10 | 2 | Tests con video inválido / no soportado / válido |
| HU-45 | Videos largos (30+ min): streaming, `analysis_fps` configurable, reanudable, en paralelo por tramos | RNF-20 | 5 | Medido el 22/09: 30 min a 30 fps ≈ 50 min, a 10 fps ≈ 20 min. Objetivo: < 10 min con 12 núcleos. Antes hay que validar que 10 fps no pierda jugadores |

**Total:** 18 pts.

## Sprint 4 — MVP: métricas, informe y CLI

**Objetivo:** cumplir los criterios de aceptación del MVP (SRS §11).
**Entregable `v1.0.0` = MVP + código fuente completo.**

| ID | Historia | SRS | Pts | Criterio de aceptación |
|---|---|---|---|---|
| HU-18 | Métricas: posición media, altura, profundidad, amplitud, compactación | RF-50…RF-54 | 5 | Tests con casos sintéticos |
| HU-19 | Series por segundo + mapas de calor | RF-55, RF-56 | 3 | CSV + imágenes |
| HU-20 | Informe HTML autocontenido | RF-80, RF-81 | 5 | Abre con doble clic, sin internet |
| HU-21 | CLI `fm24analyzer analyze / metrics / report / benchmark` | RNF-17 | 3 | Un único comando genera todo |
| HU-22 | README + guía de reproducción | RNF-19 | 2 | Otra persona lo reproduce en ≤ 15 min |

**Total:** 18 pts. Si la velocidad real no alcanza, **HU-19** pasa al Sprint 5.

---

# 5. Backlog post-MVP (priorizado)

| Prioridad | ID | Ítem | SRS |
|---|---|---|---|
| 1 | HU-30 | Detectar la pelota y la posesión | RF-90 |
| 2 | HU-31 | Métricas con / sin pelota | RF-57 |
| 3 | HU-32 | Comparar partidos | CU-08 |
| 4 | HU-33 | Reidentificación tras una pérdida larga | RF-33 |
| 5 | HU-34 | Corrección manual de identidad | CU-04 |
| 6 | HU-35 | Calibración asistida del ROI y los colores | RF-05, CU-02 |
| 7 | HU-42 | Leer la alineación del panel inferior: posición + nombre + dorsal | RF-100, RF-101 |
| 8 | HU-36 | Recuperaciones, pérdidas y fases de juego | RF-91, RF-92 |
| 9 | HU-37 | Inferencia de la formación nominal | RF-93 |
| 10 | HU-43 | Leer la formación y la mentalidad configuradas | RF-102 |
| 11 | HU-44 | Comparar la estructura configurada con la observada (4-3-3 → 3-2-5) | RF-103 |
| 12 | HU-46 | Leer nota, energía y ánimo de cada jugador del panel inferior | Módulo INT |
| 13 | HU-38 | Interfaz gráfica | — |
| 14 | HU-39 | Refactor completo a módulos por capa (RNF-13), incremental por sprint | RNF-13 |

`HU-42` está marcada como candidata a subir al Sprint 2 si sobra capacidad: viene de la idea original del proyecto (`CLAUDE/Analizar20de20Manager.md`) y es la base de `HU-44`, que es el objetivo de negocio central del proyecto (N-01, SRS §3.1).

---

# 6. Qué puede hacer Toto (tareas del cliente)

| Tarea | Para qué | Sprint | Estado |
|---|---|---|---|
| Responder D-01…D-09 de la SRS | Aprobar la SRS v1.0 | 0 | ✅ |
| Crear el tablero y cargar el backlog | Gestión visual | 0 | ✅ |
| Fijarse en FM24 si se puede ocultar la etiqueta de nombre en la vista 2D | Define HU-09 | 0 | ✅ — no se puede |
| Grabar un clip de 1–2 min de **juego en movimiento** | HU-04, HU-08 | 0–1 | ✅ (T-02, T-03) |
| Grabar el clip definitivo a 1920×1080 con zoom fijo | HU-40, T-03 | 1 | ✅ |
| Confirmar qué color es Racing en el clip definitivo (blanco o azul oscuro según el partido) | HU-40 | 1 | ✅ — Racing = grupo claro (celeste/blanco), confirmado 22/09/2026 |
| Validar las etiquetas del dataset de referencia | HU-04 | 1 | ⬜ |
| Grabar un clip del segundo tiempo (los equipos cambiados de lado) | HU-15 | 3 | ⬜ |
| Hacer la demo y la retro al cierre de cada sprint | Scrum | todos | — |
