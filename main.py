"""
===========================================
TMY Quiz Maker
Version 4.1

Fichier : main.py

Rôle :
- Point d'entrée de l'application
- Configurer CustomTkinter
- Lancer le contrôleur principal

Note :
L'intelligence artificielle fonctionne
en arrière-plan.
Aucune information technique
(API, Gemini, connexion IA) n'est affichée
à l'utilisateur.
===========================================
"""

import os
import sys
import pygame
import customtkinter as ctk
from dotenv import load_dotenv

load_dotenv()  # Charge les variables définies dans votre fichier .env
from core.app_controller import AppController
from audio.music import start_music


# ==========================================
# Fonction de compatibilité PyInstaller
# ==========================================

def resource_path(relative_path):
    """Obtient le chemin absolu vers la ressource, compatible avec le mode normal et PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ==========================================
# Configuration générale CustomTkinter
# ==========================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ==========================================
# Application principale
# ==========================================

class TMYQuizMaker(ctk.CTk):

    def __init__(self):

        super().__init__()

        # -----------------------------
        # Configuration fenêtre
        # -----------------------------

        self.title(
            "TMY Quiz Maker"
        )

        self.geometry(
            "900x700"
        )

        self.minsize(
            900,
            700
        )

        # Empêche le redimensionnement
        self.resizable(
            False,
            False
        )

        # -----------------------------
        # Contrôleur principal
        # -----------------------------

        start_music()

        self.controller = AppController(
            self
        )

        self.controller.start()

        # -----------------------------
        # Maintien du son Pygame
        # -----------------------------
        self.update_pygame()

    def update_pygame(self):
        """Maintient le flux audio actif sans dépendre du système vidéo"""
        try:
            # On vérifie l'état de la musique pour maintenir le canal audio
            if pygame.mixer.get_init():
                _ = pygame.mixer.music.get_busy()
        except Exception:
            pass
            
        self.after(500, self.update_pygame)


# ==========================================
# Lancement de l'application
# ==========================================

if __name__ == "__main__":

    app = TMYQuizMaker()

    app.mainloop()