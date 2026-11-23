# Guion de la presentación

> English version: [PRESENTATION_SCRIPT.md](PRESENTATION_SCRIPT.md).

Este guion es el texto para presentar el deck en directo o grabarlo en vídeo. Es el mismo que llevan las notas del orador de cada slide en `presentacion/OAG_vs_KG_Presentacion.pptx`, así que se puede leer en la vista del presentador mientras se pasan las slides. Se genera desde `presentacion/speaker_notes.py` al regenerar el deck; no se edita a mano.

Las líneas que empiezan por **[DEMO]** son acciones en Claude Code, no texto para leer. Los comandos, la preparación y lo que debe salir en cada paso están en [EJECUTAR_DEMO.md](EJECUTAR_DEMO.md). Para un vídeo, conviene grabar las ejecuciones de la demo aparte y montarlas sobre esas líneas.

Duración orientativa: unos 40 minutos de exposición a ritmo pausado, más unos 25 de demo y las preguntas.

## Slide 1 · Portada (1 min)

Buenas. Hoy hablamos de Ontology-Augmented Generation, OAG, y de si tiene sentido para nosotros.

La pregunta de partida es sencilla: ya tenemos un grafo de conocimiento de tickets que usamos con /kg. ¿Es eso OAG? ¿Nos falta algo? ¿Merece la pena?

La sesión tiene cuatro partes: qué es OAG, cómo se compara con nuestro grafo, qué adoptaríamos y una demo en directo con Claude Code. En la demo vamos a ver cinco formas de recuperar información sobre las mismas preguntas reales, desde la más simple, Naive RAG, hasta OAG, y vamos a medir dónde gana cada una.

No vengo a vender OAG. Vengo a enseñar, con datos, dónde ayuda y dónde no.

## Slide 2 · ¿Es OAG lo que ya hacemos? (1,5 min)

Empiezo por la respuesta corta, para que nadie tenga que esperar al final: OAG y nuestro grafo son primos, no gemelos.

Se parecen en el objetivo, que es anclar al agente en conocimiento del dominio con una fuente que se pueda citar, y en el truco de coste: lo caro se paga al construir el grafo y la consulta no llama a ningún modelo.

La diferencia clave está en el esquema. OAG define antes qué tipos de cosas y de relaciones existen; es lo que llamamos schema-first. Nuestro grafo deja que esos tipos emerjan de lo que el modelo extrae. Por eso nuestro grafo se parece más a GraphRAG que a OAG.

Lo interesante es que nuestras plantillas de tickets, sharp edges y follow-ups ya son una ontología, solo que implícita. A la derecha está lo que nos llevaríamos; lo veremos en la parte 3.

## Slide 3 · Parte 1 · Qué es OAG (0,5 min)

Primera parte: qué es OAG.

La idea en una frase: pasar de recuperar trozos de texto a recuperar hechos con tipo, según una ontología. Vamos a ver de dónde viene, qué significa el término según quién lo use, qué es una ontología y qué dice el paper de referencia, OG-RAG.

## Slide 4 · De RAG a OAG (diagrama) (1,5 min)

Este diagrama ordena las generaciones de RAG, de izquierda a derecha, de menos a más estructura.

Naive RAG trocea los documentos, los vectoriza y recupera los trozos más parecidos a la pregunta. El rerank añade un segundo modelo que reordena. Modular RAG reescribe la pregunta y combina fuentes. Agentic RAG deja que el agente planifique y busque en bucle. GraphRAG extrae un grafo de entidades y comunidades con un modelo, sin esquema fijo. Y OAG usa una ontología definida antes para guiar la extracción, validar y recuperar.

Fijaos en la fila de abajo, qué recupera cada una: de trozos de texto a hechos con tipo y con fuente.

A la izquierda montar es barato y el modelo interpreta. A la derecha el dominio decide qué es un hecho. Ninguna es mejor en abstracto: depende de la pregunta, y eso es lo que vamos a medir en la demo.

## Slide 5 · Un nombre, tres cosas distintas (1 min)

Cuidado con el término, porque OAG significa cosas distintas según quién lo use.

En el artículo de Medium de Ling Huang es una visión conceptual: la ontología como capa normativa del conocimiento, con OWL y SHACL, pero sin método ni números.

En OG-RAG, de Microsoft Research, es un método concreto y evaluado: los documentos se convierten en fact blocks mapeados a la ontología y se recuperan con un algoritmo voraz. Es el paper serio y el que usamos como referencia.

En Palantir Foundry es una plataforma: la ontología es la capa operativa del negocio, con objetos, enlaces y acciones, y el modelo consulta objetos y propone acciones.

Lo común a las tres está abajo: un esquema del dominio que el modelo respeta al recuperar, al razonar y al actuar.

## Slide 6 · Qué es una ontología (1 min)

¿Qué es una ontología? Es la especificación explícita y compartida de un dominio: qué tipos de cosas existen, cómo se relacionan y qué reglas deben cumplir. Y está escrita para que una máquina pueda usarla y comprobarla.

Tiene cuatro piezas. Clases, los tipos de cosas: ticket, invariante, símbolo, test. Relaciones con nombre: un ticket arregla un símbolo, un invariante protege un símbolo. Atributos, las propiedades de cada clase. Y restricciones, las reglas: por ejemplo, la relación «protege» solo puede salir de un invariante, y todo nodo tiene que tener fichero fuente.

A la derecha está la distinción importante: el esquema dice qué puede existir; los hechos dicen qué es verdad hoy.

Y la frase de abajo: una ontología no es una lista de etiquetas. Es un contrato sobre qué cuenta como hecho válido.

## Slide 7 · Esquema y hechos (diagrama) (1 min)

Lo mismo, con nuestro dominio. Los ejemplos están sanitizados.

Arriba, el esquema: cuatro clases, ticket, invariante, componente y test, y las relaciones permitidas entre ellas, cada una con su origen y su destino.

Abajo, los hechos: un ticket toca el componente de fin de carta, otro ticket origina un invariante, ese invariante protege el componente, un test verifica el ticket. Cada hecho cumple el esquema.

Y un detalle que va a ser clave en la demo: los sinónimos. get_letter_end, LETTER_END, «fin de carta» y «end-of-letter» son el mismo componente. Esa lista de sinónimos es lo que permite que una pregunta encuentre el componente, y es la parte que escribe quien conoce el dominio.

## Slide 8 · OWL y SHACL (1,5 min)

Dos siglas que vais a oír siempre que se hable de ontologías: OWL y SHACL. Las dos son estándares del W3C.

OWL sirve para escribir la ontología: clases, propiedades, jerarquías y axiomas, como «todo invariante tiene un ticket de origen». Con OWL, un razonador puede deducir hechos nuevos. Y trabaja en mundo abierto: si falta un dato, no es falso, es desconocido.

SHACL sirve para validar datos contra unas formas: qué tipos de nodo hay, qué relaciones se permiten, qué campos son obligatorios. Trabaja en mundo cerrado: si falta un dato obligatorio, es un error, y devuelve un informe con lo que no cumple.

En nuestra demo no usamos los estándares, sino su idea con herramientas ligeras: un YAML hace de OWL y la validación del script hace de SHACL. Si un día el dominio crece, ese YAML se traduce a los estándares.

## Slide 9 · El pipeline de OG-RAG (diagrama) (1 min)

Así funciona OG-RAG, en cinco pasos.

Uno: expertos escriben o revisan la ontología. Dos: un modelo lee cada documento y lo convierte en fact blocks, pequeños bloques JSON que siguen la ontología; abajo tenéis uno del paper, sobre cultivos. Tres: cada fact block es una hiperarista de un hipergrafo. Cuatro: para recuperar, busca los nodos que encajan con la pregunta y elige con un algoritmo voraz el mínimo conjunto de fact blocks que los cubre. Es un set cover; lo vamos a ver funcionar en la demo. Cinco: esos hechos van al prompt.

Lo importante: el modelo trabaja al construir, no al consultar. La consulta no hace llamadas extra al modelo. En eso se parece a nuestro grafo.

## Slide 10 · Lo que dicen los números (y lo que no) (1 min)

Los resultados del paper. La tabla mide recall de contexto: qué parte de los hechos necesarios llega al modelo.

OG-RAG gana con claridad en los dos dominios agrícolas, soja y trigo, frente a RAG clásico, RAPTOR y GraphRAG. En noticias empata con RAPTOR, y GraphRAG ni siquiera terminó en un día.

Los titulares del abstract son llamativos: un 55 % más de recall de hechos, un 40 % más de respuestas correctas y una atribución más rápida.

Pero leed la letra pequeña: datos propietarios, solo dos dominios, ontologías hechas a mano, y la relevancia de la respuesta no siempre mejora.

La conclusión honesta es la de abajo: la ganancia está en recuperar los hechos correctos, y el precio es construir y mantener la ontología. Esa es la cuenta que tenemos que hacer nosotros.

## Slide 11 · Parte 2 · Nuestro grafo vs OAG (0,5 min)

Segunda parte: nuestro grafo de tickets, construido con graphify, puesto al lado de OG-RAG y de Palantir. Primero un recordatorio de cómo funciona y después la comparación.

## Slide 12 · El grafo de tickets en una slide (1,5 min)

Nuestro grafo en una slide.

A la izquierda, el flujo: kg_refresh prepara el corpus, graphify lanza subagentes que extraen nodos y aristas, finalize lo deja en output y comprueba que no se filtran datos, y /kg consulta el grafo sin llamar a ningún modelo.

Las cifras son las del grafo actual, el mismo que usa la demo: 453 ficheros y unas 690.000 palabras se convierten en casi 4.000 nodos, unas 8.000 aristas y 213 comunidades. El 93 % de las aristas está extraído directamente del texto; el 7 % es inferido.

Fijaos en los tipos que han salido: conceptos, rationales, símbolos, tickets. Y en las aristas: unos dos tercios son genéricas, del tipo «referencia» o «está relacionado con». Dicen que dos cosas tienen que ver, pero no cómo. Ese es el hueco que una ontología vendría a cubrir.

## Slide 13 · La pipeline del grafo (diagrama) (1 min)

El mismo flujo, en detalle.

Arriba, la construcción con /kg-refresh, que se paga una vez: el manifest elige los ficheros, el corpus los aplana guardando su procedencia, graphify extrae con unos veinte subagentes, después se fusionan identificadores duplicados y por último se nombran las comunidades.

Abajo, la consulta con /kg, que es determinista: un tema, el grafo devuelve vecinos, caminos o coincidencias, la zona de peligro con su comunidad, y al final se lee el writeup. La regla es que el grafo apunta y el writeup manda.

La lección está abajo del todo: sin esquema, cada refresh reinventa los tipos, y por eso casi ningún nombre de comunidad sobrevive de una versión a otra.

## Slide 14 · Lado a lado (1 min)

La comparación, dimensión a dimensión. No hace falta leer la tabla entera; me quedo con cuatro filas.

Esquema: en OG-RAG y en Palantir se define antes; en el nuestro emerge, lo decide el modelo al extraer. Es la diferencia de fondo.

Recuperación: OG-RAG usa el set cover; nosotros, consultas deterministas sobre el grafo. Las dos son baratas al consultar: cero llamadas al modelo.

Salida: OG-RAG pone los hechos dentro del prompt. Nosotros devolvemos una lista de lectura: qué tickets leer y dónde está la zona de peligro. Es más prudente, pero el agente tiene que leer.

Acciones: Palantir liga acciones tipadas a la ontología. Nosotros tenemos skills y gates en la metodología, que cumplen un papel parecido.

## Slide 15 · Una ontología implícita en las plantillas (1 min)

Aquí está la buena noticia: ya tenemos una ontología, solo que está en las plantillas.

La plantilla de ticket define qué es un ticket: síntoma, causa raíz, fix, tests y estado. SHARP_EDGES define los invariantes, las reglas de «no tocar», cada una con su ticket de origen. FOLLOWUPS, la deuda abierta. Los componentes y símbolos son nuestros extractores y funciones. TEST_MAP dice qué prueba qué. Y las lecciones y decisiones están en el playbook y la memoria.

El hueco es que graphify no conoce estas clases. Cada refresh las reinventa, y por eso menos del 1 % de las etiquetas de comunidad sobrevive.

La frase de abajo resume la propuesta: no hay que inventar la ontología, hay que escribir la que ya usan las plantillas.

## Slide 16 · ¿Cuánto se parece? (1 min)

El veredicto.

En lo que somos iguales, que es más o menos la mitad del camino: conocimiento del dominio como grafo y no como trozos; construcción cara una vez y consulta barata y reproducible; cada nodo apunta a su fichero; está pensado para que el agente lo consulte antes de actuar; y somos honestos con la confianza, distinguiendo lo extraído de lo inferido.

En lo que nos falta para ser OAG: no hay esquema previo, así que los tipos son genéricos; no hay validación del grafo; no hay hechos tipados como «arregla», «rompe» o «protege»; devolvemos qué leer, no los hechos; y no hay acciones ligadas a la ontología.

Resumen: somos GraphRAG con disciplina de ingeniería. OAG añade el contrato del esquema.

## Slide 17 · Parte 3 · Qué adoptar (0,5 min)

Tercera parte: qué adoptar. Lo útil de OAG, al tamaño de un equipo pequeño y sin plataforma nueva. Veremos una ontología mínima, seis adopciones concretas, la hoja de ruta con lo que no hay que hacer, y cómo medir si mejora.

## Slide 18 · Ocho clases, diez relaciones, un fichero (1 min)

La ontología que proponemos cabe en un fichero: ocho clases y unas diez relaciones. Es un esbozo; el detalle se decide con el corpus real.

Las clases salen de las plantillas: ticket, invariante, follow-up, componente, símbolo, test, lección y decisión. Las relaciones son las que respondemos a diario: qué arregla qué, qué rompe qué, qué sustituye a qué, qué invariante protege qué símbolo, qué test lo verifica.

Las reglas de diseño importan más que la lista. Sale de nuestras plantillas, no de un libro de OWL. Es pequeña: si una relación no responde a una pregunta real, fuera. Va versionada con los scripts del grafo. Las relaciones genéricas se permiten, pero marcadas como pista. Y en la versión que sale fuera, los clientes se convierten en roles.

## Slide 19 · Seis cosas que tomar de OAG (1 min)

Seis adopciones concretas.

Una: extracción guiada. Pasar la ontología a los subagentes de graphify para que solo emitan clases y relaciones del esquema.

Dos: validación en finalize, al estilo SHACL. Rechazar aristas fuera del esquema y nodos sin fuente.

Tres: un backbone determinista. Con frontmatter en las plantillas y las citas a tickets, muchos hechos salen sin modelo.

Cuatro: /kg facts. Devolver los fact blocks mínimos que cubren la consulta, con el set cover de OG-RAG y con su fuente.

Cinco: invariantes como gate antes del merge, cruzando los símbolos tocados con los invariantes que los protegen.

Seis: identificadores estables, para que los nombres de comunidad sobrevivan al refresh.

Cada una es pequeña, reversible y medible: encaja con los gates del método.

## Slide 20 · De menos a más, y qué no hacer (1,5 min)

La hoja de ruta va de menos a más, en cuatro fases.

Fase A, el esquema: escribir la ontología desde las plantillas y añadir frontmatter a los tickets y sharp edges nuevos. Fase B, el backbone: un parser determinista y la validación en finalize. Fase C, la extracción: graphify guiado por el esquema, dejando la inferencia solo para lo que el parser no ve. Fase D, el consumo: /kg facts y el gate de invariantes dentro del flujo.

Y lo que no hay que hacer, que es igual de importante. No montar una plataforma como Foundry ni un triplestore OWL: nuestro tamaño no lo justifica. No meter hechos en el prompt en lugar de leer la fuente: el grafo apunta y el writeup manda. Y sobre todo, no hacer una ontología grande por completitud. El coste de mantenerla es el riesgo número uno de OAG.

## Slide 21 · Validar el instrumento antes de creerle (1,5 min)

¿Cómo sabremos si mejora? Midiendo antes de creer.

Necesitamos un set de 15 a 20 preguntas reales con respuesta conocida, del tipo «qué tickets tocan este componente» o «qué invariante protege esto», con la respuesta escrita a mano. La métrica es el recall de contexto, la misma que usa OG-RAG. Y lo primero es medir el grafo actual: es la línea base.

El criterio para quedarnos con el cambio: que mejore el recall en las zonas densas, que no empeore en las áreas aisladas, que el refresh no cueste más, y revisar qué tickets faltan, no solo cuántos. Y decir qué no puede mostrar el set, porque lo escribe alguien con sus sesgos.

Es el mismo principio del método: un gate verde que no puede fallar no prueba nada.

Y con esto pasamos a la demo, que es una versión pequeña de esta evaluación.

## Slide 22 · Parte 4 · La demo (0,5 min)

Cuarta parte: la demo. Seis skills de Claude Code, dos preguntas reales y la misma vara de medir para todas.

Veremos cómo funciona OAG en la demo, cómo evaluamos, las dos preguntas con sus ganadores, qué pasa al combinar GraphRAG y OAG, cómo evolucionó la ontología, qué pasa si preguntamos en castellano, y la conclusión: dónde gana cada técnica y si nos merece la pena.

## Slide 23 · La demo en Claude Code, paso a paso (1 min)

Esto es lo que vamos a ejecutar. Antes de la sesión ya he preparado el entorno: el venv activo, los hechos de OAG construidos y una pasada de la comparativa para tener la caché caliente.

Dentro de Claude Code cada técnica es una skill. Para la pregunta A lanzaré Naive RAG, Agentic RAG, GraphRAG y OAG. Para la B, GraphRAG y OAG. Si hay tiempo, OAG con la pregunta en castellano. Y al final el híbrido y la comparativa.

Dos reglas para que la comparación sea justa: hago /clear antes de cada skill, para que Claude no recuerde lo que encontró la técnica anterior, y cada técnica responde solo con lo que ella ha recuperado.

**[DEMO]** Cambiar a la terminal con Claude Code abierto en la raíz del repo. Si es la primera ejecución, aprobar «python demo/...» con «no volver a preguntar».

## Slide 24 · OAG en la demo (diagrama) (1 min)

Así está montado OAG en la demo, en cinco pasos.

Uno: la ontología es un YAML con cuatro clases, seis relaciones, los componentes con sus sinónimos en inglés y en castellano, y las reglas de extracción. Dos: un parser determinista lee el corpus: títulos, tablas de invariantes, citas a tickets, tests y sinónimos. Tres: la validación rechaza lo que el esquema no permite, por ejemplo las menciones genéricas, y lo cuenta en un informe. Cuatro: el resultado son hechos tipados, cada uno con su fichero fuente. Cinco: la consulta asocia la pregunta a un componente por sus sinónimos, aplica el set cover y devuelve fact blocks.

No hay modelo ni al construir ni al consultar. En producción la extracción se completaría con un modelo guiado por la misma ontología, y siempre validado.

## Slide 25 · Cómo evaluamos (diagrama) (2 min)

Cómo evaluamos.

Pregunta A: un bug real ya resuelto, planteado como si fuera nuevo: hay un fallo en la detección del fin de carta, ¿qué no puedo romper al arreglarlo? La hoja de respuestas es el writeup de ese bug, que lista siete tickets que no había que romper. Ese writeup se excluye de todas las técnicas, para que nadie pueda copiar la respuesta.

Pregunta B: explorar un área, el memo de comentarios. La respuesta esperada sale de una regla objetiva: los writeups cuyo título menciona el área. Son 29.

Medimos dos cosas, y conviene tenerlas claras porque salen en todas las tablas. Recall: de los tickets que había que encontrar, cuántos encuentra la técnica; mide lo que se deja fuera. Precisión: de lo que devuelve, cuánto está en la lista de referencia; mide el ruido. Un ejemplo de la pregunta A: si una técnica devuelve 53 tickets y entre ellos están los 7 de referencia, tiene un recall del 100 % y una precisión del 13 %. Es como pescar con una red enorme: sacas todos los peces que buscabas, pero con mucho más. Y la lista de referencia es un mínimo, así que un ticket de más no siempre es ruido.

Además medimos el coste, en tokens de contexto y llamadas al modelo.

Una advertencia que repetiré: dos preguntas no son una evaluación. Es una demostración. La evaluación seria es el set de 15 a 20 preguntas.

**[DEMO]** Pregunta A: /clear y /demo-naive-rag; /clear y /demo-agentic-rag; /clear y /demo-graphrag; /clear y /demo-oag. Comentar cada salida en una frase. En OAG, enseñar lo rechazado por la validación y un fact block completo.

## Slide 26 · Dos preguntas, dos ganadores (diagrama) (1 min)

El resumen de las dos preguntas antes de entrar en las tablas.

En la A, reglas sobre un componente que la ontología modela, gana OAG: encuentra los siete tickets esperados en 15 resultados en lugar de 53, y cada uno con su porqué: qué invariante origina, qué componente toca, qué test lo fija.

En la B, un área que la ontología no modela, gana GraphRAG: descubre el área sin que nadie la haya modelado y la agrupa en temas. OAG no devuelve nada, porque no ve lo que su esquema no declara.

Dos preguntas, dos ganadores. Eso es exactamente lo que queríamos enseñar.

**[DEMO]** Pregunta B: /clear y /demo-graphrag comment-memo-landscape; /clear y /demo-oag comment-memo-landscape. Subrayar que OAG devuelve cero hechos y por qué.

## Slide 27 · Pregunta A: reglas sobre un componente modelado (1,5 min)

La pregunta A en detalle. Siete tickets esperados, corpus completo de 453 ficheros.

Naive RAG encuentra cinco de los siete, con buena precisión. GraphRAG a un salto, lo mismo con menos contexto. A dos saltos lo encuentra todo, pero entre 53 tickets: la precisión cae al 13 %. OAG con la primera ontología, seis de siete. Con la ontología corregida, los siete en 15 tickets.

Un matiz importante: por F1, que mezcla recall y precisión, Naive RAG queda casi a la par. Pero se deja dos de los siete, y en una pregunta de «qué no romper», un olvido es una regresión en producción. Aquí el recall pesa más.

La última columna es la versión anterior con solo 14 ficheros: con poco corpus todo parece funcionar. Con el corpus completo es cuando se ven las diferencias.

Y Agentic RAG lo vemos en directo, porque cada ejecución es distinta.

## Slide 28 · Pregunta B: explorar un área sin modelar (1 min)

La pregunta B. 29 tickets esperados, por una regla objetiva: los writeups cuyo título menciona el área.

Naive RAG acierta los tres que devuelve, pero se queda en el 10 % de recall: cinco trozos no bastan para un área entera. GraphRAG a un salto, el 21 %. A dos saltos, el 83 %, con una precisión razonable, y además agrupa el resultado en temas usando las comunidades del grafo. OAG, cero: la pregunta no menciona ningún componente de su ontología.

No hay que disimularlo: es el límite de la técnica. OAG solo ve lo que su esquema declara. Para cubrir esta área habría que modelarla primero, y eso solo merece la pena si la pregunta se repite.

## Slide 29 · Híbrido: GraphRAG propone, la ontología filtra (1,5 min)

La pregunta natural después de ver dos ganadores: ¿y si los combinamos?

Lo probamos de la forma más sencilla. GraphRAG a dos saltos da la lista amplia: mucho recall, poca precisión. Si la pregunta nombra un componente de la ontología, la lista se filtra: primero por clases y relaciones, y después por las reglas. Si no nombra ninguno, se queda la lista del grafo tal cual, y las comunidades que encuentra se proponen para ampliar la ontología; esa propuesta la revisa una persona.

El resultado, contado sin adornos: el híbrido iguala a la mejor técnica en cada pregunta, pero no la supera. En la A el embudo es de 53 candidatos a 22 y de ahí a 15, y el grafo no aportó ningún ticket que OAG no tuviera. En la B es la lista de GraphRAG.

Lo que aporta es no tener que elegir técnica, y una lista de qué modelar después. Su punto débil: si una pregunta de exploración nombra un componente, se filtraría por error.

**[DEMO]** /clear y /demo-hybrid; después /demo-hybrid comment-memo-landscape. Enseñar el embudo 53, 22, 15 y la propuesta para la ontología.

## Slide 30 · De OAG v1 a v2: el esquema también se depura (1,5 min)

Una cosa que tengo que contar con honestidad: la ontología que gana en la pregunta A es la segunda versión.

La primera fallaba de dos formas, y las dos eran del esquema, no de la técnica. Uno, ruido: la relación «no romper» traía tickets de otras áreas, como numeración o PDF. La v2 añade una restricción al estilo SHACL: el ticket protegido tiene que compartir componente. Pasa de 17 a 11 tickets sin perder ninguno esperado. Dos, una dependencia sin declarar: la detección del fin de carta usa la función de títulos para mirar el título siguiente, pero la v1 trataba los componentes como islas. La v2 añade la relación «llama a» y recupera el invariante que faltaba: el recall sube del 86 % al 100 %.

La v2 se escribió después de ver el fallo. Es la forma normal de mantener una ontología, pero el resultado solo se puede atribuir a la técnica cuando se valide con preguntas nuevas.

**[DEMO]** Si no se vio antes: python demo/oag.py query --schema 1 para comparar con la v2.

## Slide 31 · La pregunta en castellano (1,5 min)

Una prueba más realista: el corpus está en inglés, pero alguien pregunta en castellano llano y sin nombres de código. Por ejemplo: «hay un fallo en el final de la carta, ¿qué no puedo romper?».

Sin capa semántica caen las tres técnicas deterministas, y en silencio: no avisan de que no han entendido. Naive RAG con palabras se queda en el 14 %. GraphRAG no encuentra ningún nodo que se llame así. OAG no reconoce ningún componente.

Con una capa semántica pequeña cambia mucho. Naive RAG con embeddings multilingües sube al 43 %. GraphRAG llega a la zona correcta, aunque no al nodo central. Y OAG recupera exactamente lo mismo que en inglés, de dos formas: añadiendo seis sinónimos en castellano a la ontología, o eligiendo el componente por significado con un modelo pequeño en CPU. El umbral de ese modelo está calibrado con estas dos preguntas, y lo digo.

La lección: el idioma solo afecta al primer paso, reconocer de qué componente se habla. Después, los hechos son los mismos.

**[DEMO]** Opcional: /clear y /demo-oag letter-end-runin --lang es.

## Slide 32 · Cuándo conviene cada técnica (diagrama) (1 min)

Esta tabla es la guía general, más allá de nuestra demo.

Sin RAG, cuando todo cabe en la ventana del modelo, como un ticket y su writeup. Naive RAG, para preguntas puntuales sobre mucho texto. Rerank o búsqueda híbrida, cuando hay nombres exactos como IDs o funciones. Agentic RAG, para investigar algo nuevo, aceptando más coste y variabilidad. GraphRAG, para relaciones y temas: qué hay alrededor de algo. Y OAG, para hechos tipados, reglas, auditoría y atribución, pagando el precio de escribir y mantener la ontología.

La regla práctica: empezar por lo más simple que responda a las preguntas reales, y medir antes de subir de nivel.

**[DEMO]** /clear y /demo-compare para enseñar las dos tablas con todas las técnicas.

## Slide 33 · Dónde gana cada técnica (1 min)

Traducido a nuestras preguntas del día a día.

Si la pregunta es «qué reglas, tickets o tests protegen este componente», OAG: hechos con su porqué, poco ruido y validables antes de llegar al modelo. Si es «qué hay en esta área y cómo se organiza», GraphRAG, nuestro /kg: descubre la estructura sin esquema previo. Si es «dónde se menciona este identificador», Naive RAG o una búsqueda: barato e inmediato. Si es «investiga este problema nuevo», Agentic RAG, sabiendo que es caro y variable. Y cualquiera de ellas, si se pregunta en castellano sin nombres de código, con la capa semántica.

La frase con la que me quedo: OAG no sustituye a GraphRAG, lo completa. Uno descubre la estructura y el otro la fija como contrato.

## Slide 34 · ¿Merece la pena? (1,5 min)

¿Merece la pena? Sí, por partes, y solo para las preguntas de reglas.

Lo que ha costado en la demo: una ontología de unas 70 líneas, con cuatro clases, seis relaciones, una restricción y cuatro componentes, que sale en buena parte de las plantillas que ya tenemos. La extracción es determinista, sin llamadas al modelo. Y para preguntar en castellano bastan unos sinónimos o un modelo pequeño.

Lo que no compensa: modelar todo el dominio por completitud; sustituir /kg, porque explorar lo sigue haciendo mejor el grafo; y sacar conclusiones sin un set de 15 a 20 preguntas.

Lo que llevaríamos a la metodología: primero el set de preguntas, de reglas y de exploración; una ontología mínima con sus dependencias; validar el grafo contra el esquema en /kg-refresh; y dos modos en /kg: /kg tema para explorar y /kg facts para las reglas.

Poco esfuerzo y bien acotado.

## Slide 35 · Cierre (0,5 min)

Para cerrar, en una frase: nuestro grafo ya hace la mitad de OAG. La otra mitad es escribir la ontología que nuestras plantillas ya usan, y validar el grafo contra ella.

Las referencias están en la slide, y en el repo tenéis la guía de la demo, el informe completo y todo el código, para que cualquiera pueda repetir las pruebas.

Gracias. ¿Preguntas?
