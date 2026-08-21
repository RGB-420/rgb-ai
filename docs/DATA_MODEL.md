# Data Model Specification

## 1. Objetivo

Definir las entidades principales de `rgb-ai`, sus campos y sus relaciones.

Este documento describe QUÉ datos existen en el sistema.

No fija todavía una implementación concreta de almacenamiento.

La primera versión podría utilizar:

- SQLite
- PostgreSQL
- archivos JSON/YAML
- una combinación de varios sistemas

La arquitectura debe permitir cambiar la tecnología de persistencia sin modificar el significado de los datos.


## 2. Principio general

Separar claramente:

- modelos
- hardware
- tareas
- environments
- agentes
- prompts
- herramientas
- datasets
- test cases
- benchmarks
- resultados
- RAG
- documentos
- usuarios
- perfiles
- sesiones
- conversaciones
- memoria
- tareas reales
- feedback
- correcciones
- promociones de modelos


## 3. Identificadores

Todas las entidades principales deben tener un identificador interno estable.

Ejemplo:

```json
{
  "model_id": "mdl_qwen3_06b",
  "display_name": "qwen3:0.6b"
}
```

El ID interno no debe depender necesariamente del nombre visible.

Esto permite cambiar nombres o proveedores sin romper relaciones históricas.


# MODELOS


## 4. Model

Representa un modelo disponible para inferencia.

Ejemplo:

```json
{
  "model_id": "mdl_qwen3_06b",
  "provider": "ollama",
  "name": "qwen3:0.6b",
  "family": "qwen3",
  "parameters_b": 0.6,
  "specialization": "generalist",
  "installed": true
}
```

Campos recomendados:

- model_id
- provider
- name
- family
- parameters_b
- specialization
- architecture
- quantization
- context_window
- supports_thinking
- supports_tools
- supports_structured_output
- supports_vision
- languages
- disk_size_bytes
- installed
- installed_at
- source
- notes


## 5. Model Capability

Las capacidades no deben representarse únicamente mediante texto libre.

Ejemplo:

```json
{
  "model_id": "mdl_qwen3_06b",
  "capability": "tool_calling",
  "supported": true,
  "source": "benchmark",
  "score": 0.91
}
```

Campos:

- model_id
- capability
- supported
- score
- source
- evaluated_at
- environment_id
- notes

Una capacidad puede provenir de:

- documentación del fabricante
- benchmark propio
- observación manual


## 6. Model Runtime Profile

Guarda métricas observadas al ejecutar un modelo en hardware concreto.

Ejemplo:

```json
{
  "model_id": "mdl_qwen3_06b",
  "hardware_profile_id": "hw_rgb_ai_v1",
  "ram_loaded_bytes": 1073741824,
  "processor": "cpu",
  "prompt_tokens_per_second": 62.98,
  "generation_tokens_per_second": 22.15
}
```

Campos:

- model_id
- hardware_profile_id
- context_size
- ram_loaded_bytes
- processor
- prompt_tokens_per_second
- generation_tokens_per_second
- load_duration_ms
- measured_at

Estas métricas pueden variar según:

- hardware
- versión del modelo
- contexto
- cuantización
- parámetros de generación


# HARDWARE


## 7. Hardware Profile

Representa el hardware sobre el que se ejecutan los benchmarks.

Ejemplo:

```json
{
  "hardware_profile_id": "hw_rgb_ai_v1",
  "hostname": "rgb-ai",
  "cpu": "AMD 3020e with Radeon Graphics",
  "cpu_threads": 2,
  "ram_bytes": 6120000000,
  "gpu": "AMD Radeon integrated",
  "storage": "128GB SSD"
}
```

Campos:

- hardware_profile_id
- hostname
- cpu
- cpu_cores
- cpu_threads
- ram_bytes
- gpu
- gpu_vram_bytes
- storage
- operating_system
- kernel
- ollama_version
- created_at


# TAREAS Y ENVIRONMENTS


## 8. Task

Una Task representa una función general que el sistema quiere resolver.

Ejemplos:

- document_router
- philosophy_classifier
- personal_receptionist
- librarian
- code_agent

Ejemplo:

```json
{
  "task_id": "task_document_router",
  "name": "document_router",
  "description": "Clasificación superficial de documentos"
}
```

Campos:

- task_id
- name
- description
- category
- active
- created_at
- updated_at


## 9. Environment

Representa una implementación reproducible de una Task.

Ejemplo:

```json
{
  "environment_id": "env_document_router_v1",
  "task_id": "task_document_router",
  "name": "document_router",
  "version": 1,
  "stateful": false
}
```

Campos:

- environment_id
- task_id
- name
- version
- description
- category
- stateful
- max_steps
- max_tool_calls
- timeout_seconds
- active
- created_at
- updated_at


## 10. Environment Configuration

Guarda la configuración de un environment.

Ejemplo:

```json
{
  "environment_id": "env_document_router_v1",
  "input_schema_version": "1",
  "output_schema_version": "1",
  "system_prompt_version": "1",
  "dataset_id": "ds_document_router_v1"
}
```

Campos:

- environment_id
- input_schema
- output_schema
- system_prompt_id
- dataset_id
- verifier_id
- constraints
- allowed_actions
- production_thresholds


# PROMPTS


## 11. Prompt

Los prompts deben estar versionados.

Ejemplo:

```json
{
  "prompt_id": "prompt_document_router_v1",
  "name": "document_router_system",
  "version": 1,
  "content": "Eres un clasificador documental..."
}
```

Campos:

- prompt_id
- name
- version
- type
- content
- created_at
- updated_at
- notes

Tipos posibles:

- system
- user_template
- evaluator
- retrieval
- tool


# HERRAMIENTAS


## 12. Tool

Representa una herramienta disponible para un agente.

Ejemplo:

```json
{
  "tool_id": "tool_read_excerpt",
  "name": "read_excerpt",
  "type": "read",
  "side_effects": false
}
```

Campos:

- tool_id
- name
- description
- type
- input_schema
- output_schema
- side_effects
- dangerous
- requires_confirmation
- enabled
- implementation_version


## 13. Environment Tool

Relación entre environment y herramientas.

Campos:

- environment_id
- tool_id
- enabled
- max_calls
- permissions
- notes

Un environment define explícitamente qué herramientas tiene disponibles.

Un modelo nunca debe recibir acceso automáticamente a todas las herramientas del sistema.


# AGENTES


## 14. Agent

Un Agent combina varios componentes para ofrecer una función concreta.

Ejemplo:

```json
{
  "agent_id": "agent_philosophy",
  "name": "philosophy_classifier",
  "task_id": "task_philosophy_classifier",
  "production_model_id": "mdl_qwen3_17b",
  "environment_id": "env_philosophy_v1"
}
```

Campos:

- agent_id
- name
- description
- task_id
- environment_id
- production_model_id
- system_prompt_id
- rag_collection_id
- active
- created_at
- updated_at


## 15. Agent Candidate Model

Permite probar otros modelos para un agente sin sustituir inmediatamente el modelo de producción.

Campos:

- agent_id
- model_id
- status
- added_at
- last_benchmark_at
- notes

Valores posibles:

- candidate
- testing
- rejected
- production
- deprecated


## 16. Production Assignment

Representa qué modelo está asignado a un agente en producción.

Ejemplo:

```json
{
  "agent_id": "agent_document_router",
  "model_id": "mdl_qwen3_06b",
  "effective_from": "2026-08-21"
}
```

Campos:

- assignment_id
- agent_id
- model_id
- effective_from
- effective_until
- reason
- benchmark_run_id
- created_by


## 17. Model Promotion History

Registra cada sustitución de modelo.

Campos:

- promotion_id
- agent_id
- previous_model_id
- new_model_id
- promoted_at
- benchmark_run_id
- reason
- approved_by

Nunca debe perderse el historial de qué modelo estuvo en producción.


# DATASETS


## 18. Dataset

Representa un conjunto versionado de casos de evaluación.

Ejemplo:

```json
{
  "dataset_id": "ds_document_router_v1",
  "name": "document_router",
  "version": 1,
  "split": "test"
}
```

Campos:

- dataset_id
- name
- version
- description
- split
- domain
- created_at
- frozen
- notes


## 19. Dataset Split

Cuando sea necesario, distinguir:

- train
- validation
- test

Campos:

- dataset_id
- split_name
- item_count


## 20. Test Case

Representa un caso individual de benchmark.

Ejemplo:

```json
{
  "test_case_id": "DOC_ROUTER_001",
  "dataset_id": "ds_document_router_v1",
  "input": {
    "filename": "ricoeur.pdf",
    "excerpt": "Paul Ricoeur analiza la identidad narrativa..."
  },
  "expected": {
    "category": "filosofia"
  }
}
```

Campos:

- test_case_id
- dataset_id
- input
- expected
- difficulty
- tags
- source
- active
- created_at
- reviewed_at

Valores posibles de difficulty:

- trivial
- easy
- medium
- hard
- ambiguous
- adversarial


## 21. Test Case Source

Un test case puede provenir de:

- synthetic
- public_dataset
- real_task
- human_created
- historical_failure

Guardar siempre el origen.


# VERIFICACIÓN


## 22. Verifier

Representa cómo se determina si una ejecución es correcta.

Ejemplo:

```json
{
  "verifier_id": "verifier_document_router_v1",
  "type": "exact_match"
}
```

Campos:

- verifier_id
- name
- version
- type
- configuration
- deterministic
- implementation_path

Tipos posibles:

- exact_match
- json_schema
- numeric
- unit_test
- custom_code
- llm_judge


# BENCHMARKS


## 23. Benchmark Run

Representa una ejecución completa de:

Environment × Dataset × Model

Ejemplo:

```json
{
  "benchmark_run_id": "run_20260821_001",
  "environment_id": "env_document_router_v1",
  "dataset_id": "ds_document_router_v1",
  "model_id": "mdl_qwen3_06b"
}
```

Campos:

- benchmark_run_id
- environment_id
- dataset_id
- model_id
- hardware_profile_id
- started_at
- finished_at
- status
- repetitions
- configuration
- summary_metrics


## 24. Benchmark Case Result

Resultado de un test individual dentro de un benchmark.

Campos:

- result_id
- benchmark_run_id
- test_case_id
- repetition
- success
- score
- output
- parsed_output
- verifier_result
- error
- created_at


## 25. Generation Metrics

Guarda métricas técnicas de cada generación.

Campos:

- result_id
- prompt_token_count
- output_token_count
- prompt_eval_duration_ms
- output_eval_duration_ms
- prompt_tokens_per_second
- output_tokens_per_second
- load_duration_ms
- total_duration_ms
- context_size
- processor
- ram_loaded_bytes


## 26. Thinking Trace

Cuando el modelo exponga thinking de forma utilizable, puede guardarse.

Campos:

- result_id
- thinking_text
- thinking_token_count
- thinking_duration_ms
- available
- notes

No asumir que `thinking_text` es correcto ni adecuado para entrenamiento.


# EJECUCIÓN DE AGENTES


## 27. Tool Call

Cada llamada a una herramienta debe registrarse.

Ejemplo:

```json
{
  "tool_call_id": "tc_123",
  "result_id": "res_456",
  "tool_id": "tool_read_excerpt",
  "arguments": {
    "path": "ricoeur.pdf"
  }
}
```

Campos:

- tool_call_id
- result_id
- step_number
- tool_id
- arguments
- output
- success
- error
- started_at
- finished_at
- duration_ms


## 28. Agent Episode

Representa una ejecución completa de un environment agentic.

Campos:

- episode_id
- environment_id
- agent_id
- model_id
- input
- started_at
- finished_at
- final_status
- final_output
- steps
- total_tool_calls
- total_tokens
- total_duration_ms


## 29. Episode Step

Campos:

- step_id
- episode_id
- step_number
- type
- input
- output
- tool_call_id
- created_at

Tipos:

- model
- tool
- verifier
- system
- user


# RAG


## 30. RAG Collection

Representa una base de conocimiento concreta.

Ejemplo:

```json
{
  "rag_collection_id": "rag_philosophy_v1",
  "name": "philosophy",
  "version": 1,
  "embedding_model": "..."
}
```

Campos:

- rag_collection_id
- name
- version
- domain
- embedding_model
- vector_store
- chunking_strategy
- created_at
- updated_at


## 31. Document

Representa un documento gestionado por el sistema.

Campos:

- document_id
- owner_user_id
- filename
- path
- mime_type
- size_bytes
- checksum
- created_at
- modified_at
- imported_at
- source
- current_category
- metadata
- visibility


## 32. Document Version

Si un documento cambia, registrar la versión.

Campos:

- document_version_id
- document_id
- version
- checksum
- path
- created_at


## 33. Document Chunk

Representa un fragmento indexado para RAG.

Campos:

- chunk_id
- document_id
- document_version_id
- chunk_index
- content
- token_count
- metadata
- embedding_reference


## 34. Retrieval Run

Registra una búsqueda realizada contra el RAG.

Campos:

- retrieval_run_id
- query
- rag_collection_id
- embedding_model
- top_k
- started_at
- finished_at


## 35. Retrieved Chunk

Campos:

- retrieval_run_id
- chunk_id
- rank
- score
- included_in_context

Esto permite distinguir errores del buscador de errores del LLM.


## 36. RAG Evaluation Result

Campos:

- result_id
- retrieval_run_id
- expected_chunk_ids
- hit
- recall_at_k
- precision_at_k
- generation_success


# USUARIOS


## 37. User

Representa una persona con acceso al sistema.

Ejemplo:

```json
{
  "user_id": "usr_001",
  "display_name": "Raul",
  "role": "owner"
}
```

Campos:

- user_id
- display_name
- role
- active
- created_at
- last_seen_at

Evitar almacenar información personal innecesaria.


## 38. User Role

Roles iniciales:

- owner
- member
- guest
- admin

Los permisos reales deben controlarse en backend, nunca únicamente mediante prompts.


## 39. User Profile

Información estable utilizada para personalización.

Ejemplo:

```json
{
  "user_id": "usr_001",
  "preferred_agents": [
    "biblioteca",
    "programacion"
  ],
  "recent_projects": []
}
```

Campos:

- user_id
- preferences
- preferred_agents
- recent_projects
- personalization_data
- updated_at

La memoria debe mantenerse separada del perfil estable.


# PERMISOS


## 40. Permission

Representa una capacidad concreta.

Ejemplos:

- documents.read.private
- documents.write
- agents.use.code
- admin.models
- admin.benchmarks

Campos:

- permission_id
- name
- description


## 41. Role Permission

Campos:

- role
- permission_id
- allowed


## 42. Agent Permission

Un agente también puede tener restricciones.

Campos:

- agent_id
- permission_id
- allowed

Esto impide que un agente reciba herramientas que no necesita.


# SESIONES Y CONVERSACIONES


## 43. Session

Representa una sesión de usuario.

Campos:

- session_id
- user_id
- started_at
- ended_at
- temporary
- device_info
- status

Las sesiones guest pueden usar:

```text
temporary = true
```


## 44. Conversation

Campos:

- conversation_id
- session_id
- user_id
- agent_id
- model_id
- started_at
- updated_at
- title


## 45. Message

Guardar mensajes estructurados.

Campos:

- message_id
- conversation_id
- role
- content
- created_at
- token_count
- metadata

Roles:

- system
- user
- assistant
- tool


# MEMORIA


## 46. Memory

Representa información persistente recuperable por un agente.

No equivale al historial completo de conversaciones.

Campos:

- memory_id
- user_id
- agent_id
- type
- content
- created_at
- updated_at
- active
- source_message_id
- importance
- metadata


## 47. Memory Types

Ejemplos:

- preference
- project
- fact
- instruction
- summary
- task_state

La memoria debe poder:

- añadirse
- actualizarse
- eliminarse
- desactivarse


## 48. Guest Memory

Por defecto, los invitados tendrán:

- memoria solo temporal
- ninguna memoria persistente
- ningún acceso a memorias de otros usuarios

La memoria temporal debe desaparecer al finalizar la sesión.


# TAREAS REALES Y FEEDBACK


## 49. Real Task

Representa una tarea real ejecutada fuera de un benchmark.

Ejemplo:

```json
{
  "real_task_id": "rt_123",
  "task_id": "task_document_router",
  "agent_id": "agent_document_router",
  "model_id": "mdl_qwen3_06b"
}
```

Campos:

- real_task_id
- user_id
- task_id
- environment_id
- agent_id
- model_id
- input
- output
- started_at
- finished_at
- status
- metrics


## 50. Human Feedback

Representa feedback humano sobre una ejecución.

Campos:

- feedback_id
- real_task_id
- user_id
- type
- rating
- comment
- created_at

Tipos:

- correct
- incorrect
- partially_correct
- unsafe
- irrelevant
- other


## 51. Correction

Contiene una corrección explícita proporcionada por una persona.

Ejemplo:

```json
{
  "real_task_id": "rt_123",
  "original_output": {
    "category": "literatura"
  },
  "corrected_output": {
    "category": "filosofia"
  }
}
```

Campos:

- correction_id
- real_task_id
- original_output
- corrected_output
- corrected_by
- reason
- created_at
- reviewed


## 52. Benchmark Candidate

Una tarea real corregida puede proponerse como futuro caso de benchmark.

Campos:

- candidate_id
- source_real_task_id
- correction_id
- proposed_dataset_id
- status
- reviewed_by
- created_at

Estados:

- pending
- approved
- rejected
- anonymization_required


# AUDITORÍA Y REPRODUCIBILIDAD


## 53. Audit Event

Guarda cambios importantes.

Ejemplos:

- model_promoted
- permissions_changed
- agent_created
- dataset_modified
- environment_version_created

Campos:

- audit_event_id
- event_type
- actor_user_id
- entity_type
- entity_id
- timestamp
- metadata


## 54. Configuration Snapshot

Permite reproducir configuraciones utilizadas anteriormente.

Campos:

- snapshot_id
- environment_id
- model_id
- prompt_id
- dataset_id
- generation_parameters
- tool_versions
- created_at


## 55. Generation Configuration

Campos:

- temperature
- top_p
- top_k
- seed
- context_size
- max_tokens
- thinking_enabled
- stop_sequences


## 56. Error

Representación común de errores.

Campos:

- error_id
- entity_type
- entity_id
- error_type
- message
- recoverable
- created_at
- metadata


## 57. Tags

Algunas entidades pueden admitir tags.

Ejemplos:

Model:

- fast
- agentic
- coder

Test Case:

- spanish
- adversarial
- factual

Document:

- philosophy
- ricoeur

No utilizar tags como sustituto de campos estructurados importantes.


# RELACIONES


## 58. Relaciones principales

Relación conceptual:

```text
Task
 |
 +-- Environment
 |      |
 |      +-- Dataset
 |      |      |
 |      |      +-- Test Cases
 |      |
 |      +-- Tools
 |      |
 |      +-- Prompt
 |
 +-- Agent
        |
        +-- Production Model
        +-- Candidate Models
        +-- RAG Collection
        +-- Permissions
```

Benchmark:

```text
Model
  +
Environment
  +
Dataset
  +
Hardware Profile
        |
        v
Benchmark Run
        |
        v
Case Results
```

Uso real:

```text
User
 |
Session
 |
Agent
 |
Real Task
 |
Result
 |
Human Feedback / Correction
 |
Benchmark Candidate
```


# SEPARACIÓN DE RESPONSABILIDADES


## 59. Evaluación vs Producción

No mezclar resultados de benchmark con tareas reales.

Benchmark Result:

- ejecución controlada
- dataset conocido
- expected output conocido

Real Task:

- problema real
- expected output normalmente desconocido durante la ejecución

Ambos pueden compartir estructuras técnicas, pero deben ser distinguibles.


## 60. Datos públicos y privados

Documentos, RAG y memoria deben poder indicar visibilidad.

Valores iniciales:

- private
- shared
- public

Un perfil `guest` solo podrá consultar elementos `public`.


## 61. Ownership

Recursos personales deben poder incluir:

- owner_user_id
- visibility
- permissions

Especialmente:

- documents
- conversations
- memory
- custom agents
- RAG collections


## 62. Retención

Definir políticas diferentes según el tipo de dato.

Ejemplos:

Benchmark results:
- conservar.

Model promotion history:
- conservar.

Guest conversations:
- eliminar al terminar la sesión o tras un periodo corto.

Temporary files:
- eliminar.

Tool execution logs:
- configurable.


## 63. Privacidad

Guardar únicamente la información necesaria.

Antes de convertir tareas reales en datasets:

- revisar
- anonimizar
- eliminar secretos
- eliminar credenciales
- eliminar información personal innecesaria


## 64. Secrets

Contraseñas, tokens y claves NO deben almacenarse como texto dentro de estas entidades.

Utilizar un mecanismo específico para secretos.

Los modelos no deben recibir secretos salvo que una tarea lo requiera explícitamente y exista una política segura para ello.


# IMPLEMENTACIÓN POR FASES


## 65. MVP

NO implementar todo este modelo de datos desde el primer día.

Para el primer Benchmark Engine bastan probablemente:

- Model
- HardwareProfile
- Task
- Environment
- Dataset
- TestCase
- BenchmarkRun
- BenchmarkCaseResult
- GenerationMetrics

Para `document_router_v1` necesitamos aproximadamente:

```text
Model
Environment
Dataset
TestCase
BenchmarkRun
Result
```


## 66. Fase 2

Añadir:

- Tool
- Agent
- AgentEpisode
- EpisodeStep
- ToolCall
- RealTask
- HumanFeedback
- Correction


## 67. Fase 3

Añadir:

- User
- UserProfile
- Permission
- Session
- Conversation
- Message
- Memory


## 68. Fase 4

Añadir RAG:

- Document
- DocumentVersion
- DocumentChunk
- RAGCollection
- RetrievalRun
- RetrievedChunk
- RAGEvaluationResult


## 69. Fase 5

Añadir operaciones avanzadas:

- ModelPromotionHistory
- AuditEvent
- ConfigurationSnapshot
- BenchmarkCandidate
- generación de datasets desde tareas reales


## 70. Regla de implementación

Codex NO debe implementar entidades futuras únicamente porque aparecen en este documento.

Debe implementar solo las entidades necesarias para la fase solicitada.

Este documento define el modelo conceptual completo para evitar decisiones incompatibles a medida que el proyecto crezca.


# PRINCIPIO FINAL


## 71. Trazabilidad

El modelo de datos debe permitir responder preguntas como:

- ¿qué modelo está en producción para esta tarea?
- ¿por qué fue elegido?
- ¿qué benchmark justificó la decisión?
- ¿qué modelo estaba antes?
- ¿qué modelo es más rápido?
- ¿qué modelo falla más produciendo JSON?
- ¿qué casos reales ha fallado?
- ¿qué correcciones humanas existen?
- ¿qué RAG utilizó?
- ¿qué fragmentos recuperó?
- ¿qué herramientas llamó?
- ¿qué usuario ejecutó la tarea?
- ¿qué versión exacta del environment produjo el resultado?
- ¿qué prompt utilizó?
- ¿qué parámetros de generación utilizó?
- ¿sobre qué hardware se ejecutó?
- ¿podemos reproducir el resultado?

Si el modelo de datos permite responder de forma fiable a estas preguntas, la arquitectura tendrá suficiente trazabilidad para evolucionar sin convertirse en una caja negra.
