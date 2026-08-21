# RAG Design

## 1. Objetivo

Definir cómo funcionará el sistema RAG de `rgb-ai`.

RAG significa:

Retrieval-Augmented Generation

La idea es separar claramente:

- documentos;
- extracción de texto;
- chunking;
- embeddings;
- almacenamiento vectorial;
- retrieval;
- reranking;
- construcción de contexto;
- generación mediante LLM;
- evaluación.

El RAG NO modifica los pesos del LLM.

El modelo recibe información recuperada en tiempo de consulta.


# 2. Principio fundamental

Separar siempre:

RETRIEVAL

de:

GENERATION

Un error en una respuesta puede deberse a:

1. el sistema recuperó información incorrecta;
2. recuperó información correcta pero el LLM la interpretó mal.

Nunca evaluar ambas partes como si fueran un único componente.


# 3. Arquitectura general

```text
DOCUMENTOS
    |
    v
EXTRACCIÓN DE TEXTO
    |
    v
NORMALIZACIÓN
    |
    v
CHUNKING
    |
    v
EMBEDDING MODEL
    |
    v
VECTOR STORE
    |
    v
----------------------------
          QUERY
            |
            v
     EMBEDDING MODEL
            |
            v
     VECTOR SEARCH
            |
            v
     TOP-K CHUNKS
            |
            v
        RERANKER
            |
            v
      TOP-N CHUNKS
            |
            v
    CONTEXT BUILDER
            |
            v
           LLM
            |
            v
        RESPUESTA
```


# 4. Componentes iniciales

Componentes candidatos iniciales:

Embedding model:

```text
embeddinggemma
```

Vector store:

```text
Qdrant
```

Reranker futuro:

```text
BAAI/bge-reranker-v2-m3
```

LLMs:

modelos registrados en `rgb-ai`.

Ninguno de estos componentes debe quedar hardcodeado.


# 5. Document Ingestion

Cada documento debe pasar por una pipeline de ingesta.

```text
archivo
↓
identificación
↓
extracción
↓
normalización
↓
metadata
↓
chunking
↓
embeddings
↓
indexación
```


# 6. Identificación de documentos

Cada documento debe tener un `document_id` estable.

No utilizar únicamente:

- filename;
- path;

como identificador.

Dos documentos pueden tener el mismo nombre.

Un documento también puede cambiar de ubicación.


# 7. Metadata mínima

Guardar como mínimo:

- document_id
- filename
- path
- mime_type
- size_bytes
- checksum
- imported_at
- modified_at
- source
- owner
- visibility

Metadata adicional puede añadirse posteriormente.


# 8. Formatos iniciales

Empezar únicamente con formatos fáciles de procesar.

Primera versión:

- `.txt`
- `.md`
- `.pdf`

Posteriormente:

- `.docx`
- `.epub`
- `.html`
- imágenes
- documentos escaneados
- OCR

No intentar soportar todos los formatos desde la primera versión.


# 9. Text Extraction

El extractor debe devolver texto y metadata estructurada.

Ejemplo conceptual:

```json
{
  "document_id": "doc_001",
  "text": "...",
  "metadata": {
    "pages": 142,
    "language": "es"
  }
}
```

No mezclar extracción con clasificación semántica.


# 10. Normalización

Antes del chunking puede aplicarse normalización.

Ejemplos:

- limpiar espacios redundantes;
- normalizar saltos de línea;
- eliminar headers repetidos cuando sea posible;
- conservar estructura útil;
- conservar títulos y secciones.

Evitar destruir información estructural relevante.


# 11. Chunking

Los documentos deben dividirse en fragmentos.

Un chunk debe tener:

- chunk_id
- document_id
- chunk_index
- content
- token_count aproximado
- metadata

Ejemplo:

```json
{
  "chunk_id": "chunk_001_04",
  "document_id": "doc_001",
  "chunk_index": 4,
  "content": "Ricoeur distingue entre identidad-idem...",
  "metadata": {
    "page": 42,
    "section": "Identidad narrativa"
  }
}
```


# 12. Estrategia inicial de chunking

Comenzar con una estrategia sencilla y configurable.

Ejemplo conceptual:

```text
chunk_size = 400-800 tokens
overlap = 50-100 tokens
```

Estos valores NO deben asumirse como óptimos.

Deben poder modificarse mediante configuración y benchmark.


# 13. Chunking estructural

Cuando sea posible, respetar:

- capítulos;
- secciones;
- párrafos;
- headings;
- páginas.

Preferir no cortar arbitrariamente una idea en mitad de una frase si puede evitarse.

Posteriormente pueden existir chunkers específicos por formato.


# 14. Chunk overlap

El overlap puede ayudar a evitar pérdida de información entre chunks.

Demasiado overlap produce:

- mayor almacenamiento;
- resultados duplicados;
- retrieval redundante.

Demasiado poco overlap puede perder contexto.

Debe evaluarse.


# 15. Embeddings

Los embeddings representan el significado aproximado de un texto como un vector.

Ejemplo conceptual:

```text
"Paul Ricoeur estudia la identidad narrativa"
↓
embedding model
↓
[0.18, -0.31, 0.77, ...]
```


# 16. Embedding Model

Primer candidato:

```text
embeddinggemma
```

Actualmente observado:

```text
dimensiones: 768
```

Ejemplo manual observado:

```text
Ricoeur vs filosofía ≈ 0.503
Ricoeur vs fútbol    ≈ 0.169
```

Esto demuestra comportamiento semántico básico correcto.

No asumir que será el embedding definitivo.


# 17. Embedding Registry

Los embedding models deben registrarse igual que los LLM.

Guardar:

- embedding_model_id
- provider
- name
- dimensions
- languages
- disk_size
- runtime metrics
- benchmark results


# 18. Query Embedding

La consulta del usuario debe convertirse utilizando el MISMO embedding model
utilizado para indexar los chunks.

MAL:

```text
chunks → embedding model A
query  → embedding model B
```

BIEN:

```text
chunks → embedding model A
query  → embedding model A
```


# 19. Reindexado

Si cambia el embedding model, generalmente será necesario recalcular embeddings.

Por tanto, cada embedding almacenado debe indicar:

- embedding_model_id
- model_version
- dimensions

El sistema debe poder coexistir temporalmente con varios índices/versiones.


# 20. Vector Store

Candidato inicial:

```text
Qdrant
```

Responsabilidades:

- almacenar vectores;
- metadata asociada;
- búsqueda por similitud;
- filtros;
- top-k retrieval.


# 21. Separación de almacenamiento

El vector store NO sustituye la base documental.

Qdrant almacena principalmente:

- vector;
- referencia al chunk;
- metadata útil.

El documento original y el contenido completo deben mantenerse en almacenamiento
documental normal.


# 22. Retrieval

Una consulta produce una lista de chunks candidatos.

Ejemplo:

```text
query
↓
embedding
↓
Qdrant
↓
top 20 chunks
```


# 23. Top-K

`top_k` debe ser configurable.

Ejemplo inicial:

```text
top_k = 10-20
```

Demasiado pequeño:

puede perder el chunk correcto.

Demasiado grande:

aumenta ruido y coste de reranking.


# 24. Filtros

El retrieval puede utilizar filtros de metadata.

Ejemplos:

- user_id;
- visibility;
- domain;
- document type;
- date;
- collection.

Ejemplo:

```text
search:
"identidad narrativa"

filters:
domain = filosofia
visibility = allowed_for_user
```


# 25. Privacidad en retrieval

Los permisos deben aplicarse ANTES de proporcionar chunks al LLM.

Nunca confiar únicamente en un prompt como:

```text
"No muestres documentos privados."
```

El backend debe impedir que chunks no autorizados entren en los resultados.


# 26. Reranking

El vector search es rápido pero no siempre ordena perfectamente los resultados.

Pipeline futuro:

```text
20 chunks recuperados
↓
reranker
↓
5 chunks más relevantes
```


# 27. Reranker inicial candidato

Candidato futuro:

```text
BAAI/bge-reranker-v2-m3
```

El reranker recibe conceptualmente:

```text
query + chunk
```

y devuelve una puntuación de relevancia.


# 28. Reranking no forma parte de la primera versión

La primera versión del RAG puede funcionar sin reranker.

Implementar primero:

```text
embedding
+
vector search
+
LLM
```

Después medir si el reranker mejora resultados.


# 29. Context Builder

El Context Builder recibe los chunks seleccionados y construye el contexto que se
entregará al LLM.

Responsabilidades:

- ordenar chunks;
- incluir referencias;
- evitar duplicados;
- respetar límite de contexto;
- indicar fuente;
- aplicar formato consistente.


# 30. Context Example

Ejemplo conceptual:

```text
Utiliza únicamente el contexto proporcionado cuando responda a información
documental específica.

SOURCE 1
document_id: doc_ricoeur
page: 42

Ricoeur distingue entre identidad-idem e identidad-ipse...

SOURCE 2
document_id: doc_ricoeur
page: 48

La identidad narrativa...
```


# 31. Context Budget

Los modelos locales tienen ventanas de contexto limitadas.

No enviar todos los chunks recuperados.

Debe existir un presupuesto.

Ejemplo:

```text
max_context_tokens = configurable
```

El sistema seleccionará chunks hasta alcanzar el límite.


# 32. Modelos pequeños y RAG

Un modelo pequeño puede funcionar mejor con:

- menos chunks;
- chunks más relevantes;
- instrucciones claras;
- contexto poco redundante.

La calidad del retrieval es especialmente importante cuando el LLM tiene poca
capacidad.


# 33. Generation

El LLM recibe:

```text
system prompt
+
query
+
retrieved context
```

y produce una respuesta.


# 34. Grounded Generation

Para tareas documentales, el prompt debería priorizar respuestas basadas en el
contexto.

Ejemplo:

```text
Si la información no aparece en el contexto, responde que no consta.
No inventes información para completar huecos.
```


# 35. Citations

El sistema debería conservar las fuentes utilizadas.

Una respuesta futura puede incluir referencias como:

```text
Ricoeur distingue identidad-idem e identidad-ipse [doc_ricoeur, p.42].
```

No es necesario implementar un sistema visual de citas en la primera versión,
pero las referencias deben mantenerse disponibles.


# 36. RAG Collections

Separar conocimiento por colección cuando sea útil.

Ejemplos:

```text
rag_philosophy
rag_programming
rag_football
rag_library
```

Una colección puede contener miles de documentos.


# 37. Collections vs folders

La colección RAG no debe depender directamente de la estructura física de carpetas.

Un archivo puede estar físicamente en:

```text
/inbox/pendiente/documento.pdf
```

y pertenecer semánticamente a:

```text
rag_philosophy
```

Esto permite indexar documentos antes de tener una clasificación física perfecta.


# 38. Multi-collection Retrieval

Un agente puede consultar una o varias colecciones.

Ejemplo:

```text
philosophy_agent
↓
rag_philosophy
```

Un agente generalista podría buscar primero qué colección utilizar.


# 39. Benchmark Retrieval

Crear un environment específico.

Ejemplo:

```text
retrieval_v1
```

Input:

```json
{
  "query": "...",
  "expected_chunk_ids": ["chunk_123"]
}
```

Output:

lista de chunks recuperados.


# 40. Retrieval Metrics

Medir:

- Hit@1
- Hit@3
- Hit@5
- Recall@k
- Precision@k
- rank del primer chunk correcto
- latencia
- uso de RAM
- throughput


# 41. Primer benchmark de embeddings

Crear documentos donde el resultado correcto sea conocido.

Ejemplo:

Chunk A:

```text
Paul Ricoeur desarrolla el concepto de identidad narrativa.
```

Chunk B:

```text
El delantero marcó dos goles al contraataque.
```

Query:

```text
¿Qué filósofo habla de identidad narrativa?
```

Esperado:

Chunk A por encima de Chunk B.


# 42. Casos difíciles

No limitarse a ejemplos triviales.

Crear chunks semánticamente parecidos.

Ejemplo:

Chunk A:

```text
Ricoeur estudia la identidad narrativa del sujeto.
```

Chunk B:

```text
La identidad nacional se construye mediante narraciones históricas.
```

Query:

```text
¿Cómo entiende Ricoeur la identidad personal?
```

El retrieval debe priorizar Chunk A.


# 43. Hard Negatives

Los benchmarks deben incluir hard negatives:

fragmentos muy relacionados lexicalmente pero incorrectos.

Esto permite medir la calidad real del embedding.


# 44. Benchmark Generation

Separar un environment diferente:

```text
rag_generation_v1
```

Aquí se proporciona directamente el contexto correcto.

Input:

```json
{
  "question": "...",
  "context": "..."
}
```

Esto mide únicamente la capacidad del LLM para utilizar información recuperada.


# 45. Benchmark End-to-End

Posteriormente:

```text
rag_end_to_end_v1
```

Evalúa:

```text
query
↓
embedding
↓
retrieval
↓
reranking
↓
LLM
↓
respuesta
```


# 46. Prueba de información ficticia

Utilizar información inventada para evitar conocimiento previo.

Ejemplo:

```text
Marcelo Pepinillo nació en Terrassa en 1987.
```

Pregunta:

```text
¿Dónde nació Marcelo Pepinillo?
```

Esperado:

```text
Terrassa
```

Esto demuestra que el modelo utiliza el contexto.


# 47. Información ausente

Contexto:

```text
Marcelo Pepinillo publicó tres libros.
```

Pregunta:

```text
¿Dónde nació Marcelo Pepinillo?
```

Respuesta esperada:

```text
No consta en el contexto proporcionado.
```

Medir alucinación.


# 48. Contexto contradictorio

Crear pruebas deliberadas.

Ejemplo:

Chunk A:

```text
Marcelo Pepinillo nació en Terrassa.
```

Chunk B:

```text
Marcelo Pepinillo nació en Girona.
```

El sistema debe tener estrategia definida.

Inicialmente puede:

- detectar contradicción;
- informar de ella;
- no inventar una resolución.


# 49. Retrieval Logging

Toda consulta RAG debe poder guardar:

- retrieval_run_id
- query
- embedding_model
- collection
- top_k
- chunks recuperados
- scores
- ranks
- chunks enviados al LLM
- duración


# 50. Generation Logging

Guardar:

- LLM
- prompt
- chunks utilizados
- respuesta
- tokens
- duración
- metrics
- citations utilizadas


# 51. Cambios de documentos

Usar checksum para detectar cambios.

Si un documento cambia:

```text
checksum antiguo != checksum nuevo
```

crear nueva versión e indexar de nuevo los chunks afectados.


# 52. Duplicados

El sistema debe poder detectar documentos idénticos mediante checksum.

No indexar copias idénticas sin necesidad.


# 53. Eliminación

Si un documento se elimina del sistema, deben eliminarse o invalidarse:

- chunks;
- embeddings;
- referencias vectoriales.

Evitar retrieval de documentos inexistentes.


# 54. Reindexado selectivo

No recalcular toda la biblioteca cada vez que cambia un documento.

Reindexar únicamente:

- documento modificado;
- chunks afectados;
- colección afectada cuando sea necesario.


# 55. Model Benchmarking

Embedding models deben evaluarse igual que LLM.

No elegir embedding por popularidad.

Comparar:

```text
embeddinggemma
vs
futuros modelos
```

según nuestras consultas reales.


# 56. Elección de embedding

Elegir el modelo más pequeño que alcance suficiente calidad de retrieval.

Ejemplo:

```text
Embedding A
Hit@5 = 96%
RAM = 700MB

Embedding B
Hit@5 = 97%
RAM = 2GB
```

Si el 96% supera el threshold, probablemente elegir A.


# 57. Reranker Benchmarking

Si se incorpora reranker, medir:

```text
retrieval sin reranker
vs
retrieval + reranker
```

Solo conservarlo si mejora suficientemente la calidad.


# 58. Latencia

Medir cada etapa:

```text
embedding query
vector search
reranking
context building
generation
```

Esto permite encontrar cuellos de botella.


# 59. Caché

Puede añadirse posteriormente caché para:

- embeddings de documentos;
- embeddings de queries repetidas;
- retrieval repetido.

No implementar optimizaciones prematuras.


# 60. Primer RAG MVP

La primera versión debe ser deliberadamente pequeña.

Objetivo:

```text
10-20 documentos
↓
extraer texto
↓
crear chunks
↓
embeddinggemma
↓
Qdrant
↓
buscar
↓
recuperar chunks
↓
pasarlos a un LLM
↓
respuesta
```


# 61. Qué NO implementar en la primera versión RAG

No implementar todavía:

- OCR complejo;
- cientos de formatos;
- knowledge graphs;
- reranking obligatorio;
- múltiples vector stores;
- agentes autónomos de ingesta;
- fine-tuning de embeddings;
- clasificación filosófica profunda automática.


# 62. Evolución prevista

Fase RAG 1:

```text
txt/md/pdf
+
embeddinggemma
+
Qdrant
+
simple retrieval
```

Fase RAG 2:

```text
benchmark retrieval
+
mejor chunking
```

Fase RAG 3:

```text
reranker
```

Fase RAG 4:

```text
domain collections
```

Fase RAG 5:

```text
especialistas
+
routing
```

Fase RAG 6:

```text
feedback real
+
datasets propios
```


# 63. Relación con document_router

El RAG y la clasificación documental son sistemas distintos pero pueden ayudarse.

Ejemplo:

```text
documento nuevo
↓
texto
↓
embedding
↓
document_router
↓
filosofia
↓
rag_philosophy
```

También puede utilizarse retrieval para ayudar al clasificador:

```text
documento nuevo
↓
buscar documentos similares
↓
mostrar ejemplos al clasificador
↓
clasificación
```


# 64. Relación con especialistas

Un especialista puede combinar:

```text
LLM
+
system prompt
+
RAG collection
+
tools
+
permissions
```

Ejemplo:

```text
philosophy_agent
=
qwen/deepseek/etc.
+
rag_philosophy
+
search_library
```


# 65. Principio final

RAG no debe tratarse como:

> "meter todos mis documentos dentro de una IA"

Debe tratarse como:

> un sistema de recuperación de evidencia que proporciona al modelo únicamente la
> información más relevante para resolver una consulta.

La calidad final depende de varias piezas independientes:

```text
document quality
+
chunking
+
embedding
+
retrieval
+
reranking
+
context construction
+
LLM
```

Cada pieza debe poder medirse, sustituirse y mejorarse de forma independiente.
