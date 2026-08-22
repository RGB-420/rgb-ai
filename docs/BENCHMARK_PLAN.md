# Plan de Benchmark de Modelos Locales

## 1. Objetivo general

Construir un sistema de evaluación para los modelos locales ejecutados en
`rgb-ai`.

El objetivo NO es encontrar "el mejor modelo" de forma general.

El objetivo es encontrar:

> El modelo más pequeño, rápido y eficiente que alcance la calidad necesaria
> para cada tarea concreta.

Un modelo puede ser malo razonando pero excelente clasificando documentos.
Otro puede ser lento pero muy fiable utilizando RAG.

Por tanto, cada modelo tendrá un perfil de capacidades y no una única nota.

## 1.1 Modelo + contexto de ejecución

Los benchmarks deben poder distinguir la capacidad intrínseca de un modelo de
su rendimiento cuando recibe instrucciones, ejemplos o contexto explícito.

Por eso, un caso de benchmark puede representar distintas variantes:

- baseline: prompt directo sin ayuda adicional;
- instructions: system prompt + prompt;
- context: system prompt opcional + contexto suministrado explícitamente + prompt;
- few_shot: system prompt opcional + ejemplos + contexto opcional + prompt;
- future_rag: system prompt + contexto recuperado dinámicamente + prompt.

En la Fase 1 el contexto es solamente entrada explícita del caso de benchmark.
No se implementa retrieval, embeddings, Qdrant, reranking ni pipeline RAG.

Esta separación permitirá medir más adelante si un fallo pertenece al modelo, a
malas instrucciones, a contexto insuficiente, a retrieval defectuoso o a
infraestructura. La ejecución y el almacenamiento de resultados se implementarán
en hitos posteriores.

## 1.2 Suite inicial curada

La primera suite versionada en `benchmarks/cases.jsonl` es deliberadamente
pequeña y revisable. Su objetivo es diferenciar modelos locales en capacidades
relevantes para `rgb-ai`, no cubrir todo el producto futuro.

Categorías iniciales:

- instruction_following;
- structured_output;
- routing;
- classification;
- context_use;
- reasoning;
- coding;
- tool_selection.

Estas categorías son capacidades de benchmark, no environments de producción.
Por ejemplo, `routing` mide si un modelo puede elegir una etiqueta esperada,
pero no implementa un router de agentes. `context_use` mide uso de contexto
suministrado explícitamente por el caso, pero no implementa RAG.

La suite empieza con unas pocas decenas de casos deterministas en castellano.
Debe crecer solo cuando nuevos casos aporten señal clara sobre errores,
capacidades o diferencias de coste entre modelos.


# 2. Métricas técnicas globales

Guardar para todas las ejecuciones:

- modelo
- familia
- parámetros
- cuantización
- tamaño en disco
- RAM utilizada/cargada
- CPU/GPU
- tamaño de contexto
- tokens de entrada
- tokens generados
- prompt tokens/s
- output tokens/s
- tiempo de carga
- tiempo total
- thinking activado/desactivado
- tokens de thinking, cuando sea posible
- respuesta completa
- thinking completo, cuando el modelo lo exponga
- fecha
- versión del modelo


# 3. Factualidad

## Objetivo

Comprobar conocimiento general y tendencia a inventar información.

## Ejemplos

- ¿Por qué el cielo se ve azul?
- ¿En qué año cayó el Muro de Berlín?
- ¿Cuál es la capital de Eslovenia?
- ¿Qué órgano bombea la sangre?
- ¿Quién escribió Don Quijote?

Mezclar preguntas fáciles, medias y algunas difíciles.

## Medir

- respuesta correcta
- parcialmente correcta
- incorrecta
- alucinación
- información inventada
- contradicciones
- seguridad con la que afirma información falsa

## Puntuación inicial

- 2 = correcta
- 1 = parcialmente correcta
- 0 = incorrecta


# 4. Castellano

## Objetivo

Evaluar competencia lingüística real en castellano.

## Probar

- conversación cotidiana
- explicación formal
- lenguaje coloquial
- corrección gramatical
- resumen
- cambio de registro
- instrucciones escritas informalmente
- errores ortográficos del usuario

## Medir

- gramática
- vocabulario
- naturalidad
- repeticiones
- calcos del inglés
- palabras inventadas
- comprensión de castellano informal


# 5. Seguimiento de instrucciones

## Objetivo

Comprobar si el modelo respeta restricciones exactas.

## Ejemplos

"Responde exactamente con tres palabras."

"Devuelve únicamente SI o NO."

"Explica esto en menos de 50 palabras."

"Devuelve exclusivamente el JSON solicitado."

## Medir

- cumplimiento exacto
- instrucciones ignoradas
- texto adicional no solicitado
- restricciones incumplidas

Especialmente importante para agentes y pipelines.


# 6. JSON y salida estructurada

## Objetivo

Comprobar si el modelo puede integrarse de forma fiable en software.

Ejemplo:

{
  "tipo": "libro",
  "area": "filosofia",
  "requiere_revision": false
}

## Medir

- JSON válido
- schema correcto
- tipos correctos
- campos obligatorios
- campos inventados
- valores permitidos
- texto fuera del JSON

Esta prueba debe poder evaluarse automáticamente.


# 7. Clasificación documental superficial

## Objetivo

Encontrar el modelo adecuado para actuar como "recepcionista" documental.

No debe realizar clasificaciones extremadamente profundas.

Categorías generales iniciales:

- filosofia
- literatura
- programacion
- futbol
- administracion
- finanzas
- ciencia
- multimedia
- personal
- otros

También:

- pendiente_clasificacion

## Entrada

Proporcionar:

- nombre del archivo
- extensión
- metadatos
- pequeño fragmento del contenido

## Medir

- accuracy
- categoría correcta
- matriz de confusión
- clasificaciones absurdas
- capacidad de detectar ambigüedad
- utilización correcta de pendiente_clasificacion

El modelo pequeño debe identificar el área general.

Ejemplo:

Documento de Ricoeur
→ filosofia

No necesitamos:

Documento de Ricoeur
→ filosofia/hermeneutica/francesa/sigloXX/identidad_narrativa

Eso corresponderá a agentes especializados.


# 8. Clasificación jerárquica

## Objetivo

Evaluar la arquitectura de clasificación progresiva.

Ejemplo:

Documento
↓
recepcionista
↓
filosofia
↓
especialista filosofia + RAG
↓
filosofia contemporanea
↓
especialista
↓
hermeneutica
↓
Ricoeur / identidad narrativa

Cada nivel debe reducir el espacio de decisión.

No todas las ramas necesitan la misma profundidad.


# 9. Routing de agentes

## Objetivo

Determinar qué agente debe recibir una petición.

Ejemplo:

"Tengo un PDF sobre identidad narrativa de Ricoeur."

Esperado:

{
  "agent": "filosofia"
}

Otros destinos posibles:

- programacion
- biblioteca
- filosofia
- futbol
- cocina
- administracion
- general
- etc.

## Medir

- agente correcto
- agente incorrecto
- rutas absurdas
- escalado innecesario
- utilización innecesaria de modelos grandes


# 10. RAG

## Objetivo

Evaluar la capacidad de utilizar información externa recuperada.

RAG NO modifica los parámetros del modelo.

Flujo:

documentos
↓
fragmentación
↓
embeddings
↓
base vectorial
↓
pregunta
↓
recuperación de fragmentos
↓
LLM
↓
respuesta

## Prueba controlada

Crear información ficticia que el modelo no pueda conocer.

Ejemplo:

"Marcelo Pepinillo nació en Terrassa en 1987."

Pregunta:

"¿Dónde nació Marcelo Pepinillo?"

## Comparar

A. Modelo sin RAG

B. Modelo con fragmento RAG

## Medir

- extracción correcta
- fidelidad al contexto
- información inventada
- contradicción del contexto
- capacidad de reconocer información ausente
- capacidad de responder "no consta"


# 11. Comprensión documental

## Objetivo

Evaluar capacidad para trabajar con documentos recuperados mediante RAG.

## Pruebas

- resumir
- extraer fechas
- extraer personas
- detectar argumento principal
- identificar temas
- comparar dos fragmentos
- responder preguntas
- detectar contradicciones

Especialmente importante para el futuro bibliotecario.


# 12. Razonamiento

Separar diferentes clases.

## 12.1 Lógica

Problemas pequeños con solución verificable.

## 12.2 Matemáticas

Operaciones y problemas numéricos.

## 12.3 Multi-step

Problemas que requieran varias decisiones.

## Medir

- resultado correcto
- pasos
- errores intermedios
- tiempo
- tokens utilizados
- efecto del thinking

Comparar cuando sea posible:

thinking ON
vs
thinking OFF


# 13. Thinking

Cuando el modelo exponga razonamiento, guardar:

- thinking completo
- longitud
- tokens aproximados
- duración
- respuesta final

Analizar si:

- el razonamiento contiene errores
- detecta sus propios errores
- divaga
- llega correctamente al resultado
- consume tokens innecesariamente

IMPORTANTE:

El thinking generado no debe considerarse automáticamente razonamiento
correcto ni datos adecuados para entrenamiento.


# 14. Tool Calling

## Objetivo

Evaluar comportamiento como agente.

Herramientas iniciales ficticias:

read_file(path)
inspect_metadata(path)
search_library(query)
move_file(source, destination)
ask_expert(agent, payload)
mark_pending(file)

## Medir

- herramienta correcta
- argumentos correctos
- orden de herramientas
- herramientas inventadas
- llamadas innecesarias
- capacidad de interpretar resultados
- capacidad de detenerse


# 15. Entornos de agentes

Crear entornos reproducibles para tareas reales.

Ejemplo:

ENVIRONMENT: document_router_v1

Entrada:
archivo + texto + metadatos

Herramientas:
inspect_metadata()
read_excerpt()
route_to()
mark_uncertain()

Destinos permitidos:
filosofia/
programacion/
futbol/
administracion/
personal/
otros/
pendiente/

Éxito:
destino esperado == destino elegido

Penalizaciones:

- inventar destinos
- mover sin inspeccionar
- formato inválido
- acciones innecesarias
- acciones peligrosas


# 16. Programación

Especialmente importante para modelos Coder.

## Pruebas

- escribir función
- corregir bug
- explicar código
- modificar código existente
- seguir una interfaz
- generar JSON/configuración
- producir diff
- utilizar documentación proporcionada

## Medir

- tests superados
- sintaxis
- funcionalidad
- cambios innecesarios
- APIs inventadas
- seguimiento de requisitos


# 17. Conversación

## Objetivo

Evaluar capacidad como asistente interactivo.

Probar:

- saludo
- conversación cotidiana
- cambios de tema
- preguntas sucesivas
- correcciones
- referencias anteriores
- conversaciones relativamente largas


# 18. Memoria dentro del contexto

Ejemplo:

Usuario:
"Para esta prueba mi fruta favorita es el mango."

Realizar varias interacciones.

Después:

"¿Cuál dije que era mi fruta favorita?"

## Medir

- recuperación correcta
- pérdida de información
- invención
- mezcla de datos


# 19. Estabilidad conversacional y roles

## Origen

Durante una prueba real con llama3.2:1b:

Usuario:
"hola"

Llama:
"¡Hola! ¿En qué puedo ayudarte?"

Usuario:
"Soy Raul"

Llama:
"¡Hola Raul!..."

Usuario:
"Como se suma?"

Llama:
"Raul, te pregunté cómo se suma, y no me dijiste nada..."

El modelo confundió quién había realizado la pregunta.

## Objetivo

Detectar:

- role confusion
- speaker confusion
- pérdida del estado conversacional
- atribución incorrecta de mensajes

## Caso inicial

ROLE_CONFUSION_001

1. Usuario: "Hola"
2. Asistente responde.
3. Usuario: "Soy Raul"
4. Asistente responde.
5. Usuario: "¿Cómo se suma?"

## Éxito

El modelo interpreta correctamente que el usuario está preguntando cómo sumar.

## Fallo

El modelo:

- atribuye la pregunta al asistente
- inventa conversación previa
- confunde interlocutores
- pierde el estado

## Métricas

- role_confusion
- speaker_attribution
- context_recall
- conversation_consistency
- turn_count_before_failure


# 20. Perfiles personales

## Objetivo

Evaluar el futuro recepcionista personal.

El sistema tendrá distintos perfiles de usuario.

Ejemplo:

{
  "usuario": "A",
  "intereses": [
    "filosofia",
    "programacion"
  ],
  "proyectos_recientes": [
    "biblioteca"
  ]
}

El modelo deberá recomendar agentes/secciones relevantes.

Después se cambia completamente de perfil.

## Medir

- recomendaciones relevantes
- adaptación al perfil
- mezcla entre perfiles
- utilización correcta del contexto
- privacidad entre usuarios


# 21. Perfil Invitado

Crear un usuario especial:

Invitado

Características:

- sin memoria permanente
- sin acceso a documentos privados
- herramientas restringidas
- RAG público/demo
- sesión temporal
- límites de recursos

Benchmark:

comprobar que el modelo nunca utiliza información perteneciente a otros
perfiles.


# 22. Seguridad operativa

No centrado únicamente en safety conversacional.

Nos importa proteger el sistema real.

## Reglas

- no borrar archivos sin autorización
- no sobrescribir originales
- no acceder a rutas prohibidas
- preferir pendiente ante incertidumbre
- no inventar herramientas
- respetar permisos
- no ejecutar acciones irreversibles innecesariamente

## Medir

- acciones peligrosas
- violaciones de permisos
- comportamiento ante ambigüedad
- resistencia a instrucciones conflictivas


# 23. Historial de tareas reales

Las tareas reales del sistema deben poder convertirse en benchmarks futuros.

Guardar:

- task_id
- input
- modelo
- prompt
- contexto
- herramientas disponibles
- herramientas utilizadas
- acciones
- output
- destino final
- éxito/fallo
- duración
- tokens
- corrección humana
- respuesta/destino correcto


# 24. Correcciones humanas

Cuando el usuario corrija una decisión:

Modelo:
filosofia

Usuario:
literatura/teoria_literaria

Guardar la corrección.

Esa tarea puede convertirse automáticamente en un nuevo caso del benchmark.

Así:

USO REAL
↓
DECISIONES
↓
CORRECCIONES
↓
DATASET
↓
BENCHMARK
↓
COMPARACIÓN DE MODELOS


# 25. Evaluación de modelos nuevos

Cuando aparezca un modelo nuevo:

1. Descargar.
2. Ejecutar benchmarks técnicos.
3. Ejecutar benchmarks generales.
4. Ejecutar benchmarks específicos de cada tarea.
5. Ejecutar historial de tareas reales.
6. Comparar contra modelo de producción.
7. Decidir si sustituirlo.


# 26. No utilizar una puntuación global única

Evitar:

"Qwen = 8.4/10"

Preferir:

qwen3:0.6b

Factualidad:          50%
Castellano:           82%
Clasificación:        96%
Routing:              97%
JSON:                 99%
RAG:                  89%
Tool calling:         93%
Razonamiento:         45%
Programación:         54%
Conversación:         70%
Role stability:       60%
Velocidad:            22 tok/s


# 27. Selección por tarea

Cada tarea tendrá un umbral mínimo.

Ejemplo:

TASK: document_router
accuracy mínima: 95%

Resultados:

qwen3:0.6b     96.2%
qwen3:1.7b     98.3%
modelo 4B      99.0%

Ganador:

qwen3:0.6b

Razón:

Es el modelo más pequeño que supera el requisito.

No utilizar un modelo más grande simplemente porque obtenga una puntuación
ligeramente superior.


# 28. Escalado entre modelos

Permitir pipelines jerárquicos.

Ejemplo:

0.6B
↓
clasificación superficial
↓
¿caso fácil?
├── sí → terminar
└── no
    ↓
1.7B + RAG especializado
    ↓
¿resuelto?
├── sí → terminar
└── no
    ↓
3B/4B especializado

El modelo caro solo procesa los casos difíciles.


# 29. Especialistas

No necesitamos necesariamente instalar un modelo físico por especialista.

Un mismo modelo puede alimentar:

Agente Filosofía
Agente Fútbol
Agente Programación
Agente Literatura

Cambiando:

- system prompt
- RAG
- herramientas
- permisos
- ejemplos
- memoria


# 30. Dashboard futuro

Crear un dashboard que muestre:

AI SERVER

Document Router
Modelo: qwen3:0.6b
Accuracy: 96.2%
Casos evaluados: 1843

Filosofía
Modelo: qwen3:1.7b
RAG: filosofia_v3
Accuracy: 97.1%

Programación
Modelo: qwen-coder
Accuracy: 96.8%

Bibliotecario
Modelo: ...
RAG: biblioteca

También mostrar candidatos:

Modelo actual:
qwen3:0.6b → 96.2%

Candidato:
nuevo-modelo → 98.1%

Opciones futuras:

[Comparar]
[Ejecutar benchmark]
[Promover candidato]


# 31. Configuración de modelos

La asignación de modelos debe estar en configuración, no hardcodeada.

Ejemplo conceptual:

tasks:
  document_router:
    model: qwen3:0.6b

  philosophy_classifier:
    model: qwen3:1.7b
    rag: philosophy

  code_agent:
    model: qwen-coder


# 32. Evolución del sistema

Orden previsto:

USAR
↓
EVALUAR
↓
CORREGIR
↓
ACUMULAR CASOS
↓
CREAR DATASET PROPIO
↓
COMPARAR MODELOS
↓
MEJORAR PROMPTS
↓
MEJORAR RAG
↓
MEJORAR AGENTES
↓
EVENTUALMENTE FINE-TUNING / RL


# 33. Fine-tuning

No comenzar entrenando modelos.

Plantearlo cuando tengamos:

- suficientes ejemplos reales
- errores repetitivos identificados
- prompts/RAG que ya no solucionen el problema
- dataset limpio
- evaluación reproducible

El entrenamiento probablemente se realizaría en hardware externo con GPU.


# 34. Reinforcement Learning

El Reinforcement Learning podría explorarse posteriormente para agentes.

Necesitaríamos:

- entorno
- tareas
- acciones
- herramientas
- criterio de éxito
- reward
- verificadores

Ejemplo:

Tarea:
clasificar documento

Resultado:

destino correcto → recompensa positiva

acción peligrosa → penalización

destino incorrecto → penalización


# 35. Principio fundamental

No queremos construir:

> Una IA gigantesca que haga todo.

Queremos construir:

> Una red de modelos y agentes especializados donde cada tarea sea ejecutada
> por el modelo más eficiente que pueda realizarla correctamente.

La arquitectura debe permitir sustituir modelos continuamente conforme
aparezcan modelos mejores.
