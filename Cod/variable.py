"""
Clase Variable para problemas de satisfacción de restricciones
=============================================================

Implementa una variable del CSP que representa cada celda del Sudoku.
Maneja dominios, asignaciones y restricciones.

Autor: [Tu nombre]
Curso: 2024-25
Asignatura: Sistemas Inteligentes
"""

# Clase Variable para representar cada celda del Sudoku
class Variable:
    def __init__(self, fila, columna, valor='0', dominio=None):
        """
        Inicializa una variable del CSP
        
        Args:
            fila (int): Fila de la celda en el tablero
            columna (int): Columna de la celda en el tablero
            valor (str): Valor actual de la celda ('0' si está vacía)
            dominio (list): Lista de valores posibles para esta variable
        """
        self.fila = fila
        self.columna = columna
        self.valor = valor
        self.es_fija = valor != '0'  # True si la celda tiene un valor inicial
        # Vecinos (coordenadas) restringidos con esta variable (fila, columna, bloque)
        self.vecinos = []
        
        # Inicializar el dominio
        if dominio is None:
            if self.es_fija:
                self.dominio = [valor]
            else:
                self.dominio = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        else:
            self.dominio = dominio[:]
    
    def esta_asignada(self):
        """
        Verifica si la variable tiene un valor asignado
        
        Returns:
            bool: True si la variable está asignada
        """
        return self.valor != '0'
    
    def asignar_valor(self, valor):
        """
        Asigna un valor a la variable
        
        Args:
            valor (str): Valor a asignar
        """
        if not self.es_fija:  # Solo asignar si no es una celda fija
            self.valor = valor
    
    def desasignar(self):
        """
        Desasigna el valor de la variable (la pone en '0')
        """
        if not self.es_fija:  # Solo desasignar si no es una celda fija
            self.valor = '0'
    
    def eliminar_del_dominio(self, valor):
        """
        Elimina un valor del dominio si está presente
        
        Args:
            valor (str): Valor a eliminar del dominio
            
        Returns:
            bool: True si el valor fue eliminado, False si no estaba
        """
        if valor in self.dominio and not self.es_fija:
            self.dominio.remove(valor)
            return True
        return False
    
    def restaurar_en_dominio(self, valor):
        """
        Restaura un valor al dominio si no está presente
        
        Args:
            valor (str): Valor a restaurar en el dominio
        """
        if valor not in self.dominio and not self.es_fija:
            self.dominio.append(valor)
            # Mantener el dominio ordenado
            self.dominio.sort()
    
    def dominio_vacio(self):
        """
        Verifica si el dominio está vacío
        
        Returns:
            bool: True si el dominio está vacío
        """
        return len(self.dominio) == 0
    
    def tamano_dominio(self):
        """
        Retorna el tamaño del dominio
        
        Returns:
            int: Número de valores en el dominio
        """
        return len(self.dominio)
    
    def obtener_dominio(self):
        """
        Retorna una copia del dominio
        
        Returns:
            list: Copia del dominio actual
        """
        return self.dominio[:]
    
    # Nuevo: helpers para vecinos
    def set_vecinos(self, lista_vecinos):
        self.vecinos = list(lista_vecinos)
    
    def get_vecinos(self):
        return self.vecinos
    
    def __str__(self):
        """
        Representación en string de la variable
        """
        return f"Variable({self.fila},{self.columna}) = {self.valor}, dominio: {self.dominio}"
    
    def __repr__(self):
        return self.__str__()