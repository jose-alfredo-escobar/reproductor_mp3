"""Módulo del controlador encargado de la lógica de negocio en el MVC."""


class TurnosController:
    """Controlador puro del patrón MVC para la gestión de turnos."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista

    def agregar_turno(self):
        """Lee el input de la vista, altera el modelo y refresca la pantalla."""
        nombre = self.vista.ids.txt_nombre.text.strip()
        if nombre:
            self.modelo.agregar_turno(nombre)
            self.vista.ids.txt_nombre.text = ""
            self.actualizar_vista()

    def atender_turno(self):
        """Remueve el turno del modelo y actualiza los paneles de la vista."""
        nodo_atendido = self.modelo.atender_siguiente()

        if nodo_atendido:
            texto = f"#{nodo_atendido.numero}\n{nodo_atendido.nombre}"
            self.vista.ids.lbl_atendiendo.text = texto
        else:
            self.vista.ids.lbl_atendiendo.text = "NADIE EN COLA"

        self.actualizar_vista()

    def actualizar_vista(self):
        """Sincroniza los cambios del modelo con la interfaz."""
        lista_espera = self.modelo.obtener_lista_espera()

        if lista_espera:
            self.vista.ids.lbl_lista_espera.text = "\n".join(lista_espera)
        else:
            self.vista.ids.lbl_lista_espera.text = "No hay turnos en espera"