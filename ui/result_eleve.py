"""
===========================================
TMY Quiz Maker
Version 5.4

result_eleve.py - Écran de Résultats Ajusté & Design Premium
===========================================
"""

import os
import tempfile
from datetime import datetime
from tkinter import filedialog
import tkinter.messagebox as messagebox
import customtkinter as ctk
from PIL import Image

import ui.colors as colors
import ui.fonts as fonts


class ResultElevePage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        titre_quiz="Quiz",
        nom_prof="Professeur",
        nom_eleve="Élève",
        score=0,
        total=1,
        points_earned=0,
        total_points=0,
        max_combo=0,
        average_time=0.0,
        bonnes_reponses=0,
        mauvaises_reponses=0,
        non_repondues=0,
        rang=None,
        total_participants=None,
        moyenne_classe=0,
        certificat_callback=None,
        share_callback=None,
        home_callback=None,
    ):
        super().__init__(master)

        self.master = master
        self.titre_quiz = titre_quiz
        self.nom_prof = nom_prof
        self.nom_eleve = nom_eleve
        self.score = score
        self.total = max(1, total)
        self.points_earned = points_earned
        self.total_points = total_points
        self.max_combo = max_combo
        self.rang = rang
        self.total_participants = total_participants
        self.moyenne_classe = moyenne_classe
        self.average_time = average_time
        self.bonnes_reponses = bonnes_reponses
        self.mauvaises_reponses = mauvaises_reponses
        self.non_repondues = non_repondues

        # Callbacks des boutons (Compatibilité ascendante)
        self.home_callback = home_callback or self.defaut_accueil

        self.percentage = int((self.score / self.total) * 100)

        self.configure(fg_color="#0F111A")

        # Conteneur principal fluide avec molette
        self.scroll_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scroll_container.pack(expand=True, fill="both", padx=20, pady=20)

        self.create_interface()

    # =========================================
    # Charger l'Image / Logo
    # =========================================
    def get_logo_image(self, size=(64, 64)):
        """Charge le logo TMY s'il existe dans le projet."""
        possible_paths = [
            os.path.join("assets", "logo.jpg"),
            os.path.join("assets", "logo.png"),
            "logo.jpg",
            "logo.png"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path)
                    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size), path
                except Exception:
                    pass
        return None, None

    # =========================================
    # Actions & Exports
    # =========================================
    def capture_widget_image(self):
        """Capture l'INTÉGRALITÉ du widget résultat (y compris le contenu scrollé hors écran)."""
        from PIL import ImageGrab

        root_window = self.winfo_toplevel()
        largeur_fenetre = root_window.winfo_width()
        hauteur_originale = root_window.winfo_height()

        # Remonte tout en haut du scroll pour être sûr que l'en-tête soit inclus
        try:
            self.scroll_container._parent_canvas.yview_moveto(0)
        except Exception:
            pass
        self.update()

        # Calcule la hauteur totale du contenu et agrandit temporairement la fenêtre
        try:
            bbox = self.scroll_container._parent_canvas.bbox("all")
            hauteur_contenu = bbox[3] if bbox else self.winfo_height()
        except Exception:
            hauteur_contenu = self.winfo_height()

        hauteur_necessaire = hauteur_contenu + 120
        root_window.geometry(f"{largeur_fenetre}x{hauteur_necessaire}")
        self.update()

        x = self.winfo_rootx()
        y = self.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        image = ImageGrab.grab(bbox=(x, y, x + w, y + h))

        # Remet la fenêtre à sa taille d'origine
        root_window.geometry(f"{largeur_fenetre}x{hauteur_originale}")
        self.update()

        return image

    def telecharger_pdf(self):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Module manquant", "Installe d'abord : pip install fpdf2")
            return
        try:
            from PIL import ImageGrab
        except ImportError:
            messagebox.showerror("Module manquant", "Installe d'abord : pip install pillow")
            return

        chemin = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichier PDF", "*.pdf")],
            initialfile=f"{self.nom_eleve}_{self.titre_quiz}_resultat.pdf"
        )
        if not chemin:
            return

        try:
            image = self.capture_widget_image()

            temp_path = os.path.join(tempfile.gettempdir(), "tmy_resultat_capture.png")
            image.save(temp_path)

            largeur_px, hauteur_px = image.size
            largeur_pdf = 190
            hauteur_pdf = largeur_pdf * (hauteur_px / largeur_px)

            page_h_max = 277
            if hauteur_pdf > page_h_max:
                hauteur_pdf = page_h_max
                largeur_pdf = hauteur_pdf * (largeur_px / hauteur_px)

            pdf = FPDF(unit="mm", format="A4")
            pdf.add_page()
            pdf.image(temp_path, x=10, y=10, w=largeur_pdf, h=hauteur_pdf)
            pdf.output(chemin)

            os.remove(temp_path)
            messagebox.showinfo("Export PDF", "Résultat exporté en PDF avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Le PDF n'a pas pu être généré : {e}")

    def telecharger_image(self):
        try:
            from PIL import ImageGrab
        except ImportError:
            messagebox.showerror("Module manquant", "Installe d'abord : pip install pillow")
            return

        chemin = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Image PNG", "*.png"), ("Image JPEG", "*.jpg")],
            initialfile=f"{self.nom_eleve}_{self.titre_quiz}_resultat.png"
        )
        if not chemin:
            return

        image = self.capture_widget_image()
        image.save(chemin)
        messagebox.showinfo("Export Image", "Capture du résultat enregistrée avec succès !")

    def defaut_accueil(self):
        for widget in self.master.winfo_children():
            widget.pack_forget()
        if hasattr(self.master, "show_home"):
            self.master.show_home()

    # =========================================
    # Mentions & Stickers Dynamiques
    # =========================================
    def get_appreciation(self):
        if self.percentage >= 80:
            return (
                "EXCELLENT !",
                "« Excellent travail. Les compétences évaluées sont maîtrisées avec assurance. Continuez sur cette voie. »",
                "#00E676",
                "👑",
            )
        elif self.percentage >= 50:
            return (
                "SATISFAISANT !",
                "« Les objectifs principaux sont globalement atteints. Des efforts supplémentaires permettront de consolider les acquis et d'améliorer les résultats. »",
                "#FF9800",
                "👍",
            )
        else:
            return (
                "INSUFFISANT !",
                "« Les connaissances évaluées ne sont pas encore acquises. Un travail plus régulier et des révisions approfondies sont nécessaires pour progresser. »",
                "#FF5252",
                "🌱",
            )

    # =========================================
    # Interface
    # =========================================
    def create_interface(self):
        (
            title_text,
            desc_text,
            title_color,
            sticker_icon,
        ) = self.get_appreciation()

        # 1. En-tête : Logo TMY & Métadonnées du Quiz
        header_card = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#181B26",
            corner_radius=16,
            border_width=1,
            border_color="#242838",
        )
        header_card.pack(fill="x", pady=(0, 15), ipady=12, ipadx=15)

        # Zone du Logo à gauche
        logo_img, _ = self.get_logo_image(size=(58, 58))
        if logo_img:
            logo_label = ctk.CTkLabel(header_card, image=logo_img, text="")
            logo_label.pack(side="left", padx=(10, 15))
        else:
            logo_badge = ctk.CTkLabel(
                header_card,
                text="TMY",
                font=("Arial", 16, "bold"),
                text_color="#4CC9F0",
                fg_color="#242838",
                corner_radius=29,
                width=58,
                height=58
            )
            logo_badge.pack(side="left", padx=(10, 15))

        # Conteneur grille pour les 4 métadonnées
        meta_grid = ctk.CTkFrame(header_card, fg_color="transparent")
        meta_grid.pack(side="left", fill="x", expand=True)

        for i in range(4):
            meta_grid.columnconfigure(i, weight=1)

        self.add_meta_item(
            meta_grid, 0, "💻 TITRE DU QUIZ", self.titre_quiz, "#4CC9F0"
        )
        self.add_meta_item(
            meta_grid, 1, "👤 PROFESSEUR", self.nom_prof, "#00E676"
        )
        self.add_meta_item(
            meta_grid, 2, "🎓 ÉTUDIANT", self.nom_eleve, "#FFD700"
        )
        self.add_meta_item(
            meta_grid,
            3,
            "📅 DATE DU QUIZ",
            datetime.now().strftime("%d %b %Y"),
            "#B57EDC",
        )

        # 2. Bannière de résultat (Centrée et aérée)
        banner_card = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#181B26",
            corner_radius=16,
            border_width=1,
            border_color="#242838",
        )
        banner_card.pack(fill="x", pady=(0, 15), ipady=20, ipadx=20)

        left_banner = ctk.CTkFrame(banner_card, fg_color="transparent")
        left_banner.pack(side="left", fill="both", expand=True, padx=10)

        ctk.CTkLabel(
            left_banner,
            text="🎖️ QUIZ TERMINÉ !",
            font=("Arial", 11, "bold"),
            text_color="#A0AABF",
        ).pack(anchor="w")
        ctk.CTkLabel(
            left_banner,
            text=title_text,
            font=("Arial", 28, "bold"),
            text_color=title_color,
        ).pack(anchor="w", pady=(2, 6))

        ctk.CTkLabel(
            left_banner,
            text=desc_text,
            font=("Arial", 12, "italic"),
            text_color="#A0AABF",
            wraplength=650,
            justify="left",
        ).pack(anchor="w")

        # Badge Sticker
        sticker_badge = ctk.CTkLabel(
            banner_card,
            text=sticker_icon,
            font=("Segoe UI Emoji", 40),
            width=85,
            height=85,
            fg_color="#242838",
            corner_radius=42,
        )
        sticker_badge.pack(side="right", padx=15)

        # 3. Statistiques principales (4 Colonnes)
        stats_frame = ctk.CTkFrame(
            self.scroll_container, fg_color="transparent"
        )
        stats_frame.pack(fill="x", pady=(0, 15))
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        self.add_stat_card(
            stats_frame,
            0,
            "🎯 SCORE FINAL",
            f"{self.score}/{self.total}",
            f"Précision : {self.percentage}%",
            "#1F6AA5",
            "#4CC9F0",
        )
        self.add_stat_card(
            stats_frame,
            1,
            "🏆 POINTS",
            f"{self.points_earned}/{self.total_points}",
            "Points obtenus",
            "#FFD700",
            "#FFD700",
        )
        self.add_stat_card(
            stats_frame,
            2,
            "🔥 MEILLEUR COMBO",
            f"x{self.max_combo}",
            "Série de réponses",
            "#FF9800",
            "#FF9800",
        )
        self.add_stat_card(
            stats_frame,
            3,
            "⏱ TEMPS MOYEN",
            f"{self.average_time}s",
            "Par question",
            "#00E676",
            "#00E676",
        )

        # 4. Section centrale
        middle_frame = ctk.CTkFrame(
            self.scroll_container, fg_color="transparent"
        )
        middle_frame.pack(fill="x", pady=(0, 20))
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)

        # Carte Gauche : Classement de la salle
        perf_card = ctk.CTkFrame(
            middle_frame,
            fg_color="#181B26",
            corner_radius=16,
            border_width=1,
            border_color="#242838",
        )
        perf_card.grid(
            row=0, column=0, sticky="nsew", padx=(0, 8), ipady=20, ipadx=15
        )

        ctk.CTkLabel(
            perf_card,
            text="🏆 CLASSEMENT DE LA SALLE",
            font=("Arial", 12, "bold"),
            text_color="#A0AABF",
        ).pack(anchor="w", pady=(0, 15))

        perf_body = ctk.CTkFrame(perf_card, fg_color="transparent")
        perf_body.pack(fill="both", expand=True)

        perf_center = ctk.CTkFrame(perf_body, fg_color="transparent")
        perf_center.place(relx=0.5, rely=0.5, anchor="center")

        rang_suffix = "er" if self.rang == 1 else "ème"
        rang_texte = f"{self.rang}{rang_suffix}" if self.rang else "--"

        badge_rang = ctk.CTkLabel(
            perf_center,
            text=rang_texte,
            font=("Arial", 20, "bold"),
            text_color=title_color,
            width=75,
            height=75,
            fg_color="#242838",
            corner_radius=37,
        )
        badge_rang.pack(side="left", padx=(0, 15))

        perf_info = ctk.CTkFrame(perf_center, fg_color="transparent")
        perf_info.pack(side="left")

        total_txt = (
            self.total_participants if self.total_participants else "?"
        )
        ctk.CTkLabel(
            perf_info,
            text=f"sur {total_txt} participants",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")
        ctk.CTkLabel(
            perf_info,
            text=f"Moyenne de la salle : {self.moyenne_classe} pts",
            font=("Arial", 11),
            text_color="#8A8F9E",
        ).pack(anchor="w", pady=(4, 0))

        # Carte Droite : Récapitulatif
        recap_card = ctk.CTkFrame(
            middle_frame,
            fg_color="#181B26",
            corner_radius=16,
            border_width=1,
            border_color="#242838",
        )
        recap_card.grid(
            row=0, column=1, sticky="nsew", padx=(8, 0), ipady=20, ipadx=15
        )

        ctk.CTkLabel(
            recap_card,
            text="📋 RÉCAPITULATIF DES RÉPONSES",
            font=("Arial", 12, "bold"),
            text_color="#A0AABF",
        ).pack(anchor="w", pady=(0, 15))

        recap_body = ctk.CTkFrame(recap_card, fg_color="transparent")
        recap_body.pack(fill="both", expand=True)

        recap_center = ctk.CTkFrame(recap_body, fg_color="transparent")
        recap_center.place(relx=0.5, rely=0.5, anchor="center")

        self.add_recap_row(
            recap_center,
            "☑  Bonnes réponses",
            str(self.bonnes_reponses),
            "#00E676",
        )
        self.add_recap_row(
            recap_center,
            "✖  Mauvaises réponses",
            str(self.mauvaises_reponses),
            "#FF5252",
        )
        self.add_recap_row(
            recap_center,
            "➖  Non répondues",
            str(self.non_repondues),
            "#4CC9F0",
        )

        # 5. Les 3 boutons du bas (Télécharger PDF, Télécharger Image, Accueil)
        action_bar = ctk.CTkFrame(
            self.scroll_container, fg_color="transparent"
        )
        action_bar.pack(fill="x", pady=(10, 5))

        action_bar.columnconfigure(0, weight=1)
        action_bar.columnconfigure(1, weight=1)
        action_bar.columnconfigure(2, weight=1)

        btn_pdf = ctk.CTkButton(
            action_bar,
            text="📄 TÉLÉCHARGER LE PDF DU RÉSULTAT",
            font=("Arial", 13, "bold"),
            fg_color="#1F6AA5",
            hover_color="#144970",
            height=48,
            corner_radius=10,
            command=self.telecharger_pdf,
        )
        btn_pdf.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        btn_image = ctk.CTkButton(
            action_bar,
            text="🖼️ TÉLÉCHARGER L'IMAGE DU RÉSULTAT",
            font=("Arial", 13, "bold"),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=48,
            corner_radius=10,
            command=self.telecharger_image,
        )
        btn_image.grid(row=0, column=1, padx=6, sticky="ew")

        btn_home = ctk.CTkButton(
            action_bar,
            text="🏠 RETOUR À L'ACCUEIL",
            font=("Arial", 13, "bold"),
            fg_color="#37474F",
            hover_color="#263238",
            height=48,
            corner_radius=10,
            command=self.home_callback,
        )
        btn_home.grid(row=0, column=2, padx=(6, 0), sticky="ew")

    # =========================================
    # Helpers
    # =========================================
    def add_meta_item(self, parent, col, title, value, color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="ew", padx=10)
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 10, "bold"),
            text_color="#A0AABF",
        ).pack(anchor="w")
        ctk.CTkLabel(
            frame, text=value, font=("Arial", 14, "bold"), text_color=color
        ).pack(anchor="w", pady=(2, 0))

    def add_stat_card(
        self, parent, col, title, main_val, sub_val, border_col, text_col
    ):
        card = ctk.CTkFrame(
            parent,
            fg_color="#181B26",
            corner_radius=12,
            border_width=1,
            border_color="#242838",
        )
        card.grid(row=0, column=col, sticky="nsew", padx=4, ipady=10)

        top_bar = ctk.CTkFrame(
            card, fg_color=border_col, height=3, corner_radius=2
        )
        top_bar.pack(fill="x", padx=15, pady=(8, 10))

        ctk.CTkLabel(
            card, text=title, font=("Arial", 10, "bold"), text_color="#A0AABF"
        ).pack()
        ctk.CTkLabel(
            card, text=main_val, font=("Arial", 22, "bold"), text_color=text_col
        ).pack(pady=(4, 2))
        ctk.CTkLabel(
            card, text=sub_val, font=("Arial", 11), text_color="#6C728F"
        ).pack()

    def add_recap_row(self, parent, label, count, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(
            row, text=label, font=("Arial", 13), text_color="#FFFFFF"
        ).pack(side="left")
        ctk.CTkLabel(
            row, text=count, font=("Arial", 14, "bold"), text_color=color
        ).pack(side="right")