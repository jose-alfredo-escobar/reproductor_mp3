"""Módulo que contiene la lógica de datos (lista doblemente enlazada),

la gestión de reproducción de audio y la persistencia en JSON.
"""

import json # herramienta de Python para leer y escribir archivos de texto estructurados, permite que las canciones se guarden al cerrar la app
import os # herramienta para hablar con el SO (buscar carpetas, revisar si archivos existen, etc)
import pygame # libreria externa que da superpoderes a Python para reproducir sonidos y controlar el audio

pygame.mixer.init() # inicializamos el mezclador interno de pygame. Es como encender el amplificador de sonido antes de conectar los parlantes


class SongNode:
    """Representa una canción individual (Nodo de la lista doblemente enlazada)."""

    def __init__(self, title: str, artist: str, file_path: str):
        self.title = title
        self.artist = artist
        self.file_path = file_path
        self.duration = 180.0  # Duración por defecto en segundos

        try:     # intenta hacer esto
            sound = pygame.mixer.Sound(file_path) # leemos el archivo MP3
            self.duration = sound.get_length()  # calculamos su duracion exacta y actualizamos el atributo de ese objeto
        except Exception:   # si falla, no detener el programa, solo continuar pass
            pass

        self.next = None    # Apunta al nodo siguiente
        self.prev = None    # Apunta al nodo anterior


class PlaylistModel:
    """Gestiona la lista enlazada, la reproducción y la persistencia de datos."""

    def __init__(self, json_file: str = "playlist.json"):
        self.head = None
        self.tail = None
        self.current = None
        self.json_file = json_file

    def add_song(self, title: str, artist: str, file_path: str) -> SongNode:
        """Agrega una nueva canción al final de la lista enlazada."""
        new_song = SongNode(title, artist, file_path)

        if not self.head:
            self.head = new_song
            self.tail = new_song
            self.current = new_song
        else:
            self.tail.next = new_song
            new_song.prev = self.tail
            self.tail = new_song

        return new_song

    def go_to_index(self, target_index: int) -> bool:
        """Mueve el puntero current al nodo correspondiente según el índice."""
        current_node = self.head
        idx = 0
        while current_node and idx < target_index:
            current_node = current_node.next
            idx += 1

        if current_node:
            self.current = current_node
            self.play_current()
            return True
        return False

    def seek_position(self, position_seconds: float):
        """Salta a un segundo específico recargando y reproduciendo desde esa posición."""
        if self.current:
            try:
                pygame.mixer.music.load(self.current.file_path)
                pygame.mixer.music.play(start=position_seconds)
            except pygame.error as e:
                print(f"No se pudo realizar el salto de posición: {e}")

    def set_volume(self, volume: float):
        """Ajusta el volumen de reproducción entre 0.0 y 1.0."""
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception as e:
            print(f"No se pudo ajustar el volumen: {e}")

    def save_playlist(self):
        """Guarda las rutas de todas las canciones actuales en un archivo JSON."""
        paths = []
        current_node = self.head
        while current_node:
            paths.append(current_node.file_path)
            current_node = current_node.next

        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(paths, f, indent=4)
        except Exception as e:
            print(f"Error al guardar la playlist: {e}")

    def load_playlist(self, directory_path: str = "music"):
        """Carga la playlist desde el JSON si existe; si no, escanea la carpeta."""
        loaded_from_json = False

        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    paths = json.load(f)
                    for file_path in paths:
                        if os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            base_name = os.path.splitext(filename)[0]
                            if " - " in base_name:
                                artist, title = base_name.split(" - ", 1)
                            else:
                                artist, title = "Desconocido", base_name
                            self.add_song(title, artist, file_path)
                            loaded_from_json = True
            except Exception as e:
                print(f"Error al leer el archivo JSON: {e}")

        if not loaded_from_json:
            self.load_from_directory(directory_path)

    def load_from_directory(self, directory_path: str):
        """Escanea una carpeta local y carga automáticamente todos los MP3."""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            return

        for filename in os.listdir(directory_path):
            if filename.lower().endswith(".mp3"):
                file_path = os.path.join(directory_path, filename)
                base_name = os.path.splitext(filename)[0]
                
                if " - " in base_name:
                    artist, title = base_name.split(" - ", 1)
                else:
                    artist, title = "Desconocido", base_name

                self.add_song(title, artist, file_path)
        
        self.save_playlist()

    def play_current(self) -> bool:
        """Reproduce la canción actual utilizando Pygame."""
        if self.current:
            try:
                pygame.mixer.music.load(self.current.file_path)
                pygame.mixer.music.play()
                return True
            except pygame.error as e:
                print(f"Error al reproducir audio: {e}")
        return False

    def pause_audio(self):
        """Pausa la reproducción actual."""
        pygame.mixer.music.pause()

    def unpause_audio(self):
        """Reanuda la reproducción pausada."""
        pygame.mixer.music.unpause()

    def stop_audio(self):
        """Detiene la música por completo."""
        pygame.mixer.music.stop()

    def next_song(self) -> bool:
        """Avanza al siguiente nodo en la lista."""
        if self.current and self.current.next:
            self.current = self.current.next
            self.play_current()
            return True
        return False

    def previous_song(self) -> bool:
        """Retrocede al nodo anterior en la lista."""
        if self.current and self.current.prev:
            self.current = self.current.prev
            self.play_current()
            return True
        return False

    def get_songs_list(self) -> list:
        """Retorna una lista con la información de todas las canciones."""
        songs = []
        current_node = self.head
        while current_node:
            songs.append((current_node.title, current_node.artist))
            current_node = current_node.next
        return songs

    def remove_song_at_index(self, index: int) -> bool:
        """Elimina una canción según su índice reparando los enlaces de la lista."""
        # 1. Buscar el nodo que corresponde a ese índice
        target_node = self.head
        idx = 0
        while target_node and idx < index:
            target_node = target_node.next
            idx += 1

        # 2. Si el índice no existe en la lista, salimos
        if not target_node:
            return False

        # 3. Gestión especial si borramos la canción actual (reproduciéndose)
        if target_node == self.current:
            if target_node.next:
                self.current = target_node.next
                self.play_current()
            elif target_node.prev:
                self.current = target_node.prev
                self.play_current()
            else:
                self.current = None
                self.stop_audio()

        # 4. Modificar los enlaces de los nodos de los lados (Cirugía)
        if target_node.prev:
            target_node.prev.next = target_node.next
        else:
            self.head = target_node.next

        if target_node.next:
            target_node.next.prev = target_node.prev
        else:
            self.tail = target_node.prev

        # 5. Guardar la lista actualizada en el JSON
        self.save_playlist()
        return True