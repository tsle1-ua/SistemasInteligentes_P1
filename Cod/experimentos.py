"""
Script de experimentos (Sesión 7)
---------------------------------

- Compara Backtracking (BT) y Forward Checking (FC) sin AC3 y después de aplicar AC3.
- Dos modos de partida: con pre-reducción de dominios por valores fijos (por defecto del CSP)
  y sin pre-reducción (todos los no fijos comienzan con 1..9).
- Mide tiempos (ms), tiempos de AC3, nodos y éxito.
- Guarda resultados en resultados.csv y genera gráficas comparativas (si matplotlib está disponible).

Uso:
    python experimentos.py

Opcional:
    python experimentos.py --max-nodos 2000000 --sin-pre --ambos --sin-graficas --subset m1 m2
"""

from __future__ import annotations
import argparse
import csv
import os
import time
from typing import List, Dict, Optional

from tablero import Tablero
from algoritmos import (
    backtracking_stats,
    forward_checking_stats,
    ac3,
)

SUDOKUS = [
    "m0.txt",
    "m1.txt",
    "m2.txt",
    "m3.txt",
    "m4.txt",
    "m5.txt",
    "m6.txt",
]

CSV_FILE = "resultados.csv"


def verificar_solucion(tablero: Tablero) -> bool:
    # Filas
    for fila in range(9):
        vistos = set()
        for col in range(9):
            v = tablero.getCelda(fila, col)
            if v == '0' or v in vistos:
                return False
            vistos.add(v)
    # Columnas
    for col in range(9):
        vistos = set()
        for fila in range(9):
            v = tablero.getCelda(fila, col)
            if v == '0' or v in vistos:
                return False
            vistos.add(v)
    # Bloques 3x3
    for br in range(3):
        for bc in range(3):
            vistos = set()
            for fila in range(br*3, br*3+3):
                for col in range(bc*3, bc*3+3):
                    v = tablero.getCelda(fila, col)
                    if v == '0' or v in vistos:
                        return False
                    vistos.add(v)
    return True


def dominios_completos(tablero: Tablero) -> List[List[List[str]]]:
    """Genera dominios 9x9 con 1..9 para celdas no fijas y [valor] para fijas."""
    full = []
    todos = ['1','2','3','4','5','6','7','8','9']
    for f in range(9):
        fila = []
        for c in range(9):
            v = tablero.getCelda(f, c)
            if v != '0':
                fila.append([v])
            else:
                fila.append(todos[:])
        full.append(fila)
    return full


def ejecutar_experimentos(max_nodos: int, pre_reduccion: bool, subset: Optional[List[str]] = None) -> List[Dict]:
    resultados: List[Dict] = []

    lista = SUDOKUS if not subset else subset
    for nombre in lista:
        if not os.path.exists(nombre):
            print(f"Aviso: {nombre} no existe, se omite.")
            continue

        print(f"\nResolviendo {nombre} | pre_reduccion={pre_reduccion} ...")
        tab = Tablero(nombre)
        dominios = None if pre_reduccion else dominios_completos(tab)
        etiqueta = os.path.splitext(nombre)[0].upper()

        # BT sin AC3
        t0 = time.perf_counter()
        r_bk = backtracking_stats(tab, max_nodos=max_nodos, dominios=dominios)
        t1 = time.perf_counter()
        tiempo_bk_ms = (t1 - t0) * 1000
        solucion_valida_bk = r_bk['exito'] and verificar_solucion(r_bk['tablero'])
        resultados.append({
            'nombre': etiqueta,
            'algoritmo': 'BT',
            'tiempo_ms': round(tiempo_bk_ms, 3),
            'tiempo_total_ms': round(tiempo_bk_ms, 3),
            'tiempo_ac3_ms': 0.0,
            'nodos': r_bk['nodos'],
            'exito': int(r_bk['exito']),
            'solucion_valida': int(solucion_valida_bk),
            'limite_excedido': int(r_bk['limite_excedido']),
            'ac3_aplicado': 0,
            'pre_reduccion': int(pre_reduccion),
        })

        # FC sin AC3
        t0 = time.perf_counter()
        r_fc = forward_checking_stats(tab, max_nodos=max_nodos, dominios=dominios)
        t1 = time.perf_counter()
        tiempo_fc_ms = (t1 - t0) * 1000
        solucion_valida_fc = r_fc['exito'] and verificar_solucion(r_fc['tablero'])
        resultados.append({
            'nombre': etiqueta,
            'algoritmo': 'FC',
            'tiempo_ms': round(tiempo_fc_ms, 3),
            'tiempo_total_ms': round(tiempo_fc_ms, 3),
            'tiempo_ac3_ms': 0.0,
            'nodos': r_fc['nodos'],
            'exito': int(r_fc['exito']),
            'solucion_valida': int(solucion_valida_fc),
            'limite_excedido': int(r_fc['limite_excedido']),
            'ac3_aplicado': 0,
            'pre_reduccion': int(pre_reduccion),
        })

        # AC3 + BT
        import copy
        t_ac3_0 = time.perf_counter()
        tab_ac3 = copy.deepcopy(tab)
        res_ac3 = ac3(tab_ac3, dominios=dominios)
        t_ac3_1 = time.perf_counter()
        tiempo_ac3_ms = (t_ac3_1 - t_ac3_0) * 1000

        if res_ac3['consistente']:
            t0 = time.perf_counter()
            r_bk2 = backtracking_stats(tab_ac3, max_nodos=max_nodos, dominios=res_ac3['dominios_despues'])
            t1 = time.perf_counter()
            tiempo_bk2_ms = (t1 - t0) * 1000
            solucion_valida_bk2 = r_bk2['exito'] and verificar_solucion(r_bk2['tablero'])
            resultados.append({
                'nombre': etiqueta,
                'algoritmo': 'AC3+BT',
                'tiempo_ms': round(tiempo_bk2_ms, 3),
                'tiempo_total_ms': round(tiempo_bk2_ms + tiempo_ac3_ms, 3),
                'tiempo_ac3_ms': round(tiempo_ac3_ms, 3),
                'nodos': r_bk2['nodos'],
                'exito': int(r_bk2['exito']),
                'solucion_valida': int(solucion_valida_bk2),
                'limite_excedido': int(r_bk2['limite_excedido']),
                'ac3_aplicado': 1,
                'pre_reduccion': int(pre_reduccion),
            })
        else:
            resultados.append({
                'nombre': etiqueta,
                'algoritmo': 'AC3+BT',
                'tiempo_ms': 0.0,
                'tiempo_total_ms': round(tiempo_ac3_ms, 3),
                'tiempo_ac3_ms': round(tiempo_ac3_ms, 3),
                'nodos': 0,
                'exito': 0,
                'solucion_valida': 0,
                'limite_excedido': 0,
                'ac3_aplicado': 1,
                'pre_reduccion': int(pre_reduccion),
            })

        # AC3 + FC
        t_ac3_0 = time.perf_counter()
        tab_ac3 = copy.deepcopy(tab)
        res_ac3 = ac3(tab_ac3, dominios=dominios)
        t_ac3_1 = time.perf_counter()
        tiempo_ac3_ms = (t_ac3_1 - t_ac3_0) * 1000

        if res_ac3['consistente']:
            t0 = time.perf_counter()
            r_fc2 = forward_checking_stats(tab_ac3, max_nodos=max_nodos, dominios=res_ac3['dominios_despues'])
            t1 = time.perf_counter()
            tiempo_fc2_ms = (t1 - t0) * 1000
            solucion_valida_fc2 = r_fc2['exito'] and verificar_solucion(r_fc2['tablero'])
            resultados.append({
                'nombre': etiqueta,
                'algoritmo': 'AC3+FC',
                'tiempo_ms': round(tiempo_fc2_ms, 3),
                'tiempo_total_ms': round(tiempo_fc2_ms + tiempo_ac3_ms, 3),
                'tiempo_ac3_ms': round(tiempo_ac3_ms, 3),
                'nodos': r_fc2['nodos'],
                'exito': int(r_fc2['exito']),
                'solucion_valida': int(solucion_valida_fc2),
                'limite_excedido': int(r_fc2['limite_excedido']),
                'ac3_aplicado': 1,
                'pre_reduccion': int(pre_reduccion),
            })
        else:
            resultados.append({
                'nombre': etiqueta,
                'algoritmo': 'AC3+FC',
                'tiempo_ms': 0.0,
                'tiempo_total_ms': round(tiempo_ac3_ms, 3),
                'tiempo_ac3_ms': round(tiempo_ac3_ms, 3),
                'nodos': 0,
                'exito': 0,
                'solucion_valida': 0,
                'limite_excedido': 0,
                'ac3_aplicado': 1,
                'pre_reduccion': int(pre_reduccion),
            })

    return resultados


def guardar_csv(resultados: List[Dict], csv_file: str = CSV_FILE) -> None:
    campos = [
        'nombre', 'algoritmo', 'tiempo_ms', 'tiempo_total_ms', 'nodos',
        'exito', 'solucion_valida', 'limite_excedido', 'ac3_aplicado', 'tiempo_ac3_ms', 'pre_reduccion'
    ]
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in resultados:
            w.writerow(r)
    print(f"\nCSV generado: {csv_file}")


def generar_graficas(csv_file: str = CSV_FILE, pre_reduccion: Optional[bool] = True) -> None:
    try:
        import csv
        import matplotlib.pyplot as plt
        from collections import defaultdict

        # Cargar CSV
        datos = defaultdict(lambda: {'BT': None, 'FC': None, 'AC3+BT': None, 'AC3+FC': None})
        with open(csv_file, 'r', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                nombre = row['nombre']
                alg = row['algoritmo']
                # Filtrar por modo pre_reduccion si se especifica
                if pre_reduccion is not None and int(row.get('pre_reduccion', 1)) != int(pre_reduccion):
                    continue
                datos[nombre][alg] = {
                    'tiempo_ms': float(row['tiempo_ms']),
                    'nodos': float(row['nodos']),
                }

        nombres = sorted(datos.keys())
        tiempos_bt = [datos[n]['BT']['tiempo_ms'] if datos[n]['BT'] else 0 for n in nombres]
        tiempos_fc = [datos[n]['FC']['tiempo_ms'] if datos[n]['FC'] else 0 for n in nombres]
        tiempos_ac3_bt = [datos[n]['AC3+BT']['tiempo_ms'] if datos[n]['AC3+BT'] else 0 for n in nombres]
        tiempos_ac3_fc = [datos[n]['AC3+FC']['tiempo_ms'] if datos[n]['AC3+FC'] else 0 for n in nombres]
        nodos_bt = [datos[n]['BT']['nodos'] if datos[n]['BT'] else 0 for n in nombres]
        nodos_fc = [datos[n]['FC']['nodos'] if datos[n]['FC'] else 0 for n in nombres]
        nodos_ac3_bt = [datos[n]['AC3+BT']['nodos'] if datos[n]['AC3+BT'] else 0 for n in nombres]
        nodos_ac3_fc = [datos[n]['AC3+FC']['nodos'] if datos[n]['AC3+FC'] else 0 for n in nombres]

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Tiempos
        x = range(len(nombres))
        width = 0.2
        axes[0].bar([i - 1.5*width for i in x], tiempos_bt, width=width, label='BT')
        axes[0].bar([i - 0.5*width for i in x], tiempos_fc, width=width, label='FC')
        axes[0].bar([i + 0.5*width for i in x], tiempos_ac3_bt, width=width, label='AC3+BT')
        axes[0].bar([i + 1.5*width for i in x], tiempos_ac3_fc, width=width, label='AC3+FC')
        axes[0].set_title('Tiempo de resolución por algoritmo (con y sin AC3)')
        axes[0].set_xlabel('Plantilla')
        axes[0].set_ylabel('Tiempo (ms)')
        axes[0].set_xticks(list(x))
        axes[0].set_xticklabels(nombres)
        axes[0].set_yscale('log')
        axes[0].legend()

        # Nodos
        axes[1].bar([i - 1.5*width for i in x], nodos_bt, width=width, label='BT')
        axes[1].bar([i - 0.5*width for i in x], nodos_fc, width=width, label='FC')
        axes[1].bar([i + 0.5*width for i in x], nodos_ac3_bt, width=width, label='AC3+BT')
        axes[1].bar([i + 1.5*width for i in x], nodos_ac3_fc, width=width, label='AC3+FC')
        axes[1].set_title('Nodos explorados por algoritmo (con y sin AC3)')
        axes[1].set_xlabel('Plantilla')
        axes[1].set_ylabel('Nodos explorados')
        axes[1].set_xticks(list(x))
        axes[1].set_xticklabels(nombres)
        axes[1].set_yscale('log')
        axes[1].legend()

        plt.tight_layout()
        out = 'graficas_resultados.png'
        plt.savefig(out, dpi=150)
        print(f"Gráficas guardadas en: {out}")
    except Exception as e:
        print("No se pudieron generar gráficas (¿matplotlib instalado?):", e)


def main():
    parser = argparse.ArgumentParser(description='Experimentos BT/FC con y sin AC3 (Sesión 7)')
    parser.add_argument('--max-nodos', type=int, default=1_000_000, help='Límite de nodos por ejecución')
    parser.add_argument('--sin-pre', action='store_true', help='Ejecutar también sin pre-reducción inicial de dominios')
    parser.add_argument('--ambos', action='store_true', help='Ejecutar ambos modos (con y sin pre-reducción)')
    parser.add_argument('--sin-graficas', action='store_true', help='No generar gráficas')
    parser.add_argument('--subset', nargs='*', help='Lista de ficheros de sudoku a ejecutar (p.ej. m1.txt m2.txt)')
    args = parser.parse_args()

    resultados = []
    if args.ambos:
        resultados.extend(ejecutar_experimentos(args.max_nodos, pre_reduccion=True, subset=args.subset))
        resultados.extend(ejecutar_experimentos(args.max_nodos, pre_reduccion=False, subset=args.subset))
    else:
        resultados.extend(ejecutar_experimentos(args.max_nodos, pre_reduccion=not args.sin_pre, subset=args.subset))

    guardar_csv(resultados)
    if not args.sin_graficas:
        # Por defecto graficamos el modo con pre-reducción (más cercano a clase)
        generar_graficas(CSV_FILE, pre_reduccion=True)


if __name__ == '__main__':
    main()
