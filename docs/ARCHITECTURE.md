# AI Server Architecture

## Objetivo

Construir una plataforma local multi-modelo y multi-agente que permita:

- ejecutar distintos LLM mediante Ollama;
- asignar el modelo más eficiente a cada tarea;
- evaluar modelos automáticamente;
- utilizar RAG especializado;
- crear agentes con herramientas;
- registrar tareas reales;
- convertir correcciones humanas en nuevos benchmarks;
- cambiar modelos sin modificar la lógica de las aplicaciones;
- soportar distintos perfiles de usuario.

## Principio fundamental

No existe un único modelo principal.

Cada tarea tiene:

- un entorno;
- un conjunto de herramientas;
- un modelo de producción;
- modelos candidatos;
- benchmarks;
- criterios mínimos de calidad.

El sistema selecciona el modelo más pequeño que alcance la calidad necesaria.

## Componentes

### Ollama

Responsable de:

- almacenar modelos;
- cargar modelos en RAM;
- ejecutar inferencia;
- proporcionar API local.

### Model Registry

Mantiene información sobre los modelos disponibles:

- nombre;
- familia;
- parámetros;
- especialización;
- tamaño;
- capacidades;
- resultados de benchmarks.

Ejemplo:

qwen3:0.6b
- role: candidate
- strengths: routing, velocidad
- weaknesses: factualidad
- installed: true

### Task Registry

Define las tareas disponibles.

Ejemplos:

- document_router
- philosophy_classifier
- code_agent
- librarian
- personal_receptionist

Cada tarea debe definir:

- modelo de producción;
- modelos candidatos;
- entorno;
- prompt;
- RAG;
- herramientas;
- métricas;
- umbrales mínimos.

### Environments

Un entorno representa una tarea reproducible.

Ejemplo:

document_router_v1

Entrada:
- filename
- extension
- metadata
- excerpt

Herramientas:
- inspect_metadata()
- read_excerpt()
- route_to()
- mark_pending()

Salida esperada:
- categoría válida

Verificador:
- compara clasificación contra ground truth.

### Benchmark Engine

Responsable de:

1. cargar modelos;
2. ejecutar tests;
3. recoger métricas de Ollama;
4. guardar respuestas;
5. ejecutar verificadores;
6. calcular scores;
7. comparar modelos.

Debe permitir algo conceptual como:

benchmark run document_router --model qwen3:0.6b

o:

benchmark compare document_router

### Result Store

Guardar cada ejecución.

Ejemplo conceptual:

{
  "run_id": "...",
  "task": "document_router",
  "model": "qwen3:0.6b",
  "input": {...},
  "output": {...},
  "expected": {...},
  "success": true,
  "tokens": 120,
  "tokens_per_second": 21.4,
  "duration": 5.6
}

### RAG

Cada especialista puede disponer de una base de conocimiento diferente.

Ejemplos:

rag_philosophy
rag_programming
rag_football
rag_library

El modelo físico puede ser el mismo.

Ejemplo:

qwen3:1.7b
    |
    +-- agente filosofía + rag_philosophy
    +-- agente fútbol + rag_football
    +-- agente literatura + rag_literature

### Agent Layer

Los agentes combinan:

- LLM;
- system prompt;
- perfil;
- RAG;
- memoria;
- herramientas;
- permisos.

Los agentes no deben depender directamente de un modelo concreto.

Ejemplo:

agent: philosophy_classifier
model: configurable

Esto permite sustituir Qwen por Gemma sin modificar el agente.

## Pipeline documental inicial

Archivo nuevo
    |
    v
Recepcionista / router pequeño
    |
    +-- clasificación clara -> destino general
    |
    +-- ambiguo -> pending
                     |
                     v
             especialista de área
                     |
                     v
               RAG especializado
                     |
                     v
            clasificación profunda

Ejemplo:

ricoeur.pdf
|
qwen3:0.6b
|
filosofia
|
qwen3:1.7b + rag_philosophy
|
hermeneutica
|
clasificación final

## Escalado

Una tarea puede escalar automáticamente.

Nivel 1:
modelo pequeño

Si falla:
Nivel 2:
modelo medio + RAG

Si falla:
Nivel 3:
modelo grande / especialista

Nunca utilizar el modelo más grande por defecto.

## Perfiles de usuario

El sistema tendrá perfiles independientes.

Ejemplos:

- usuario principal
- otro usuario
- invitado

Cada perfil puede tener:

- memoria propia;
- historial;
- agentes favoritos;
- documentos;
- RAG privados;
- permisos.

## Invitado

Debe:

- tener sesión temporal;
- no acceder a memoria privada;
- no acceder a documentos privados;
- utilizar herramientas limitadas;
- eliminar datos de sesión al terminar.

## Feedback Loop

Uso real
|
v
modelo ejecuta tarea
|
v
resultado
|
+-- correcto -> registrar
|
+-- incorrecto
       |
       v
 corrección humana
       |
       v
nuevo caso de benchmark

Con el tiempo, el benchmark debe representar cada vez mejor el uso real.

## Evolución futura

Fase 1:
benchmarks manuales.

Fase 2:
benchmark engine automático.

Fase 3:
environments reales.

Fase 4:
RAG.

Fase 5:
agentes y herramientas.

Fase 6:
dashboard.

Fase 7:
dataset basado en uso real.

Fase 8:
fine-tuning / reinforcement learning si existe suficiente evidencia para justificarlo.

## Remote Inference Architecture

Los modelos LLM no tienen que ejecutarse en la misma máquina que el código cliente.

La arquitectura inicial utiliza dos máquinas:

```text
Development Machine
├── repository: rgb-ai
├── Codex
├── Python
├── tests
└── development tools
        |
        | HTTP / private network
        v
AI Server: rgb-ai
├── Ollama
├── local models
└── inference hardware
```

### Ollama Server

Ollama se ejecuta en el servidor `rgb-ai`.

El resto del sistema debe comunicarse con Ollama mediante su API HTTP.

El código NO debe asumir:

```text
http://localhost:11434
```

La dirección debe ser configurable mediante una variable de entorno:

```text
OLLAMA_BASE_URL
```

Ejemplo en desarrollo:

```text
OLLAMA_BASE_URL=http://192.168.x.x:11434
```

La IP concreta no debe quedar hardcodeada en el código.

### Ollama Client

Debe existir una única abstracción para comunicarse con Ollama.

Ejemplo conceptual:

```text
Application
     ↓
OllamaClient
     ↓
HTTP
     ↓
AI Server
     ↓
Ollama
     ↓
Model
```

El resto de componentes no deben realizar llamadas HTTP directamente a Ollama.

### Network Security

Durante desarrollo, Ollama puede ser accesible desde la red local privada.

No exponer directamente el puerto 11434 a Internet.

Para acceso remoto futuro utilizar:

- red privada;
- VPN como Tailscale;
- o backend autenticado.

### Future Architecture

A largo plazo:

```text
Clients
   ↓
RGB-AI Backend
   ├── authentication
   ├── permissions
   ├── routing
   ├── agents
   ├── benchmarks
   └── logging
          ↓
     Ollama Server
          ↓
        Models
```

Los clientes finales no deberían necesitar comunicarse directamente con Ollama.

Esta separación permite sustituir posteriormente:

- servidor;
- hardware;
- Ollama;
- modelo;
- proveedor de inferencia;

sin modificar la lógica principal de la aplicación.
