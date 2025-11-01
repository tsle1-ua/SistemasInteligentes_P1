"""
Modelado del Sudoku como problema de satisfacción de restricciones (CSP)
=======================================================================

Esta clase representa el problema de Sudoku como un CSP con:
- 81 variables (una por celda)
- 27 restricciones (9 filas + 9 columnas + 9 submatrices 3x3)
- Dominios de 1-9 para cada variable

Autor: [Tu nombre]
Curso: 2024-25
Asignatura: Sistemas Inteligentes
"""

import copy
from variable import Variable

class SudokuCSP:
    """
    Clase que representa el problema de satisfacción de restricciones del Sudoku
    """
    
    def __init__(self, tablero, dominios=None):
        """
        Inicializa el CSP del Sudoku
        
        Args:
            tablero (Tablero): Objeto tablero con la configuración inicial
            dominios (list[list[list[str]]] | None): Matriz 9x9 con los dominios
                para cada celda (solo usado para celdas no fijas). Si es None,
                se inicializan dominios por defecto y se aplica una reducción
                inicial en base a los valores fijos en el tablero.
        """
        self.tablero = tablero
        self.variables = []
        self.restricciones = []
        self.inicializar_variables()
        self.generar_restricciones()
        # Asignar vecinos (conjunto de celdas relacionadas) a cada variable
        self._asignar_vecinos()
        # Aplicar dominios externos si se proporcionan; en caso contrario aplicar reducción inicial
        if dominios is not None:
            self._aplicar_dominios_iniciales(dominios)
        else:
            # Reducción inicial de dominios con los valores fijos ya presentes
            self._reduccion_inicial_dominios()
    
    def inicializar_variables(self):
        """
        Crea las variables del CSP basadas en el tablero
        """
        self.variables = []
        for fila in range(9):
            fila_variables = []
            for columna in range(9):
                valor = self.tablero.getCelda(fila, columna)
                variable = Variable(fila, columna, valor)
                fila_variables.append(variable)
            self.variables.append(fila_variables)
    
    def generar_restricciones(self):
        """
        Genera todas las restricciones del Sudoku:
        - Fila: no repetir números en la misma fila
        - Columna: no repetir números en la misma columna
        - Submatriz 3x3: no repetir números en la misma submatriz
        """
        self.restricciones = []
        # Filas
        for fila in range(9):
            self.restricciones.append([(fila, c) for c in range(9)])
        # Columnas
        for columna in range(9):
            self.restricciones.append([(f, columna) for f in range(9)])
        # Bloques 3x3
        for bf in range(3):
            for bc in range(3):
                self.restricciones.append([
                    (f, c)
                    for f in range(bf*3, bf*3+3)
                    for c in range(bc*3, bc*3+3)
                ])

    def _aplicar_dominios_iniciales(self, dominios):
        """
        Aplica una matriz de dominios a las variables no fijas.

        Args:
            dominios (list[list[list[str]]]): Matriz 9x9 con listas de valores permitidos por celda.
        """
        if len(dominios) != 9 or any(len(fila) != 9 for fila in dominios):
            raise ValueError("La matriz de dominios debe ser 9x9")
        for f in range(9):
            for c in range(9):
                v = self.variables[f][c]
                if v.es_fija:
                    # Mantener el dominio consistente con el valor fijo
                    v.dominio = [v.valor]
                else:
                    dom = dominios[f][c][:] if dominios[f][c] is not None else v.dominio
                    # Asegurar que el dominio no sea vacío; si está vacío se deja como está para que el algoritmo detecte inconsistencia
                    v.dominio = dom if isinstance(dom, list) else v.dominio

    def _asignar_vecinos(self):
        """
        Asigna el conjunto de celdas relacionadas (vecinos) a cada celda del Sudoku.
        Los vecinos son todas las celdas en la misma fila, columna y bloque 3x3.
        """
        for f in range(9):
            for c in range(9):
                vecinos = set()
                # Fila y columna
                for cc in range(9):
                    if cc != c:
                        vecinos.add((f, cc))
                for ff in range(9):
                    if ff != f:
                        vecinos.add((ff, c))
                # Bloque
                bf, bc = f // 3, c // 3
                for ff in range(bf*3, bf*3+3):
                    for cc in range(bc*3, bc*3+3):
                        if ff != f or cc != c:
                            vecinos.add((ff, cc))
                self.variables[f][c].set_vecinos(vecinos)

    def _reduccion_inicial_dominios(self):
        """
        Reduce dominios de variables no fijas usando los valores fijos ya colocados.
        Elimina de los dominios los valores que ya están en la misma fila, columna o bloque 3x3.
        """
        todos = set(['1','2','3','4','5','6','7','8','9'])
        for f in range(9):
            for c in range(9):
                v = self.variables[f][c]
                if not v.es_fija:
                    usados = set()
                    # fila
                    usados.update(self.variables[f][cc].valor for cc in range(9) if self.variables[f][cc].esta_asignada())
                    # columna
                    usados.update(self.variables[ff][c].valor for ff in range(9) if self.variables[ff][c].esta_asignada())
                    # bloque
                    bf, bc = f // 3, c // 3
                    for ff in range(bf*3, bf*3+3):
                        for cc in range(bc*3, bc*3+3):
                            if self.variables[ff][cc].esta_asignada():
                                usados.add(self.variables[ff][cc].valor)
                    nuevo_dom = sorted(list(todos - usados))
                    v.dominio = nuevo_dom if nuevo_dom else v.dominio

    def vecinos(self, fila, columna):
        """
        Devuelve el conjunto de vecinos (celdas relacionadas) de una celda específica.
        
        Args:
            fila (int): Fila de la celda
            columna (int): Columna de la celda
            
        Returns:
            set: Conjunto de tuplas (fila, columna) de las celdas vecinas
        """
        return self.variables[fila][columna].get_vecinos()
    
    def obtener_variables_relacionadas(self, fila, columna):
        """
        Obtiene todas las variables que están relacionadas con la variable dada
        por las restricciones (misma fila, columna o submatriz)
        
        Args:
            fila (int): Fila de la variable
            columna (int): Columna de la variable
            
        Returns:
            list: Lista de tuplas (fila, columna) de variables relacionadas
        """
        return list(self.vecinos(fila, columna))

    def es_consistente(self, fila, columna, valor):
        """
        Verifica si asignar un valor a una variable es consistente
        con las restricciones actuales
        
        Args:
            fila (int): Fila de la variable
            columna (int): Columna de la variable
            valor (str): Valor a verificar
            
        Returns:
            bool: True si la asignación es consistente
        """
        # Verificar fila
        for c in range(9):
            if c != columna and self.variables[fila][c].valor == valor:
                return False
        
        # Verificar columna
        for f in range(9):
            if f != fila and self.variables[f][columna].valor == valor:
                return False
        
        # Verificar submatriz 3x3
        bloque_fila = fila // 3
        bloque_columna = columna // 3
        for f in range(bloque_fila * 3, (bloque_fila + 1) * 3):
            for c in range(bloque_columna * 3, (bloque_columna + 1) * 3):
                if (f != fila or c != columna) and self.variables[f][c].valor == valor:
                    return False
        
        return True
    
    def obtener_variable_no_asignada(self):
        """
        Obtiene la primera variable no asignada usando la heurística MRV
        (Minimum Remaining Values)
        
        Returns:
            tuple: (fila, columna) de la variable no asignada, o None si todas están asignadas
        """
        variable_elegida = None
        min_dominio = 10  # Mayor que el máximo posible
        
        for fila in range(9):
            for columna in range(9):
                variable = self.variables[fila][columna]
                if not variable.esta_asignada():
                    if variable.tamano_dominio() < min_dominio:
                        min_dominio = variable.tamano_dominio()
                        variable_elegida = (fila, columna)
        
        return variable_elegida
    
    def esta_completo(self):
        """
        Verifica si todas las variables están asignadas
        
        Returns:
            bool: True si el CSP está completamente resuelto
        """
        for fila in range(9):
            for columna in range(9):
                if not self.variables[fila][columna].esta_asignada():
                    return False
        return True
    
    def actualizar_tablero(self):
        """
        Actualiza el objeto tablero con los valores actuales de las variables
        """
        for fila in range(9):
            for columna in range(9):
                valor = self.variables[fila][columna].valor
                self.tablero.setCelda(fila, columna, valor)
    
    def imprimir_dominios(self):
        """
        Imprime los dominios de todas las variables para debugging
        """
        print("Dominios de las variables:")
        for fila in range(9):
            for columna in range(9):
                variable = self.variables[fila][columna]
                print(f"({fila},{columna}): {variable.dominio}")

    def snapshot_dominios(self):
        """
        Devuelve una copia profunda de los dominios actuales (9x9 listas).

        Returns:
            list[list[list[str]]]: Matriz de dominios.
        """
        matriz = []
        for f in range(9):
            fila = []
            for c in range(9):
                fila.append(self.variables[f][c].obtener_dominio())
            matriz.append(fila)
        return matriz