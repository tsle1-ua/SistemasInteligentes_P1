Práctica 1: Satisfacción de Restricciones - Sudoku
================================================

## Descripción
Implementación de algoritmos de satisfacción de restricciones para resolver Sudokus:
- Backtracking
- Forward Checking  
- AC3 (Arc Consistency 3)

## Archivos del proyecto
- `main.py`: Programa principal con interfaz gráfica
- `tablero.py`: Clase que representa el tablero del Sudoku
- `variable.py`: Clase Variable para cada celda del CSP
- `sudoku_csp.py`: Modelado del problema como CSP
- `algoritmos.py`: Implementación de los tres algoritmos
- `experimentos.py`: Experimentos de la sesión 7 (BT/FC con y sin AC3; tiempos, nodos, CSV + gráficas)
- `info_sistema.py`: Informe rápido del equipo (para documentación)
- `m0.txt`..`m6.txt`: Plantillas de Sudoku

## Instrucciones de uso (GUI)

Ejecutar el programa con o sin plantilla:

    python main.py           
    python main.py m2.txt

Botones:
- **Load**: Carga un archivo de Sudoku
- **BK**: Ejecuta algoritmo Backtracking
- **FC**: Ejecuta algoritmo Forward Checking  
- **AC3**: Ejecuta algoritmo AC3 (reduce dominios)

### Notas GUI
- Los números en negro son los dados inicialmente
- Los números en gris son los calculados por el algoritmo

## Sesión 7 (experimentos con AC3)

Comparativa de BT y FC sin AC3 y después de aplicar AC3, para m0..m6.

Ejemplos:

        # Modo por defecto: con pre-reducción inicial de dominios (recomendado)
        python experimentos.py --max-nodos 2000000

        # Solo algunas plantillas
        python experimentos.py --subset m1.txt m2.txt --max-nodos 2000000

        # Ejecutar ambos modos: con y sin pre-reducción
        python experimentos.py --ambos --max-nodos 2000000

        # Evitar la generación de gráficas
        python experimentos.py --sin-graficas

Genera:
- `resultados.csv` con columnas:
    nombre, algoritmo, tiempo_ms, tiempo_total_ms, nodos, exito, solucion_valida,
    limite_excedido, ac3_aplicado, tiempo_ac3_ms, pre_reduccion
- `graficas_resultados.png` con barras comparando BT, FC, AC3+BT y AC3+FC (escala log)

## Sesión 8 (documentación y entrega final)

Estructura recomendada de entrega (ZIP a Moodle):

- /Cod: todo el código `.py`, plantillas `.txt` y artefactos de resultados (CSV/PNG opcional).
- /Doc: documentación en PDF (exportada desde `Doc/Informe_Practica_1.md`).

Pasos sugeridos:

1) Regenerar resultados y gráficas (opcional):

```
python experimentos.py --max-nodos 2000000
```

2) Exportar a PDF el informe `Doc/Informe_Practica_1.md` (p.ej., con su editor preferido) y guardarlo en `/Doc`.

3) Empaquetar para entrega (PowerShell):

```
# Crear estructura temporal
New-Item -ItemType Directory -Force Cod, Doc | Out-Null

# Copiar código y datos
Copy-Item *.py, *.txt -Destination Cod -Force
Copy-Item resultados.csv, graficas_resultados.png -Destination Cod -ErrorAction Ignore

# Copiar documentación
Copy-Item Doc\*.pdf -Destination Doc -ErrorAction Ignore

# Crear ZIP
Compress-Archive -Path Cod, Doc -DestinationPath Practica1_SI.zip -Force
```

Notas:
- `informacion_sistema.txt` puede incluirse en `/Cod` como anexo informativo.
- Si no desea adjuntar artefactos, puede entregar sólo el código; el script de experimentos permite reproducirlos.

## Informe de sistema (para la documentación)

    python info_sistema.py

Guarda `info_sistema.txt` con OS, versión de Python y CPU/núcleos.

Autor: Teferi Samuel Laforga Ena
Curso: 2025-26
