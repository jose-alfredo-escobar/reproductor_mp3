"""Módulo controlador que gestiona la comunicación entre el Modelo y la Vista."""

import os
import pygame
from tkinter import filedialog, messagebox
from model import PlaylistModel
from view import MusicPlayerView


class MusicPlayerController:
    """Controlador principal de la aplicación."""

    def __init__(self):
        self.model = PlaylistModel()
        self.view = MusicPlayerView(self)
        self.current_index = 0
        
        self.is_playing = False
        self.is_paused = False
        self.seek_offset = 0.0
        self.is_seeking = False
        self.volume_visible = False  # Estado del menú flotante de volumen

        # Inicializar el volumen al 70% por defecto
        self.model.set_volume(0.7)

        self._load_initial_playlist()
        self._update_progress_loop()

    def run(self):
        """Inicia la ejecución de la interfaz gráfica."""
        self.view.mainloop()

    def _load_initial_playlist(self):
        """Carga la lista de reproducción al arrancar la app."""
        self.model.load_playlist("music")
        
        if self.model.head:
            self.current_index = 0
            self._refresh_view()
            self._update_status()

    def _update_progress_loop(self):
        """Actualiza la barra de progreso solo si el usuario no está interactuando con ella."""
        if self.is_playing and pygame.mixer.music.get_busy() and not self.is_seeking:
            current_ms = pygame.mixer.music.get_pos()
            if current_ms >= 0:
                current_sec = self.seek_offset + (current_ms / 1000.0)
                if self.model.current and current_sec <= self.model.current.duration:
                    self.view.progress_slider.set(current_sec)

        self.view.after(1000, self._update_progress_loop)

    def handle_seek_start(self, event):
        """Indica que el usuario empezó a interactuar con la barra."""
        self.is_seeking = True

    def handle_seek_release(self, event):
        """Aplica el salto de audio y reactiva la actualización automática al soltar la barra."""
        self.is_seeking = False
        if self.model.current and self.is_playing:
            seek_seconds = self.view.progress_slider.get()
            self.seek_offset = seek_seconds
            self.model.seek_position(seek_seconds)

    def toggle_volume_slider(self):
        """Muestra u oculta la barrita flotante de volumen al hacer clic en el altavoz."""
        self.volume_visible = not self.volume_visible
        self.view.toggle_volume_popup(self.volume_visible)

    def handle_volume_change(self, value):
        """Ajusta el volumen del reproductor en tiempo real."""
        volume = float(value)
        self.model.set_volume(volume)

    def handle_add_song(self):
        """Maneja la selección manual de un MP3 y guarda el estado en JSON."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Canción",
            filetypes=[("Archivos MP3", "*.mp3"), ("Todos los archivos", "*.*")],
        )

        if file_path:
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            if " - " in base_name:
                artist, title = base_name.split(" - ", 1)
            else:
                artist, title = "Desconocido", base_name

            self.model.add_song(title, artist, file_path)
            self.model.save_playlist()
            self._refresh_view()

            if not self.model.current or self.model.head == self.model.tail:
                self.current_index = 0
                self._update_status()

    def handle_select_song(self, index: int):
        """Reproduce directamente la canción seleccionada reiniciando el offset."""
        self.seek_offset = 0.0
        self.is_seeking = False
        if self.model.go_to_index(index):
            self.current_index = index
            self.is_playing = True
            self.is_paused = False
            self.view.btn_play.configure(text="⏸ Pausa")
            self._refresh_view()
            self._update_status()

    def handle_delete_current_song(self):
        """Elimina la canción seleccionada actualmente en el reproductor usando el basurero global."""
        if not self.model.current or self.current_index < 0:
            messagebox.showwarning(
                "Advertencia", "No hay ninguna canción seleccionada para eliminar."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Estás seguro de que deseas eliminar '{self.model.current.title}' de la playlist?"
        )
        if not confirm:
            return

        target_index = self.current_index

        # Llama a la lógica de punteros del modelo pasándole el índice
        success = self.model.remove_song_at_index(target_index)
        
        if success:
            if not self.model.current:
                # Si la lista se quedó vacía tras borrar el nodo
                self.current_index = -1
                self.is_playing = False
                self.is_paused = False
                self.view.btn_play.configure(text="▶ Play")
            else:
                # Si borramos el último, retrocedemos una posición; si no, hereda la misma posición
                songs_count = len(self.model.get_songs_list())
                if target_index >= songs_count:
                    self.current_index = songs_count - 1
                else:
                    self.current_index = target_index
                
                # Reiniciar estados ya que la canción eliminada detuvo el audio
                self.seek_offset = 0.0
                self.is_playing = False
                self.is_paused = False
                self.view.btn_play.configure(text="▶ Play")

            # Actualizar la interfaz gráfica de forma inmediata
            self._refresh_view()
            self._update_status()

    def handle_play_pause(self):
        """Controla las acciones de reproducción, pausa y reanudación."""
        if not self.model.current:
            messagebox.showwarning(
                "Advertencia", "No hay canciones en la playlist."
            )
            return

        if self.is_paused:
            self.model.unpause_audio()
            self.is_paused = False
            self.is_playing = True
            self.view.btn_play.configure(text="⏸ Pausa")
        elif self.is_playing:
            self.model.pause_audio()
            self.is_paused = True
            self.is_playing = False
            self.view.btn_play.configure(text="▶ Reanudar")
        else:
            self.seek_offset = 0.0
            self.is_seeking = False
            self.model.play_current()
            self.is_playing = True
            self.is_paused = False
            self.view.btn_play.configure(text="⏸ Pausa")
            self._update_status()

    def handle_next(self):
        """Avanza a la siguiente canción utilizando la lista enlazada."""
        self.seek_offset = 0.0
        self.is_seeking = False
        if self.model.next_song():
            self.current_index += 1
            self.is_playing = True
            self.is_paused = False
            self.view.btn_play.configure(text="⏸ Pausa")
            self._refresh_view()
            self._update_status()
        else:
            messagebox.showinfo("Fin", "Estás en la última canción.")

    def handle_previous(self):
        """Regresa a la canción anterior utilizando la lista enlazada."""
        self.seek_offset = 0.0
        self.is_seeking = False
        if self.model.previous_song():
            self.current_index -= 1
            self.is_playing = True
            self.is_paused = False
            self.view.btn_play.configure(text="⏸ Pausa")
            self._refresh_view()
            self._update_status()
        else:
            messagebox.showinfo("Inicio", "Estás en la primera canción.")

    def _refresh_view(self):
        """Refresca la lista visual de canciones."""
        songs = self.model.get_songs_list()
        self.view.update_playlist_view(songs, self.current_index)

    def _update_status(self):
        """Actualiza la etiqueta de estado de la canción actual y ajusta la barra."""
        if self.model.current:
            text = f"{self.model.current.title} - {self.model.current.artist}"
            self.view.update_current_label(text)
            self.view.update_slider_max(self.model.current.duration)