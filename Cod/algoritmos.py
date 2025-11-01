"""
Algoritmos de satisfacción de restricciones para resolver Sudoku
================================================================

Este módulo implementa tres algoritmos principales:
1. Backtracking: Búsqueda con retroceso
2. Forward Checking: Propagación de restricciones hacia adelante  
3. AC3: Consistencia de arco para reducción de dominios

Autor: [Tu nombre]
Curso: 2024-25
Asignatura: Sistemas Inteligentes
"""

import copy
from sudoku_csp import SudokuCSP

# Flags de traza (para entrega: dejar dominios de AC3 opcionalmente visibles)
DEBUG_TRAZA_AC3_DOMINIOS = False

def backtracking(tablero, dominios=None):
    """
    Algoritmo de backtracking para resolver Sudoku
    
    Args:
        tablero (Tablero): Tablero inicial del Sudoku
        
    Returns:
        bool: True si encuentra solución, False en caso contrario
    """
    csp = SudokuCSP(tablero, dominios=dominios)
    
    def backtrack_recursivo():
        # Si está completo, hemos encontrado la solución
        if csp.esta_completo():
            return True
        
        # Seleccionar variable no asignada
        pos = csp.obtener_variable_no_asignada()
        if pos is None:
            return True
        
        fila, columna = pos
        variable = csp.variables[fila][columna]
        
        # Probar cada valor en el dominio
        for valor in variable.obtener_dominio():
            if csp.es_consistente(fila, columna, valor):
                # Asignar valor
                variable.asignar_valor(valor)
                
                # Llamada recursiva
                if backtrack_recursivo():
                    return True
                
                # Deshacer asignación (backtrack)
                variable.desasignar()
        
        return False
    
    # Ejecutar algoritmo
    if backtrack_recursivo():
        csp.actualizar_tablero()
        return True
    return False


def backtracking_stats(tablero, max_nodos=None, dominios=None):
    """
    Variante de Backtracking que devuelve métricas.

    Args:
        tablero (Tablero): Tablero inicial del Sudoku (no se modifica).
        max_nodos (int|None): Límite de nodos (llamadas recursivas). Si None, sin límite.

    Returns:
        dict: {
            'exito': bool,
            'nodos': int,
            'limite_excedido': bool,
            'tablero': Tablero (copia resuelta si exito=True)
        }
    """
    tablero_copia = copy.deepcopy(tablero)
    csp = SudokuCSP(tablero_copia, dominios=dominios)

    nodos = 0
    limite_excedido = False

    def backtrack_recursivo():
        nonlocal nodos, limite_excedido
        nodos += 1
        if max_nodos is not None and nodos > max_nodos:
            limite_excedido = True
            return False

        if csp.esta_completo():
            return True

        pos = csp.obtener_variable_no_asignada()
        if pos is None:
            return True

        fila, columna = pos
        variable = csp.variables[fila][columna]

        for valor in variable.obtener_dominio():
            if csp.es_consistente(fila, columna, valor):
                variable.asignar_valor(valor)
                if backtrack_recursivo():
                    return True
                variable.desasignar()
        return False

    exito = backtrack_recursivo()
    if exito:
        csp.actualizar_tablero()
    return {
        'exito': exito,
        'nodos': nodos,
        'limite_excedido': limite_excedido,
        'tablero': tablero_copia if exito else None,
    }


def forward_checking(tablero, dominios=None):
    """
    Algoritmo de Forward Checking para resolver Sudoku
    
    Args:
        tablero (Tablero): Tablero inicial del Sudoku
        
    Returns:
        bool: True si encuentra solución, False en caso contrario
    """
    csp = SudokuCSP(tablero, dominios=dominios)
    
    def propagar_restricciones(fila, columna, valor):
        """
        Propaga las restricciones eliminando el valor de los dominios
        de las variables relacionadas
        
        Returns:
            list: Lista de cambios realizados para poder revertirlos
        """
        cambios = []
        relacionadas = csp.obtener_variables_relacionadas(fila, columna)
        
        for f, c in relacionadas:
            variable_relacionada = csp.variables[f][c]
            if not variable_relacionada.esta_asignada():
                if variable_relacionada.eliminar_del_dominio(valor):
                    cambios.append((f, c, valor))
        
        return cambios
    
    def revertir_cambios(cambios):
        """
        Revierte los cambios realizados en la propagación
        """
        for fila, columna, valor in cambios:
            csp.variables[fila][columna].restaurar_en_dominio(valor)
    
    def verificar_dominios_vacios():
        """
        Verifica si alguna variable no asignada tiene dominio vacío
        """
        for fila in range(9):
            for columna in range(9):
                variable = csp.variables[fila][columna]
                if not variable.esta_asignada() and variable.dominio_vacio():
                    return True
        return False
    
    def forward_check_recursivo():
        # Si está completo, hemos encontrado la solución
        if csp.esta_completo():
            return True
        
        # Seleccionar variable no asignada (heurística MRV)
        pos = csp.obtener_variable_no_asignada()
        if pos is None:
            return True
        
        fila, columna = pos
        variable = csp.variables[fila][columna]
        
        # Probar cada valor en el dominio
        for valor in variable.obtener_dominio()[:]:  # Copia para evitar modificaciones durante iteración
            if csp.es_consistente(fila, columna, valor):
                # Asignar valor
                variable.asignar_valor(valor)
                
                # Propagar restricciones (forward checking)
                cambios = propagar_restricciones(fila, columna, valor)
                
                # Verificar si algún dominio se quedó vacío
                if not verificar_dominios_vacios():
                    # Llamada recursiva
                    if forward_check_recursivo():
                        return True
                
                # Deshacer asignación y revertir cambios
                variable.desasignar()
                revertir_cambios(cambios)
        
        return False
    
    # Ejecutar algoritmo
    if forward_check_recursivo():
        csp.actualizar_tablero()
        return True
    return False


def forward_checking_stats(tablero, max_nodos=None, dominios=None):
    """
    Variante de Forward Checking que devuelve métricas.

    Args:
        tablero (Tablero): Tablero inicial del Sudoku (no se modifica).
        max_nodos (int|None): Límite de nodos (llamadas recursivas). Si None, sin límite.

    Returns:
        dict: {
            'exito': bool,
            'nodos': int,
            'limite_excedido': bool,
            'tablero': Tablero (copia resuelta si exito=True)
        }
    """
    tablero_copia = copy.deepcopy(tablero)
    csp = SudokuCSP(tablero_copia, dominios=dominios)

    nodos = 0
    limite_excedido = False

    def propagar_restricciones(fila, columna, valor):
        cambios = []
        relacionadas = csp.obtener_variables_relacionadas(fila, columna)
        for f, c in relacionadas:
            variable_relacionada = csp.variables[f][c]
            if not variable_relacionada.esta_asignada():
                if variable_relacionada.eliminar_del_dominio(valor):
                    cambios.append((f, c, valor))
        return cambios

    def revertir_cambios(cambios):
        for fila, columna, valor in cambios:
            csp.variables[fila][columna].restaurar_en_dominio(valor)

    def verificar_dominios_vacios():
        for fila in range(9):
            for columna in range(9):
                variable = csp.variables[fila][columna]
                if not variable.esta_asignada() and variable.dominio_vacio():
                    return True
        return False

    def forward_check_recursivo():
        nonlocal nodos, limite_excedido
        nodos += 1
        if max_nodos is not None and nodos > max_nodos:
            limite_excedido = True
            return False

        if csp.esta_completo():
            return True

        pos = csp.obtener_variable_no_asignada()
        if pos is None:
            return True

        fila, columna = pos
        variable = csp.variables[fila][columna]

        for valor in variable.obtener_dominio()[:]:
            if csp.es_consistente(fila, columna, valor):
                variable.asignar_valor(valor)
                cambios = propagar_restricciones(fila, columna, valor)
                if not verificar_dominios_vacios():
                    if forward_check_recursivo():
                        return True
                variable.desasignar()
                revertir_cambios(cambios)
        return False

    exito = forward_check_recursivo()
    if exito:
        csp.actualizar_tablero()
    return {
        'exito': exito,
        'nodos': nodos,
        'limite_excedido': limite_excedido,
        'tablero': tablero_copia if exito else None,
    }


def ac3(tablero, dominios=None):
    """
    Algoritmo AC3 (Arc Consistency 3) para reducir dominios
    
    Args:
        tablero (Tablero): Tablero inicial del Sudoku
        
    Returns:
        bool: True si el problema es consistente, False si es inconsistente
    """
    csp = SudokuCSP(tablero, dominios=dominios)
    dominios_antes = csp.snapshot_dominios()
    
    def obtener_arcos():
        """
        Genera todos los arcos (restricciones binarias) del problema
        
        Returns:
            list: Lista de arcos como tuplas ((fila1, col1), (fila2, col2))
        """
        arcos = []
        
        for fila in range(9):
            for columna in range(9):
                relacionadas = csp.obtener_variables_relacionadas(fila, columna)
                for f_rel, c_rel in relacionadas:
                    arcos.append(((fila, columna), (f_rel, c_rel)))
        
        return arcos
    
    def revisar_arco(xi, xj):
        """
        Revisa si el arco (xi, xj) es consistente
        
        Args:
            xi (tuple): Coordenadas de la primera variable
            xj (tuple): Coordenadas de la segunda variable
            
        Returns:
            bool: True si se modificó el dominio de xi
        """
        fi, ci = xi
        fj, cj = xj
        
        variable_i = csp.variables[fi][ci]
        variable_j = csp.variables[fj][cj]
        
        # Consistencia por desigualdad: para cada valor v en Di debe existir
        # algún u en Dj tal que u != v. Si Dj == {v}, entonces v no está soportado.
        cambiado = False
        if not variable_i.es_fija:
            di = variable_i.obtener_dominio()
            dj = variable_j.obtener_dominio()
            # Caso típico en Sudoku: si Dj es singleton y coincide con v, eliminar v de Di
            if len(dj) == 1:
                unico = dj[0]
                if unico in di:
                    cambiado = variable_i.eliminar_del_dominio(unico) or cambiado
        return cambiado
        
        return False
    
    # Algoritmo AC3
    cola_arcos = obtener_arcos()
    
    while cola_arcos:
        xi, xj = cola_arcos.pop(0)
        
        if revisar_arco(xi, xj):
            # Si el dominio de xi está vacío, el problema es inconsistente
            fi, ci = xi
            if csp.variables[fi][ci].dominio_vacio() and not csp.variables[fi][ci].esta_asignada():
                # Inconsistencia detectada
                return {
                    'consistente': False,
                    'dominios_antes': dominios_antes,
                    'dominios_despues': csp.snapshot_dominios(),
                    'resueltas': 0,
                }
            
            # Añadir todos los arcos (xk, xi) donde xk es vecino de xi
            relacionadas = csp.obtener_variables_relacionadas(fi, ci)
            for fk, ck in relacionadas:
                if (fk, ck) != xj:  # No añadir el arco que acabamos de revisar
                    cola_arcos.append(((fk, ck), xi))
    
    # Actualizar el tablero con los dominios reducidos
    # Solo para variables con dominio de tamaño 1
    variables_resueltas = 0
    for fila in range(9):
        for columna in range(9):
            variable = csp.variables[fila][columna]
            if not variable.esta_asignada() and variable.tamano_dominio() == 1:
                nuevo_valor = variable.dominio[0]
                variable.asignar_valor(nuevo_valor)
                tablero.setCelda(fila, columna, nuevo_valor)
                variables_resueltas += 1
    dominios_despues = csp.snapshot_dominios()

    # Imprimir cambios de dominios (solo celdas que cambiaron) si está habilitado
    if DEBUG_TRAZA_AC3_DOMINIOS:
        print("Dominios antes y después de AC3 (solo cambios):")
        for f in range(9):
            for c in range(9):
                antes = dominios_antes[f][c]
                despues = dominios_despues[f][c]
                if antes != despues:
                    print(f"({f},{c}) {antes} -> {despues}")
    print(f"AC3 completado: {variables_resueltas} variables resueltas mediante reducción de dominios")

    return {
        'consistente': True,
        'dominios_antes': dominios_antes,
        'dominios_despues': dominios_despues,
        'resueltas': variables_resueltas,
    }


def resolver_con_ac3_y_backtracking(tablero):
    """
    Aplica AC3 primero y luego Backtracking
    
    Args:
        tablero (Tablero): Tablero inicial del Sudoku
        
    Returns:
        bool: True si encuentra solución, False en caso contrario
    """
    # Crear copia del tablero para AC3
    tablero_copia = copy.deepcopy(tablero)
    
    # Aplicar AC3
    res_ac3 = ac3(tablero_copia)
    if not res_ac3['consistente']:
        print("El problema es inconsistente después de AC3")
        return False
    
    # Aplicar Backtracking con dominios reducidos
    return backtracking(tablero_copia, dominios=res_ac3['dominios_despues'])


def resolver_con_ac3_y_forward_checking(tablero):
    """
    Aplica AC3 primero y luego Forward Checking
    
    Args:
        tablero (Tablero): Tablero inicial del Sudoku
        
    Returns:
        bool: True si encuentra solución, False en caso contrario
    """
    # Crear copia del tablero para AC3
    tablero_copia = copy.deepcopy(tablero)
    
    # Aplicar AC3
    res_ac3 = ac3(tablero_copia)
    if not res_ac3['consistente']:
        print("El problema es inconsistente después de AC3")
        return False
    
    # Aplicar Forward Checking con dominios reducidos
    return forward_checking(tablero_copia, dominios=res_ac3['dominios_despues'])