import os
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import de ReportLab pour la génération du PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class HistoryDetailPage(ctk.CTkFrame):
    """
    Page complète de détails d'une session de quiz :
    - Affichage des questions et de leurs options
    - Mise en évidence de la réponse choisie et de la bonne réponse
    - Exportation PDF professionnelle avec logo
    """
    def __init__(self, master, session_data, on_back_callback, **kwargs):
        super().__init__(master, fg_color="#0f172a", **kwargs)
        self.session_data = session_data or {}
        self.on_back_callback = on_back_callback

        # ----------------------------------------------------
        # 1. EN-TÊTE SUPÉRIEUR (HEADER)
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="#1e293b", height=70, corner_radius=12)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.btn_back = ctk.CTkButton(
            self.header_frame,
            text="← Retour à l'historique",
            font=("Roboto", 13, "bold"),
            fg_color="#334155",
            hover_color="#475569",
            text_color="#f8fafc",
            height=38,
            corner_radius=8,
            command=self.on_back_callback
        )
        self.btn_back.pack(side="left", padx=15, pady=16)

        quiz_title = (
            self.session_data.get("quiz_title") or 
            self.session_data.get("sujet") or 
            self.session_data.get("title") or 
            "Détails de la Session"
        )
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=f"📋 {quiz_title}",
            font=("Roboto", 18, "bold"),
            text_color="#f8fafc"
        )
        self.title_label.pack(side="left", padx=10)

        # ----------------------------------------------------
        # 2. CARTE RÉSUMÉ (Score & Date)
        # ----------------------------------------------------
        self.summary_card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12, border_width=1, border_color="#334155")
        self.summary_card.pack(fill="x", padx=20, pady=5)

        score = self.session_data.get("score", "0")
        mode = self.session_data.get("mode", "Solo")
        date_played = (
            self.session_data.get("played_at") or 
            self.session_data.get("date") or 
            self.session_data.get("created_at") or 
            self.session_data.get("timestamp") or 
            "Date non renseignée"
        )

        score_frame = ctk.CTkFrame(self.summary_card, fg_color="transparent")
        score_frame.pack(side="left", padx=20, pady=12)

        ctk.CTkLabel(score_frame, text="SCORE FINAL", font=("Roboto", 10, "bold"), text_color="#94a3b8").pack(anchor="w")
        ctk.CTkLabel(score_frame, text=f"🏆 {score}", font=("Roboto", 18, "bold"), text_color="#38bdf8").pack(anchor="w")

        meta_frame = ctk.CTkFrame(self.summary_card, fg_color="transparent")
        meta_frame.pack(side="right", padx=20, pady=12)

        ctk.CTkLabel(meta_frame, text=f"Mode : {mode}", font=("Roboto", 11, "bold"), text_color="#cbd5e1").pack(anchor="e")
        ctk.CTkLabel(meta_frame, text=f"📅 Joué le : {date_played}", font=("Roboto", 12), text_color="#94a3b8").pack(anchor="e")

        # ----------------------------------------------------
        # 3. LISTE DES QUESTIONS (SCROLLABLE)
        # ----------------------------------------------------
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#334155",
            scrollbar_button_hover_color="#475569"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(10, 10))

        self.questions = self.extract_questions(self.session_data)

        if not self.questions:
            empty_card = ctk.CTkFrame(self.scroll_frame, fg_color="#1e293b", corner_radius=12)
            empty_card.pack(fill="x", pady=40, padx=20)
            ctk.CTkLabel(
                empty_card,
                text="⚠️ Aucun détail de question disponible pour cette session.",
                font=("Roboto", 14),
                text_color="#94a3b8"
            ).pack(pady=30)
        else:
            for idx, q in enumerate(self.questions, 1):
                self.render_question_card(idx, q)

        # ----------------------------------------------------
        # 4. PIED DE PAGE : BOUTON TÉLÉCHARGER PDF
        # ----------------------------------------------------
        footer_bar = ctk.CTkFrame(self, fg_color="#1e293b", height=65, corner_radius=12)
        footer_bar.pack(fill="x", padx=20, pady=(5, 15))

        self.btn_pdf = ctk.CTkButton(
            footer_bar,
            text="📥 Télécharger le Rapport PDF",
            font=("Roboto", 13, "bold"),
            fg_color="#6366f1",
            hover_color="#4f46e5",
            text_color="#ffffff",
            height=42,
            corner_radius=8,
            command=self.export_to_pdf
        )
        self.btn_pdf.pack(side="right", padx=20, pady=11)

    def extract_questions(self, session_data):
        """Extrait et aplatit toutes les questions quel que soit le format de sauvegarde."""
        if "questions" in session_data and isinstance(session_data["questions"], list):
            return session_data["questions"]

        details = session_data.get("details", {})
        flat = []
        if isinstance(details, dict):
            for q in details.get("correct", []):
                q_copy = dict(q)
                q_copy["is_correct"] = True
                flat.append(q_copy)
            for q in details.get("wrong", []):
                q_copy = dict(q)
                q_copy["is_correct"] = False
                flat.append(q_copy)
            for q in details.get("unanswered", []):
                q_copy = dict(q)
                q_copy["is_correct"] = False
                q_copy["user_answer"] = "Non répondue"
                flat.append(q_copy)
        return flat

    def render_question_card(self, idx, q):
        """Affiche la carte de chaque question avec ses options et la correction."""
        card = ctk.CTkFrame(self.scroll_frame, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#334155")
        card.pack(fill="x", pady=6, padx=5)

        # Intitulé de la question
        q_text = q.get("question") or q.get("title") or f"Question {idx}"
        
        q_header = ctk.CTkFrame(card, fg_color="transparent")
        q_header.pack(fill="x", padx=15, pady=(12, 6))

        ctk.CTkLabel(q_header, text=f"Q{idx}.", font=("Roboto", 13, "bold"), text_color="#6366f1").pack(side="left", anchor="n", padx=(0, 8))
        ctk.CTkLabel(q_header, text=q_text, font=("Roboto", 13, "bold"), text_color="#f8fafc", anchor="w", justify="left", wraplength=750).pack(side="left", fill="x", expand=True)

        # Récupération souple des choix et réponses
        options = q.get("options") or q.get("choices") or []
        user_ans = str(q.get("user_answer") or q.get("your_answer") or q.get("selected") or "Aucune").strip()
        correct_ans = str(q.get("correct_answer") or q.get("correct") or "").strip()

        # Si correct_ans est une clé (ex: "A") et que les options contiennent les réponses
        if len(correct_ans) == 1 and correct_ans in q:
            correct_ans = str(q.get(correct_ans)).strip()

        # Détermination du statut de réussite
        is_correct = q.get("is_correct")
        if is_correct is None:
            is_correct = (user_ans.lower() == correct_ans.lower()) and user_ans != "Aucune"

        # Zone des options de réponses
        opts_box = ctk.CTkFrame(card, fg_color="#0f172a", corner_radius=8)
        opts_box.pack(fill="x", padx=15, pady=6)

        if options:
            for opt in options:
                opt_str = str(opt).strip()
                opt_color = "#94a3b8"
                prefix = "  • "

                # Test de correspondance avec la réponse correcte
                if (opt_str.lower() == correct_ans.lower()) or (len(correct_ans) == 1 and opt_str.startswith(correct_ans)):
                    opt_color = "#22c55e"
                    prefix = "  ✔ "
                
                # Test de correspondance avec le choix utilisateur
                if (opt_str.lower() == user_ans.lower()) or (len(user_ans) == 1 and opt_str.startswith(user_ans)):
                    if not is_correct:
                        opt_color = "#ef4444"
                        prefix = "  ✖ "

                ctk.CTkLabel(opts_box, text=f"{prefix}{opt_str}", font=("Roboto", 12), text_color=opt_color, anchor="w").pack(anchor="w", padx=10, pady=3)
        else:
            # Si pas de liste d'options explicites enregistrée
            u_col = "#22c55e" if is_correct else "#ef4444"
            ctk.CTkLabel(opts_box, text=f"• Votre choix : {user_ans}", font=("Roboto", 12), text_color=u_col, anchor="w").pack(anchor="w", padx=10, pady=2)
            if not is_correct:
                ctk.CTkLabel(opts_box, text=f"• Bonne réponse : {correct_ans}", font=("Roboto", 12), text_color="#22c55e", anchor="w").pack(anchor="w", padx=10, pady=2)

        # Pied de carte : Bilan visuel
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(6, 10))

        status_color = "#22c55e" if is_correct else "#ef4444"
        badge_text = "✅ Réponse Correcte" if is_correct else "❌ Réponse Incorrecte"

        badge = ctk.CTkFrame(footer, fg_color=status_color, corner_radius=6)
        badge.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(badge, text=badge_text, font=("Roboto", 11, "bold"), text_color="#ffffff").pack(padx=8, pady=2)

        summary_txt = f"Choix effectué : {user_ans}"
        if not is_correct:
            summary_txt += f"  |  Réponse attendue : {correct_ans}"

        ctk.CTkLabel(footer, text=summary_txt, font=("Roboto", 11), text_color="#cbd5e1").pack(side="left")

    # ----------------------------------------------------
    # EXPORTATION PDF
    # ----------------------------------------------------
    def export_to_pdf(self):
        """Génère un document PDF complet avec le logo et la liste des questions/réponses."""
        if not HAS_REPORTLAB:
            messagebox.showerror(
                "Bibliothèque manquante",
                "Pour exporter en PDF, installez reportlab via votre terminal :\npip install reportlab"
            )
            return

        # --- RECUPERATION PRECISE DU SUJET / TITRE ---
        quiz_title = (
            self.session_data.get("quiz_title") or 
            self.session_data.get("sujet") or 
            self.session_data.get("title") or 
            "Quiz Sans Titre"
        )
        
        clean_title = "".join(c for c in quiz_title if c.isalnum() or c in (" ", "_", "-")).rstrip()
        default_filename = f"Rapport_{clean_title.replace(' ', '_')}.pdf"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf")],
            initialfile=default_filename,
            title="Enregistrer le rapport du quiz"
        )

        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )
            story = []
            styles = getSampleStyleSheet()

            # Definition des styles ReportLab
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1e293b'), spaceAfter=5)
            subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'))
            meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#334155'))
            q_style = ParagraphStyle('QStyle', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#0f172a'), spaceBefore=10, spaceAfter=4)
            opt_style = ParagraphStyle('OptStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), leftIndent=15)

            # En-tête avec Logo
            logo_path = os.path.join("assets", "logo.png")
            if os.path.exists(logo_path):
                img = RLImage(logo_path, width=45, height=45)
                header_data = [[img, Paragraph(f"<b>TMY QUIZ MAKER</b><br/>Rapport de Quiz Résolu", title_style)]]
                header_table = Table(header_data, colWidths=[55, 485])
            else:
                header_data = [[Paragraph(f"<b>TMY QUIZ MAKER</b> - Rapport de Quiz", title_style)]]
                header_table = Table(header_data, colWidths=[540])

            header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(header_table)
            story.append(Spacer(1, 10))

            # Métadonnées dans le PDF
            score = self.session_data.get("score", "N/A")
            date_played = self.session_data.get("played_at") or self.session_data.get("date") or datetime.now().strftime("%d/%m/%Y %H:%M")
            
            meta_text = f"<b>Sujet :</b> {quiz_title} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Score :</b> {score} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date :</b> {date_played}"
            story.append(Paragraph(meta_text, meta_style))
            story.append(Spacer(1, 10))

            # Rendu de chaque question dans le PDF
            for idx, q in enumerate(self.questions, 1):
                q_text = q.get("question") or q.get("title") or f"Question {idx}"
                story.append(Paragraph(f"<b>Q{idx}. {q_text}</b>", q_style))

                options = q.get("options") or q.get("choices") or []
                user_ans = str(q.get("user_answer") or q.get("your_answer") or q.get("selected") or "Aucune").strip()
                correct_ans = str(q.get("correct_answer") or q.get("correct") or "").strip()

                if options:
                    for opt in options:
                        opt_str = str(opt).strip()
                        prefix = "• "
                        color_hex = "#334155"

                        if (opt_str.lower() == correct_ans.lower()) or (len(correct_ans) == 1 and opt_str.startswith(correct_ans)):
                            prefix = "✔ [BONNE RÉPONSE] "
                            color_hex = "#16a34a"
                        elif (opt_str.lower() == user_ans.lower()) or (len(user_ans) == 1 and opt_str.startswith(user_ans)):
                            prefix = "✖ [VOTRE CHOIX] "
                            color_hex = "#dc2626"

                        story.append(Paragraph(f"<font color='{color_hex}'>{prefix}{opt_str}</font>", opt_style))
                else:
                    story.append(Paragraph(f"<b>Votre choix :</b> {user_ans}", opt_style))
                    story.append(Paragraph(f"<b>Bonne réponse :</b> {correct_ans}", opt_style))

                story.append(Spacer(1, 6))

            doc.build(story)
            messagebox.showinfo("Export Réussi", f"Le rapport PDF a été généré avec succès :\n{file_path}")

        except Exception as e:
            messagebox.showerror("Erreur d'exportation", f"Erreur lors de la création du PDF : {str(e)}")