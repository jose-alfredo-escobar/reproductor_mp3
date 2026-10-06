"""Módulo que construye la interfaz gráfica de usuario (UI)

utilizando CustomTkinter con elementos interactivos, barra de progreso y menú de volumen desplegable.
"""

import customtkinter as ctk

# Configuración inicial del tema visual
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MusicPlayerView(ctk.CTk):
    """Vista principal del reproductor de música."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.title("🎵 Reproductor de Música - Lista Enlazada")
        self.geometry("850x530")  # Ampliado ligeramente a 850 para dar espacio al nuevo botón
        self.resizable(True, True)

        self._create_widgets()

    def _create_widgets(self):
        """Inicializa y organiza los elementos visuales en la ventana."""
        # Título principal
        self.lbl_title = ctk.CTkLabel(
            self, text="Mi Reproductor", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_title.pack(pady=(20, 10))

        # Marco con desplazamiento para la lista de canciones en botones
        self.playlist_frame = ctk.CTkScrollableFrame(self, width=620, height=160)
        self.playlist_frame.pack(pady=5)

        # Etiqueta de canción actual
        self.lbl_current = ctk.CTkLabel(
            self,
            text="Reproduciendo: Ninguna",
            font=ctk.CTkFont(size=14, slant="italic"),
        )
        self.lbl_current.pack(pady=5)

        # Barra de progreso (Slider interactivo)
        self.progress_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=100,
            command=None
        )
        self.progress_slider.set(0)
        self.progress_slider.pack(pady=10, fill="x", padx=40)

        # Eventos para la barra de progreso
        self.progress_slider.bind("<ButtonPress-1>", self.controller.handle_seek_start)
        self.progress_slider.bind("<ButtonRelease-1>", self.controller.handle_seek_release)

        # Panel de controles de reproducción y volumen
        self.frame_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controls.pack(pady=5)

        self.btn_prev = ctk.CTkButton(
            self.frame_controls,
            text="⏮",
            width=50,
            command=self.controller.handle_previous,
        )
        self.btn_prev.grid(row=0, column=0, padx=5)

        self.btn_play = ctk.CTkButton(
            self.frame_controls,
            text="▶ Play",
            width=120,
            command=self.controller.handle_play_pause,
        )
        self.btn_play.grid(row=0, column=1, padx=5)

        self.btn_next = ctk.CTkButton(
            self.frame_controls,
            text="⏭",
            width=50,
            command=self.controller.handle_next,
        )
        self.btn_next.grid(row=0, column=2, padx=5)

        # Botón desplegable de Volumen
        self.btn_volume_toggle = ctk.CTkButton(
            self.frame_controls,
            text="🔊",
            width=50,
            fg_color="gray50",
            hover_color="gray40",
            command=self.controller.toggle_volume_slider,
        )
        self.btn_volume_toggle.grid(row=0, column=3, padx=5)

        # NUEVO: Botón de Basurero Global en el panel inferior de controles
        self.btn_delete_global = ctk.CTkButton(
            self.frame_controls,
            text="🗑",
            width=50,
            font=ctk.CTkFont(size=16),
            fg_color="#CC3333",
            hover_color="#991111",
            command=self.controller.handle_delete_current_song,
        )
        self.btn_delete_global.grid(row=0, column=4, padx=5)

        # Marco flotante para el slider de volumen (inicialmente oculto)
        self.frame_volume_popup = ctk.CTkFrame(self, fg_color=("gray85", "gray20"))

        self.volume_slider = ctk.CTkSlider(
            self.frame_volume_popup,
            from_=0.0,
            to=1.0,
            width=150,
            command=self.controller.handle_volume_change
        )
        self.volume_slider.set(0.7)
        self.volume_slider.pack(padx=10, pady=10)

        # Botón para agregar archivos MP3 manualmente
        self.btn_add = ctk.CTkButton(
            self,
            text="+ Agregar Canción (MP3)",
            fg_color="green",
            hover_color="darkgreen",
            command=self.controller.handle_add_song,
        )
        self.btn_add.pack(pady=(15, 20))

    def toggle_volume_popup(self, show: bool):
        """Muestra u oculta la barra de volumen flotante."""
        if show:
            self.frame_volume_popup.place(relx=0.70, rely=0.60, anchor="center")
        else:
            self.frame_volume_popup.place_forget()

    def update_playlist_view(self, songs: list, current_index: int):
        """Actualiza la lista visual creando botones interactivos limpios para cada tema."""
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()

        for idx, (title, artist) in enumerate(songs):
            is_current = (idx == current_index)
            prefix = "▶ " if is_current else "  "
            btn_text = f"{prefix}{idx + 1}. {title} - {artist}"

            fg_color = ("gray75", "gray30") if is_current else "transparent"
            text_color = ("blue", "cyan") if is_current else ("black", "white")

            song_button = ctk.CTkButton(
                self.playlist_frame,
                text=btn_text,
                anchor="w",
                fg_color=fg_color,
                text_color=text_color,
                command=lambda index=idx: self.controller.handle_select_song(index)
            )
            song_button.pack(fill="x", pady=2)

    def update_current_label(self, text: str):
        """Actualiza el texto descriptivo de la canción actual."""
        self.lbl_current.configure(text=f"Reproduciendo: {text}")

    def update_slider_max(self, duration: float):
        """Actualiza el valor máximo del slider según la duración de la canción."""
        self.progress_slider.configure(to=duration)