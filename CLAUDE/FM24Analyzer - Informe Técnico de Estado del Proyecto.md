# FM24Analyzer
## Informe técnico de estado, arquitectura y metodología

**Proyecto:** FM24Analyzer  
**Objetivo:** análisis automatizado de partidos de Football Manager 24 mediante visión por computadora  
**Estado:** prototipo funcional en validación de tracking  
**Entorno:** Windows · Python 3.13 · OpenCV 5.0.0  
**Última prueba:** 31 frames observados, 30 transiciones de tracking

---

# 1. Objetivo y alcance

FM24Analyzer busca transformar una grabación de Football Manager 24 en datos estructurados capaces de representar el comportamiento de los jugadores y, posteriormente, permitir análisis táctico.

El objetivo final es obtener:

- posición e identidad de cada jugador;
- equipo, dorsal y rol;
- movimiento y trayectorias;
- formación y estructura posicional;
- presión, bloque y transiciones;
- cambios tácticos;
- análisis automático del partido.

El proyecto se desarrolla por capas:

```text
Video
 ↓
ROI
 ↓
Detección
 ↓
Clasificación
 ↓
Dorsal
 ↓
Identidad
 ↓
Tracking
 ↓
Trayectorias
 ↓
Eventos
 ↓
Análisis táctico
```

La prioridad actual sigue siendo la percepción y el tracking. El análisis táctico se incorporará cuando los datos subyacentes sean suficientemente estables.

---

# 2. Estrategia técnica

Se decidió comenzar con una solución específica para FM24 utilizando OpenCV y algoritmos clásicos de visión por computadora, en lugar de depender inicialmente de modelos genéricos como YOLO.

La decisión se basa en que el entorno presenta características muy controladas:

- campo visual estable;
- fichas circulares;
- tamaño relativamente constante;
- colores diferenciables;
- dorsales ubicados en una zona predecible;
- interfaz y cámara con poca variabilidad.

La arquitectura podrá incorporar posteriormente deep learning si las pruebas muestran que la solución clásica no alcanza la robustez necesaria.

---

# 3. Entorno y estructura

### Entorno

```text
Sistema:        Windows
Python:         3.13
OpenCV:         5.0.0
Bibliotecas:    NumPy, Pandas, SciPy
Procesamiento:  local
```

### Video de prueba

```text
Archivo:        partido_prueba.mp4
FPS:            30
Frames totales: 2172
Resolución:     1280 × 720
Duración:       72,40 s
```

A 30 FPS, cada frame representa aproximadamente **33,3 ms**.

### Estructura principal

```text
FM24Analyzer/
├── videos/
├── output/
│   ├── dorsals_v2/
│   ├── templates/
│   └── match/
└── src/
    ├── detect_*
    ├── classify_tokens.py
    ├── extract_*
    ├── benchmark_templates.py
    ├── build_match_json.py
    ├── track_step.py
    └── batch_tracker.py
```

La organización actual es experimental. La refactorización modular queda para una etapa posterior.

---

# 4. Detección y clasificación

## 4.1. Región de interés

La cancha se aisló mediante:

```text
X = 183
Y = 48
Ancho = 913
Alto = 623
```

**ROI** es la región de la imagen que realmente procesa el sistema.

---

## 4.2. Detección de jugadores

La detección utiliza HoughCircles sobre el ROI, complementado por una segunda detección sensible para casos difíciles.

Características observadas de los tokens:

```text
Radio mínimo: 7 px
Radio máximo: 8 px
Radio medio:  7,26 px
Mediana:      7 px
```

En la prueba inicial:

```text
22 jugadores válidos
0 falsos positivos
0 duplicados
```

**Radio:** tamaño visual estimado de la ficha.  
**Falso positivo:** círculo detectado que no corresponde a un jugador.  
**Duplicado:** dos detecciones para una misma ficha.

---

## 4.3. Arqueros

Los arqueros presentan una apariencia más desaturada, por lo que requieren un detector específico basado en CLAHE, Hough y restricción espacial a las áreas de penal.

Se recuperaron:

```text
2 arqueros
0 falsos positivos
```

Su comportamiento temporal todavía requiere validación.

---

## 4.4. Clasificación por equipo

Se utilizaron características HSV.

```text
S < 30
    → ARQUERO

V > 180
    → RIVAL

V <= 180 y S >= 50
    → RACING
```

**H:** tono.  
**S:** saturación.  
**V:** luminosidad.

Los valores anteriores son **umbrales de clasificación**, no métricas de calidad.

---

# 5. Identificación mediante dorsal

La extracción del dorsal se realizó específicamente para el formato visual de FM24:

```text
token
 ↓
recorte
 ↓
reescalado
 ↓
máscara
 ↓
zona interior
 ↓
componentes
 ↓
separación de dígitos
```

Se procesaron correctamente los 22 tokens de la muestra y se identificaron **26 dígitos** debido a la existencia de dorsales de dos cifras.

### Banco de templates

Se construyó un banco de:

```text
21 templates
```

Un template es una imagen de referencia de un determinado dígito.

### Benchmark

Se utilizó:

```text
cv2.matchTemplate
TM_CCOEFF_NORMED
```

Se calcularon:

- **Winner score:** mejor similitud encontrada.
- **Second-best score:** segunda mejor similitud.
- **Gap:** diferencia entre ambas.

```text
gap = winner - second-best
```

Un gap alto implica una decisión más separada; uno bajo, mayor ambigüedad.

Umbral experimental:

```text
gap < 0,10 → LOW
```

Esto indica ambigüedad, no necesariamente error.

### Resultado

```text
23 / 26 dígitos correctos
Exactitud del benchmark: 88,46 %
```

Los errores se concentraron en muestras visualmente degradadas.

---

# 6. Modelo de identidad

Se estableció una separación fundamental:

### `token_id`

Identifica una detección concreta dentro de un frame.

### `track_id`

Identifica al jugador persistente a través del tiempo.

Esto permite que una detección pueda cambiar de `token_id` sin perder la identidad representada por `track_id`.

---

# 7. Tracking

El tracking utiliza:

- Hungarian Algorithm;
- `linear_sum_assignment`;
- gating espacial;
- asociación separada para Racing, Rival y GK.

Parámetros actuales:

```text
MAX_DISTANCE = 15 px
LARGE_COST = 10000
```

**MAX_DISTANCE:** distancia máxima permitida para una asociación.

**LARGE_COST:** costo artificialmente elevado para impedir asociaciones consideradas inválidas.

---

## 7.1. Movimiento entre frames

Se calcula:

```text
dx = x_actual - x_anterior
dy = y_actual - y_anterior

distance = sqrt(dx² + dy²)
```

La distancia se expresa en píxeles.

Por ejemplo:

```text
dx = -2
dy = +2

distance ≈ 2,83 px
```

Esto representa desplazamiento visual entre dos frames, no metros ni velocidad real.

---

# 8. Primera validación del tracking

Entre `frame_0000` y `frame_0001` se obtuvieron:

```text
Tracks:            22
Distancia media:   ≈ 0,31 px
Distancia máxima:  ≈ 2,83 px
```

La mayoría de las identidades mantuvieron posiciones prácticamente constantes y no se observaron intercambios evidentes entre jugadores de campo.

Esta prueba validó el mecanismo básico de asociación.

---

# 9. Validación temporal: 31 frames

La prueba siguiente procesó:

```text
frame_0000
...
frame_0030
```

Esto representa:

```text
31 frames observados
30 transiciones de tracking
1 segundo de video
```

La diferencia es importante:

```text
3 frames → 2 transiciones
31 frames → 30 transiciones
```

Cada transición compara un frame con el inmediatamente anterior.

### Resultados

```text
22 matches → 12 transiciones
21 matches → 13 transiciones
20 matches →  5 transiciones
```

Con 22 tracks:

```text
22/22 = 100 %
21/22 ≈ 95,45 %
20/22 ≈ 90,91 %
```

Estos valores representan **cobertura de asociación**, no accuracy global.

---

# 10. Métricas del tracking

| Métrica | Significado |
|---|---|
| **Frames** | Cantidad de imágenes observadas |
| **Transiciones** | Comparaciones entre frames consecutivos |
| **Detecciones** | Candidatos encontrados por el detector |
| **Matches** | Asociaciones aceptadas entre tracks y detecciones |
| **Match coverage** | Matches / tracks activos |
| **Distance** | Desplazamiento de un jugador entre dos frames |
| **Mean distance** | Promedio de desplazamiento de los matches de una transición |
| **Max distance** | Mayor desplazamiento registrado en una transición |
| **dist_total** | Suma de las distancias de todos los matches de una transición |
| **Distancia acumulada** | Suma de desplazamientos de un track durante toda la prueba |
| **Winner score** | Mejor similitud entre un dígito y los templates |
| **Second-best** | Segunda mejor similitud |
| **Gap** | Diferencia entre las dos mejores similitudes |
| **ROI** | Región de la imagen analizada |
| **Radio** | Tamaño visual estimado de una ficha |
| **MAX_DISTANCE** | Límite de distancia utilizado para aceptar asociaciones |

Ninguna de las métricas de distancia representa todavía distancia física en metros. Para eso será necesaria una calibración espacial de la cancha.

---

# 11. Resultado de la prueba de 31 frames

El sistema generó:

```text
output/trajectory_30frames.jpg
```

y:

```text
frame_0001.json
...
frame_0030.json
```

Las mayores distancias acumuladas registradas fueron:

```text
RACING #01 → 33,31 px
RIVAL  #01 → 16,49 px
```

Estos valores indican mayor desplazamiento de la **detección** durante la ventana, pero todavía no permiten determinar si se trata de movimiento real, jitter del detector o una combinación de ambos.

---

# 12. Metodología de trabajo

El desarrollo se realiza mediante un ciclo controlado:

```text
Problema
 ↓
Hipótesis
 ↓
Experimento
 ↓
Medición
 ↓
Inspección visual
 ↓
Diagnóstico
 ↓
Cambio mínimo
 ↓
Revalidación
 ↓
Escalamiento
```

Los principios centrales son:

**Evidencia antes que hipótesis.**  
Una sospecha no se considera diagnóstico hasta ser comprobada.

**Una capa por vez.**  
No se analiza tácticamente algo que todavía no puede detectarse o seguirse de forma fiable.

**Una métrica para cada problema.**  
Detección, identificación y tracking se validan con métricas diferentes.

**No cambiar varias variables simultáneamente.**  
La modificación debe ser lo suficientemente acotada para poder atribuir el resultado.

**No optimizar prematuramente.**  
La complejidad se incorpora cuando una limitación real la justifica.

**No declarar resuelto más de lo demostrado.**  
Un resultado válido sobre una muestra pequeña no implica funcionamiento universal.

**Mantener separadas configuración, medición y conclusión.**  
Por ejemplo, `MAX_DISTANCE = 15` es una configuración; `distance = 2,83 px` es una medición; “el tracking es estable” es una conclusión que requiere evidencia.

---

# 13. Criterio de diagnóstico

Cuando aparece un error, se analiza de abajo hacia arriba:

```text
¿Los datos originales son correctos?
        ↓
¿La detección es correcta?
        ↓
¿La clasificación es correcta?
        ↓
¿La identidad es correcta?
        ↓
¿La asociación es correcta?
        ↓
¿La interpretación es correcta?
```

Esto evita corregir una capa superior cuando el problema está realmente en una inferior.

---

# 14. Estado actual

| Componente | Estado |
|---|---|
| Lectura de video | Funcional |
| ROI | Funcional |
| Detección de jugadores | Funcional inicial |
| Recuperación de detecciones difíciles | Funcional inicial |
| Detección de arqueros | Funcional, requiere validación temporal |
| Clasificación de equipos | Funcional inicial |
| Extracción de dorsales | Funcional inicial |
| Banco de templates | Funcional |
| Matching de dígitos | Funcional inicial |
| Identidad persistente | Funcional |
| JSON por frame | Funcional |
| Tracking 1 transición | Validado |
| Tracking 30 transiciones / 31 frames | En validación |
| Predicción por velocidad | Pendiente |
| Coast mode | Pendiente |
| Tracking largo | Pendiente |
| Detección de eventos | Pendiente |
| Análisis táctico | Pendiente |
| Interfaz gráfica | Pendiente |

---

# 15. Próximo paso

El próximo experimento no consiste todavía en agregar velocidad, `coast mode`, reidentificación ni modificar el Hungarian.

Primero debe auditarse cada transición donde:

```text
matches < 22
```

para determinar:

```text
qué track quedó sin match
qué detección quedó libre
distancia al candidato más cercano
bloque afectado:
Racing / Rival / GK
```

Con esa evidencia se podrá determinar si el problema está en:

- detección;
- arqueros;
- jugadores de campo;
- gating;
- asociación.

Después se aplicará únicamente la corrección necesaria y se repetirá exactamente la misma prueba antes de ampliar la ventana.

---

# 16. Roadmap

```text
VALIDACIÓN 31 FRAMES
        ↓
AUDITORÍA DE PÉRDIDAS
        ↓
CORRECCIÓN ESPECÍFICA
        ↓
100 TRANSICIONES
        ↓
TRACKING LARGO
        ↓
CALIBRACIÓN ESPACIAL
        ↓
TRAYECTORIAS
        ↓
EVENTOS
        ↓
ANÁLISIS TÁCTICO
```

---

# 17. Conclusión

FM24Analyzer ya cuenta con un pipeline funcional que transforma una captura de FM24 en información estructurada sobre **22 identidades**, incluyendo detección, clasificación, dorsal y una primera capa de tracking temporal.

Los componentes básicos ya demostraron funcionar en muestras controladas. El principal desafío actual es la **robustez temporal de la asociación**, no la ausencia de infraestructura.

La metodología del proyecto permanece deliberadamente conservadora:

> **Primero entender. Después medir. Luego decidir. Finalmente implementar.**

El siguiente avance debe surgir de la auditoría de las transiciones imperfectas, no de introducir complejidad antes de conocer su necesidad.