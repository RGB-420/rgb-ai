# RGB-AI Benchmark Results

## Experiment Overview

Raw JSONL files are the source of truth. Estimated thinking metrics are non-authoritative and use `character_ratio_v1` when available.

Strict pass rate measures whether the complete benchmark requirement was satisfied, including required output format.
Task accuracy measures whether the underlying task answer was correct according to deterministic semantic rules configured for that benchmark case.

| Model | Model ID | Run ID | Tests | Pass | Fail | Pass rate | Task accuracy | Format-only | Wrong answer | Total duration | Avg time/test | Prompt tokens | Output tokens | Output tok/s | Est. thinking |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-r1:1.5b | mdl_deepseek_r1_15b | run_e113d20cd1364ab3a7b129ba57f94891 | 32 | 6 | 26 | 18.8% | 18.8% | 0 | 26 | 924410.98 ms | 28887.84 ms | 1919 | 10080 | 12.37 | 82.8% |
| gemma3:1b | mdl_gemma3_1b | run_5da61bf89cb54cfb976d11f28d5f0b03 | 32 | 11 | 21 | 34.4% | 43.8% | 3 | 18 | 170329.98 ms | 5322.81 ms | 2107 | 463 | 15.59 | 0.0% |
| granite4:350m-h | mdl_granite4_350m_h | run_25e477e4ccbe4cda8eae88fb06a25657 | 32 | 14 | 18 | 43.8% | 50.0% | 2 | 16 | 60774.98 ms | 1899.22 ms | 2473 | 289 | 38.54 | 0.0% |
| llama3.2:1b | mdl_llama32_1b | run_3380a765b06c4e66ba511919fa130d0e | 32 | 2 | 30 | 6.2% | 15.6% | 3 | 27 | 220356.52 ms | 6886.14 ms | 2610 | 1252 | 14.48 | 0.0% |
| phi3.5:3.8b | mdl_phi35_38b | run_4cb20f178436483fb3438bf5d65b7f7f | 32 | 13 | 15 | 40.6% | 53.6% | 2 | 13 | 617873.57 ms | 19308.55 ms | 2344 | 1390 | 5.73 | 0.0% |
| qwen2.5:1.5b | mdl_qwen25_15b | run_6ab7d3abd7f642bfbd549b0de8c7273b | 32 | 13 | 19 | 40.6% | 46.9% | 2 | 17 | 149948.82 ms | 4685.90 ms | 2463 | 517 | 16.25 | 0.0% |
| qwen2.5-coder:1.5b | mdl_qwen25_coder_15b | run_d376c7a0ba62474eba9cb6adfd624249 | 32 | 11 | 21 | 34.4% | 46.9% | 4 | 17 | 158586.84 ms | 4955.84 ms | 2463 | 625 | 17.38 | 0.0% |
| qwen3:0.6b | mdl_qwen3_06b | run_6213ba4a91764aaa8679f414fc215b98 | 32 | 23 | 9 | 71.9% | 75.0% | 1 | 8 | 325418.00 ms | 10169.31 ms | 2233 | 6170 | 23.70 | 97.2% |
| qwen3:1.7b | mdl_qwen3_17b | run_76629e7d74164931b9888a8a2623c2c4 | 32 | 25 | 6 | 78.1% | 80.6% | 0 | 6 | 886359.58 ms | 27698.74 ms | 2184 | 7440 | 10.13 | 97.4% |

## Overall Comparison

| Model | Strict pass | Strict pass rate | Task accuracy | Format-only | Wrong answer | Avg time/test | Output tok/s | Est. thinking |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-r1:1.5b | 6/32 | 18.8% | 18.8% | 0 | 26 | 28887.84 ms | 12.37 | 82.8% |
| gemma3:1b | 11/32 | 34.4% | 43.8% | 3 | 18 | 5322.81 ms | 15.59 | 0.0% |
| granite4:350m-h | 14/32 | 43.8% | 50.0% | 2 | 16 | 1899.22 ms | 38.54 | 0.0% |
| llama3.2:1b | 2/32 | 6.2% | 15.6% | 3 | 27 | 6886.14 ms | 14.48 | 0.0% |
| phi3.5:3.8b | 13/32 | 40.6% | 53.6% | 2 | 13 | 19308.55 ms | 5.73 | 0.0% |
| qwen2.5:1.5b | 13/32 | 40.6% | 46.9% | 2 | 17 | 4685.90 ms | 16.25 | 0.0% |
| qwen2.5-coder:1.5b | 11/32 | 34.4% | 46.9% | 4 | 17 | 4955.84 ms | 17.38 | 0.0% |
| qwen3:0.6b | 23/32 | 71.9% | 75.0% | 1 | 8 | 10169.31 ms | 23.70 | 97.2% |
| qwen3:1.7b | 25/32 | 78.1% | 80.6% | 0 | 6 | 27698.74 ms | 10.13 | 97.4% |

No automatic production recommendation is made from these measurements.

## Category Comparison

Cells show `strict pass rate / task accuracy`.

| Model | Instructions | JSON | Routing | Classification | Context | Reasoning | Coding | Tools |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-r1:1.5b | 40.0% / 40.0% | 40.0% / 40.0% | 25.0% / 25.0% | 25.0% / 25.0% | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% |
| gemma3:1b | 0.0% / 0.0% | 20.0% / 20.0% | 50.0% / 50.0% | 50.0% / 50.0% | 50.0% / 100.0% | 25.0% / 50.0% | 33.3% / 33.3% | 66.7% / 66.7% |
| granite4:350m-h | 60.0% / 60.0% | 100.0% / 100.0% | 75.0% / 75.0% | 0.0% / 0.0% | 50.0% / 75.0% | 0.0% / 25.0% | 0.0% / 0.0% | 33.3% / 33.3% |
| llama3.2:1b | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% | 25.0% / 25.0% | 25.0% / 75.0% | 0.0% / 25.0% | 0.0% / 0.0% | 0.0% / 0.0% |
| phi3.5:3.8b | 40.0% / 50.0% | 20.0% / 25.0% | 25.0% / 25.0% | 100.0% / 100.0% | 50.0% / 75.0% | 25.0% / 66.7% | 33.3% / 33.3% | 33.3% / 50.0% |
| qwen2.5-coder:1.5b | 60.0% / 60.0% | 0.0% / 0.0% | 50.0% / 50.0% | 50.0% / 50.0% | 25.0% / 75.0% | 25.0% / 50.0% | 0.0% / 33.3% | 66.7% / 66.7% |
| qwen2.5:1.5b | 40.0% / 40.0% | 20.0% / 20.0% | 75.0% / 75.0% | 100.0% / 100.0% | 25.0% / 50.0% | 0.0% / 0.0% | 33.3% / 66.7% | 33.3% / 33.3% |
| qwen3:0.6b | 80.0% / 80.0% | 80.0% / 80.0% | 75.0% / 75.0% | 75.0% / 75.0% | 50.0% / 75.0% | 50.0% / 50.0% | 66.7% / 66.7% | 100.0% / 100.0% |
| qwen3:1.7b | 80.0% / 80.0% | 100.0% / 100.0% | 100.0% / 100.0% | 50.0% / 50.0% | 100.0% / 100.0% | 50.0% / 66.7% | 33.3% / 33.3% | 100.0% / 100.0% |

## Variant Comparison

Current variant groups are not necessarily balanced and should not be interpreted causally yet.

Cells show `strict pass rate / task accuracy`.

| Model | baseline | context | few_shot | instructions |
| --- | --- | --- | --- | --- |
| deepseek-r1:1.5b | 28.6% / 28.6% | 0.0% / 0.0% | 0.0% / 0.0% | 15.4% / 15.4% |
| gemma3:1b | 42.9% / 50.0% | 50.0% / 100.0% | 100.0% / 100.0% | 15.4% / 15.4% |
| granite4:350m-h | 28.6% / 35.7% | 50.0% / 75.0% | 100.0% / 100.0% | 53.8% / 53.8% |
| llama3.2:1b | 7.1% / 14.3% | 25.0% / 75.0% | 0.0% / 0.0% | 0.0% / 0.0% |
| phi3.5:3.8b | 42.9% / 58.3% | 50.0% / 75.0% | 100.0% / 100.0% | 30.8% / 36.4% |
| qwen2.5-coder:1.5b | 42.9% / 57.1% | 25.0% / 75.0% | 100.0% / 100.0% | 23.1% / 23.1% |
| qwen2.5:1.5b | 35.7% / 42.9% | 25.0% / 50.0% | 100.0% / 100.0% | 46.2% / 46.2% |
| qwen3:0.6b | 85.7% / 85.7% | 50.0% / 75.0% | 100.0% / 100.0% | 61.5% / 61.5% |
| qwen3:1.7b | 78.6% / 84.6% | 100.0% / 100.0% | 100.0% / 100.0% | 69.2% / 69.2% |

## Efficiency

| Model | Avg time/test | Total output tokens | Output tok/s | Est. thinking tokens | Est. response tokens | Est. thinking share |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek-r1:1.5b | 28887.84 ms | 10080 | 12.37 | 8346 | 1734 | 82.8% |
| gemma3:1b | 5322.81 ms | 463 | 15.59 | 0 | 463 | 0.0% |
| granite4:350m-h | 1899.22 ms | 289 | 38.54 | 0 | 289 | 0.0% |
| llama3.2:1b | 6886.14 ms | 1252 | 14.48 | 0 | 1252 | 0.0% |
| phi3.5:3.8b | 19308.55 ms | 1390 | 5.73 | 0 | 1390 | 0.0% |
| qwen2.5:1.5b | 4685.90 ms | 517 | 16.25 | 0 | 517 | 0.0% |
| qwen2.5-coder:1.5b | 4955.84 ms | 625 | 17.38 | 0 | 625 | 0.0% |
| qwen3:0.6b | 10169.31 ms | 6170 | 23.70 | 5999 | 171 | 97.2% |
| qwen3:1.7b | 27698.74 ms | 7440 | 10.13 | 7244 | 196 | 97.4% |

## Failed Cases

### deepseek-r1:1.5b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_EXACT_001 | instruction_following | baseline | wrong_answer | SI | ¡Hola! ¿Cómo puedo ayudarte si estás en need? Si no teches algo, neveré oré el respuesta. |
| INST_NEGATIVE_001 | instruction_following | instructions | wrong_answer | listo | Listo. |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | La respuesta debe ser clara y directa. Aquí tienes la respuesta: La responses must return exactly two limits. Linea 1: archivo. Linea 2: ... |
| JSON_FIELD_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofía" } ``` |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | True | { "true": "true" } |
| JSON_ENUM_001 | structured_output | instructions | wrong_answer | None | ```json { "prioridad": "alta" } ``` |
| ROUTE_LIB_001_INSTRUCTIONS | routing | instructions | wrong_answer | biblioteca | Recuerde que estás buscando organizar un PDF sobre la identidad narrativa de Ricoeur en su biblioteca. La mejor forma de organizarlo serí... |
| ROUTE_LIB_001_FEWSHOT | routing | few_shot | wrong_answer | biblioteca | pendiente |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | puedo decir si ya he pagado el bill de internet completo por el dato de vencimiento o si todavía tengo descontos pendientes. ¿Cuánticos h... |
| CLASS_DOC_CODE_001 | classification | baseline | wrong_answer | programacion | pendiente_clasificacion |
| CLASS_DOC_ADMIN_001 | classification | baseline | wrong_answer | administracion | pendiente_clasificacion |
| CLASS_DOC_AMBIG_001 | classification | instructions | wrong_answer | pendiente_clasificacion | programacion |
| CTX_DIRECT_001 | context_use | context | wrong_answer | 14 de octubre de 2027 | October 14, 2027 |
| CTX_COMBINE_001 | context_use | context | wrong_answer | Irene Salvatierra | Irene Salvatierra **Answer:** Irene Salvatierra |
| CTX_ABSENT_001 | context_use | context | wrong_answer | no consta | Fierro de los Tres Jonos creó la colección Lince Rojo en 1972. |
| CTX_DISTRACTOR_001 | context_use | context | wrong_answer | administracion | El proyecto Senda Clara pertenece al área de administración. |
| REASON_ARITH_001 | reasoning | baseline | wrong_answer | 31 | Para resolver el problema, sigamos los siguientes pasos: 1. **Calcular el número total de archivos procesados:** - Cada lote tiene **12 a... |
| REASON_ORDER_001 | reasoning | baseline | wrong_answer | Ana | Para resolver este problema, primero identificamos la relación entre las tareas que terminaron: - **Ana terminó antes que Bruno.** - **Br... |
| REASON_PROB_001 | reasoning | baseline | wrong_answer | 1/2 | Para determinar la probabilidad de extraer una ficha roja de la caja, sigamos los siguientes pasos: 1. **Determinar el total de fichas:**... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | Para resolver el problema, sigamos los pasos detallados: 1. **Identificar las carpetas**: Existen carpetas A, B y C. 2. **Dados de la pro... |
| CODE_EXPR_001 | coding | baseline | wrong_answer | datos[0] | ```python data[0] ``` |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | Para definir la función `normalizar` que recibe un parámetro texto, procedamos de manera clara y estructurada: 1. **Definir la función**:... |
| CODE_CONTAINS_001 | coding | instructions | wrong_answer | None | ```python def es_categoría_valida(category, category_validas): return category not in category_validas ``` |
| TOOL_SELECT_LIBRARY_001 | tool_selection | baseline | wrong_answer | search_library | ningonal |
| TOOL_SELECT_READ_001 | tool_selection | baseline | wrong_answer | read_file | Para Retrievar el contenido de un archivo de la rutanotes/ricoeur.md usando las herramientas disponibles, la mejor opción es usar el coma... |
| TOOL_SELECT_EXPERT_001 | tool_selection | instructions | wrong_answer | ask_expert | search_library |

### gemma3:1b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_EXACT_001 | instruction_following | baseline | wrong_answer | SI | SI. Okay, understood. |
| INST_WORDCOUNT_001 | instruction_following | baseline | wrong_answer | pendiente revisión humana | Revisión humana. |
| INST_ALLOWED_001 | instruction_following | baseline | wrong_answer | None | Aprobar |
| INST_NEGATIVE_001 | instruction_following | instructions | wrong_answer | listo | mesta |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | archivo pendiente. pendiente archivo. |
| JSON_VALID_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofía" } ``` |
| JSON_FIELD_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofía" } ``` |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | None | ```json { "requiere_revision": true } ``` |
| JSON_ENUM_001 | structured_output | instructions | wrong_answer | None | ```json { "prioridad": "alta" } ``` |
| ROUTE_LIB_001_INSTRUCTIONS | routing | instructions | wrong_answer | biblioteca | Biblioteca |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | general |
| CLASS_DOC_CODE_001 | classification | baseline | wrong_answer | programacion | programicion |
| CLASS_DOC_AMBIG_001 | classification | instructions | wrong_answer | pendiente_clasificacion | administacion |
| CTX_ABSENT_001 | context_use | context | format_only | no consta | No consta. |
| CTX_DISTRACTOR_001 | context_use | context | format_only | administracion | administración |
| REASON_ARITH_001 | reasoning | baseline | wrong_answer | 31 | 12 |
| REASON_PROB_001 | reasoning | baseline | format_only | 1/2 | La probabilidad de que una ficha sea roja es la cantidad de fichas rojas dividida por el total de fichas. En el escenario proporcionado: ... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | baja |
| CODE_EXPR_001 | coding | baseline | wrong_answer | datos[0] | ```python datos = [1, 2, 3, 4, 5] primer_elemento = datos[0] print(primer_elemento) ``` |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | ```python def normalizar_nombre(nombre): return nombre.lower().strip() ``` |
| TOOL_SELECT_EXPERT_001 | tool_selection | instructions | wrong_answer | ask_expert | ask\\_expert |

### granite4:350m-h

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_WORDCOUNT_001 | instruction_following | baseline | wrong_answer | pendiente revisión humana | I am sorry, but I am unable to assist with that request. |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | File: archivo.txt Deadline: |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | pendiente |
| CLASS_DOC_PHIL_001 | classification | baseline | wrong_answer | filosofia | categoría: filosofia |
| CLASS_DOC_CODE_001 | classification | baseline | wrong_answer | programacion | Categoría: programacion |
| CLASS_DOC_ADMIN_001 | classification | baseline | wrong_answer | administracion | Categoría: Administracion |
| CLASS_DOC_AMBIG_001 | classification | instructions | wrong_answer | pendiente_clasificacion | futbol |
| CTX_DIRECT_001 | context_use | context | wrong_answer | 14 de octubre de 2027 | 14 de octubre |
| CTX_DISTRACTOR_001 | context_use | context | format_only | administracion | Administracion |
| REASON_ARITH_001 | reasoning | baseline | wrong_answer | 31 | 4 |
| REASON_ORDER_001 | reasoning | baseline | wrong_answer | Ana | Carla |
| REASON_PROB_001 | reasoning | baseline | format_only | 1/2 | La probabilidad de que sea roja es 1/2. |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | baja |
| CODE_EXPR_001 | coding | baseline | wrong_answer | datos[0] | el_primer_elemento |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | def normalizar_nombre(texto): return texto.strip() |
| CODE_CONTAINS_001 | coding | instructions | wrong_answer | None | A continuación se muestra un fragmento de código Python que verifica si una categoria está dentro de las categorias_validas: ```python ca... |
| TOOL_SELECT_LIBRARY_001 | tool_selection | baseline | wrong_answer | search_library | read_file |
| TOOL_SELECT_EXPERT_001 | tool_selection | instructions | wrong_answer | ask_expert | search_library |

### llama3.2:1b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_EXACT_001 | instruction_following | baseline | wrong_answer | SI | No puedo ayudar con solicitudes que promuevan o faciliten actividades ilegales o inapropiadas, incluyendo el acoso sexual. ¿Hay algo más ... |
| INST_WORDCOUNT_001 | instruction_following | baseline | wrong_answer | pendiente revisión humana | Pendiente pendiente pendiente |
| INST_ALLOWED_001 | instruction_following | baseline | wrong_answer | None | Aprobar. |
| INST_NEGATIVE_001 | instruction_following | instructions | wrong_answer | listo | Listo |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | 0,9 |
| JSON_VALID_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofía", "nombre": "La filosofía", "autor": "Friedrich Nietzsche", "publicacion": "1879", "descripcion": "La fi... |
| JSON_FIELD_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofia" } ``` |
| JSON_MULTIFIELD_001 | structured_output | instructions | wrong_answer | {"tipo":"documento","area":"programacion"} | ``` {"tipo":"documento","area":"programacion"} ``` |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | None | ```json { "requiere_revision": true } ``` |
| JSON_ENUM_001 | structured_output | instructions | wrong_answer | None | ```json { "factura": { "importe": 100, "fecha_vencimiento": "2023-02-20", "prioridad": "alta" } } ``` Este JSON devuelve solo el campo pr... |
| ROUTE_LIB_001_BASE | routing | baseline | wrong_answer | biblioteca | Biblioteca. |
| ROUTE_LIB_001_INSTRUCTIONS | routing | instructions | wrong_answer | biblioteca | ¡Excelente elección! Organizar un PDF sobre identidad narrativa de Ricoeur puede ser un desafío interesante. Aquí te dejo algunas sugeren... |
| ROUTE_LIB_001_FEWSHOT | routing | few_shot | wrong_answer | biblioteca | [Example 1] Input: Necesito revisar una función de Python que falla. Output: biblioteca [Example 2] Input: Quiero guardar un ensayo sobre... |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | general |
| CLASS_DOC_PHIL_001 | classification | baseline | wrong_answer | filosofia | programacion |
| CLASS_DOC_ADMIN_001 | classification | baseline | wrong_answer | administracion | programacion |
| CLASS_DOC_AMBIG_001 | classification | instructions | wrong_answer | pendiente_clasificacion | programacion |
| CTX_DIRECT_001 | context_use | context | wrong_answer | 14 de octubre de 2027 | 14 de octubre de 2027. |
| CTX_ABSENT_001 | context_use | context | format_only | no consta | No consta |
| CTX_DISTRACTOR_001 | context_use | context | format_only | administracion | Administración |
| REASON_ARITH_001 | reasoning | baseline | wrong_answer | 31 | 15 |
| REASON_ORDER_001 | reasoning | baseline | wrong_answer | Ana | Ana. |
| REASON_PROB_001 | reasoning | baseline | format_only | 1/2 | Para encontrar la probabilidad de que sea roja, debemos dividir el número de fichas rojas por el total número de fichas. Hay 2 fichas roj... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | Categoría baja, media y alta. |
| CODE_EXPR_001 | coding | baseline | wrong_answer | datos[0] | ```python datos = [1, 2, 3, 4, 5] primer_elemento = datos[0] print(primer_elemento) ``` |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | def normalizar_nombre(nombre): return nombre.replace(" ", "_") |
| CODE_CONTAINS_001 | coding | instructions | wrong_answer | None | ```python # Definir las categorias válidas categorias_validas = ['física', 'bíoquinica', 'química', 'biología', 'matemáticas', 'literatur... |
| TOOL_SELECT_LIBRARY_001 | tool_selection | baseline | wrong_answer | search_library | Lo siento, pero no puedo cumplir esa solicitud. |
| TOOL_SELECT_READ_001 | tool_selection | baseline | wrong_answer | read_file | La herramienta correcta para leer el contenido de un archivo MD es la `read_file`. |
| TOOL_SELECT_EXPERT_001 | tool_selection | instructions | wrong_answer | ask_expert | La herramienta adecuada para esta tarea sería la **search_library**. |

### phi3.5:3.8b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_WORDCOUNT_001 | instruction_following | baseline | wrong_answer | pendiente revisión humana | Pendiente revisión en curso |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | archivo.txt 1.0 |
| JSON_MULTIFIELD_001 | structured_output | instructions | wrong_answer | {"tipo":"documento","area":"programacion"} | {"tipo":"documento","area":"programacion"} (Nota: La compactación del JSON ya es el formato más minimalista posible, por lo que no se agr... |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | None | { "require_revision": true } la respuesta proporcionada es un objeto JSON válido que contiene una clave "require_revision" con un valor b... |
| JSON_ENUM_001 | structured_output | instructions | wrong_answer | None | ```json { "priority": "alta" } ``` |
| ROUTE_LIB_001_BASE | routing | baseline | wrong_answer | biblioteca | biblioteca Explicación: Un PDF sobre identidad narrativa de Ricoeur pertenece al campo de la filosofía y la literatura, lo que lo convier... |
| ROUTE_LIB_001_INSTRUCTIONS | routing | instructions | wrong_answer | biblioteca | biblioteca Explicación: El proceso de organizar un PDF, especialmente uno relacionado con un tema académico como la identidad narrativa d... |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | pendiente |
| CTX_ABSENT_001 | context_use | context | wrong_answer | no consta | No consta información sobre quién creó la colección Lince Rojo en el contexto proporcionado. |
| CTX_DISTRACTOR_001 | context_use | context | format_only | administracion | administración |
| REASON_PROB_001 | reasoning | baseline | format_only | 1/2 | Hay un total de 4 fichas (2 rojas y 2 azules). La probabilidad de extraer una ficha roja es el número de fichas rojas dividido por el núm... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | media Razonamiento: Si A no es alta, entonces debe ser media o baja. Sin embargo, sabemos que B es baja, por lo que A no puede ser baja y... |
| CODE_EXPR_001 | coding | baseline | wrong_answer | datos[0] | data[0] |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | ```python def normalizar_nombre(texto): # Código para normalizar el nombre return normalizado_texto ``` Nota: El código anterior es una d... |
| TOOL_SELECT_READ_001 | tool_selection | baseline | wrong_answer | read_file | search_library |

### qwen2.5-coder:1.5b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_WORDCOUNT_001 | instruction_following | baseline | wrong_answer | pendiente revisión humana | Proceso pendiente revisión humanista. |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | ``` archivo.txt True ``` |
| JSON_VALID_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofia" } ``` |
| JSON_FIELD_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofia" } ``` |
| JSON_MULTIFIELD_001 | structured_output | instructions | wrong_answer | {"tipo":"documento","area":"programacion"} | ```json {"tipo":"documento","area":"programacion"} ``` |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | None | ```json { "requiere_revision": true } ``` |
| JSON_ENUM_001 | structured_output | instructions | wrong_answer | None | ```json { "prioridad": "alta" } ``` |
| ROUTE_LIB_001_BASE | routing | baseline | wrong_answer | biblioteca | Biblioteca |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | pendiente |
| CLASS_DOC_PHIL_001 | classification | baseline | wrong_answer | filosofia | literatura |
| CLASS_DOC_ADMIN_001 | classification | baseline | wrong_answer | administracion | pendiente_clasificacion |
| CTX_DIRECT_001 | context_use | context | wrong_answer | 14 de octubre de 2027 | 14 de octubre |
| CTX_ABSENT_001 | context_use | context | format_only | no consta | no consta. |
| CTX_DISTRACTOR_001 | context_use | context | format_only | administracion | Administración |
| REASON_ARITH_001 | reasoning | baseline | wrong_answer | 31 | 6 |
| REASON_PROB_001 | reasoning | baseline | format_only | 1/2 | Para calcular la probabilidad de que se extraiga una ficha roja de una caja que contiene 2 fichas rojas y 2 fichas azules, podemos siguie... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | media |
| CODE_EXPR_001 | coding | baseline | format_only | datos[0] | ```python datos[0] ``` |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | ```python def normalizar_nombre(texto): # Aquí puedes implementar el algoritmo para normalizar el nombre pass ``` |
| CODE_CONTAINS_001 | coding | instructions | wrong_answer | None | ```python categoría = "vivienda" categorias_validas = ["hogar", "casa", "vivienda"] if categoría in categorias_validas: print("La categor... |
| TOOL_SELECT_EXPERT_001 | tool_selection | instructions | wrong_answer | ask_expert | search_library |

### qwen2.5:1.5b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_WORDCOUNT_001 | instruction_following | baseline | wrong_answer | pendiente revisión humana | Revisando. |
| INST_ALLOWED_001 | instruction_following | baseline | wrong_answer | None | Pendiente |
| INST_NEGATIVE_001 | instruction_following | instructions | wrong_answer | listo | Listo |
| JSON_VALID_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofia" } ``` |
| JSON_FIELD_001 | structured_output | instructions | wrong_answer | None | ```json { "category": "filosofia" } ``` |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | None | ```json { "requiere_revision": true } ``` |
| JSON_ENUM_001 | structured_output | instructions | wrong_answer | None | ```json { "prioridad": "alta" } ``` |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | pendiente |
| CTX_DIRECT_001 | context_use | context | wrong_answer | 14 de octubre de 2027 | 14 de octubre de 2027. |
| CTX_ABSENT_001 | context_use | context | format_only | no consta | No consta. |
| CTX_DISTRACTOR_001 | context_use | context | wrong_answer | administracion | La área que el expediente Senda Clara pertenece es administración. |
| REASON_ARITH_001 | reasoning | baseline | wrong_answer | 31 | 32 |
| REASON_ORDER_001 | reasoning | baseline | wrong_answer | Ana | Ana terminó primero. |
| REASON_PROB_001 | reasoning | baseline | wrong_answer | 1/2 | Para resolver este problema, necesitamos determinar la probabilidad de que se extraiga una ficha roja al azar de una caja que contiene 2 ... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | baja |
| CODE_EXPR_001 | coding | baseline | format_only | datos[0] | ```python datos[0] ``` |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | ```python def normalizar_nombre(texto): return texto.strip().lower() ``` |
| TOOL_SELECT_LIBRARY_001 | tool_selection | baseline | wrong_answer | search_library | search_library("Paul Ricoeur") |
| TOOL_SELECT_READ_001 | tool_selection | baseline | wrong_answer | read_file | read_file("notes/ricoeur.md") |

### qwen3:0.6b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | archivo pendiente |
| JSON_BOOLEAN_001 | structured_output | instructions | wrong_answer | True | { "requires_revision": true } |
| ROUTE_ADMIN_001 | routing | baseline | wrong_answer | administracion | pendiente |
| CLASS_DOC_AMBIG_001 | classification | instructions | wrong_answer | pendiente_clasificacion | programacion |
| CTX_COMBINE_001 | context_use | context | wrong_answer | Irene Salvatierra | Irene Salvatierra. |
| CTX_ABSENT_001 | context_use | context | format_only | no consta | No consta. |
| REASON_PROB_001 | reasoning | baseline | wrong_answer | 1/2 | La probabilidad de que se obtenga una ficha roja es la fracción simplificada $\\frac{2}{4}$. Simplificando, obtenemos $\\frac{1}{2}$. **Res... |
| REASON_CONSTRAINT_001 | reasoning | instructions | wrong_answer | alta | media |
| CODE_CONTAINS_001 | coding | instructions | wrong_answer | None | ```python if category in ['categoria1', 'categoria2', ...]: # Replace with actual valid categories ``` |

### qwen3:1.7b

| Test ID | Category | Variant | Failure type | Expected | Actual response |
| --- | --- | --- | --- | --- | --- |
| INST_MULTI_001 | instruction_following | instructions | wrong_answer | archivo<br>pendiente | data.txt slope |
| CLASS_DOC_ADMIN_001 | classification | baseline | wrong_answer | administracion | pendiente_clasificacion |
| CLASS_DOC_AMBIG_001 | classification | instructions | wrong_answer | pendiente_clasificacion | administracion |
| REASON_PROB_001 | reasoning | baseline | wrong_answer | 1/2 | La probabilidad de extraer una ficha roja es el número de fichas rojas dividido por el total de fichas. - Número de fichas rojas: 2 - Tot... |
| CODE_SIGNATURE_001 | coding | instructions | wrong_answer | def normalizar_nombre(texto): | def normalizar_nombre(texto): return ''.join(c.lower() for c in texto if c.isalnum()) |
| CODE_CONTAINS_001 | coding | instructions | wrong_answer | None | if category in ['electronics', 'books', 'clothing']: |


## Per-Category Observations

This report exposes measurements only. It does not generate subjective recommendations or production routing decisions.

## Reproducibility

- Generated at: `2026-08-22T20:55:46.809585+00:00`
- Benchmark result schema versions: `1`
- Benchmark cases represented: `32`
- Source result files:
  - `results/reevaluated/qwen3_0_6b.jsonl`
  - `results/reevaluated/qwen3_1_7b.jsonl`
  - `results/reevaluated/llama3_2_1b.jsonl`
  - `results/reevaluated/gemma3_1b.jsonl`
  - `results/reevaluated/qwen2_5_1_5b.jsonl`
  - `results/reevaluated/qwen2_5_coder_1_5b.jsonl`
  - `results/reevaluated/deepseek_r1_1_5b.jsonl`
  - `results/reevaluated/phi3_5_3_8b.jsonl`
  - `results/reevaluated/granite4_350m_h.jsonl`
- Raw JSONL result files are the source of truth.
