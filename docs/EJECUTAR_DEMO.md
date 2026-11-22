# Cómo ejecutar la demo en Claude Code

> English version: [RUN_DEMO.md](RUN_DEMO.md). Qué contar en cada paso: [GUIA_DEMO.md](GUIA_DEMO.md), sección 5.
> Qué ejecuta cada skill por dentro: [GUIA_TECNICA.md](GUIA_TECNICA.md).

Esta guía es la chuleta para la sesión: qué preparar en la terminal, cómo se llama a cada skill dentro de
Claude Code y qué debería salir. Todos los comandos se han probado con el corpus completo.

## 1. Antes de la sesión (en la terminal de WSL)

```bash
cd /mnt/d/repos3/oag_vs_kg_ml_engineer       # o donde tengas el repo
git pull
uv sync --group embed                        # entorno con la capa semántica (sin ella: uv sync)
source .venv/bin/activate                    # imprescindible: las skills llaman a `python`
python demo/oag.py build --q letter-end-runin
python demo/oag.py build --q comment-memo-landscape
python demo/compare.py                       # comprueba que todo responde y precalienta la caché
claude                                       # Claude Code, desde la raíz del repo y con el venv activo
```

Notas:

- `uv sync` a secas desinstala el grupo `embed`. Si vas a usar la capa semántica, usa siempre
  `uv sync --group embed`.
- La primera ejecución de la capa semántica descarga el modelo (unos 470 MB) y calcula los embeddings del
  corpus: tarda unos minutos. `python demo/compare.py` lo deja hecho antes de la sesión; después cada
  consulta tarda segundos.
- Los datos reales tienen que estar en `data/` (corpus, grafo, `questions.yaml`). Ver
  [`demo/README.md`](../demo/README.md#datos).

## 2. Cómo se llama a una skill

Dentro de Claude Code, una skill se invoca escribiendo `/` y su nombre. Al escribir `/demo` aparecen las
seis. Lo que va después del nombre son los argumentos:

```
/demo-oag                                   pregunta por defecto (letter-end-runin), en inglés
/demo-oag comment-memo-landscape            otra pregunta, por su id
/demo-oag letter-end-runin --lang es        la pregunta en castellano llano, sin nombres de código
```

También se puede pedir en lenguaje natural («muestra OAG con la pregunta del memo de comentarios»): Claude
reconoce la skill por su descripción. En la demo es mejor el comando, para que se vea qué se ejecuta.

Cada skill ejecuta su script (`python demo/...`), enseña la salida, responde la pregunta usando solo lo que
ha recuperado esa técnica y registra la respuesta en `data/runs/<id>/`.

**Permisos.** La primera vez que una skill ejecute `python demo/...`, Claude Code pedirá permiso. Elige la
opción de aprobar y no volver a preguntar para ese comando en este proyecto: las skills usan siempre la misma
forma (`python demo/<script>.py`), así que una aprobación cubre toda la demo. Si prefieres dejarlo
configurado antes, añade la regla `Bash(python demo/*)` a `permissions.allow` en
`.claude/settings.local.json` (fichero local, no se sube).

**Limpia el contexto entre técnicas.** Escribe `/clear` antes de cada skill. Si no, Claude recuerda lo
que recuperó la técnica anterior y la comparación deja de ser justa.

## 3. El guion, comando a comando

### Pregunta A: reglas sobre un componente modelado (gana OAG)

| Comando | Qué hace | Qué debería salir |
|---|---|---|
| `/demo-naive-rag` | 5 trozos por TF-IDF y respuesta con ellos | 8 tickets, recall 71 %, precisión 62 % |
| `/demo-agentic-rag` | Claude busca y lee en bucle (máximo 12 llamadas) | Variable; en la prueba, 9 llamadas, recall 71 % |
| `/demo-graphrag` | Vecinos de `get_letter_end` a 1 salto; repite a 2 saltos | 1 salto: 71 % / 50 %. 2 saltos: 100 % / 13 % (53 tickets) |
| `/demo-oag` | Ontología, `build`, consulta con esquema v1 y v2 | v1: 86 % / 35 %. v2: 100 % / 47 % (15 tickets) |

### Pregunta B: explorar un área sin modelar (gana GraphRAG)

| Comando | Qué hace | Qué debería salir |
|---|---|---|
| `/demo-graphrag comment-memo-landscape` | Vecinos del extractor a 2 saltos y temas (comunidades) | 83 % / 43 %, y los temas del área |
| `/demo-oag comment-memo-landscape` | Consulta sin componentes | 0 hechos: el área no está en la ontología |
| `/demo-naive-rag comment-memo-landscape` (opcional) | Top-5 trozos | 3 tickets, recall 10 % |

### La pregunta en castellano llano (opcional)

| Comando | Qué hace | Qué debería salir |
|---|---|---|
| `/demo-naive-rag letter-end-runin --lang es` | TF-IDF y después embeddings multilingües | 14 % y después 43 % |
| `/demo-oag letter-end-runin --lang es` | v2 (sin componentes), v3 (sinónimos en castellano) y `--semantic` | 0 %, 100 % y 100 % |
| `/demo-graphrag comment-memo-landscape --lang es` | Semilla por nombre y después por similitud | 0 % y después 59 % / 25 % |

### Combinar GraphRAG y OAG

| Comando | Qué hace | Qué debería salir |
|---|---|---|
| `/demo-hybrid` | GraphRAG a 2 saltos propone; la ontología filtra (componente, reglas) | 53 candidatos, 22 y 15: 100 % / 47 %, igual que OAG v2 |
| `/demo-hybrid comment-memo-landscape` | Sin componentes: lista del grafo y propuesta para la ontología | 83 % / 43 %, igual que GraphRAG, y las comunidades a revisar |

### Cierre

| Comando | Qué hace | Qué debería salir |
|---|---|---|
| `/demo-compare` | Relanza las técnicas deterministas y lee las respuestas registradas | Dos tablas por pregunta (inglés y castellano llano) y dónde gana cada técnica |

Las cifras de Agentic RAG y de la respuesta final de Claude cambian entre ejecuciones; las de los scripts no.

## 4. Sin Claude Code

Los scripts funcionan solos, con la misma salida que ven las skills:

```bash
python demo/naive_rag.py --q letter-end-runin [--embed] [--lang es]
python demo/graphrag.py --q comment-memo-landscape [--hops 2] [--semantic] [--lang es]
python demo/oag.py query --q letter-end-runin [--schema 1|2|3] [--semantic] [--lang es]
python demo/hybrid.py --q letter-end-runin [--semantic] [--lang es]
python demo/compare.py
```

## 5. Si algo falla

| Síntoma | Causa | Solución |
|---|---|---|
| Al escribir `/demo` no aparecen las skills | Claude Code no se lanzó desde la raíz del repo | Salir y lanzar `claude` en la carpeta del repo |
| `python: command not found`, o Claude prueba `.venv/bin/python` o `uv run` | El venv no estaba activo al lanzar `claude` | Salir, `source .venv/bin/activate` y volver a lanzar `claude` |
| Pide permiso en cada paso | Se aprobó solo una vez, o el comando no tenía la forma `python demo/...` | Elegir «no volver a preguntar», o la regla de la sección 2 |
| `The semantic layer needs sentence-transformers` | Falta el grupo `embed` | `uv sync --group embed` |
| Error al descargar el modelo | Sin acceso a huggingface.co | Probar con red, o copiar `~/.cache/huggingface` de otra máquina y usar `HF_HUB_OFFLINE=1` |
| `No facts yet` | No se ejecutó `build` para esa pregunta | `python demo/oag.py build --q <id>` |
| La respuesta usa cosas que la técnica no recuperó | Contexto de una skill anterior | `/clear` antes de cada skill |
