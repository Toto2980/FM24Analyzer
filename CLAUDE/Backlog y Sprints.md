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
| E1 | Percepción | RF-10…RF-14 | 🟡 |
| E2 | Identificación | RF-20…RF-23 | 🟡 |
| E3 | Tracking robusto | RF-30…RF-34 | 🟡 |
| E4 | Calidad y benchmark | RF-70…RF-73, CU-09 | 🟡 |
| E5 | Reconstrucción espacial | RF-40…RF-42 | ⬜ |
| E6 | Métricas tácticas | RF-50…RF-56 | ⬜ |
| E7 | Salidas, CLI e informe | RF-01…RF-05, RF-60…RF-63, RF-80…RF-81 | ⬜ |
| E8 | Post-MVP: eventos, comparación, UI | RF-57, RF-90…RF-93, CU-04, CU-08 | ⬜ |

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

## Sprint 0 — Proceso y fundaciones (en curso)

**Objetivo:** que el proyecto tenga plano (SRS), tablero y repositorio.
**Entregable:** SRS v1.0 aprobada, repo git con `v0.0.1`.

| ID | Historia / tarea | SRS | Pts | Estado |
|---|---|---|---|---|
| HU-00 | Escribir la SRS v0.1 | — | 3 | ✅ Terminado |
| HU-01 | Resolver las decisiones D-01…D-08 y aprobar la SRS v1.0 | SRS §12 | 2 | ⬜ **Toto** |
| HU-02 | Inicializar git, `.gitignore` (excluir `videos/`, `output/`), `requirements.txt` con versiones fijas, README mínimo | RNF-08, RNF-15 | 2 | 🟡 git init + `.gitignore` + `requirements.txt` hechos; faltan README y primer commit |
| HU-02b | Crear el tablero (Trello u otro) con las columnas de §1.1 y cargar este backlog | — | 1 | ⬜ **Toto** |

## Sprint 1 — Tracking confiable en el clip de prueba

**Objetivo:** 0 pérdidas por clasificación y red de seguridad de regresión.
**Entregable `v0.1.0`:** tracker con clasificación por anillo, regresión automática y dataset de referencia inicial.

| ID | Historia | SRS | Pts | Criterio de aceptación |
|---|---|---|---|---|
| HU-03 | **Como** desarrollador **quiero** un test de regresión sobre los frames 0–30 **para** que ningún cambio empeore lo que ya funciona | RF-73, RNF-14 | 3 | `pytest` compara contra `output/baseline_31f/` y contra los resultados esperados |
| HU-04 | **Como** mánager **quiero** etiquetar un dataset de referencia (≥ 5 frames repartidos en un clip con movimiento) **para** medir la exactitud real | CU-09, RF-72 | 5 | Existe un archivo versionado con 22 posiciones + grupo + dorsal por frame. **Toto graba el clip y valida las etiquetas** |
| HU-05 | **Como** mánager **quiero** que la clasificación de equipo mire la camiseta y no el dorsal **para** que el Rival #10 no se pierda | RF-12, RNF-02 | 2 | La auditoría del clip de prueba da 0 `WRONG_BLOCK`. Distribución esperada: 23×22, 7×21 |
| HU-06 | **Como** mánager **quiero** que el falso arquero sobre el arco del área desaparezca **para** que no robe asociaciones | RF-11 | 2 | 0 candidatos GK libres en el clip de prueba, sin perder a ningún arquero real |
| HU-07 | Integrar `audit_transitions` al pipeline como informe de calidad | RF-70 | 3 | Cada corrida genera `quality.json` |

**Total:** 15 pts.

## Sprint 2 — Tracking con movimiento y oclusiones

**Objetivo:** tracking estable en ≥ 100 transiciones con juego en movimiento.
**Entregable `v0.2.0`.**

| ID | Historia | SRS | Pts | Criterio de aceptación |
|---|---|---|---|---|
| HU-08 | Ejecutar la auditoría en un clip con movimiento (≥ 100 transiciones) y documentar las causas | RF-70 | 2 | Documento de auditoría con la distribución de causas |
| HU-09 | Resolver la oclusión por etiqueta de nombre, según D-03: grabar sin etiqueta **o** implementar RF-13/RF-32 | RF-13, RF-32 | 5 | Racing #10 (frames 24–30) sin pérdida o con `estimated` |
| HU-10 | Ajustar el gating **solo si** HU-08 muestra pérdidas `GATING` | RF-30 | 2 | Pérdidas `GATING` = 0 en el clip de HU-08 |
| HU-11 | Votación del dorsal por track | RF-21, RNF-03 | 3 | Exactitud por track ≥ objetivo D-01 |
| HU-12 | Benchmark contra el dataset de referencia | RF-72 | 3 | `benchmark` reporta RNF-01…RNF-05 |

**Total:** 15 pts.

## Sprint 3 — Espacio, configuración y exportación

**Objetivo:** datos en metros, exportables, sin constantes en el código.
**Entregable `v0.3.0`.**

| ID | Historia | SRS | Pts | Criterio de aceptación |
|---|---|---|---|---|
| HU-13 | Configuración centralizada (YAML/JSON) con los nombres de equipo | RF-02, RF-03 | 3 | Ninguna constante fuera de la configuración |
| HU-14 | Coordenadas normalizadas y en metros | RF-40, RF-41 | 3 | Test de esquinas y de las distancias de las áreas |
| HU-15 | Normalizar la dirección de ataque | RF-42 | 2 | Test con un clip de cada tiempo |
| HU-16 | Carpeta por ejecución + `tracks.csv` + `run.json` versionados | RF-60…RF-63 | 3 | Esquema validado por test |
| HU-17 | Validación de la entrada | RF-01, RNF-10 | 2 | Tests con video inválido / no soportado / válido |

**Total:** 13 pts.

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
| 7 | HU-36 | Recuperaciones, pérdidas y fases de juego | RF-91, RF-92 |
| 8 | HU-37 | Inferencia de la formación nominal | RF-93 |
| 9 | HU-38 | Interfaz gráfica | — |
| 10 | HU-39 | Refactor completo a módulos por capa (RNF-13), incremental por sprint | RNF-13 |

---

# 6. Qué puede hacer Toto (tareas del cliente)

| Tarea | Para qué | Sprint |
|---|---|---|
| Responder D-01…D-08 de la SRS | Aprobar la SRS v1.0 | 0 |
| Crear el tablero y cargar el backlog | Gestión visual | 0 |
| Fijarse en FM24 si se puede ocultar la etiqueta de nombre en la vista 2D | Define HU-09 | 0–1 |
| Grabar un clip de 1–2 min de **juego en movimiento** (1280×720, 30 FPS, 2D, cancha completa) | HU-04, HU-08 | 1 |
| Validar las etiquetas del dataset de referencia | HU-04 | 1 |
| Grabar un clip del segundo tiempo (los equipos cambiados de lado) | HU-15 | 3 |
| Hacer la demo y la retro al cierre de cada sprint | Scrum | todos |
