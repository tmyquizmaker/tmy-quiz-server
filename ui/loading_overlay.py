"""
Superposition plein écran Ultra-Pro avec logo tournant (assets/logo.png),
carte moderne et barre de progression animée et fluide.
"""
import os
import customtkinter as ctk
from PIL import Image

# Chemin direct vers le logo à la racine du projet
LOGO_PATH = os.path.join("assets", "logo.png")


class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, parent, message="Veuillez patienter..."):
        super().__init__(parent, fg_color="#0B0E14")
        self._angle = 0
        self._logo_original = None
        self._progress_val = 0.0
        self._animating = False

        # Chargement obligatoire du logo depuis assets/logo.png
        try:
            if os.path.exists(LOGO_PATH):
                self._logo_original = Image.open(LOGO_PATH).convert("RGBA")
            else:
                alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo.png")
                self._logo_original = Image.open(alt_path).convert("RGBA")
        except Exception as e:
            print(f"Erreur critique lors du chargement du logo pour l'overlay : {e}")
            self._logo_original = None

        # ===============================================
        # CARTE CENTRALE DESIGN
        # ===============================================
        self.card = ctk.CTkFrame(
            self,
            width=420,
            height=260,
            fg_color="#1E222D",
            corner_radius=24,
            border_width=1,
            border_color="#2B303C"
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # 1. Logo animé (haut de la carte)
        self.logo_label = ctk.CTkLabel(self.card, text="")
        self.logo_label.place(relx=0.5, rely=0.25, anchor="center")

        if self._logo_original:
            init_img = ctk.CTkImage(light_image=self._logo_original, dark_image=self._logo_original, size=(56, 56))
            self.logo_label.configure(image=init_img)
            self.logo_label.image = init_img

        # 2. Message dynamique
        self.message_label = ctk.CTkLabel(
            self.card,
            text=message,
            font=("Arial", 15, "bold"),
            text_color="#FFFFFF"
        )
        self.message_label.place(relx=0.5, rely=0.52, anchor="center")

        # 3. Barre de progression moderne
        self.progress_bar = ctk.CTkProgressBar(
            self.card,
            width=320,
            height=10,
            corner_radius=5,
            progress_color="#1F6AA5",
            fg_color="#121620"
        )
        self.progress_bar.set(0.0)
        self.progress_bar.place(relx=0.5, rely=0.72, anchor="center")

        # 4. Footer discret
        self.footer = ctk.CTkLabel(
            self.card,
            text="TMY Engine • Sécurisé",
            font=("Arial", 9),
            text_color="#555861"
        )
        self.footer.place(relx=0.5, rely=0.90, anchor="center")

    def afficher(self, message=None):
        if message:
            self.message_label.configure(text=message)
        
        # Afficher l'overlay en premier plan
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        
        # Activer les animations et lancer les boucles
        self._animating = True
        self._progress_val = 0.0
        
        if self._logo_original:
            self._animer_logo()
        
        self._animer_barre()

    def masquer(self):
        self._animating = False
        self.progress_bar.set(0.0)
        self.place_forget()

    def _animer_logo(self):
        if not self._animating:
            return
        
        self._angle = (self._angle - 6) % 360
        try:
            if self._logo_original:
                image_tournee = self._logo_original.rotate(self._angle, expand=False)
                ctk_img = ctk.CTkImage(light_image=image_tournee, dark_image=image_tournee, size=(56, 56))
                self.logo_label.configure(image=ctk_img)
                self.logo_label.image = ctk_img
        except Exception:
            pass
        
        # Relance la rotation toutes les 40 millisecondes
        self.after(40, self._animer_logo)

    def _animer_barre(self):
        if not self._animating:
            return
        
        # Fait progresser la barre en boucle fluide
        self._progress_val += 0.03
        if self._progress_val > 1.0:
            self._progress_val = 0.0
            
        try:
            self.progress_bar.set(self._progress_val)
        except Exception:
            pass
            
        # Relance la progression toutes les 50 millisecondes
        self.after(50, self._animer_barre)