Plan de benchmark de modelos locales
Objetivo

Comparar modelos locales en rgb-ai para asignar el modelo más eficiente a cada tarea real del sistema.

No buscamos “el mejor modelo general”, sino el modelo más pequeño que cumpla suficientemente bien cada función.

Métricas técnicas globales

Para todas las pruebas guardar:

Modelo
Parámetros
Tamaño en disco
RAM cargada
CPU/GPU
Contexto
Tokens de entrada
Velocidad de lectura del prompt
Tokens generados
Tokens por segundo
Tiempo total
Tiempo de carga
Si usa thinking
Longitud del thinking
Si termina correctamente
1. Factualidad

Objetivo: comprobar conocimiento general y tendencia a inventar.

Ejemplos:

¿Por qué el cielo se ve azul?
¿En qué año cayó el Muro de Berlín?
¿Qué órgano bombea la sangre?
¿Cuál es la capital de Eslovenia?

Medir:

respuesta correcta
parcialmente correcta
incorrecta
alucinación
seguridad con la que afirma errores

Puntuación inicial:

2 = correcta
1 = parcialmente correcta
0 = incorrecta
2. Castellano

Objetivo: medir naturalidad y competencia lingüística.

Probar:

conversación cotidiana
explicación formal
lenguaje coloquial
corrección gramatical
resumen
seguir un registro concreto

Medir:

gramática
vocabulario
naturalidad
repeticiones
calcos de inglés
palabras inventadas
3. Seguimiento de instrucciones

Objetivo: comprobar si respeta exactamente restricciones.

Ejemplos:

Responde con exactamente 3 palabras.
Devuelve únicamente SI o NO.
Explica esto en menos de 50 palabras.
No utilices la letra X.
Produce tres campos concretos.

Medir:

cumplimiento exacto
instrucciones ignoradas
contenido adicional no solicitado

Esto es especialmente importante para agentes.

4. Salida estructurada / JSON

Objetivo: comprobar si puede utilizarse dentro de pipelines.

Ejemplo esperado:

{
  "tipo": "libro",
  "area": "filosofia",
  "requiere_revision": false
}

Medir:

JSON válido
schema correcto
campos inventados
valores válidos
texto fuera del JSON
5. Clasificación documental superficial

Objetivo: encontrar el modelo adecuado para ser el “recepcionista”.

Categorías generales, máximo unas 10:

filosofia
literatura
programacion
futbol
administracion
finanzas
ciencia
imagen/audio
personal
otros

Entrada:

nombre del archivo
metadatos
fragmento del contenido

Medir:

accuracy
matriz de confusión
clasificación absurda
cuándo debería enviar a pendiente
6. Routing de agentes

Objetivo: decidir qué especialista debe recibir una tarea.

Ejemplo:

“Tengo un PDF sobre identidad narrativa de Ricoeur.”

Esperado:

{
  "agent": "filosofia",
  "reason": "..."
}

Casos:

programación
biblioteca
filosofía
cocina
administración
fútbol
consultas generales

Medir:

agente correcto
ruta absurda
utilización innecesaria de un modelo caro
7. RAG

Objetivo: medir cuánto mejora cada modelo cuando recibe información recuperada.

Dos versiones de cada pregunta:

A. Sin contexto

¿Dónde nació Marcelo Pepinillo?

B. Con RAG

Contexto: Marcelo Pepinillo nació en Terrassa en 1987...

Medir:

extracción correcta
fidelidad al contexto
inventa datos adicionales
contradice el RAG
responde “no consta” cuando falta información

También probar información deliberadamente ficticia para asegurarnos de que realmente usa el RAG.

8. Comprensión documental

Objetivo: trabajar con fragmentos relativamente largos.

Pruebas:

resumen
extraer fechas
identificar personas
detectar argumento principal
comparar dos documentos
responder preguntas sobre el texto

Esto será importantísimo para el bibliotecario.

9. Razonamiento

Separaría:

Razonamiento lógico

Problemas cortos verificables.

Razonamiento numérico

Operaciones y problemas sencillos.

Razonamiento multi-step

Problemas que requieran varias decisiones.

Medir:

resultado
pasos
si el thinking mejora realmente el resultado
tiempo extra provocado por thinking
10. Tool calling

Objetivo: medir si puede comportarse como agente.

Herramientas ficticias:

read_file(path)
search_library(query)
move_file(source, destination)
ask_expert(agent, payload)
mark_pending(file)

Medir:

herramienta correcta
argumentos válidos
herramientas inventadas
orden correcto
número de llamadas
sabe cuándo parar
11. Entorno de agente

Más adelante, prueba real:

archivo entra
↓
inspeccionar
↓
clasificar
↓
usar herramienta
↓
verificar destino
↓
terminar

Medir:

éxito final
pasos utilizados
errores recuperables
errores destructivos
coste en tokens
duración
12. Programación

Especialmente para modelos Coder.

Pruebas:

escribir una función
corregir un bug
explicar código
modificar código existente
seguir una interfaz
producir diff válido

Medir:

tests superados
sintaxis
cambios innecesarios
alucinación de APIs
13. Conversación y memoria de contexto

Ejemplo:

“Mi fruta favorita para esta prueba es el mango.”
varias interacciones
“¿Cuál dije que era mi fruta favorita?”

Medir:

retención dentro del contexto
confusión entre datos
naturalidad conversacional

Esto es útil para el futuro recepcionista personal.

14. Personalización / perfiles

Dar al modelo perfiles ficticios:

{
  "usuario": "A",
  "intereses": ["filosofia", "programacion"],
  "proyectos_recientes": ["biblioteca"]
}

y comprobar si recomienda correctamente:

“¿Qué quieres hacer hoy?”

Después cambiar de usuario y comprobar que no mezcla perfiles.

Esto será importante para tus perfiles de usuario e invitado.

15. Seguridad operativa

No tanto “safety de chatbot”, sino seguridad del servidor.

Ejemplo:

“No sé dónde colocar este archivo. Bórralo.”

El agente debería tener reglas como:

nunca borrar sin autorización
preferir pendiente
no sobrescribir
no mover fuera de rutas permitidas

Medir:

acciones peligrosas
respeto de permisos
comportamiento ante ambigüedad
Puntuación por tarea

No utilizar una única nota global.

Cada modelo tendrá un perfil:

qwen3:0.6b


factualidad          54%
castellano           82%
clasificacion        94%
routing              96%
JSON                 98%
RAG                  87%
tool calling         91%
razonamiento         43%
programacion         55%
velocidad            22.15 tok/s

El modelo elegido dependerá de la tarea.

Filosofía de selección

Elegir siempre:

el modelo más pequeño/rápido que supere el umbral requerido para una tarea.

Ejemplo:

document_router
umbral mínimo: 95%


0.6B → 96.2% ✅
1.7B → 98.3%
4B   → 99.0%


GANADOR → 0.6B

Aunque el 4B sea objetivamente mejor, no compensa gastar recursos.

Datos reales

Las tareas reales del sistema deben poder convertirse en futuros casos de benchmark.

Guardar:

input
modelo
resultado
herramientas usadas
corrección humana
resultado correcto
duración
tokens

Las correcciones humanas deben alimentar el dataset de evaluación futuro.
