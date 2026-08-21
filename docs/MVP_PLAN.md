# MVP Plan

## 1. Objetivo

Construir `rgb-ai` de forma incremental, evitando implementar demasiado pronto
componentes que todavía no necesitamos.

La prioridad es conseguir un sistema pequeño, medible y funcional que permita:

- ejecutar modelos locales mediante Ollama;
- evaluar modelos de forma reproducible;
- comparar modelos por tarea;
- guardar resultados y métricas;
- añadir posteriormente agentes, RAG, usuarios y dashboard sin rehacer la base.

La regla principal es:

> No avanzar a una fase nueva hasta que la anterior funcione, tenga tests y sea suficientemente estable.


# 2. Principios de desarrollo

## 2.1 Implementar solo lo necesario

No implementar una entidad o servicio únicamente porque aparezca en
`DATA_MODEL.md`.

Ese documento describe el modelo conceptual completo.

El MVP debe implementar únicamente los componentes necesarios para la fase actual.


## 2.2 Medir antes de añadir complejidad

Antes de incorporar:

- un modelo mayor;
- RAG;
- un nuevo agente;
- nuevas herramientas;
- fine-tuning;
- reinforcement learning;

debe existir un problema medido que justifique esa complejidad.


## 2.3 Todo debe ser sustituible

No acoplar tareas a un modelo concreto.

La lógica debe permitir cambiar:

```text
qwen3:0.6b
```

por:

```text
gemma3:1b
```

sin reescribir la tarea.


## 2.4 Separar producción y experimentación

Los benchmarks deben poder probar modelos candidatos sin afectar al modelo
actualmente asignado a una tarea real.


## 2.5 Priorizar verificadores automáticos

Siempre que sea posible:

- JSON → validar con schema
- clasificación → comparar categoría
- matemáticas → calcular resultado
- código → ejecutar tests
- routing → comparar destino esperado

Evitar evaluación subjetiva cuando exista una alternativa determinista.


# 3. Fase 0 — Documentación y laboratorio manual

Estado: EN PROGRESO / CASI COMPLETADA

Objetivo:

Definir el sistema antes de programarlo.

Documentación inicial:

```text
docs/
├── ARCHITECTURE.md
├── BENCHMARK_PLAN.md
├── DATA_MODEL.md
├── ENVIRONMENTS.md
├── IDEAS.md
└── MVP_PLAN.md
```

Laboratorio actual:

```text
rgb-ai server
↓
Ollama
↓
modelos locales
↓
benchmarks manuales
↓
CSV
```

Modelos iniciales probados o en proceso:

- qwen3:0.6b
- qwen3:1.7b
- llama3.2:1b
- gemma3:1b
- qwen2.5:1.5b
- qwen2.5-coder:1.5b
- deepseek-r1:1.5b
- modelos adicionales

Criterio de finalización:

- documentación base creada;
- Ollama funcionando;
- varios modelos instalados;
- primeras métricas manuales disponibles.


# 4. Fase 1 — Benchmark Engine mínimo

Esta es la PRIMERA fase que Codex debe implementar.

No implementar todavía:

- RAG;
- frontend web;
- usuarios;
- memoria;
- agentes complejos;
- tool calling real;
- clasificación de archivos reales;
- fine-tuning;
- RL.


## 4.1 Objetivo

Crear un motor de benchmarks capaz de ejecutar un prompt contra un modelo de
Ollama y guardar automáticamente:

- respuesta;
- métricas;
- tiempos;
- tokens;
- modelo;
- configuración;
- resultado.


## 4.2 Funcionalidad mínima

Debe poder ejecutarse algo conceptualmente similar a:

```bash
python -m rgb_ai benchmark run \
  --model qwen3:0.6b \
  --test factual_001
```

No es obligatorio que esta sea exactamente la interfaz final.

El objetivo funcional es:

```text
test case
   +
model
   ↓
Ollama
   ↓
response
   ↓
metrics
   ↓
result store
```


## 4.3 Cliente Ollama

Crear una capa propia para comunicarse con Ollama.

Responsabilidades:

- enviar prompt;
- elegir modelo;
- configurar parámetros;
- recoger respuesta;
- recoger métricas;
- manejar errores;
- controlar timeout.

El resto del proyecto no debe llamar directamente a Ollama por todas partes.

Debe existir una abstracción reutilizable.


## 4.4 Registro inicial de modelos

Crear un registro sencillo de modelos.

Puede comenzar en YAML o JSON.

Ejemplo conceptual:

```yaml
models:
  qwen3_06b:
    ollama_name: qwen3:0.6b
    family: qwen3
    parameters_b: 0.6
    specialization: generalist

  deepseek_r1_15b:
    ollama_name: deepseek-r1:1.5b
    family: deepseek-r1
    parameters_b: 1.5
    specialization: reasoning
```

No implementar todavía una base de datos compleja si no hace falta.


## 4.5 Test cases

Crear una estructura simple para tests.

Ejemplo:

```json
{
  "id": "FACTUAL_001",
  "category": "factual",
  "prompt": "Explica en unas 100 palabras por qué el cielo se ve azul. Responde en castellano."
}
```

Más adelante estos tests evolucionarán hacia environments y datasets completos.


## 4.6 Resultados

Guardar resultados en formato estructurado.

Ejemplo:

```json
{
  "test_id": "FACTUAL_001",
  "model": "qwen3:1.7b",
  "response": "...",
  "metrics": {
    "prompt_tokens": 36,
    "output_tokens": 322,
    "prompt_tokens_per_second": 19.16,
    "output_tokens_per_second": 9.91,
    "total_duration_seconds": 34.99
  }
}
```

Inicialmente puede utilizarse:

- JSONL;
- JSON;
- SQLite.

Preferencia inicial:

usar una solución sencilla.

No diseñar una infraestructura de datos distribuida.


## 4.7 Importar benchmarks manuales existentes

Si es sencillo, permitir incorporar posteriormente los resultados ya guardados en
`benchmarks.csv`.

No bloquear la Fase 1 por esta migración.


## 4.8 Tests de Fase 1

Crear tests para:

- cliente Ollama;
- parsing de métricas;
- registro de modelos;
- carga de test cases;
- guardado de resultados;
- manejo de modelo inexistente;
- timeout;
- respuesta vacía.

Criterio de finalización:

- se puede ejecutar un benchmark de principio a fin;
- resultado queda guardado automáticamente;
- métricas principales quedan registradas;
- tests pasan.


# 5. Fase 2 — Primer Environment: document_router_v1

Solo comenzar cuando Fase 1 esté terminada.


## 5.1 Objetivo

Crear el primer environment reproducible real.

Tarea:

```text
document_router
```

Objetivo:

clasificar documentos superficialmente.


## 5.2 No mover archivos todavía

En esta fase el sistema NO toca archivos reales.

Entrada simulada:

```json
{
  "filename": "ricoeur.pdf",
  "extension": ".pdf",
  "excerpt": "Paul Ricoeur analiza la identidad narrativa..."
}
```

Salida:

```json
{
  "category": "filosofia"
}
```


## 5.3 Categorías iniciales

```text
filosofia
literatura
programacion
futbol
administracion
finanzas
ciencia
multimedia
personal
otros
pendiente_clasificacion
```


## 5.4 Dataset inicial

Crear aproximadamente:

- 10 casos triviales;
- 20 casos fáciles;
- 20 casos medios;
- 10 casos difíciles;
- 10 ambiguos;
- algunos adversariales.

El dataset debe crecer posteriormente.


## 5.5 Verifier

El verifier inicial puede ser determinista:

```text
predicted_category == expected_category
```

También validar:

- JSON válido;
- categoría permitida;
- ausencia de texto adicional si se exige JSON puro.


## 5.6 Comparar modelos

Ejecutar el mismo dataset contra todos los modelos relevantes.

Ejemplo:

```text
qwen3:0.6b
gemma3:1b
qwen3:1.7b
llama3.2:1b
...
```

Generar:

- accuracy;
- invalid output rate;
- duración media;
- tokens medios;
- tok/s;
- estabilidad.


## 5.7 Primer modelo de producción

Elegir el modelo más pequeño que supere el threshold definido.

No elegir automáticamente el de mayor accuracy.


## 5.8 Criterio de finalización

- environment implementado;
- dataset versionado;
- verifier funcionando;
- varios modelos comparados;
- resultados reproducibles;
- primer modelo seleccionado para la tarea.


# 6. Fase 3 — Tool Calling simulado

Objetivo:

introducir comportamiento agentic sin permitir todavía acciones reales.


## 6.1 Herramientas simuladas

Ejemplo:

```text
inspect_metadata()
read_excerpt()
route_to()
mark_pending()
```

Las herramientas devolverán datos simulados o trabajarán sobre fixtures.


## 6.2 Evaluar

Medir:

- herramienta correcta;
- argumentos válidos;
- orden;
- herramientas inventadas;
- llamadas innecesarias;
- loops;
- capacidad de terminar.


## 6.3 Primer Agent Environment

Crear una versión agentic de document_router.

Ejemplo:

```text
archivo
↓
inspect_metadata
↓
read_excerpt
↓
route_to
↓
done
```

Criterio de finalización:

- se pueden ejecutar episodios;
- se registran steps;
- se registran tool calls;
- verifier evalúa resultado final;
- no existe acceso a archivos reales.


# 7. Fase 4 — Documentos reales en sandbox

Objetivo:

trabajar con archivos reales sin poner en riesgo documentos del usuario.


## 7.1 Sandbox

Crear una carpeta temporal controlada.

Ejemplo:

```text
sandbox/
├── inbox/
├── filosofia/
├── literatura/
├── programacion/
└── pendiente/
```


## 7.2 Archivos de prueba

Utilizar:

- documentos sintéticos;
- copias;
- archivos creados específicamente para tests.

Nunca usar documentos importantes como primera prueba.


## 7.3 Tools reales pero restringidas

Ejemplo:

```text
read_document()
inspect_metadata()
move_document()
mark_pending()
```

Las herramientas deben validar rutas.

Nunca aceptar paths arbitrarios generados por el modelo.


## 7.4 Seguridad

Impedir:

- acceso fuera del sandbox;
- borrado;
- overwrite;
- shell arbitrario.

Criterio de finalización:

- el agente puede clasificar y mover archivos de prueba;
- ningún modelo puede escapar del sandbox;
- tests de seguridad pasan.


# 8. Fase 5 — Ingesta documental

Objetivo:

crear una pipeline básica para documentos.

```text
archivo
↓
detección tipo
↓
extracción texto
↓
metadata
↓
document_id
↓
almacenamiento
```


## 8.1 Formatos iniciales

Empezar con pocos formatos:

- txt
- md
- pdf

Posteriormente:

- docx
- html
- epub
- imágenes/OCR cuando sea necesario.


## 8.2 Metadata mínima

Guardar:

- document_id;
- filename;
- path;
- mime_type;
- checksum;
- size;
- imported_at;
- extracted_text status.


## 8.3 No hacer taxonomía profunda todavía

La ingesta no depende de que el sistema de carpetas sea perfecto.


# 9. Fase 6 — RAG mínimo

Objetivo:

crear la primera recuperación semántica local.


## 9.1 Pipeline

```text
document
↓
text
↓
chunks
↓
embedding model
↓
vector store
↓
query
↓
retrieval
↓
LLM
```


## 9.2 Modelo de embeddings

Seleccionar mediante benchmark.

No asumir que el primer embedding model probado es definitivo.


## 9.3 Vector store

Qdrant es candidato principal.

No implementar hasta esta fase.


## 9.4 Chunking

Comenzar con una estrategia sencilla y configurable.

Guardar siempre:

- document_id;
- chunk_id;
- índice;
- contenido;
- metadata.


## 9.5 Benchmark de retrieval

Crear casos donde conozcamos el fragmento correcto.

Medir:

- hit@k;
- recall@k;
- ranking.


## 9.6 Benchmark de generación

Proporcionar directamente el fragmento correcto a distintos LLM.

Esto permite separar:

```text
retrieval error
```

de:

```text
generation/reasoning error
```


## 9.7 Prueba ficticia

Crear información que ningún modelo pueda conocer.

Ejemplo:

```text
Marcelo Pepinillo nació en Terrassa en 1987.
```

Pregunta:

```text
¿Dónde nació Marcelo Pepinillo?
```

Comparar:

- sin RAG;
- con RAG;
- contexto irrelevante;
- contexto contradictorio.


# 10. Fase 7 — Especialistas por dominio

Objetivo:

crear los primeros agentes especializados.

Ejemplos:

- filosofia;
- programacion;
- futbol;
- biblioteca.


## 10.1 No instalar un modelo por especialista

Un agente está definido por:

```text
modelo
+
prompt
+
RAG
+
tools
+
permissions
```

Varios agentes pueden utilizar el mismo modelo físico.


## 10.2 Routing jerárquico

Ejemplo:

```text
document_router pequeño
↓
filosofia
↓
philosophy_agent + RAG
↓
clasificación más profunda
```


## 10.3 Escalado

Permitir:

```text
modelo pequeño
↓
caso difícil
↓
modelo medio
↓
caso muy difícil
↓
modelo grande
```

Medir siempre el pipeline completo.


# 11. Fase 8 — Tareas reales y feedback

Objetivo:

empezar a utilizar el sistema en tareas reales.


## 11.1 Registrar

Guardar:

- input;
- modelo;
- environment;
- respuesta;
- herramientas;
- tiempo;
- tokens.


## 11.2 Feedback

Permitir marcar:

- correcto;
- incorrecto;
- parcialmente correcto.


## 11.3 Correcciones

Cuando el usuario corrija una salida:

guardar la corrección.


## 11.4 Benchmark Candidates

Una tarea corregida debe poder proponerse como futuro test case.

Flujo:

```text
real task
↓
error
↓
human correction
↓
benchmark candidate
↓
review
↓
dataset
```


# 12. Fase 9 — Personal Receptionist

Objetivo:

crear el punto de entrada personal a la plataforma.

Entrada:

- usuario;
- perfil;
- actividad reciente;
- agentes disponibles;
- petición actual.

Salida:

- agente recomendado;
- acción sugerida;
- routing.


## 12.1 Perfiles

Crear inicialmente:

- owner;
- member;
- guest.


## 12.2 Personalización

Utilizar:

- preferencias;
- agentes recientes;
- proyectos recientes;
- memoria resumida.


## 12.3 Benchmark

Evaluar:

- routing;
- personalización;
- confusión entre perfiles;
- estabilidad conversacional;
- role confusion.


# 13. Fase 10 — Invitado

Objetivo:

permitir demos seguras.

Guest debe tener:

- sesión temporal;
- sin memoria persistente;
- sin acceso privado;
- herramientas limitadas;
- RAG público/demo.

La seguridad debe implementarse en backend.


# 14. Fase 11 — Dashboard web

No comenzar antes de que el backend tenga datos reales útiles.

Objetivo:

mostrar el estado del sistema.


## 14.1 Pantalla modelos

Mostrar:

- modelos instalados;
- tamaños;
- especialización;
- benchmarks;
- rendimiento.


## 14.2 Pantalla tareas

Ejemplo:

```text
Document Router
Production: qwen3:0.6b
Accuracy: 96.2%
Average latency: ...
```

Mostrar candidatos.


## 14.3 Comparación

Permitir visualizar:

```text
actual
vs
candidate
```


## 14.4 Promoción

En el futuro permitir promover un modelo candidato a producción.

La acción debe quedar auditada.


# 15. Fase 12 — Automatización de benchmarks

Objetivo:

ejecutar periódicamente benchmarks contra nuevos modelos.

Ejemplo:

```text
nuevo modelo
↓
registry
↓
benchmark suite
↓
comparación
↓
candidate report
```


# 16. Fase 13 — Dataset propio

Cuando exista suficiente uso real:

crear datasets internos derivados de:

- errores;
- correcciones;
- tareas reales;
- casos difíciles;
- casos adversariales.

Separar:

- train
- validation
- test


# 17. Fase 14 — Fine-tuning

Solo plantearlo si existe evidencia.

Condiciones mínimas:

- dataset suficientemente grande;
- errores repetitivos;
- buen benchmark;
- prompt + RAG insuficientes;
- ventaja clara esperada.

El entrenamiento puede realizarse en hardware externo.


# 18. Fase 15 — Reinforcement Learning

Fase experimental futura.

Solo si ya existen:

- environments maduros;
- verificadores;
- rewards;
- datasets;
- tareas agentic repetibles.

No forma parte del MVP.


# 19. Qué debe implementar Codex primero

Cuando Codex empiece a trabajar en el proyecto debe:

1. Leer toda la documentación de `docs/`.
2. Inspeccionar el repositorio.
3. Implementar únicamente Fase 1.
4. Crear tests.
5. Documentar decisiones necesarias.
6. No implementar componentes de fases futuras salvo interfaces mínimas necesarias.


# 20. Qué NO debe hacer Codex en la primera fase

No debe:

- instalar Qdrant;
- crear frontend;
- implementar usuarios;
- crear autenticación;
- implementar memoria;
- montar RAG;
- mover archivos reales;
- crear agentes complejos;
- introducir Docker salvo que exista una necesidad clara;
- implementar PostgreSQL sin necesidad;
- crear decenas de abstracciones futuras;
- hacer fine-tuning;
- implementar RL.


# 21. Definition of Done — Fase 1

La Fase 1 termina cuando:

```text
modelo registrado
↓
test cargado
↓
Ollama ejecutado
↓
respuesta recibida
↓
métricas parseadas
↓
resultado guardado
```

y además:

- existen tests;
- errores básicos están manejados;
- documentación mínima está actualizada;
- puede ejecutarse más de un modelo;
- resultados son comparables.


# 22. Definition of Done — MVP inicial

Considerar el primer MVP realmente útil cuando podamos:

1. registrar modelos;
2. ejecutar benchmarks;
3. crear environments;
4. comparar modelos;
5. ejecutar `document_router_v1`;
6. seleccionar un modelo para esa tarea;
7. probarlo sobre archivos dentro de sandbox;
8. registrar resultados y correcciones.

En ese punto ya existe un sistema funcional, aunque todavía no haya:

- RAG;
- usuarios;
- dashboard;
- memoria;
- agentes avanzados.


# 23. Principio final

El proyecto debe evolucionar desde:

```text
experimentos manuales
```

hacia:

```text
experimentos reproducibles
```

después:

```text
tareas reales controladas
```

y finalmente:

```text
plataforma multiagente adaptativa
```

Nunca debemos saltar directamente al último nivel.

Cada capa debe existir porque la anterior ha demostrado una necesidad real.

