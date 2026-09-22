# FM24Analyzer
## Informe maestro del proyecto

**Proyecto:** FM24Analyzer  
**Tipo:** Sistema de visión por computadora aplicado a Football Manager 24  
**Objetivo final:** transformar una grabación de un partido en datos estructurados, reconstruir el comportamiento de los jugadores y generar análisis táctico automatizado.  
**Estado actual:** prototipo funcional en etapa de validación temporal del tracking.  
**Entorno:** Windows · Python 3.13 · OpenCV 5.0.0 · NumPy · Pandas · SciPy  
**Última prueba:** 31 frames observados, 30 transiciones de tracking, equivalentes a 1 segundo de video.

---

# 1. Resumen ejecutivo

FM24Analyzer nació como un proyecto para analizar partidos de Football Manager 24 a partir de video, evitando depender inicialmente de modelos de inteligencia artificial pesados o servicios externos.

La idea central es convertir una imagen de un partido en información cada vez más estructurada:

```text
VIDEO
 ↓
CANCHA
 ↓
JUGADORES
 ↓
EQUIPOS
 ↓
DORSALES
 ↓
IDENTIDADES
 ↓
MOVIMIENTO
 ↓
TRAYECTORIAS
 ↓
EVENTOS
 ↓
ESTRUCTURA TÁCTICA
 ↓
ANÁLISIS
```

Durante el desarrollo ya se construyó y validó buena parte de las primeras capas.

El sistema actualmente puede:

- leer el video;
- aislar la cancha;
- detectar fichas de jugadores;
- recuperar detecciones difíciles;
- detectar arqueros mediante un detector específico;
- clasificar Racing, Rival y arquero;
- extraer dorsales;
- reconocer dígitos mediante templates;
- generar una identidad persistente mediante `track_id`;
- asociar jugadores entre frames mediante Hungarian + gating;
- guardar estados en JSON;
- generar visualizaciones de trayectorias.

Los resultados más importantes obtenidos hasta ahora son:

```text
22 jugadores detectados en la muestra inicial
0 falsos positivos
0 duplicados
2 arqueros recuperados
26 dígitos extraídos
21 templates construidos
23/26 dígitos correctamente reconocidos
88,46 % de exactitud en el benchmark de dorsales
22/22 asociaciones correctas en la primera transición
31 frames observados en la prueba temporal
30 transiciones de tracking
```

El proyecto todavía no está terminado.

La principal deuda técnica actual es demostrar que el tracking es suficientemente robusto durante períodos largos y, a partir de allí, construir la capa superior de eventos y análisis táctico.

---

# 2. Objetivo del proyecto

El objetivo final de FM24Analyzer es producir una representación estructurada de un partido a partir de un video.

El sistema debería terminar pudiendo responder preguntas como:

### Sobre los jugadores

- ¿Dónde está cada jugador?
- ¿Cuál es su dorsal?
- ¿A qué equipo pertenece?
- ¿Qué rol tiene?
- ¿Dónde estuvo durante el partido?
- ¿Cuánto se desplazó?
- ¿Qué zonas ocupó?

### Sobre la estructura

- ¿Qué formación utiliza cada equipo?
- ¿Cómo cambia la formación con y sin pelota?
- ¿Qué jugadores forman cada línea?
- ¿Qué amplitud tiene el equipo?
- ¿Qué profundidad tiene?
- ¿Qué tan compacto está?

### Sobre el comportamiento

- ¿Cuándo presiona?
- ¿Dónde recupera?
- ¿Cómo inicia una transición?
- ¿Qué ocurre después de perder la pelota?
- ¿Cuándo cambia de estructura?
- ¿Qué jugador abandona su zona?
- ¿Cómo reaccionan los laterales, extremos y mediocampistas?

### Sobre el partido

- ¿Qué patrones tácticos aparecen?
- ¿Cuándo cambian?
- ¿Qué secuencias se repiten?
- ¿Qué diferencias aparecen entre distintos momentos del partido?

El objetivo final no es simplemente detectar círculos. Los círculos son el principio del problema.

---

# 3. Alcance técnico completo

El proyecto se divide en ocho grandes capas.

```text
FASE 1
Captura y preparación
        ↓
FASE 2
Percepción visual
        ↓
FASE 3
Identificación
        ↓
FASE 4
Tracking temporal
        ↓
FASE 5
Reconstrucción espacial
        ↓
FASE 6
Detección de eventos
        ↓
FASE 7
Análisis táctico
        ↓
FASE 8
Producto final
```

Cada fase depende de la anterior.

La metodología impide avanzar simplemente porque “se puede”. Una capa debe alcanzar un nivel suficiente de confiabilidad antes de convertirse en fundamento de la siguiente.

---

# 4. Lo que ya hicimos

## 4.1. Preparación del entorno

Se estableció el entorno de desarrollo:

```text
Python 3.13
OpenCV 5.0.0
NumPy
Pandas
SciPy
```

El proyecto funciona localmente en Windows.

También se resolvió el problema inicial de las diferentes versiones de Python instaladas, seleccionando explícitamente Python 3.13 para el proyecto.

---

# 5. Procesamiento del video

Se creó `video_info.py` para inspeccionar las características del archivo.

Video actual:

```text
Resolución: 1280 × 720
FPS: 30
Frames: 2172
Duración: 72,40 s
```

También se desarrolló `extract_frame.py` para extraer imágenes individuales y trabajar con frames concretos.

Esto permitió pasar de analizar el video como un objeto abstracto a trabajar sobre imágenes controladas.

---

# 6. Aislamiento de la cancha

Se desarrolló `select_field.py` para seleccionar manualmente la región útil.

ROI actual:

```text
X = 183
Y = 48
Ancho = 913
Alto = 623
```

Esto fue fundamental porque eliminó gran parte de la interfaz de FM24 del problema de detección.

La cancha pasó a ser el espacio principal de análisis.

---

# 7. Detección de jugadores

Se desarrolló un detector basado en HoughCircles.

El tamaño observado de los tokens fue:

```text
Radio mínimo: 7 px
Radio máximo: 8 px
Media:        7,26 px
Mediana:      7 px
```

En la muestra inicial:

```text
22 detecciones válidas
0 falsos positivos
0 duplicados
```

Se añadió además un segundo detector sensible para recuperar fichas difíciles.

Esto resolvió el caso particular del jugador parcialmente cubierto por elementos gráficos.

---

# 8. Detección específica de arqueros

Los arqueros presentan características visuales diferentes a los jugadores de campo.

Se desarrolló un detector específico utilizando:

- CLAHE;
- Hough;
- restricciones espaciales sobre las áreas de penal.

Resultado inicial:

```text
2 arqueros recuperados
0 falsos positivos
```

Este detector funciona como componente independiente, pero todavía debe demostrar estabilidad temporal durante secuencias largas.

---

# 9. Clasificación de equipos

Se analizaron los colores mediante HSV.

Se observaron patrones diferentes para:

- Racing;
- Rival;
- arqueros.

Se construyó una primera clasificación por reglas:

```text
S < 30
→ Arquero

V > 180
→ Rival

V <= 180 y S >= 50
→ Racing
```

En el frame inicial se obtuvo:

```text
10 jugadores de campo Racing
10 jugadores de campo Rival
2 arqueros
```

También se evitó asumir que el lado de la cancha define permanentemente al equipo, porque durante un partido los equipos cambian de lado.

---

# 10. Extracción de dorsales

En lugar de utilizar OCR genérico como primera solución, se diseñó un extractor específico para las fichas de FM24.

El proceso pasó por varias iteraciones hasta alcanzar una máscara suficientemente estable:

```text
recorte
→ reescalado
→ HSV
→ máscara interior
→ componentes
→ separación de dígitos
```

La versión final de extracción permitió trabajar con los 22 tokens de la muestra.

Se identificaron:

```text
18 dorsales de un dígito
4 dorsales de dos dígitos
26 dígitos en total
```

Esto estableció la base para construir reconocimiento por template.

---

# 11. Banco de templates

Se construyó un banco curado de:

```text
21 templates
```

La selección fue deliberada.

Se descartaron muestras contaminadas o deformadas y se conservaron únicamente ejemplos suficientemente limpios.

Se recuperó específicamente una muestra confiable del `0`, descartando otra que presentaba contaminación.

---

# 12. Reconocimiento de dorsales

El sistema utiliza:

```text
cv2.matchTemplate
TM_CCOEFF_NORMED
```

y calcula:

```text
winner score
second-best score
gap
```

El `gap` permite conocer cuánto mejor es la mejor coincidencia respecto de la segunda.

Esto permite distinguir:

```text
coincidencia clara
```

de:

```text
coincidencia ambigua
```

Benchmark actual:

```text
23 / 26 correctos
88,46 % de exactitud
```

Los errores quedaron concentrados en muestras visualmente degradadas.

La decisión metodológica fue no seguir perfeccionando indefinidamente esta capa antes de construir el tracking.

---

# 13. Modelo de identidad

Se estableció una distinción arquitectónica fundamental:

```text
token_id
```

representa una detección concreta dentro de un frame.

```text
track_id
```

representa la identidad persistente del jugador a lo largo del tiempo.

Esta separación permite que el detector entregue identificadores diferentes sin destruir la identidad temporal.

Esto es una de las bases estructurales del proyecto.

---

# 14. JSON estructurado

Se creó `build_match_json.py` para transformar las detecciones en una representación estructurada.

Cada jugador puede contener:

```text
identity
state
detection
```

Dentro de `identity`:

```text
team
role
number
confidence
```

Dentro de `state`:

```text
frame
timestamp
x
y
radius
dx
dy
distance
```

Esto permite pasar de imágenes a datos que posteriormente pueden ser analizados matemáticamente.

---

# 15. Primer tracking

Se implementó un tracker basado en:

```text
Hungarian Algorithm
linear_sum_assignment
gating por distancia
```

El sistema separa las asociaciones en:

```text
Racing
Rival
GK
```

Parámetros actuales:

```text
MAX_DISTANCE = 15 px
LARGE_COST = 10000
```

La primera prueba fue:

```text
frame 0 → frame 1
```

Resultado:

```text
22 tracks
22 asociaciones
```

Distancia media:

```text
≈ 0,31 px
```

Distancia máxima:

```text
≈ 2,83 px
```

El resultado validó el mecanismo básico.

---

# 16. Primera prueba temporal

Después del primer paso se realizó una prueba más larga.

Se procesaron:

```text
frame_0000
hasta
frame_0030
```

Esto significa:

```text
31 frames observados
30 transiciones
1 segundo de video
```

La distribución fue:

```text
22 matches → 12 transiciones
21 matches → 13 transiciones
20 matches →  5 transiciones
```

Esto demuestra que la asociación funciona durante una ventana corta, pero también muestra que existen transiciones en las que uno o dos tracks no se asocian.

Todavía no se determinó cuál es exactamente la causa.

---

# 17. Qué está terminado

Dentro del alcance actual, las siguientes piezas pueden considerarse construidas y funcionales:

| Componente | Estado |
|---|---|
| Entorno de desarrollo | ✅ |
| Lectura de video | ✅ |
| Extracción de frames | ✅ |
| ROI de cancha | ✅ |
| Detección general | ✅ |
| Recuperación de detecciones difíciles | ✅ |
| Detector específico de arqueros | ✅ inicial |
| Clasificación por equipo | ✅ inicial |
| Extracción de dorsales | ✅ inicial |
| Banco de templates | ✅ |
| Reconocimiento de dígitos | ✅ inicial |
| Modelo `token_id` / `track_id` | ✅ |
| JSON estructurado | ✅ |
| Hungarian + gating | ✅ |
| Tracking frame a frame | ✅ inicial |
| Visualización de trayectorias | ✅ inicial |

La palabra importante en algunos casos es **inicial**. Significa que el componente existe y funciona, pero todavía no se considera suficientemente validado para cualquier situación de un partido completo.

---

# 18. Qué NO está terminado

Todavía falta construir y validar una cantidad importante de trabajo.

## Tracking robusto

Falta:

- auditar las pérdidas de asociación;
- resolver las causas demostradas;
- validar o ajustar el gating;
- determinar si realmente hace falta predicción;
- implementar `coast mode` si las pruebas lo justifican;
- manejar oclusiones;
- recuperar tracks después de pérdidas prolongadas;
- probar durante ventanas mucho mayores;
- validar un partido completo.

## Identificación robusta

Falta mejorar:

- reconocimiento de dorsales difíciles;
- confianza de identidad;
- reidentificación después de oclusiones;
- situaciones donde el dorsal no pueda leerse.

## Coordenadas del campo

Actualmente trabajamos con píxeles.

Falta:

- definir coordenadas normalizadas del campo;
- mapear posiciones a una representación consistente;
- establecer una relación con dimensiones reales;
- resolver posibles distorsiones de perspectiva.

## Eventos

Todavía falta detectar automáticamente:

- movimientos relevantes;
- cambios de posición;
- agrupamientos;
- separación de líneas;
- recuperaciones;
- transiciones;
- situaciones de presión;
- cambios estructurales.

## Análisis táctico

Falta construir el sistema capaz de inferir:

- formación;
- estructura ofensiva;
- estructura defensiva;
- roles espaciales;
- altura del bloque;
- amplitud;
- profundidad;
- compactación;
- presión;
- ocupación de espacios;
- cambios tácticos.

## Producto final

También falta:

- interfaz;
- configuración de análisis;
- procesamiento de partidos completos;
- visualizaciones;
- informes;
- almacenamiento organizado;
- manejo de errores;
- documentación de usuario.

---

# 19. Qué significa realmente "100 %"

El 100 % del proyecto no significa simplemente:

> “el programa detecta jugadores”.

El sistema estará completo cuando exista un flujo integrado:

```text
video
 ↓
detección
 ↓
identificación
 ↓
tracking estable
 ↓
coordenadas normalizadas
 ↓
eventos
 ↓
estructura táctica
 ↓
análisis
 ↓
informe final
```

Además, una versión completa debe poder procesar un partido largo de forma reproducible, no solamente una captura corta.

Por lo tanto, el 100 % requiere tanto **funcionalidad** como **robustez**, **validación** y **usabilidad**.

---

# 20. Criterios de finalización del proyecto

Para declarar FM24Analyzer terminado, cada capa debería cumplir cuatro condiciones:

### 1. Funcionalidad

La función existe y produce el resultado esperado.

### 2. Validación

Fue probada en una cantidad suficiente de datos.

### 3. Robustez

No depende de una única captura favorable.

### 4. Integración

Forma parte del pipeline completo.

Una herramienta que funciona perfectamente durante 30 frames pero falla al procesar un partido de 90 minutos no se considera terminada.

---

# 21. Roadmap completo

## Fase 0. Fundaciones

**Objetivo:** establecer entorno y estructura.

```text
Python
OpenCV
dependencias
estructura de carpetas
video de prueba
```

**Estado:** completado.

---

## Fase 1. Percepción visual básica

**Objetivo:** detectar correctamente las fichas.

### Tareas

- ROI;
- Hough general;
- detector sensible;
- detector de arqueros;
- eliminación de falsos positivos;
- combinación de detectores.

**Estado:** funcional inicial.

### Criterio de salida

Detectar de manera estable los 22 jugadores en una variedad razonable de frames.

---

## Fase 2. Clasificación e identificación

**Objetivo:** saber quién es cada ficha.

### Tareas

- clasificación Racing/Rival/GK;
- extracción de dorsales;
- templates;
- reconocimiento;
- confidence;
- manejo de casos ambiguos.

**Estado:** funcional inicial.

### Criterio de salida

Identidad suficientemente estable para usarla como entrada del tracker.

---

## Fase 3. Tracking robusto

**Objetivo:** mantener la identidad durante todo el video.

### Tareas inmediatas

1. Auditar tracks sin match.
2. Identificar detecciones libres.
3. Identificar bloque afectado.
4. Determinar causa.
5. Corregir solamente esa causa.
6. Repetir benchmark.

### Después

- 100 transiciones;
- ventanas largas;
- coast mode si hace falta;
- predicción por velocidad si hace falta;
- manejo de oclusiones;
- reidentificación.

**Estado:** etapa actual.

### Criterio de salida

Tracking estable durante secuencias largas y, finalmente, durante un partido completo.

---

## Fase 4. Reconstrucción espacial

**Objetivo:** convertir píxeles en posiciones útiles para análisis futbolístico.

### Tareas

- coordenadas normalizadas;
- referencia del campo;
- calibración;
- orientación;
- zonas del terreno;
- coordenadas comparables entre partidos.

**Estado:** pendiente.

### Criterio de salida

Cada jugador debe disponer de una posición consistente dentro de un sistema espacial del campo.

---

## Fase 5. Trayectorias y movimiento

**Objetivo:** transformar posiciones en comportamiento temporal.

### Tareas

- trayectoria individual;
- velocidad aproximada;
- aceleración aproximada;
- distancia;
- ocupación espacial;
- zonas frecuentes;
- cambios de posición.

**Estado:** pendiente.

### Criterio de salida

Poder describir el movimiento de cada jugador durante cualquier segmento del partido.

---

## Fase 6. Detección de eventos

**Objetivo:** identificar cambios significativos del juego.

### Tareas

- cambios bruscos de posición;
- avance de líneas;
- retrocesos;
- presión;
- pérdida/recuperación;
- transiciones;
- agrupamientos;
- cambios estructurales;
- secuencias repetidas.

**Estado:** pendiente.

### Criterio de salida

El sistema debe poder dividir el partido en segmentos relevantes en lugar de tratarlo como una secuencia homogénea de frames.

---

## Fase 7. Análisis táctico

**Objetivo:** transformar datos de movimiento en conceptos futbolísticos.

### Tareas

- detección de formación;
- estructura con pelota;
- estructura sin pelota;
- líneas;
- bloque;
- amplitud;
- profundidad;
- compactación;
- ocupación de espacios;
- comportamiento individual;
- relaciones entre jugadores;
- cambios de sistema;
- presión;
- transiciones.

**Estado:** pendiente.

### Criterio de salida

Poder describir de forma reproducible estructuras y comportamientos tácticos observables.

---

## Fase 8. Motor de análisis

**Objetivo:** convertir eventos tácticos en conclusiones estructuradas.

### Tareas

- comparación entre períodos;
- comparación entre equipos;
- comparación entre partidos;
- detección de patrones;
- métricas agregadas;
- indicadores tácticos;
- generación de conclusiones.

**Estado:** pendiente.

### Criterio de salida

Generar un análisis estructurado a partir de los datos procesados.

---

## Fase 9. Visualización

**Objetivo:** hacer interpretable el resultado.

### Tareas

- mapa de posiciones;
- trayectorias;
- heatmaps;
- líneas de equipo;
- zonas ocupadas;
- eventos sobre timeline;
- comparativas;
- reproducción sincronizada.

**Estado:** pendiente.

### Criterio de salida

Un usuario debe poder entender visualmente qué ocurrió.

---

## Fase 10. Informe automático

**Objetivo:** generar un informe final del partido.

El sistema debería poder producir:

```text
Resumen del partido
↓
Formaciones
↓
Estructura ofensiva
↓
Estructura defensiva
↓
Presión
↓
Transiciones
↓
Cambios tácticos
↓
Comportamiento individual
↓
Conclusiones
```

**Estado:** pendiente.

---

## Fase 11. Interfaz y producto

**Objetivo:** convertir el prototipo en una herramienta utilizable.

### Tareas

- cargar video;
- seleccionar parámetros;
- iniciar análisis;
- mostrar progreso;
- revisar resultados;
- visualizar partido;
- exportar informe;
- manejar errores;
- conservar sesiones.

**Estado:** pendiente.

---

## Fase 12. Validación final

**Objetivo:** demostrar que el sistema funciona fuera de la muestra original.

### Tareas

- diferentes partidos;
- distintos equipos;
- cambios de campo;
- distintos niveles de movimiento;
- oclusiones;
- cambios de cámara;
- diferentes interfaces;
- diferentes situaciones de partido.

**Estado:** pendiente.

### Criterio de salida

El sistema debe funcionar de forma reproducible más allá del video utilizado para desarrollar el prototipo.

---

# 22. Roadmap resumido

```text id="4bxr1k"
[✅] ENTORNO
      ↓
[✅] VIDEO / ROI
      ↓
[✅] DETECCIÓN INICIAL
      ↓
[✅] CLASIFICACIÓN
      ↓
[✅] DORSALES
      ↓
[✅] IDENTIDAD
      ↓
[🟡] TRACKING ROBUSTO
      ↓
[⬜] COORDENADAS DEL CAMPO
      ↓
[⬜] TRAYECTORIAS
      ↓
[⬜] EVENTOS
      ↓
[⬜] ANÁLISIS TÁCTICO
      ↓
[⬜] MOTOR DE ANÁLISIS
      ↓
[⬜] VISUALIZACIÓN
      ↓
[⬜] INFORME AUTOMÁTICO
      ↓
[⬜] INTERFAZ
      ↓
[⬜] VALIDACIÓN MULTIPARTIDO
      ↓
[100 %] FM24Analyzer
```

---

# 23. Prioridad real de trabajo

No todas las tareas pendientes tienen la misma prioridad.

## Prioridad crítica

**Tracking robusto.**

Sin esto no hay trayectorias confiables.

## Prioridad alta

**Coordenadas espaciales y trayectorias.**

Son la base de todo análisis táctico.

## Prioridad media

**Eventos y estructuras tácticas.**

Dependen de las capas anteriores.

## Prioridad posterior

**Visualización, informes e interfaz.**

Son importantes para convertir el sistema en producto, pero no solucionan problemas de percepción.

## Prioridad condicional

**Deep learning, YOLO, modelos avanzados, IA generativa.**

Solo deben incorporarse cuando una limitación concreta demuestre que son necesarios.

---

# 24. Deuda técnica actual

El proyecto todavía tiene varias cuestiones pendientes que no son funcionalidades nuevas, sino consolidación.

### Código

Los scripts todavía contienen lógica experimental repetida.

Ejemplo:

```text
detección
clasificación
tracking
```

aparecen parcialmente duplicados entre distintos scripts.

Más adelante conviene separar:

```text
vision_detector.py
classifier.py
digit_reader.py
tracker.py
models.py
pipeline.py
```

### Configuración

Parámetros como:

```text
ROI
Hough
HSV
gating
```

deberían terminar centralizados y configurables.

### Tests

Actualmente existe principalmente validación manual y benchmarks específicos.

Será necesario agregar:

- tests unitarios;
- casos de regresión;
- datasets de referencia;
- benchmarks repetibles.

### Logs

Los scripts deberán evolucionar hacia un sistema de logging más estructurado.

### Datos

Conviene definir un formato estable para:

- detección;
- identidad;
- trayectoria;
- eventos;
- análisis.

---

# 25. Riesgos técnicos principales

Los principales riesgos del proyecto son:

### 1. Detección inestable

Puede generar errores aguas arriba.

### 2. Oclusiones

Un jugador puede quedar parcialmente cubierto.

### 3. Cambios visuales

La interfaz puede variar entre situaciones.

### 4. Identidad incorrecta

Un error de dorsal puede contaminar el tracking.

### 5. Pérdida de asociación

Puede romper una trayectoria.

### 6. Interpretación excesiva

Un patrón geométrico no necesariamente implica automáticamente una intención táctica.

### 7. Generalización

Un sistema ajustado al video de prueba puede no funcionar igual en otros partidos.

### 8. Complejidad creciente

El análisis táctico será considerablemente más complejo que detectar tokens.

Por eso la metodología incremental no es solamente una preferencia. Es una forma de controlar estos riesgos.

---

# 26. Criterio de calidad del producto final

El sistema final no debería evaluarse únicamente por una única cifra.

La calidad deberá observarse en varias dimensiones:

```text
Percepción
→ ¿Detecta correctamente?

Identidad
→ ¿Sabe quién es quién?

Tracking
→ ¿Mantiene identidades?

Espacio
→ ¿Ubica correctamente?

Eventos
→ ¿Detecta cambios significativos?

Táctica
→ ¿Describe estructuras observables?

Generalización
→ ¿Funciona fuera del video de desarrollo?

Usabilidad
→ ¿Una persona puede utilizarlo?
```

Solo cuando todas estas capas sean suficientemente sólidas tendrá sentido hablar de un sistema terminado.

---

# 27. Definición de éxito del proyecto

FM24Analyzer puede considerarse terminado cuando sea capaz de recibir:

```text
un video de un partido
```

y producir automáticamente:

```text
1. jugadores detectados
2. identidades
3. posiciones
4. trayectorias
5. eventos
6. estructuras tácticas
7. análisis
8. visualizaciones
9. informe final
```

de forma reproducible y con un nivel de error conocido.

Ese último punto es importante.

El objetivo no es que el sistema sea mágicamente perfecto. El objetivo es que sus resultados sean suficientemente confiables, medibles y explicables como para utilizarlos.

---

# 28. Estado global del proyecto

La situación actual puede resumirse así:

```text
PERCEPCIÓN
██████████████████░░  ~90 %

IDENTIFICACIÓN
████████████████░░░░  ~80 %

TRACKING
████████░░░░░░░░░░░░  ~40 %

ESPACIO
██░░░░░░░░░░░░░░░░░░  ~10 %

TRAYECTORIAS
██░░░░░░░░░░░░░░░░░░  ~10 %

EVENTOS
░░░░░░░░░░░░░░░░░░░░   ~0 %

ANÁLISIS TÁCTICO
░░░░░░░░░░░░░░░░░░░░   ~0 %

PRODUCTO FINAL
░░░░░░░░░░░░░░░░░░░░   ~0 %
```

Estos porcentajes son **estimaciones de avance por capa**, no métricas científicas de calidad ni porcentajes exactos de código completado.

La mayor parte del trabajo futuro se encuentra en las capas superiores, no en la detección básica.

---

# 29. Próximo paso inmediato

El próximo trabajo concreto es uno solo:

## Auditar las pérdidas de tracking

Para todas las transiciones con:

```text
matches < 22
```

hay que registrar:

```text
transición
track_id perdido
equipo
dorsal
rol
detección libre
distancia al candidato
bloque afectado
```

El objetivo es responder:

> **¿Qué está fallando realmente?**

Solo después se decidirá si corresponde implementar:

```text
coast mode
predicción
velocidad
reidentificación
ajuste de gating
mejora de detección
```

Esto mantiene exactamente la metodología que se utilizó durante todo el proyecto:

> **No optimizar lo que todavía no entendemos.**

---

# 30. Conclusión general

FM24Analyzer dejó de ser una idea y pasó a ser un prototipo técnico funcional.

Hoy existe una cadena real que transforma:

```text
video
```

en:

```text
detecciones
→ equipos
→ dorsales
→ identidades
→ tracking
→ JSON
```

Se resolvieron los problemas fundamentales de la primera etapa y se construyeron las herramientas necesarias para continuar.

El proyecto todavía está lejos del 100 %, pero ahora la distancia restante está estructurada y puede dividirse en etapas concretas.

El núcleo pendiente es pasar de:

**“sé dónde está cada ficha”**

a:

**“sé quién es, dónde está, cómo se mueve, qué está haciendo el equipo y qué patrón táctico representa ese comportamiento”.**

El roadmap completo es, por lo tanto:

```text id="c9l0r8"
VIDEO
 ↓
PERCEPCIÓN
 ↓
IDENTIDAD
 ↓
TRACKING ROBUSTO
 ↓
CALIBRACIÓN ESPACIAL
 ↓
TRAYECTORIAS
 ↓
EVENTOS
 ↓
ESTRUCTURA TÁCTICA
 ↓
ANÁLISIS
 ↓
VISUALIZACIÓN
 ↓
INFORME
 ↓
INTERFAZ
 ↓
VALIDACIÓN MULTIPARTIDO
 ↓
FM24Analyzer 100 %
```

Y la regla que sigue gobernando todo el desarrollo continúa siendo:

> **Primero entender. Después medir. Luego decidir. Finalmente implementar.**