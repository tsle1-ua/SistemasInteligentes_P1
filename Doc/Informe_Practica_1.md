# Práctica 1 – CSP Sudoku

Este documento resume el diseño, implementación, experimentación y conclusiones del solucionador de Sudokus mediante satisfacción de restricciones.

## 1. Clase Variable

- Fichero: `variable.py`.
- Representa cada celda (i,j) del Sudoku con:
  - Atributos: fila, columna, valor ('0' si está vacía), dominio (lista de strings), es_fija (bool), vecinos (coordenadas relacionadas).
  - Operaciones principales:
    - `esta_asignada()`, `asignar_valor()`, `desasignar()`.
    - Gestión de dominio: `eliminar_del_dominio()`, `restaurar_en_dominio()`, `dominio_vacio()`, `tamano_dominio()`, `obtener_dominio()`.
    - Vecindario: `set_vecinos()`, `get_vecinos()`.
- Decisiones:
  - Los valores se manejan como strings ('1'..'9') para mantener coherencia con la lectura del fichero.
  - Si la celda es fija, su dominio queda restringido a `[valor]`.

## 2. Tratamiento de casillas fijas

- Las casillas con valor inicial distinto de '0' se marcan `es_fija=True`, su dominio es singleton y no se permite desasignar.
- `SudokuCSP` aplica una reducción de dominios inicial con los fijos salvo que se proporcionen dominios externos (ver punto 3). Esto elimina de los dominios de las celdas libres los valores ya presentes en su fila, columna y bloque.

## 3. Especificación formal del problema (CSP)

- Tupla formal: ⟨V, E, c, I, a⟩
  - V: conjunto de variables {X_ij | i,j ∈ {0..8}}; cada una representa una celda 9×9.
  - E: estructura de restricciones binarias de desigualdad entre celdas vecinas (misma fila, columna o bloque 3×3). Implementadas mediante el conjunto de vecinos por variable.
  - c: para todo par (X,Y) en E, la restricción c(X,Y) ≡ X ≠ Y.
  - I (instanciación inicial): valores fijos del tablero; si X_ij tiene valor v∈{'1'..'9'}, entonces X_ij=v y Dom(X_ij)={v}.
  - a (dominios iniciales):
    - Con pre-reducción: para celdas no fijas Dom(X_ij) = {1..9} \ {valores presentes en su fila/columna/bloque}.
    - Sin pre-reducción (modo opcional de experimentación): Dom(X_ij) = {1..9} para no fijas; Dom(X_ij)={v} para fijas.

## 4. Algoritmos implementados

- Fichero: `algoritmos.py`.
- Backtracking (BT):
  - Selección MRV (Minimum Remaining Values) para elegir variable no asignada.
  - Comprueba consistencia local con `es_consistente` antes de asignar.
- Forward Checking (FC):
  - Tras asignar, elimina el valor asignado de los dominios de las variables relacionadas y revierte en backtrack.
- AC3:
  - Revisión de arcos basada en desigualdad: si Dj es singleton {v}, eliminar v del dominio Di.
  - Devuelve: `{'consistente': bool, 'dominios_antes': 9x9, 'dominios_despues': 9x9, 'resueltas': int}`.
  - Permite arrancar con dominios externos (útil para el modo sin pre-reducción).

## 5. Integración y flujo de dominios

- `SudokuCSP(tablero, dominios=None)` acepta dominios opcionales; si se pasan, NO aplica la pre-reducción automática.
- `snapshot_dominios()` permite capturar el estado 9×9 de dominios.
- En GUI (`main.py`): al pulsar AC3 se guardan dominios reducidos y BK/FC los usan si se lanzan a continuación.

## 6. Experimentación (Sesiones 7–8)

- Script: `experimentos.py`.
- Compara para cada sudoku m0..m6:
  - BT, FC (sin AC3)
  - AC3+BT, AC3+FC (BT/FC consumiendo dominios tras AC3)
- Modos de partida:
  - Con pre-reducción de dominios (por defecto, recomendado)
  - Sin pre-reducción (`--sin-pre` o `--ambos`)
- Métricas registradas (CSV):
  - nombre, algoritmo, tiempo_ms, tiempo_total_ms, nodos, exito, solucion_valida, limite_excedido, ac3_aplicado, tiempo_ac3_ms, pre_reduccion.
- Gráficas: `graficas_resultados.png` (tiempos y nodos, escala log, agrupando BT/FC/AC3+BT/AC3+FC).

### Objetivo de pruebas

- Plantillas con muchas celdas fijas (p.ej., m0) vs con menos: observar impacto de AC3 en reducción de búsqueda y tiempos.
- Confirmar que AC3 aporta ganancias combinada con FC/BT y que el coste de AC3 (tiempo_ac3_ms) compensa.

## 7. Estudio de tiempos (resumen)

- Ver `resultados.csv` y `graficas_resultados.png` generados en el repo.
- Hallazgos típicos observados:
  - AC3+FC tiende a explorar menos nodos y resolver más rápido en sudokus con suficiente propagación.
  - En plantillas ya “casi resueltas” (m0), AC3 aporta poco y su coste puede ser marginal.

## 8. Dificultades encontradas

- Sincronización de dominios entre AC3 y los algoritmos de búsqueda.
- Evitar trazas verbosas en entrega final; se añadió una bandera para activar/desactivar impresión de dominios en AC3.
- Modelado de vecinos correcto y consistente (fila, columna, bloque) sin recomputar en cada paso.

## 9. Uso de IAs generativas

- Se empleó asistencia para: refactorizar el CSP, diseñar el pipeline AC3→BK/FC, y estructurar los experimentos y documentación.
- Toda la implementación y decisiones fueron verificadas con pruebas locales (scripts y GUI), y se ajustaron a los requisitos de la asignatura.

## 10. Referencias

- Russell & Norvig, "Artificial Intelligence: A Modern Approach" (Capítulo de CSPs y AC3).
- Apuntes de la asignatura (sesiones 4–8).
- Documentación de Python (módulos estándar utilizados).

## 11. Cómo reproducir

- Experimentos (pre-reducción, recomendado):

```powershell
python experimentos.py --max-nodos 2000000
```

- Sin pre-reducción (y comparar ambos modos):

```powershell
python experimentos.py --ambos --max-nodos 2000000
```

- GUI:

```powershell
python main.py
# o con plantilla
python main.py m2.txt
```

Los artefactos resultantes (CSV y PNG) se generan en la raíz del proyecto.
