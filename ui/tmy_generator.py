"""
===========================================
TMY Quiz Maker
Version 5.1

tmy_generator.py - Interface Moderne & Interactive
===========================================
"""

import customtkinter as ctk

from ui.cards import ModernCard
from ui.buttons import LargeButton
from ui.widgets import ModernEntry

import ui.colors as colors
import ui.fonts as fonts


class TMYGeneratorPage(ctk.CTkFrame):

    def __init__(
            self,
            master,
            start_callback,
            back_callback,
            initial_data=None
    ):
        super().__init__(master)

        self.start_callback = start_callback
        self.back_callback = back_callback
        self.initial_data = initial_data or {}
        self.quiz_started = False

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal avec padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=60, pady=20)

        # =====================================
        # EN-TÊTE : Titre & Sous-titre
        # =====================================
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))

        self.title = ctk.CTkLabel(
            self.header_frame,
            text="🧠 CRÉER UN QUIZ AVEC TMY",
            font=("Arial", 22, "bold"),
            text_color="#FFFFFF"
        )
        self.title.pack()

        self.subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Personnalisez vos options et laissez l'IA générer votre quiz",
            font=("Arial", 12),
            text_color=colors.TEXT_SECONDARY
        )
        self.subtitle.pack(pady=(2, 0))

        # =====================================
        # CARTE PRINCIPALE
        # =====================================
        self.card = ModernCard(self.container)
        self.card.pack(fill="both", expand=True, padx=10, pady=5)

        # -------------------------------------
        # 1. SUJET + SUGGESTIONS
        # -------------------------------------
        self.subject_label = ctk.CTkLabel(
            self.card,
            text="🎯 SUJET DU QUIZ",
            font=("Arial", 12, "bold"),
            text_color="#AAAAAA"
        )
        self.subject_label.pack(anchor="w", padx=30, pady=(15, 5))

        self.subject = ModernEntry(
            self.card,
            placeholder_text="Ex : Python, Histoire de France, Astronomie..."
        )
        self.subject.pack(fill="x", padx=30, pady=(0, 8))

        # Pré-remplissage sujet
        sujet_initial = self.initial_data.get("sujet", "")
        if sujet_initial:
            self.subject.insert(0, sujet_initial)

        # Chips / Tags de suggestions rapides
        self.suggestions_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.suggestions_frame.pack(fill="x", padx=30, pady=(0, 15))

        suggested_topics = ["🐍 Python", "🌌 Astronomie", "🏰 Histoire", "⚡ Physique", "🎬 Cinéma"]
        for topic in suggested_topics:
            clean_topic = topic.split(" ")[1] if " " in topic else topic
            btn = ctk.CTkButton(
                self.suggestions_frame,
                text=topic,
                font=("Arial", 10, "bold"),
                height=26,
                corner_radius=13,
                fg_color="#2B2D42",
                hover_color="#1F6AA5",
                text_color="#DDDDDD",
                command=lambda t=clean_topic: self.set_suggested_subject(t)
            )
            btn.pack(side="left", padx=(0, 6))

        # -------------------------------------
        # 2. NIVEAU DE DIFFICULTÉ (Pilules)
        # -------------------------------------
        self.level_label = ctk.CTkLabel(
            self.card,
            text="📊 NIVEAU DE DIFFICULTÉ",
            font=("Arial", 12, "bold"),
            text_color="#AAAAAA"
        )
        self.level_label.pack(anchor="w", padx=30, pady=(5, 5))

        self.selected_level = ctk.StringVar(value=self.initial_data.get("niveau", "Intermédiaire"))

        self.level_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.level_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.level_buttons = {}
        levels = [("Débutant", "#2E7D32"), ("Intermédiaire", "#1F6AA5"), ("Avancé", "#C62828")]

        for lvl_name, color in levels:
            btn = ctk.CTkButton(
                self.level_frame,
                text=lvl_name,
                font=("Arial", 12, "bold"),
                height=36,
                corner_radius=10,
                fg_color=color if self.selected_level.get() == lvl_name else "#1E222D",
                border_width=1,
                border_color=color,
                command=lambda l=lvl_name: self.select_level(l)
            )
            btn.pack(side="left", expand=True, fill="x", padx=4)
            self.level_buttons[lvl_name] = (btn, color)

        # -------------------------------------
        # 3. NOMBRE DE QUESTIONS (Slider)
        # -------------------------------------
        self.num_header_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.num_header_frame.pack(fill="x", padx=30, pady=(5, 5))

        self.number_label = ctk.CTkLabel(
            self.num_header_frame,
            text="🔢 NOMBRE DE QUESTIONS",
            font=("Arial", 12, "bold"),
            text_color="#AAAAAA"
        )
        self.number_label.pack(side="left")

        initial_count = self.initial_data.get("nombre", 10)
        self.number_val_label = ctk.CTkLabel(
            self.num_header_frame,
            text=f"{initial_count} questions",
            font=("Arial", 13, "bold"),
            text_color="#FFD700"
        )
        self.number_val_label.pack(side="right")

        self.slider = ctk.CTkSlider(
            self.card,
            from_=3,
            to=25,
            number_of_steps=22,
            command=self.update_slider_label
        )
        self.slider.set(initial_count)
        self.slider.pack(fill="x", padx=30, pady=(0, 20))

        # =====================================
        # BOUTONS D'ACTION (Pied de page)
        # =====================================
        self.actions_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.actions_frame.pack(fill="x", pady=(15, 0))

        # Bouton Créer (Principal)
        self.create_button = ctk.CTkButton(
            self.actions_frame,
            text="🚀 Lancer la génération",
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#1F6AA5",
            hover_color="#144870",
            command=self.create_quiz
        )
        self.create_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Bouton Retour (Secondaire)
        self.back_button = ctk.CTkButton(
            self.actions_frame,
            text="← Annuler",
            font=("Arial", 13, "bold"),
            height=45,
            fg_color="#2B2D42",
            hover_color="#1A1B29",
            command=self.back_callback
        )
        self.back_button.pack(side="right", expand=True, fill="x", padx=(5, 0))

    # =====================================
    # Méthodes d'interaction UI
    # =====================================
    def set_suggested_subject(self, topic):
        self.subject.delete(0, "end")
        self.subject.insert(0, topic)

    def select_level(self, level_name):
        self.selected_level.set(level_name)
        for lvl, (btn, color) in self.level_buttons.items():
            if lvl == level_name:
                btn.configure(fg_color=color)
            else:
                btn.configure(fg_color="#1E222D")

    def update_slider_label(self, value):
        self.number_val_label.configure(text=f"{int(value)} questions")

    # =====================================
    # Méthodes système & Rétrocompatibilité
    # =====================================
    def load_quiz(self, data):
        self.subject.delete(0, "end")
        self.subject.insert(0, data.get("sujet", ""))
        self.select_level(data.get("niveau", "Intermédiaire"))
        count = data.get("nombre", 10)
        self.slider.set(count)
        self.update_slider_label(count)

    def get_settings(self):
        return {
            "sujet": self.subject.get().strip(),
            "niveau": self.selected_level.get(),
            "nombre": int(self.slider.get())
        }

    def disable_button(self):
        self.quiz_started = True
        self.create_button.configure(state="disabled", text="⏳ Génération en cours...")

    def enable_button(self):
        self.quiz_started = False
        self.create_button.configure(state="normal", text="🚀 Lancer la génération")

    def clear_form(self):
        self.subject.delete(0, "end")
        self.select_level("Intermédiaire")
        self.slider.set(10)
        self.update_slider_label(10)
        self.enable_button()

    def validate_subject(self):
        sujet = self.subject.get().strip()
        if len(sujet) < 2:
            self.subject.focus()
            return False
        return True

    def create_quiz(self):
        if self.quiz_started:
            return

        if not self.validate_subject():
            return

        sujet = self.subject.get().strip()
        niveau = self.selected_level.get()
        nombre = int(self.slider.get())

        self.disable_button()

        quiz_settings = {
            "sujet": sujet,
            "niveau": niveau,
            "nombre": nombre
        }

        self.last_settings = quiz_settings
        self.history_ready = True
        self.statistics_ready = True
        self.adaptive_ai_ready = True
        self.android_ready = True
        self.xp_ready = True
        self.modify_ready = True
        self.antiduplicate_ready = True

        self.start_callback(sujet, nombre, niveau)

    def update_settings(self, settings):
        self.load_quiz(settings)

    def get_last_settings(self):
        return getattr(self, "last_settings", self.get_settings())

    def generation_failed(self):
        self.enable_button()

    def generation_finished(self):
        self.enable_button()