"""
===========================================
TMY Quiz Maker
Version 5.0

join_modal.py - Fenêtre modale pour entrer le Nom et le PIN
===========================================
"""

import customtkinter as ctk

class JoinRoomModal(ctk.CTkToplevel):

    def __init__(self, master, join_callback):
        super().__init__(master)

        self.title("Rejoindre un Quiz")
        self.geometry("400x380")
        self.configure(fg_color="#121620")
        self.resizable(False, False)

        self.join_callback = join_callback

        # Garder la modale au premier plan
        self.grab_set()

        self.container = ctk.CTkFrame(self, fg_color="#1E222D", corner_radius=15, border_width=1, border_color="#2B303C")
        self.container.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(self.container, text="🎮 REJOINDRÈ UNE SALLE", font=("Arial", 16, "bold"), text_color="#FFFFFF").pack(pady=(20, 15))

        # Entrée du Nom / Pseudo
        ctk.CTkLabel(self.container, text="Ton Nom / Pseudo :", font=("Arial", 11, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=25)
        self.name_entry = ctk.CTkEntry(self.container, placeholder_text="Ex: Marc Dupuis", font=("Arial", 13), fg_color="#121620", border_color="#2B303C", height=40)
        self.name_entry.pack(fill="x", padx=25, pady=(2, 15))

        # Entrée du Code PIN
        ctk.CTkLabel(self.container, text="Code PIN de la salle :", font=("Arial", 11, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=25)
        self.pin_entry = ctk.CTkEntry(self.container, placeholder_text="Ex: 291 714", font=("Arial", 14, "bold"), fg_color="#121620", border_color="#1F6AA5", height=40)
        self.pin_entry.pack(fill="x", padx=25, pady=(2, 20))

        # Bouton Validation
        self.join_btn = ctk.CTkButton(
            self.container, text="REJOINDRÈ LA SALLE", font=("Arial", 12, "bold"),
            fg_color="#1F6AA5", hover_color="#144870", height=42, command=self.submit
        )
        self.join_btn.pack(fill="x", padx=25)

    def submit(self):
        name = self.name_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if name and pin:
            self.join_callback(pin, name)
            self.destroy()