# Estudio de conceptos — RAG-against-the-machine-

## (a) Proyecto y objetivo

**Proyecto:** RAG-against-the-machine- (subject de la 42 "RAG against the machine", v2.0).

**Qué es:** un sistema RAG que responde preguntas sobre el código de vLLM (vllm-0.10.1). Trocea los archivos .py, .md y .txt y los indexa con BM25 más embeddings semánticos en un almacén versionado. Después recupera las k fuentes más relevantes y genera respuestas basadas en ellas con Qwen3-0.6B. Se usa desde una CLI con Fire o desde un servidor FastAPI local.

**Objetivo medible:** recall@5 >= 80 % en preguntas de documentación y >= 50 % en preguntas de código; indexado completo en 5 minutos o menos; 200 preguntas en 90 segundos o menos; respuestas fieles a sus fuentes; ningún traceback sin manejar. Se construyen además los cinco bonus: índice semántico, búsqueda híbrida con RRF, indexado incremental, caché y API HTTP local.

**Para quién:** los evaluadores de la 42 y la moulinette (usuario principal) y los reclutadores que revisan el repositorio (usuario secundario).

**Cómo están citadas las filas:** x = prohibitions (prohibiciones), c = constraints (restricciones técnicas), g = goals (objetivos medibles).

---

## (b) Conceptos

### 1. RAG (Retrieval-Augmented Generation)

- **Nivel:** partial
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** un patrón que, antes de que un modelo responda, busca fragmentos relevantes en una base de documentos y se los pasa como contexto.
  - **Qué problema resuelve:** el problema de un modelo que responde solo con lo que aprendió: no conoce tus datos y puede alucinar.
  - **Cómo funciona:** las cuatro etapas: indexar, recuperar, aumentar y generar, y qué hace cada una.
  - **Opciones y compromisos:** preguntar al modelo sin contexto frente a darle fuentes recuperadas; de qué depende la calidad de la respuesta.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** es la arquitectura de todo el proyecto (spec punto 1: un sistema RAG con cuatro etapas: indexar, recuperar, aumentar y generar). En la defensa hay que explicar cada etapa.
  - **Filas que lo tocan:** g1 (recall@5), g4 (respuestas fieles), c8 (Qwen3-0.6B), c10 (un chunker por tipo).
  - **Decidido en la spec:** cuatro etapas sobre el código de vLLM, con los comandos de la spec.
  - **Abierto:** nada propio de este concepto; lo abierto está en cada etapa.

### 2. Chunking

- **Nivel:** partial
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** dividir un documento en fragmentos que se indexan y se recuperan por separado.
  - **Qué problema resuelve:** un documento entero mete ruido al buscar y puede no caber en el contexto del modelo.
  - **Cómo funciona:** qué entra, qué sale y qué hay que conservar de cada fragmento para poder citarlo; qué hacer si una unidad supera el máximo.
  - **Opciones y compromisos:** tamaño fijo, solape y corte por estructura; fragmentos grandes frente a pequeños.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.1 (index: tres estrategias de chunking y la regla del tamaño de chunk) y c10 (un chunker por tipo). Es lo que más influye en g1 (recall@5), y el subject pide justificar la estrategia en el README.
  - **Filas que lo tocan:** c10 (un chunker por tipo), x2 (ninguna fuente de más de 2000 caracteres), g1 (recall@5), c15 (README: sección Chunking strategy).
  - **Decidido en la spec:** un chunker por tipo (.py, .md, .txt); 2000 caracteres es un techo, no un objetivo; el tamaño se elige midiendo recall@5; si se mide el corte estructural, no se juntan unidades pequeñas.
  - **Abierto:** el tamaño ganador (pendiente 29) y la unidad natural de cada .txt (pendiente 43).

### 3. BM25 and tokenization

- **Nivel:** partial
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** una función de ranking léxico que puntúa un texto según los términos de la consulta que contiene.
  - **Qué problema resuelve:** ordenar documentos por relevancia a partir de palabras exactas, sin un modelo.
  - **Cómo funciona:** la frecuencia del término con saturación, el IDF, la normalización por longitud, y la tokenización.
  - **Opciones y compromisos:** léxico frente a semántico; distintas formas de tokenizar y lo que encuentra o pierde cada una.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.1 (método de recuperación: al menos TF-IDF o BM25; lo que se guarda al indexar decide qué se puede encontrar) y spec punto 4 (BM25 por defecto). Es el buscador obligatorio y el método por defecto de search, search_dataset y answer.
  - **Filas que lo tocan:** c9 (interfaz de retriever), g1 (recall@5), g3 (200 preguntas en 90 s).
  - **Decidido en la spec:** es el método por defecto; una pregunta sin ningún token del vocabulario se rechaza (spec 4.2, caso 3).
  - **Abierto:** las opciones del tokenizador para identificadores (pendiente 44).

### 4. Recall@k and IoU

- **Nivel:** partial
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** recall@k es la proporción de fuentes correctas que aparecen en los k primeros resultados; IoU es el solapamiento de dos rangos dividido por su unión.
  - **Qué problema resuelve:** medir si un buscador encuentra lo correcto, con un criterio que admite coincidencias parciales.
  - **Cómo funciona:** calcular recall@k y calcular IoU a mano con dos rangos; qué pasa con una pregunta sin fuentes correctas.
  - **Opciones y compromisos:** qué mide recall frente a precisión; efecto de subir k o de exigir más solapamiento.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec punto 3 (definición de recall@k: mismo archivo y solapamiento del rango de caracteres con IoU > 0.05) y 4.6 (evaluate). Hace falta para decidir los tamaños de chunk (pendiente 29) y para leer lo que dicen evaluate y la moulinette.
  - **Filas que lo tocan:** g1 (recall@5), x1 (no usar la moulinette), x2 (ninguna fuente de más de 2000 caracteres).
  - **Decidido en la spec:** una fuente cuenta con el mismo file_path e IoU > 0.05; evaluate solo informa Recall@N con N <= k y excluye las preguntas sin fuentes.
  - **Abierto:** nada propio de este concepto.

### 5. Embeddings and cosine similarity

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** un vector que representa el significado de un texto; la similitud coseno mide el ángulo entre dos vectores.
  - **Qué problema resuelve:** encontrar textos parecidos aunque no compartan palabras.
  - **Cómo funciona:** cómo un modelo convierte texto en un vector, cómo se calcula el coseno y por qué con vectores normalizados basta el producto escalar.
  - **Opciones y compromisos:** búsqueda semántica frente a léxica; qué hacer con un texto más largo que lo que lee el modelo; búsqueda exacta frente a aproximada.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec punto 5 (embeddings semánticos: all-MiniLM-L6-v2 en CPU, límite de 256 tokens, búsqueda coseno por fuerza bruta en numpy) y c7 (embeddings semánticos). Es el bonus 1 y la base del híbrido. Tú decides con las mediciones de los pendientes 17 (comparar fastembed y sentence-transformers) y 34 (truncado a 256 tokens).
  - **Filas que lo tocan:** c7 (embeddings semánticos), g2 (indexado en 5 min), g5 (búsqueda híbrida), c18 (máquina solo CPU).
  - **Decidido en la spec:** all-MiniLM-L6-v2 en CPU, límite de 256 tokens, búsqueda coseno por fuerza bruta con numpy.
  - **Abierto:** la librería (pendiente 17) y truncar o usar ventanas de 256 tokens (pendiente 34).

### 6. Reciprocal Rank Fusion (hybrid retrieval)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** un método para unir varias listas ordenadas en una sola.
  - **Qué problema resuelve:** combinar rankings cuyas puntuaciones están en escalas distintas.
  - **Cómo funciona:** la suma de 1/(c + posición) por lista, el efecto de c y un ejemplo calculado a mano.
  - **Opciones y compromisos:** unir posiciones frente a unir puntuaciones.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec punto 4 (método de recuperación: el híbrido une los rankings léxico y semántico con RRF, c = 100 salvo que el recall medido favorezca 60) y c9 (interfaz de retriever). Es el bonus 2. Une posiciones y no puntuaciones porque BM25 y el coseno están en escalas distintas.
  - **Filas que lo tocan:** c9 (interfaz de retriever), g5 (búsqueda híbrida).
  - **Decidido en la spec:** el híbrido une BM25 y embeddings con RRF, y cae a bm25 con aviso si falla la parte semántica.
  - **Abierto:** c = 100 frente a c = 60, según el recall medido (pendiente 38).

### 7. LLM generation and prompting (Qwen3-0.6B)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** generar texto con un modelo de lenguaje a partir de un prompt.
  - **Qué problema resuelve:** obtener una respuesta en lenguaje natural que se apoye en un contexto dado.
  - **Cómo funciona:** qué son los tokens y la ventana de contexto; cómo un prompt limita al modelo a las fuentes; cómo se genera token a token.
  - **Opciones y compromisos:** modelos grandes frente a pequeños en CPU; qué hacer si el contexto no cabe; razonamiento visible (thinking) o no.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.4 (answer: presupuesto de tokens, modo thinking, quitar el bloque <think>, red de seguridad del contexto) y c8 (Qwen3-0.6B). g4 (respuestas fieles) depende de esto, y la nota de answer premia la estrategia de prompt.
  - **Filas que lo tocan:** c8 (Qwen3-0.6B), g4 (respuestas fieles), c18 (máquina solo CPU).
  - **Decidido en la spec:** Qwen3-0.6B; las fuentes entran en orden de ranking hasta llenar el presupuesto; se quita el bloque <think>; no se llama al modelo sin fuentes.
  - **Abierto:** el modo thinking (pendiente 39) y si alguna pregunta supera el presupuesto (pendiente 40).

### 8. pydantic

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** una librería para definir modelos de datos con tipos y validarlos.
  - **Qué problema resuelve:** datos de entrada con forma incorrecta que fallan tarde y de forma confusa.
  - **Cómo funciona:** campos tipados, valores por defecto, herencia, uniones, validar un JSON y leer un ValidationError.
  - **Opciones y compromisos:** validar en el borde del programa frente a comprobaciones sueltas; modelos frente a diccionarios.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.9 (modelos de datos) y c5 (modelos pydantic). Todos los JSON de entrada y salida pasan por estos modelos; un campo mal puesto invalida la salida para la moulinette.
  - **Filas que lo tocan:** c5 (modelos pydantic), c6 (FastAPI + uvicorn), c12 (capa de servicio compartida), g8 (API local).
  - **Decidido en la spec:** todos los JSON de entrada y salida pasan por modelos (spec 4.9), con los de preguntas respondidas y sin responder.
  - **Abierto:** nada propio de este concepto.

### 9. FastAPI and uvicorn

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** FastAPI es un framework web de Python; uvicorn es el servidor que lo ejecuta.
  - **Qué problema resuelve:** exponer funciones por HTTP con validación automática de lo que entra y lo que sale.
  - **Cómo funciona:** métodos HTTP y rutas, parámetros de query y sus tipos, validación automática, errores y response_model; arrancar el servidor.
  - **Opciones y compromisos:** qué código HTTP corresponde a cada error; lógica en la ruta frente a una capa aparte.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.7 (API HTTP local: rutas GET, parámetros en la query, validación con pydantic, códigos 200/400/422/503) y c6 (FastAPI + uvicorn). Es el bonus 5 y se demuestra en la defensa. Ya tienes lo básico de API y HTTP.
  - **Filas que lo tocan:** c6 (FastAPI + uvicorn), c12 (capa de servicio compartida), g8 (API local), x6 (API solo en 127.0.0.1).
  - **Decidido en la spec:** GET /search, /answer y /health; códigos 200, 400, 422 y 503; 127.0.0.1 con --port.
  - **Abierto:** nada propio de este concepto; lo de la cola, en el concepto 10.

### 10. asyncio concurrency in the API (event loop, worker thread, bounded queue, lock)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** cómo un servidor atiende varias peticiones a la vez sin bloquearse.
  - **Qué problema resuelve:** una operación lenta que congela a todas las demás peticiones.
  - **Cómo funciona:** async/await y el event loop; pasar trabajo lento a un hilo; colas limitadas; locks.
  - **Opciones y compromisos:** corrutinas frente a hilos; rechazar frente a esperar cuando la cola se llena; diferencias con pthreads.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.7 (la cola de /answer, la llamada al modelo en un hilo aparte esperado desde el event loop, y la recarga del índice una sola vez con un lock). Sin esto, un solo /answer congela todo el servidor, y eso es justo lo que comprueba g8 (API local). Ya conoces pthreads, así que los locks y las colas te son familiares.
  - **Filas que lo tocan:** g8 (API local), c6 (FastAPI + uvicorn).
  - **Decidido en la spec:** el modelo corre con asyncio.to_thread; cola limitada en /answer con 503 si no cabe; un lock para recargar el índice una sola vez.
  - **Abierto:** el valor de W del límite de la cola (pendiente 41).

### 11. Atomic writes, versioned store and content hashing (os.replace, pointer file, sha256)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** escribir de forma que un corte nunca deje un archivo a medias, y detectar cambios por el contenido.
  - **Qué problema resuelve:** archivos rotos tras un Ctrl+C, un kill o un corte de luz, y rehacer trabajo que no cambió.
  - **Cómo funciona:** archivo temporal más renombrado atómico, archivo puntero a la versión activa, y hash de contenido.
  - **Opciones y compromisos:** sobrescribir frente a versionar; comparar por hash frente a por fecha.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.1, casos 7 a 15 (índice versionado, archivo puntero, limpieza de carpetas huérfanas, sha256 por archivo) y c11 (índice versionado). Evita índices rotos y permite g6 (indexado incremental). La misma técnica se usa en la salida de search_dataset y en la caché.
  - **Filas que lo tocan:** c11 (índice versionado), g6 (indexado incremental), c13 (caché por versión), x5 (ningún traceback).
  - **Decidido en la spec:** índice versionado, os.replace, archivo puntero, limpieza de carpetas huérfanas y sha256 por archivo (spec 4.1, casos 7 a 15).
  - **Abierto:** nada propio de este concepto.

### 12. Disk cache keyed by index version

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** guardar en disco resultados ya calculados para no repetir el trabajo.
  - **Qué problema resuelve:** repetir cálculos caros con la misma entrada, también entre ejecuciones.
  - **Cómo funciona:** qué condición debe cumplir la clave, qué se guarda, qué pasa con un acierto o un fallo.
  - **Opciones y compromisos:** invalidar borrando frente a incluir la versión en la clave; qué hacer si falla la propia caché.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec 4.8 (caché) y c13 (caché por versión). Es el bonus 4 (g7, caché). Se estudia a fondo al empezar la fase de caché (pendiente 32).
  - **Filas que lo tocan:** c13 (caché por versión), g7 (caché).
  - **Decidido en la spec:** clave con versión del índice, method, query y k; un fallo de la caché nunca rompe search ni answer.
  - **Abierto:** se estudia a fondo al empezar la fase de caché (pendiente 32).

### 13. pdb (Python debugger)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** el depurador integrado de Python.
  - **Qué problema resuelve:** entender qué hace un programa mientras corre, sin llenarlo de prints.
  - **Cómo funciona:** breakpoint(), avanzar (n), entrar (s), imprimir (p, pp), moverse por la pila (w, u, d), continuar (c) y salir (q).
  - **Opciones y compromisos:** depurador frente a prints o logs.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** c3 (la regla debug del Makefile usa pdb). Es tu decisión del 2026-10-31; lo practicarás con un bug que se mete en cada bloque (pendiente 37).
  - **Filas que lo tocan:** c3 (Makefile).
  - **Decidido en la spec:** la regla debug del Makefile usa pdb.
  - **Abierto:** la práctica con un bug en cada bloque (pendiente 37).

### 14. pytest

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** un framework de tests para Python.
  - **Qué problema resuelve:** comprobar casos de forma repetible sin probarlos a mano.
  - **Cómo funciona:** funciones test_ con assert, fixtures y parametrize; comprobar salida y exit code.
  - **Opciones y compromisos:** probar funciones frente a probar el comando entero.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** c17 (tests) y spec punto 5 (tests con pytest o unittest que cubran casos límite). Comprueban x5 (ningún traceback) en todos los casos límite sin tener que probarlos a mano.
  - **Filas que lo tocan:** c17 (tests), x5 (ningún traceback).
  - **Decidido en la spec:** tests con pytest o unittest que cubran casos límite (no se califican).
  - **Abierto:** nada propio de este concepto.

### 16. uv (project and package manager)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** un gestor de proyectos y paquetes de Python.
  - **Qué problema resuelve:** entornos que funcionan en una máquina y no en otra.
  - **Cómo funciona:** dependencias declaradas frente a versiones exactas (lockfile); add, sync y run.
  - **Opciones y compromisos:** lockfile frente a solo declarar dependencias; por qué probar en un clon limpio.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** c1 (solo uv: pyproject.toml, uv.lock y `uv sync` en un clon limpio). Si `uv sync` falla en la máquina del evaluador, todo el proyecto cuenta como no funcional.
  - **Filas que lo tocan:** c1 (solo uv), c3 (Makefile), c14 (estructura del repo).
  - **Decidido en la spec:** solo uv: pyproject.toml, uv.lock y uv sync en un clon limpio.
  - **Abierto:** nada propio de este concepto.

### 17. Python Fire and tqdm

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** Fire convierte funciones o clases en una CLI; tqdm dibuja barras de progreso.
  - **Qué problema resuelve:** escribir a mano el análisis de argumentos y no saber cuánto falta en un proceso largo.
  - **Cómo funciona:** de métodos a comandos y de argumentos a opciones; cómo Fire interpreta los tipos; envolver un bucle con tqdm.
  - **Opciones y compromisos:** conversión automática de tipos frente a declararlos; por qué la barra no debe ensuciar la salida.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** c4 (CLI con Fire y barras de progreso tqdm). Es la entrada que usa el evaluador; cómo Fire convierte los tipos de los argumentos (por ejemplo --k 5 a int) afecta a los casos de error de k.
  - **Filas que lo tocan:** c4 (CLI con Fire), c12 (capa de servicio compartida), x3 (rutas hardcodeadas).
  - **Decidido en la spec:** CLI con Fire y barras tqdm, con la interfaz de comandos que fija la spec.
  - **Abierto:** nada propio de este concepto.

### 18. Interfaces and design patterns (ABC/Protocol, registry, factory)

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** formas de organizar el código para que las piezas se puedan cambiar entre sí.
  - **Qué problema resuelve:** añadir una variante obliga a reescribir lo que ya funciona.
  - **Cómo funciona:** una interfaz común (clase abstracta o Protocol), el patrón registro, el patrón fábrica y una capa de servicio.
  - **Opciones y compromisos:** ABC frente a Protocol; cuándo un patrón ayuda y cuándo sobra.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec punto 7 (métodos 1, 2, 4 y 6), c9 (interfaz de retriever), c10 (un chunker por tipo) y c12 (capa de servicio compartida). Permite añadir cada bonus sin reescribir lo que ya funciona, y en la defensa te pueden pedir un recode pequeño que lo toque.
  - **Filas que lo tocan:** c9 (interfaz de retriever), c10 (un chunker por tipo), c12 (capa de servicio compartida), c8 (Qwen3-0.6B, interfaz de generador).
  - **Decidido en la spec:** interfaz de retriever, registro de chunkers por extensión, fábrica según --method y capa de servicio común a CLI y API (spec punto 7).
  - **Abierto:** nada propio de este concepto.

### 19. numpy

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** la librería de arrays numéricos de Python.
  - **Qué problema resuelve:** cálculos sobre muchos números, lentos con bucles de Python.
  - **Cómo funciona:** arrays y shape, producto matriz-vector, sacar el top-k (argsort, argpartition), guardar y cargar.
  - **Opciones y compromisos:** vectorizar frente a bucles; argsort frente a argpartition.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** c7 (embeddings semánticos: búsqueda coseno por fuerza bruta con numpy). El producto de matrices hace que la búsqueda semántica tarde milisegundos, lo que importa para g3 (200 preguntas en 90 s).
  - **Filas que lo tocan:** c7 (embeddings semánticos), g3 (200 preguntas en 90 s).
  - **Decidido en la spec:** búsqueda coseno por fuerza bruta con numpy.
  - **Abierto:** nada propio de este concepto.

### 20. logging, stderr and exit codes

- **Nivel:** need2learn
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** cómo un programa informa de lo que pasa sin mezclarlo con sus resultados.
  - **Qué problema resuelve:** salidas ilegibles para quien las procesa y errores que no se pueden detectar.
  - **Cómo funciona:** stdout frente a stderr, el módulo logging, exit codes, y capturar interrupciones y excepciones esperadas.
  - **Opciones y compromisos:** qué va a cada salida; mensaje claro frente a traceback.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** spec punto 4 (archivo de log de cada ejecución con --log_dir) y x5 (ningún traceback). Casi todos los casos límite de la spec terminan en un mensaje claro, un exit code != 0 y un aviso en stderr y en el log.
  - **Filas que lo tocan:** x5 (ningún traceback), c16 (excepciones y recursos), x3 (rutas hardcodeadas: --log_dir).
  - **Decidido en la spec:** stdout solo para resultados; log JSON Lines por ejecución con --log_dir, creado solo si hay algo que registrar; ningún traceback.
  - **Abierto:** los campos type y error del log (pendiente 42).

### 23. git and .gitignore

- **Nivel:** partial
- **Lo que DEBES saber explicar** (en general, sin detalles del proyecto):
  - **Qué es:** el control de versiones y la lista de archivos que git ignora.
  - **Qué problema resuelve:** perder historial y subir archivos que no deben estar en el repo.
  - **Cómo funciona:** commits, ramas, patrones de .gitignore, dejar de seguir un archivo y comprobar qué se sube.
  - **Opciones y compromisos:** qué se versiona y qué se genera.
- **Cómo se aplica aquí** (solo informativo, no se evalúa):
  - **Para qué se usa:** x4 (nada generado en el repo) y spec punto 8 (solo se evalúa lo que está dentro del repositorio de git). Un archivo grande subido por error, o un archivo necesario sin subir, rompe la entrega.
  - **Filas que lo tocan:** x4 (nada generado en el repo), c14 (estructura del repo), c1 (solo uv: uv.lock va en el repo).
  - **Decidido en la spec:** nada generado en el repo: data/, logs/, caché, pesos y project.db fuera; solo se evalúa lo que está en el repositorio.
  - **Abierto:** nada propio de este concepto.

---

## (c) Spec completa

### 1. Qué es

Un sistema de Retrieval-Augmented Generation (RAG) que responde preguntas sobre un código fuente (el repositorio de vLLM que se entrega, vllm-0.10.1).

Pipeline: Corpus (data/raw/vllm-0.10.1) → Chunking (.py código | .md Markdown | .txt texto plano) → Índice (BM25 léxico + embeddings semánticos, versionado en data/processed) → Recuperar las k fuentes principales → Aumentar (construir el contexto) → Generar (Qwen3-0.6B) → Respuesta (JSON). La calidad de la recuperación se evalúa con recall@k (IoU > 0.05).

Cuatro etapas de RAG: indexar (organizar los datos para poder buscarlos), recuperar (comparar una pregunta con el índice y sacar los fragmentos más relevantes), aumentar (filtrar los fragmentos y meterlos en la ventana de contexto del modelo) y generar (leer ese contexto y producir la respuesta).

Además del pipeline obligatorio, se construyen los cinco bonus del punto 6: un índice vectorial semántico junto al léxico, ranking híbrido de los dos, indexado incremental, caché y una API HTTP local.

### 2. Cliente / usuario

1. Principal: los evaluadores de la 42 y la moulinette, que lo ejecutan con los scripts de referencia del examen y le meten entradas raras; las preguntas son sobre el código de vLLM (preguntas de documentación y preguntas de código).
2. Secundario: los reclutadores que revisan el proyecto, sobre todo a través del README y del repositorio (calidad del código, decisiones de diseño, análisis de rendimiento, ejemplos de uso).

### 3. Objetivo del producto (medible)

Recuperar la evidencia correcta de un código grande y hacer que un modelo pequeño responda fielmente a partir de ella.

1. Recall@5 >= 80 % en preguntas de documentación y >= 50 % en preguntas de código (datasets de referencia, moulinette oficial).
2. Indexar el corpus entero: 5 minutos como máximo. Se mide en la fase del índice semántico (decisión del usuario, 2026-10-29): el tiempo del indexado completo en la máquina del campus solo CPU (índice léxico + embeddings) sobre todo el corpus. Si pasa de 5 minutos, se para y se decide con el usuario antes de seguir.
3. Rendimiento de recuperación: 90 segundos como máximo para 200 preguntas; el índice debe poder consultarse en milisegundos. Se mide en la fase de search_dataset con bm25 y otra vez en la fase de recuperación híbrida, donde cada pregunta calcula también su embedding (decisión del usuario, 2026-10-29). Si pasa de 90 segundos, se para y se decide con el usuario antes de seguir.
4. Respuestas: coherentes, basadas en las fuentes recuperadas (sin alucinaciones graves) y al grano. No es un aprobado/suspenso estricto: la nota prioriza la calidad de la recuperación, que las respuestas se basen en las fuentes y la estrategia de prompt por encima de una redacción perfecta (Qwen3-0.6B tiene límites de razonamiento conocidos).
5. Nunca fallar con un traceback sin manejar (un fallo durante la revisión = no funcional).

Recall@k: para cada pregunta, la proporción de sus fuentes correctas que se encuentran en los k primeros resultados. Una fuente correcta cuenta como encontrada cuando un resultado está en el mismo archivo (file_path comparado literalmente) y su rango de caracteres se solapa con IoU > 0.05 (estricto, como en el diagrama del subject; decisión del usuario, 2026-10-31: se confirma con el pendiente 11, comparando evaluate con la moulinette sobre la misma salida).

### 4. Qué hace (funcionalidades, casos límite, fallos)

CLI con Python Fire, invocada como `uv run python -m src <comando> [opciones]` (las opciones que se muestran son el mínimo; se pueden añadir más). Barras de progreso tqdm en las operaciones largas. Todas las rutas de entrada y salida son argumentos de la CLI, nunca hardcodeadas.

Canales de salida (todos los comandos): los resultados van a stdout; todo mensaje, aviso y error (por ejemplo "run index first", "results N/N") va a stderr, de modo que redirigir stdout (> archivo) captura solo los resultados y el usuario sigue viendo los mensajes.

Todo aviso y error que se imprime en stderr (por ejemplo "results N/N", preguntas saltadas, caídas a bm25, fuentes que se quedan fuera del contexto) también se registra en el archivo de log de la ejecución, en todos los comandos, sin excepción (decisión del usuario, 2026-10-28).

Archivo de log de cada ejecución: todos los comandos aceptan --log_dir (por defecto: logs/ en la raíz del proyecto, ignorado por git), un argumento de la CLI como pide el subject. La carpeta y el archivo solo se crean cuando hay algo que registrar; un archivo por ejecución, en JSON Lines (un objeto JSON por línea), y cada evento se añade como una línea nueva sin reescribir el archivo, así una ejecución que muere solo pierde su última línea. Cada evento tiene los campos type y error (provisional: pueden cambiar durante la implementación; decisión del usuario, 2026-10-28).

Método de recuperación (search, search_dataset, answer): BM25 por defecto; la recuperación híbrida (bonus) solo cuando se pide con --method hybrid. Si la parte semántica falla (por ejemplo, el modelo de embeddings no está descargado, o los embeddings faltan o no se pueden leer), el comando cae automáticamente a BM25 y sigue; la caída se informa como un aviso que dice el motivo y que se usa bm25, en stderr y en el log, y en search_dataset se decide una vez por ejecución, para que todas las preguntas usen el mismo método. El híbrido une los rankings léxico y semántico con Reciprocal Rank Fusion (cada chunk puntúa la suma de 1/(c + posición) en ambos rankings), con c = 100 salvo que el recall@k medido muestre que c = 60 es mejor (decisión del usuario, 2026-10-28). También existe --method semantic (solo embeddings); si falla, es un error normal: mensaje claro en stderr y en el log, exit code != 0, sin traceback (en search_dataset es un fallo de toda la ejecución: no se procesa ninguna pregunta).

#### 4.1 index --max_chunk_size <int>

Lee data/raw/ (los archivos del repo de vLLM que se consideran útiles), divide cada uno en chunks y guarda el índice en data/processed/.

Tres estrategias de chunking, una por tipo de archivo indexado (el subject pide al menos dos; decisión del usuario, 2026-10-29): chunking de código Python (.py), chunking de Markdown (.md, puede usar los títulos #) y chunking de texto plano (.txt). Los .txt no son Markdown y son distintos entre sí (código de build en CMakeLists.txt, listas de paquetes en requirements/*.txt, listas de prompts y de modelos en tests/ y benchmarks/), así que el chunker de .txt tiene su propio diseño, ajustado sobre estos archivos reales en la fase de chunking. max_chunk_size por defecto 2000 caracteres, nunca por encima de 2000 (la moulinette rechaza cualquier fuente de más de 2000 caracteres, y una sola fuente demasiado larga invalida toda la salida); se permite un valor menor, informando de su efecto en el recall@k.

Regla del tamaño de chunk (se mide en la fase de chunking; decisión del usuario, 2026-10-29): 2000 es un techo, no un objetivo. El tamaño efectivo del chunk (nunca por encima de max_chunk_size) se elige midiendo el recall@5 con search_dataset + evaluate en los dos datasets públicos (docs y code) para al menos 2000, 1500, 1000 y 500 caracteres, y también para un corte estructural: un chunk por unidad natural (una función o clase en Python, una sección en Markdown, la unidad natural de cada tipo de .txt, por ejemplo un bloque de CMake o un grupo de requirements, que se decide en la fase de chunking), sin juntar nunca unidades pequeñas para llenar el límite (por ejemplo, cinco funciones de 200 caracteres dan cinco chunks, no uno de 1000), y partiendo más una unidad mayor que max_chunk_size. Se queda el tamaño con la mayor suma de recall@5 en docs y code, y cada tamaño medido con su recall@k va al README. Razones para medir: un chunk mucho más grande que una fuente correcta puede no llegar a IoU > 0.05 aunque la contenga (por ejemplo, una fuente de 80 caracteres dentro de un chunk de 2000 da 0.04); las fuentes correctas de los datasets públicos tienen una mediana de 1154 caracteres (docs) y 878 (code); el modelo de embeddings lee como máximo 256 tokens por texto (unos 1000 caracteres de inglés, menos en código). Si ningún tamaño cumple los objetivos del punto 3, se para y se decide con el usuario.

Método de recuperación: al menos TF-IDF o BM25 (se pueden añadir otros encima). Pista: las preguntas pueden parafrasear una idea o citar un identificador literalmente; lo que se guarda al indexar decide cuál de las dos se podrá encontrar.

Ejemplo de salida: "Ingestion complete! Indexed 13466 chunks under data/processed/".

Casos límite / fallos:
1. max_chunk_size fuera de 1..2000 (por ejemplo 0, -5, 3000) → se rechaza: mensaje claro ("max_chunk_size must be between 1 and 2000"), exit code != 0, no se indexa nada, sin traceback.
2. data/raw no existe o no tiene ningún archivo indexable → mensaje claro ("data/raw not found or empty"), exit code != 0, data/processed queda intacto.
3. Archivos binarios y no útiles → no se leen: solo se indexa una lista blanca de extensiones: .py (chunking de código Python), .md (chunking de Markdown) y .txt (chunking de texto plano). Motivo (decisión del usuario, 2026-10-29): las 199 fuentes correctas de los datasets públicos citan solo .py (99), .md (97) y .txt (3, CMakeLists.txt), así que se toman como lo que se evalúa.
4. Texto que no es UTF-8 válido → el archivo se salta con un aviso (errors="replace" movería los índices de caracteres). Los archivos se leen con newline="" para que \r\n no se convierta en \n y los índices de caracteres coincidan con el archivo original. Comprobación de rangos (se mide en la fase de indexado): ejecutar evaluate y la moulinette sobre la misma salida de search_dataset; si dan el mismo recall@k, nuestros rangos de caracteres coinciden con los de la moulinette; si no, revisar primero los 4 archivos del corpus (.py, .md, .txt) que contienen \r y adaptar la lectura. Si no se encuentra la causa, se para y se decide con el usuario.
5. Archivos vacíos (por ejemplo un __init__.py vacío) → se saltan en silencio, sin chunk [0:0].
6. Ctrl+C durante el indexado → se captura KeyboardInterrupt, mensaje claro, sin traceback.
7. Una interrupción o un fallo de escritura nunca debe dejar un índice escrito a medias o mezclado: cada versión del índice (chunks + estadísticas + el hash de contenido, sha256, de cada archivo indexado, que answer_dataset usa en 4.5 caso 8) se escribe completa en su propia subcarpeta de data/processed; se verifica (carga sin error y el número de chunks coincide entre las dos partes) y solo entonces se activa con un único os.replace de un pequeño archivo puntero que nombra la versión actual (el puntero temporal se escribe en la misma carpeta, para que el replace sea atómico). Si la verificación falla, el puntero no cambia, la versión fallida se borra e index sale con un error claro y exit code != 0 (sin reintento: lo más probable es que el fallo sea determinista, por ejemplo disco lleno o un bug del chunking). Tras el cambio, la versión anterior se borra.
8. Ctrl+C mientras se escribe una versión nueva → el manejador de KeyboardInterrupt borra la subcarpeta escrita a medias antes de salir.
9. Muerte brusca (terminal cerrada, kill -9, corte de luz): no se ejecuta ningún código y puede quedar una subcarpeta huérfana → al arrancar, index borra toda subcarpeta de versión que no sea la que nombra el puntero.
10. Cuando index termina, imprime en stderr: "if the API server is running, it will load <version> on its next request", con el nombre real de la nueva versión activa. index nunca llama al servidor (puede estar apagado y no conoce su --port).

Índice semántico e indexado incremental (bonus; decisión del usuario, 2026-10-29):

11. Cada versión del índice guarda, en su propia subcarpeta: los chunks, las estadísticas BM25, la matriz de embeddings (un vector por chunk), el hash de contenido de cada archivo indexado y los ajustes con los que se construyó (max_chunk_size, modelo de embeddings). La verificación del caso 7 comprueba también que haya tantos vectores como chunks.
12. Ejecución incremental: el hash de cada archivo de la lista blanca se compara con la versión anterior. Archivo sin cambios → sus chunks y vectores se copian de la versión anterior (sin chunking ni modelo). Archivo nuevo o cambiado → se trocea y se calculan sus embeddings. Archivo borrado → sus chunks no se copian. Las estadísticas BM25 se recalculan siempre sobre todos los chunks (dependen de todos; no usan el modelo).
13. Reconstrucción completa cuando max_chunk_size o el modelo de embeddings son distintos de los de la versión anterior (por ejemplo, reutilizar un chunk de 2000 caracteres rompería --max_chunk_size 1000): no se reutiliza nada.
14. Versión anterior inexistente o ilegible (por ejemplo, un archivo de embeddings corrupto) → reconstrucción completa, con un aviso en stderr y en el log; nunca es un error.
15. Modelo de embeddings no disponible durante index (no descargado y sin conexión) → el índice léxico (obligatorio) se construye igualmente sin la parte semántica, con un aviso en stderr y en el log; --method hybrid cae entonces a bm25 según la regla del punto 4.

#### 4.2 search <query> --k <int>

Devuelve las k fuentes principales para una sola consulta: cada fuente es file_path + [first_character_index:last_character_index], de 2000 caracteres de ancho como máximo. file_path debe coincidir exactamente con la ruta del corpus (por ejemplo data/raw/vllm-0.10.1/docs/features/lora.md).

Casos límite: consulta vacía, consulta sin sentido, k=0, índice inexistente → se manejan sin fallar.
1. No hay archivo puntero (index nunca se ejecutó) → mensaje claro "run index first", exit code != 0, sin traceback.
2. Consulta vacía ("" o solo espacios) → se rechaza: mensaje claro ("query must not be empty"), exit code != 0, no se busca nada, sin traceback.
3. Consulta sin sentido: ningún token de la consulta existe en el vocabulario del índice, así que todos los chunks puntúan 0 y cualquier top-k sería arbitrario → se rechaza: mensaje claro ("no indexed term matches the query"), exit code != 0, sin traceback. Una consulta con al menos un token que coincida (por ejemplo "asdkjh model") se busca normalmente.
4. k = 0 → devuelve 0 fuentes (lista vacía), exit code 0, no se calcula ninguna puntuación (el subject solo pide que k=0 se maneje sin fallar).
5. k negativo (por ejemplo -2) → se rechaza: mensaje claro ("k must be >= 0"), exit code != 0, no se busca nada, sin traceback.
6. k mayor que el número de chunks N del índice activo (por ejemplo --k 999999 con 100 chunks) → no es un error: k se limita a N, se devuelven las N fuentes ordenadas, con el mensaje "results N/N" (por ejemplo "results 100/100") en stderr, para que el usuario vea que solo existen N mientras stdout conserva solo las fuentes; exit code 0, sin traceback. N se lee de la versión activa del índice, nunca está hardcodeado, porque cambia con cada ejecución de index y con max_chunk_size.

#### 4.3 search_dataset --dataset_path <path> --k <int> --save_directory <dir>

Busca sobre un dataset completo de preguntas leído desde JSON; escribe un archivo JSON StudentSearchResults. save_directory siempre separado por dataset (UnansweredQuestions o AnsweredQuestions), porque los datasets públicos comparten nombres de archivo.

Casos límite: archivos inexistentes, JSON mal formado, k=0 → se manejan sin fallar.
1. Comprobaciones de toda la ejecución (mismas reglas que 4.2 casos 1, 4, 5 y 6), hechas una vez antes de procesar ninguna pregunta: sin índice o con k negativo → mensaje claro en stderr, exit code != 0, no se procesa ninguna pregunta, no hay archivo de salida; k = 0 → cada pregunta recibe 0 fuentes; k > N → k se limita a N en todas las preguntas y "results N/N" se imprime una vez en stderr.
2. Fallos de una pregunta (pregunta vacía o sin sentido, según 4.2 casos 2 y 3) → se salta la pregunta, nunca el dataset entero: se queda en la salida con retrieved_sources: [] para que estén todos los question_id del dataset (la moulinette valida la salida, y un id que falte podría invalidar todo el archivo) y puntúa 0 en recall; el question_id y el motivo se registran en el log, y se sigue con la siguiente pregunta.
3. --dataset_path no existe o es una carpeta → mensaje claro, exit code != 0, sin archivo de salida.
4. JSON mal formado → mensaje claro que dice la línea y la columna del error, exit code != 0, sin archivo de salida.
5. JSON válido que no es un RagDataset (por ejemplo, falta rag_questions o los tipos no encajan) → error de pydantic resumido, sin traceback, exit code != 0, sin archivo de salida.
6. rag_questions vacío → salida válida con search_results: [], aviso "0 questions" en stderr, exit code 0.
7. question_id duplicado → solo se saltan las preguntas duplicadas (se registran en el log con sus ids) y se procesa el resto. Provisional, se prueba en la fase de search_dataset: pasar a mano la moulinette sobre una salida en la que se saltaron las preguntas duplicadas; si la rechaza, se para y se decide con el usuario cómo adaptar este caso.
8. --save_directory no existe → se crea con sus carpetas padre. Sin permisos de escritura, o es un archivo existente → mensaje claro antes de hacer ninguna búsqueda (para no perder el trabajo de búsqueda al guardar), exit code != 0.
9. El archivo de salida ya existe → se sobrescribe; se escribe en un archivo temporal de la misma carpeta y se activa con os.replace, así nunca existe un JSON escrito a medias.
10. Ctrl+C durante la ejecución → mensaje claro, sin traceback, sin archivo de salida (un archivo parcial dejaría question_id sin resultados).

#### 4.4 answer <query> --k <int>

Responde una sola consulta con Qwen/Qwen3-0.6B usando el contexto recuperado, que se pasa dentro del presupuesto de tokens del modelo.

Salida: un JSON MinimalAnswer en stdout (el mismo modelo que devuelve /answer).

Casos límite / fallos:
1. Consulta vacía, k negativo, k mayor que N → mismas reglas que 4.2 (casos 2, 5 y 6). Cuando k es mayor que N, se usan las N fuentes, y el log registra además que solo se usaron N porque solo existen N (por ejemplo, k = 1000 con 10 chunks → 10 fuentes).
2. Consulta sin sentido (ningún token de la consulta está en el vocabulario del índice) → se rechaza como en 4.2 caso 3: responder sin contexto haría que el modelo se lo inventara.
3. k = 0 → se rechaza: mensaje claro ("k must be >= 1 for answer"), exit code != 0, sin traceback.
4. Modelo no descargado y sin conexión, o disco lleno mientras se descarga → mensaje claro, exit code != 0, sin traceback.
5. Modo thinking de Qwen3: los dos modos (con y sin thinking) se comparan durante los tests en calidad de la respuesta y tiempo, y la elección sigue las mediciones; no se descarta de antemano, porque las preguntas son moderadamente exigentes. Cualquier bloque <think>...</think> se quita siempre de la respuesta.
6. Respuesta vacía del modelo → aviso en stderr y en el log, se devuelve answer: "" con sus fuentes, exit code 0 (la recuperación sí funcionó).
7. Ctrl+C durante la generación → mensaje claro, sin traceback.
8. Hipótesis que solo se prueba si hace falta (decisión del usuario, 2026-10-28): primero medir si alguna pregunta de los datasets, con sus fuentes, supera el presupuesto de tokens del modelo. Si alguna lo supera, probar a repartir las fuentes en 2 prompts (3 como máximo): cada prompt lleva una nota que dice que su respuesta se basa solo en las fuentes n..m porque el contexto del modelo es pequeño; las partes se generan una tras otra y se unen en una sola respuesta, que es la que se devuelve.
9. Red de seguridad del contexto (con cualquier k, se use o no el caso 8): las fuentes entran en el prompt en orden de ranking hasta llenar el presupuesto de tokens; las demás se quedan fuera del prompt pero se mantienen en retrieved_sources. Un mensaje claro en stderr y en el log dice que solo se usaron n/k fuentes para generar la respuesta por el límite de contexto del modelo (por ejemplo "only 12/1000 sources were used to generate the answer (context limit)") (decisión del usuario, 2026-10-28).

#### 4.5 answer_dataset --student_search_results_path <path> --save_directory <dir>

Genera respuestas para un dataset a partir de resultados de búsqueda; escribe un archivo JSON StudentSearchResultsAndAnswer (por ejemplo "Loaded 100 questions ... Processed 100 of 100 questions").

Nunca vuelve a buscar: lee del corpus el texto de cada fuente (file_path + rango de caracteres) y se lo pasa al modelo.

Casos límite / fallos:
1. --student_search_results_path no existe o es una carpeta, JSON mal formado, JSON válido que no es un StudentSearchResults → mismas reglas que 4.3 casos 3, 4 y 5.
2. search_results vacío → igual que 4.3 caso 6.
3. question_id duplicado → igual que 4.3 caso 7 (provisional, la misma prueba con la moulinette).
4. --save_directory, archivo de salida existente, Ctrl+C → igual que 4.3 casos 8, 9 y 10.
5. Respuesta vacía del modelo y límite de contexto → igual que 4.4 casos 6 y 9, aplicado a cada pregunta.
6. Modelo no descargado y sin conexión, o disco lleno mientras se descarga → se comprueba una vez antes de la primera pregunta: mensaje claro, exit code != 0, sin archivo de salida.
7. Pregunta con retrieved_sources: [] (por ejemplo, saltada en search_dataset) o sin ninguna fuente válida (caso 8) → no se llama al modelo (sin contexto se lo inventaría, como en 4.4 caso 2); la pregunta se queda en la salida con answer: "" y se registra en el log. Al final de la ejecución, un resumen en stderr dice cuántas preguntas no tienen respuesta y la ruta exacta del log (por ejemplo "3/100 questions have no answer (no valid sources); details in logs/<file>.jsonl"). El README explica que answer: "" significa: mirar el log.
8. Fuente no válida (el archivo de entrada viene de fuera y puede estar desactualizado o editado a mano): (a) file_path no está en el corpus, o el rango de caracteres se sale del archivo o tiene más de 2000 caracteres; (b) el hash de contenido del archivo citado no coincide con el guardado en la versión activa del índice (el corpus cambió desde el último index, así que el rango puede apuntar a otro texto). El texto de la fuente se deja fuera del prompt, pero la fuente se mantiene en retrieved_sources, para que la salida siga coincidiendo con el archivo de resultados que evaluó la moulinette; un aviso en stderr y en el log nombra el archivo y dice que hay que volver a ejecutar index y search_dataset. answer_dataset nunca reindexa ni vuelve a buscar por su cuenta (decisión del usuario, 2026-10-29). La pregunta se responde con las fuentes válidas que queden; si no queda ninguna → caso 7.
9. El k de la salida = el k del archivo de entrada, copiado tal cual (answer_dataset no tiene --k: no busca).

#### 4.6 evaluate --student_search_results_path <path> --dataset_path <path>

Informa del recall@k propio frente a un dataset con las respuestas correctas, para iterar por cuenta propia. El recall@k oficial lo calcula la moulinette que se entrega; la solución nunca debe importar ni llamar a la moulinette.

Salida: Recall@1/3/5/10 en stdout (los mismos valores que da la moulinette), calculados con la definición de recall@k del punto 3.

Casos límite / fallos:
1. Cualquiera de los dos archivos no existe o es una carpeta, JSON mal formado, o no es el modelo esperado (StudentSearchResults para --student_search_results_path, RagDataset para --dataset_path) → mismas reglas que 4.3 casos 3, 4 y 5, para los dos archivos.
2. --dataset_path es un dataset UnansweredQuestions (sin fuentes correctas) → no se puede calcular el recall: mensaje claro ("dataset_path must be an AnsweredQuestions dataset"), exit code != 0.
3. question_id que no coinciden entre los dos archivos: (a) una pregunta está en los resultados pero no en el dataset → se ignora, con un aviso en stderr y en el log; (b) una pregunta está en el dataset pero no en los resultados → cuenta como recall 0 (no se respondió); (c) ningún question_id en común → mensaje claro ("no common question_id", lo más probable es que sea el dataset equivocado), exit code != 0.
4. Una pregunta del dataset con sources: [] → su recall no está definido (0/0): se excluye de la media, con un aviso en stderr y en el log.
5. Solo se informan los Recall@N con N <= k del archivo de resultados (por ejemplo k = 5 → @1, @3, @5); cada uno que falta se explica en stderr (por ejemplo "recall@10 needs k >= 10 (file has k = 5)"), porque calcularlo con menos resultados falsearía una medida que no se hizo.
6. Una fuente de más de 2000 caracteres en los resultados → el recall se calcula igualmente, con un aviso en stderr y en el log: "the moulinette would reject this file" (invalida toda la salida, 4.1).

#### 4.7 API HTTP local (bonus)

El servidor es opcional y está separado de la CLI (decisión del usuario, 2026-11-05): la CLI siempre trabaja en local y nunca llama al servidor, así que no se escribe ningún archivo con el host y el puerto del servidor y la CLI no hace comprobación de health. Otros programas usan el servidor directamente por HTTP.

El servidor escucha solo en 127.0.0.1, para que nadie más de la red pueda llegar a él (la API no tiene autenticación) (decisión del usuario, 2026-10-28). Endpoints (parámetros en la query string de la URL): GET /search (query, k, method), GET /answer (query, k, method), GET /health (sin parámetros); los valores por defecto son los mismos que en la CLI (method=bm25). Códigos de estado: 422 cuando un parámetro no encaja con su tipo o falta uno obligatorio (validación automática); 400 cuando un valor incumple las reglas de 4.2 (consulta vacía o sin sentido, k negativo), con los mismos mensajes; 503 cuando no hay índice (/search y /answer, mensaje "run index first") o la cola de /answer está llena; 200 en el resto de casos. k = 0: /search devuelve 200 con una lista vacía (4.2 caso 4); /answer devuelve 400 con "k must be >= 1 for answer" (4.4 caso 3) (decisiones del usuario, 2026-10-29 y 2026-10-28). Las respuestas se validan con modelos pydantic compartidos con la CLI: /search devuelve un MinimalSearchResults, /answer un MinimalAnswer (4.9; question_id es un uuid nuevo, porque una consulta suelta no tiene) y /health un HealthStatus (4.9); una respuesta que no encaja con su modelo nunca sale del servidor (500). El servidor se arranca desde la CLI y acepta --port <int>, para que el usuario pueda elegir otro puerto si el de por defecto ya está en uso (decisión del usuario, 2026-10-28). Las peticiones que necesitan el modelo (solo /answer; /search y /health nunca esperan en ella) entran en una cola y se atienden de una en una, para que las peticiones simultáneas esperen su turno en vez de bloquear o tumbar el servidor (decisión del usuario, 2026-10-28). La llamada al modelo se ejecuta en un hilo de trabajo dentro del proceso del servidor (esperado desde el event loop), así una generación en curso nunca congela /search ni /health. Máximo de peticiones esperando en la cola = W / T, donde T es el tiempo medido de una respuesta en CPU y W = 60 segundos (provisional, se ajusta durante los tests); una petición que pasa ese límite recibe 503 al instante con un mensaje claro.

Sin índice al arrancar (decisión del usuario, 2026-10-29): el servidor arranca igualmente; /search y /answer responden 503 ("run index first"); /health responde 200 (el servidor en sí está disponible) con index_loaded: false y action_suggest: "no index found: run index"; en cuanto se ejecuta index, el servidor lo carga en la siguiente petición según la regla de recarga de abajo.

Versión del índice en el servidor (decisión del usuario, 2026-10-29; se eligió la recarga automática frente a un PUT /index manual): el servidor carga entera en memoria la versión activa del índice al arrancar (index borra la carpeta de la versión anterior tras un cambio, así que después no se puede leer nada de ella). Antes de atender cada /search, /answer o /health, lee el archivo puntero; si nombra una versión distinta de la cargada, el servidor la carga aparte y la cambia en cuanto está lista, así una petición en curso (por ejemplo, un /answer generando) termina con la versión vieja sin errores; varias peticiones simultáneas que ven el cambio provocan una sola carga (lock). Si la versión nueva no se puede cargar (corrupta, o no hay índice), el servidor sigue sirviendo la vieja, registra un aviso, lo informa en el action_suggest de /health y no vuelve a intentar esa misma versión hasta que el puntero nombre otra (lo más probable es que el fallo sea determinista). Se mide en la fase de la API: el tiempo de cargar una versión del índice en el servidor; si pasa de 2 segundos, se añade una tarea de fondo que lee el puntero cada n segundos (n se ajusta durante los tests) y carga una versión nueva antes de que llegue ninguna petición, para que ninguna petición pague el tiempo de carga (decisión del usuario, 2026-10-29); la comprobación en cada petición se mantiene.

#### 4.8 Caché (bonus)

Los resultados de las consultas se guardan en caché en disco, con la clave query, k, method y versión del índice; una versión nueva del índice los invalida, y las entradas de versiones que ya no existen se borran cuando cambia la versión activa, así la caché nunca crece sin límite (decisión del usuario, 2026-10-29).

Casos límite / fallos (decisión del usuario, 2026-10-29): un fallo de la caché nunca rompe search ni answer: el resultado se calcula sin la caché, con un aviso en stderr y en el log, sin traceback.
1. Entrada de caché ilegible o corrupta → se ignora y se recalcula.
2. Carpeta de caché sin permisos de escritura, o disco lleno → la respuesta se devuelve igualmente, solo que no se guarda en la caché.
3. Entrada escrita a medias (por ejemplo, Ctrl+C mientras se guarda) → no puede existir: cada entrada se escribe en un archivo temporal de la misma carpeta y se activa con os.replace, como en 4.3 caso 9. Diseño provisional: puede cambiar durante la implementación (decisión del usuario, 2026-10-28).

#### 4.9 Modelos de datos (pydantic; son una base: se pueden ampliar con modelos nuevos o campos extra)

- MinimalSource: file_path: str, first_character_index: int, last_character_index: int
- UnansweredQuestion: question_id: str = Field(default_factory=lambda: str(uuid.uuid4())), question: str
- AnsweredQuestion(UnansweredQuestion): sources: List[MinimalSource], answer: str
- RagDataset: rag_questions: List[AnsweredQuestion | UnansweredQuestion]
- MinimalSearchResults: question_id: str, question: str, retrieved_sources: List[MinimalSource]
- MinimalAnswer(MinimalSearchResults): answer: str
- StudentSearchResults: search_results: List[MinimalSearchResults], k: int
- StudentSearchResultsAndAnswer: search_results: List[MinimalAnswer], k: int
- HealthStatus (lo devuelve /health): index_loaded: bool, loaded_version: str | None (la versión que el servidor tiene en memoria), active_version: str | None (la versión que nombra el archivo puntero, leída en cada llamada a /health), action_suggest: str | None (null cuando las dos versiones coinciden; "no index found: run index" cuando no hay índice; si no, tras una carga automática fallida, "<version> could not be loaded: <reason>; still serving <loaded version>; run index again", con los nombres reales)

#### 4.10 Salida

Cada comando escribe JSON conforme a los modelos. Búsqueda → StudentSearchResults (search_results con question_id, question, retrieved_sources; k). Respuestas → StudentSearchResultsAndAnswer (lo mismo + answer). file_path relativo a la raíz del proyecto, escrito exactamente como en el corpus leído (data/raw/vllm-0.10.1/...).

#### 4.11 Pipeline completo (defensa)

1. `uv run python -m src index --max_chunk_size 2000`
2. `uv run python -m src search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json --k 10 --save_directory data/output/search_results/UnansweredQuestions`
3. `./moulinette evaluate_student_search_results <student results> <AnsweredQuestions dataset> --k 10 --max_context_length 2000` (renombrar moulinette-ubuntu/-fedora a moulinette) → "Student data is valid: True", Recall@1/3/5/10.
4. `uv run python -m src answer_dataset --student_search_results_path ... --save_directory data/output/search_results_and_answer/UnansweredQuestions`

### 5. Tecnologías

- Python >= 3.10; flake8; type hints en parámetros, retornos y variables; mypy sin errores; docstrings PEP 257 (estilo Google o NumPy).
- Excepciones manejadas sin fallar (try-except); context managers para archivos y conexiones; sin fugas de recursos.
- pydantic para los modelos de datos que se pasan entre etapas (las clases de servicio u orquestación, como el indexador, el retriever o el pipeline, no tienen por qué ser pydantic).
- uv como gestor de proyecto y de paquetes (el evaluador y la moulinette solo ejecutan `uv sync`); pyproject.toml y uv.lock en la raíz del repo.
- CLI con Python Fire; barras de progreso tqdm.
- API HTTP local (bonus): FastAPI, servida con uvicorn.
- Embeddings semánticos (bonus): all-MiniLM-L6-v2 en CPU, búsqueda coseno por fuerza bruta con numpy. Librería: fastembed (ONNX Runtime, sin PyTorch) o sentence-transformers; se prueban y se miden las dos en la fase del índice semántico, de forma simple y práctica, en lo que nos podría afectar (tamaño de instalación y tiempo de uv sync, tiempo de calcular los embeddings de todo el corpus en CPU frente al objetivo de 5 minutos, recall@5 en docs y code, tiempo de carga del modelo en el servidor de la API, funcionar sin conexión una vez el modelo está en caché), y la elección se hace con el usuario a partir de esos números (decisión del usuario, 2026-10-29). Las dos dan el mismo resultado en nuestro caso: un vector por texto (la librería hace el mean pooling), vectores ya normalizados, truncado silencioso a 256 tokens, procesamiento por lotes y caché del modelo; fastembed solo es más ligera y rápida (comprobado el 2026-10-29 con fastembed 0.9.1: entorno de 152 MB, modelo de 87 MB, normas 1.0, truncado max_length 256), así que la elección no cambia el comportamiento ni el recall. Nuestro código comprueba con token_count() si un chunk cabe en 256 tokens. Se mide en la fase del índice semántico (decisión del usuario, 2026-10-29): la proporción de chunks de más de 256 tokens, y el recall@5 en docs y code de (a) aceptar el truncado (solo se calculan embeddings de los primeros 256 tokens) frente a (b) un vector por cada ventana de 256 tokens del chunk, puntuando el chunk con su mejor ventana; la elección se hace con el usuario a partir de esos números.
- Modelo: Qwen/Qwen3-0.6B (por defecto). Se permiten otros modelos solo si todo sigue funcionando con Qwen3-0.6B.
- Se permite cualquier otra librería.
- Reglas del Makefile: install, run, debug (pdb), clean (__pycache__, .mypy_cache...), lint (`flake8 .` y `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`), lint-strict opcional (`flake8 .` y `mypy . --strict`).
- Tests con pytest o unittest que cubran casos límite (no se califican); .gitignore para los artefactos de Python; se recomienda un entorno virtual.
- Entorno: máquina del campus solo CPU; binarios de la moulinette para Ubuntu y Fedora. El stack de deep learning y los pesos pueden sumar varios GB: construir y ejecutar desde un sitio con espacio en disco suficiente.
- Estructura del repositorio: src/ (ejecutable como `uv run python -m src <comando>`), pyproject.toml, uv.lock, README.md, data/raw/ (repo de vLLM), data/processed/ (índice), data/datasets/UnansweredQuestions/ y data/datasets/AnsweredQuestions/, data/output/search_results/<DatasetScope>/, data/output/search_results_and_answer/<DatasetScope>/. Si no se respeta la estructura o la interfaz, los scripts de referencia no pueden ejecutarse y las comprobaciones fallan por diseño.
- README.md (en inglés): primera línea en cursiva "This project has been created as part of the 42 curriculum by <login1>[, <login2>...]"; secciones Description, Instructions, Resources (referencias + cómo se usó la IA, para qué tareas y partes); además System architecture, Chunking strategy, Retrieval method, Performance analysis (recall@k y rendimiento), Design decisions, Challenges faced, Example usage. Cualquier texto del proyecto que diga qué hizo la IA se decide hablándolo con el usuario, nunca se supone (decisión del usuario, 2026-10-31).

### 6. Alcance (dirección de crecimiento)

Los cinco bonus están comprometidos y se implementan (decisión del usuario, 2026-10-28). Solo se califican si toda la parte obligatoria valida, incluida la robustez cuando un evaluador la fuerza en direcciones raras; cada uno vale un punto, debe funcionar en una máquina solo CPU y puede que haya que demostrarlo:
1. Embeddings semánticos: un índice vectorial con un modelo ligero en CPU (por ejemplo all-MiniLM-L6-v2) junto al índice léxico.
2. Recuperación híbrida: combinar los rankings léxico y semántico en una sola lista.
3. Indexado incremental: reindexar solo un archivo que cambió.
4. Caché: guardar en caché el índice y los resultados de las consultas para el arranque en frío y las consultas repetidas.
5. API HTTP local: consultar el índice y responder preguntas a través de una pequeña API HTTP local.

Flake8 se aplica también a los archivos de los bonus.

### 7. Métodos de arquitectura que permiten crecer

Decisiones del usuario, 2026-10-29. Cada bonus se añade sin reescribir lo que ya funciona:
1. Una interfaz de retriever: Bm25Retriever, SemanticRetriever y HybridRetriever (RRF sobre los otros dos) comparten el mismo método search(query, k) -> list[MinimalSource]; --method solo elige cuál se crea, así que el resto del programa (CLI, API, search_dataset) nunca sabe cuál está corriendo. Permite los bonus 1 y 2.
2. Un chunker por tipo de archivo indexado, elegido desde un registro cuya clave es la extensión: .py (código), .md (Markdown), .txt (texto plano), cada uno con su propia lógica (4.1). Añadir un tipo es añadir una clase de chunker.
3. Almacén de índice versionado (4.1 casos 7 y 11 a 15): los chunks, los embeddings y el hash de contenido se guardan por archivo; lo usan index, la CLI y el servidor de la API; hace posible el indexado incremental. Permite el bonus 3.
4. Una capa de servicio compartida: las funciones de búsqueda y respuesta reciben y devuelven modelos pydantic; la CLI de Fire y el servidor FastAPI son envoltorios finos que solo las llaman, así la API nunca duplica lógica. Permite el bonus 5.
5. Una caché cuya clave incluye la versión del índice (versión del índice, method, query, k): cuando la versión cambia, las entradas viejas simplemente no se vuelven a usar; el modelo y el índice se cargan una vez por proceso (arranque en frío y consultas repetidas). Permite el bonus 4. Se estudia a fondo con el usuario al empezar la fase de caché, antes de implementarla (decisión del usuario, 2026-10-29).
6. Una interfaz de generador: Qwen/Qwen3-0.6B por defecto; se puede cambiar por otro modelo sin tocar el resto, siempre que todo siga funcionando con Qwen3-0.6B.

### 8. Límites

- Nunca llamar ni importar la moulinette.
- Ninguna fuente de más de 2000 caracteres; max_chunk_size nunca por encima de 2000.
- Ninguna ruta de entrada o salida hardcodeada.
- Nada de archivos de datos grandes, pesos de modelos ni salidas generadas en el repositorio (el evaluador los genera).
- Ningún traceback sin manejar con ninguna entrada.
- Debe seguir funcionando con Qwen/Qwen3-0.6B.
- El gestor de paquetes es solo uv para el evaluador.
- Entrega: solo se evalúa el trabajo que está dentro del repositorio de Git (src/, pyproject.toml, uv.lock, Makefile con install/run/debug/clean/lint, README.md y los archivos de configuración necesarios). Durante la defensa se puede pedir un recode breve (un pequeño cambio de comportamiento o una función pequeña).
- Uso de IA (capítulo III del subject): usar solo contenido generado por IA que se entienda por completo y se pueda explicar y justificar en la evaluación.

---

## (d) Documentación oficial

Revisa estas URLs y dáselas a NotebookLM como fuente de referencia.

1. RAG (Retrieval-Augmented Generation): artículo original de Lewis et al., 2020 — https://arxiv.org/abs/2005.11401
2. Chunking: sin URL verificada (no tiene documentación oficial; la referencia es la spec, punto 4.1).
3. BM25 and tokenization: sin URL verificada de documentación oficial (referencia general, no oficial: https://en.wikipedia.org/wiki/Okapi_BM25).
4. Recall@k and IoU: sin URL verificada (la definición que vale es la de la spec, punto 3).
5. Embeddings and cosine similarity: ficha del modelo — https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 ; sentence-transformers — https://www.sbert.net ; fastembed — https://github.com/qdrant/fastembed
6. Reciprocal Rank Fusion: artículo original de Cormack, Clarke y Büttcher, 2009 — https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
7. LLM generation and prompting (Qwen3-0.6B): ficha del modelo — https://huggingface.co/Qwen/Qwen3-0.6B ; transformers — https://huggingface.co/docs/transformers
8. pydantic: https://docs.pydantic.dev
9. FastAPI and uvicorn: https://fastapi.tiangolo.com ; https://www.uvicorn.org
10. asyncio concurrency in the API: https://docs.python.org/3/library/asyncio.html
11. Atomic writes, versioned store and content hashing: os.replace — https://docs.python.org/3/library/os.html#os.replace ; hashlib — https://docs.python.org/3/library/hashlib.html
12. Disk cache keyed by index version: sin URL verificada (es un diseño propio; la referencia es la spec, punto 4.8).
13. pdb (Python debugger): https://docs.python.org/3/library/pdb.html
14. pytest: https://docs.pytest.org
15. uv: https://docs.astral.sh/uv/
16. Python Fire and tqdm: https://github.com/google/python-fire ; https://tqdm.github.io
17. Interfaces and design patterns: abc — https://docs.python.org/3/library/abc.html ; typing.Protocol — https://docs.python.org/3/library/typing.html#typing.Protocol
18. numpy: https://numpy.org/doc/stable/
19. logging, stderr and exit codes: logging — https://docs.python.org/3/library/logging.html ; sys.exit — https://docs.python.org/3/library/sys.html#sys.exit
20. git and .gitignore: https://git-scm.com/doc ; https://git-scm.com/docs/gitignore
