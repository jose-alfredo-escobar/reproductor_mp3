"""Archivo principal que inicializa y coordina la aplicación."""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from controller import TurnosController
from model import ListaTurnos


class GestionTurnosWidget(BoxLayout):
    """Contenedor de la vista raíz de la aplicación."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controlador = None

    def vincular_controlador(self, controlador):
        """Asigna la referencia del controlador."""
        self.controlador = controlador


class TurnosApp(App):
    """Clase encargada del ciclo de vida de la aplicación Kivy."""

    def build(self):
        self.title = "Gestor de Turnos (MVC Desacoplado)"
        Builder.load_file("vista.kv")

        # Inyección de dependencias
        modelo = ListaTurnos()
        vista = GestionTurnosWidget()
        controlador = TurnosController(modelo, vista)

        vista.vincular_controlador(controlador)

        return vista


if __name__ == "__main__":
    TurnosApp().run()