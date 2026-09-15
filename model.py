"""Módulo del modelo que implementa la estructura de datos."""


class NodoTurno:
    """Representa un nodo individual en la lista enlazada de turnos."""

    def __init__(self, numero: int, nombre: str):
        self.numero = numero
        self.nombre = nombre
        self.siguiente = None


class ListaTurnos:
    """Implementación de una lista enlazada simple para gestionar turnos."""

    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.contador_turnos = 0

    def agregar_turno(self, nombre: str) -> NodoTurno:
        """Inserta un nuevo turno al final de la lista."""
        self.contador_turnos += 1
        nuevo_nodo = NodoTurno(self.contador_turnos, nombre.upper())

        if not self.cabeza:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo

        return nuevo_nodo

    def atender_siguiente(self) -> NodoTurno | None:
        """Elimina y retorna el primer turno de la lista (el más antiguo)."""
        if not self.cabeza:
            return None

        nodo_atendido = self.cabeza
        self.cabeza = self.cabeza.siguiente

        if not self.cabeza:
            self.cola = None

        return nodo_atendido

    def obtener_lista_espera(self) -> list[str]:
        """Recorre la lista enlazada y devuelve los turnos en una lista."""
        espera = []
        actual = self.cabeza
        while actual:
            espera.append(f"#{actual.numero} - {actual.nombre}")
            actual = actual.siguiente
        return espera