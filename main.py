"""Archivo principal para iniciar la ejecución del reproductor de música."""

from controller import MusicPlayerController

if __name__ == "__main__":
    app = MusicPlayerController()
    app.run()