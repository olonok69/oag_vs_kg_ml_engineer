---
name: demo-oag
description: Demo paso 4. Responde la pregunta de la demo con OAG, hechos tipados extraídos y validados contra una ontología mínima. Usar cuando se pida /demo-oag o mostrar OAG.
---

# Demo: OAG (Ontology-Augmented Generation)

Objetivo: mostrar la diferencia de definir el esquema antes (schema-first). Ver `demo/README.md` y
`demo/oag/ontology.yaml`.

1. Enseña la ontología: `demo/oag/ontology.yaml`. Resume en cuatro líneas clases, relaciones, componentes
   con sus sinónimos (altLabels) y reglas de extracción.
2. Construye los hechos: `python demo/oag.py build`. Comenta el informe: hechos por relación y, sobre
   todo, lo rechazado por la validación (relaciones que no están en el esquema).
3. Consulta: `python demo/oag.py query`. Explica cómo la pregunta se mapea a un componente de la ontología
   y cómo el set cover elige el mínimo de fact blocks.
4. Responde la pregunta de `data/questions.yaml` usando SOLO los fact blocks. Para cada ticket di el hecho
   (qué invariante origina, quién lo nombra como "no romper", qué test lo fija) y su fuente.
5. Registra tu respuesta: `python demo/record_answer.py oag "<ids>"`.
6. Cierra con dos líneas: qué aporta frente a /kg y cuál es el precio (escribir y mantener la ontología).
