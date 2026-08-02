"""
===========================================
TMY Quiz Maker
Version 5.3 (Correction de l'affichage du Sujet)

play_quiz.py - Interface de jeu moderne & dynamique
===========================================
"""

import customtkinter as ctk
import winsound
import uuid
from datetime import datetime

from voice import parler, parler_sequence, stop
from auth_client import session
from library_manager import LibraryManager
import ui.colors as colors
import ui.fonts as fonts

# Importation sécurisée du gestionnaire d'historique TMY
try:
    from data.history_manager import HistoryManager
    history_mgr = HistoryManager()
except Exception as e:
    print(f"⚠️ Impossible de charger HistoryManager : {e}")
    history_mgr = None


class PlayQuizPage(ctk.CTkFrame):

    def __init__(self, master, quiz, finish_callback, quiz_title="Quiz Solo", cancel_callback=None):
        super().__init__(master)

        # Extraction prioritaire du sujet / titre / niveau du quiz
        if isinstance(quiz, dict):
            self.quiz_title = quiz.get("sujet") or quiz.get("title") or quiz.get("quiz_title") or quiz_title
            self.quiz_niveau = quiz.get("niveau", "")
            self.quiz = quiz.get("questions", [])
        else:
            self.quiz = quiz
            self.quiz_title = quiz_title
            self.quiz_niveau = ""

        self.finish_callback = finish_callback
        self.cancel_callback = cancel_callback

        self.index = 0
        self.score = 0
        self.answered = False
        self.quiz_finished = False

        # Historique précis des choix de l'utilisateur pour le rapport PDF/Détails
        self.user_answers = {}

        self.total_time = 0
        self.question_times = []
        self.fast_answers = 0
        self.time_out = 0
        self.total_xp = 0
        self.combo = 0
        self.max_combo = 0
        self.current_time = 0
        self.remaining_time = 0
        self.timer_running = False
        self.can_answer = False

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=15)

        self.create_interface()
        self.load_question()

    # =========================================
    # Bruitages
    # =========================================
    def start_sound(self):
        winsound.Beep(1500, 400)

    def beep(self):
        winsound.Beep(1000, 200)

    def timeout_sound(self):
        winsound.Beep(500, 800)

    def correct_sound(self):
        winsound.Beep(1800, 200)

    def wrong_sound(self):
        winsound.Beep(350, 400)

    # =========================================
    # Création de l'interface
    # =========================================
    def create_interface(self):
        # -------------------------------------
        # 1. EN-TÊTE DASHBOARD
        # -------------------------------------
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))

        # Affichage du VRAI SUJET du Quiz + niveau
        titre_affiche = f"🧠 {self.quiz_title}"
        if self.quiz_niveau:
            titre_affiche += f"  •  {self.quiz_niveau}"

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text=titre_affiche,
            font=("Arial", 16, "bold"),
            text_color="#1F6AA5"
        )
        self.title_lbl.pack(side="left")

        # Bouton Annuler (avec confirmation) : n'enregistre ni l'XP ni l'historique
        self.cancel_button = ctk.CTkButton(
            self.header_frame,
            text="✖ Annuler",
            font=("Arial", 12, "bold"),
            width=90,
            height=30,
            fg_color="#3A3D52",
            hover_color="#C62828",
            command=self.demander_annulation
        )
        self.cancel_button.pack(side="left", padx=(15, 0))

        # Statut Combo / XP à droite (le classement/rang a été retiré : quiz solo, pas de sens)
        self.stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_frame.pack(side="right")

        self.combo_label = ctk.CTkLabel(
            self.stats_frame,
            text="🔥 x0",
            font=("Arial", 13, "bold"),
            text_color="#FF9800"
        )
        self.combo_label.pack(side="left", padx=(0, 10))

        self.xp_label = ctk.CTkLabel(
            self.stats_frame,
            text="⚡ 0 XP",
            font=("Arial", 13, "bold"),
            text_color="#FFD700"
        )
        self.xp_label.pack(side="left")

        # -------------------------------------
        # 2. PROGRESSION & CHRONOMÈTRE
        # -------------------------------------
        self.info_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.info_bar.pack(fill="x", pady=(0, 5))

        self.counter = ctk.CTkLabel(
            self.info_bar,
            text="Question 1/10",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        self.counter.pack(side="left")

        self.timer_label = ctk.CTkLabel(
            self.info_bar,
            text="⏱ 0s",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.timer_label.pack(side="right")

        # Barre de progression du temps
        self.timer_bar = ctk.CTkProgressBar(
            self.container,
            height=8,
            corner_radius=4,
            progress_color="#1F6AA5",
            fg_color="#1E222D"
        )
        self.timer_bar.set(1)
        self.timer_bar.pack(fill="x", pady=(2, 15))

        # -------------------------------------
        # 3. CARTE DE LA QUESTION
        # -------------------------------------
        self.question_card = ctk.CTkFrame(
            self.container,
            fg_color="#1E222D",
            corner_radius=16,
            border_width=1,
            border_color="#2B303C"
        )
        self.question_card.pack(fill="x", ipady=15, pady=(0, 15))

        self.question = ctk.CTkLabel(
            self.question_card,
            text="Chargement de la question...",
            font=("Arial", 15, "bold"),
            text_color="#FFFFFF",
            wraplength=650,
            justify="center"
        )
        self.question.pack(expand=True, padx=25, pady=15)

        # -------------------------------------
        # 4. GRILLE DES RÉPONSES
        # -------------------------------------
        self.answers_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.answers_frame.pack(fill="both", expand=True)

        self.buttons = {}
        self.button_frames = {}

        for lettre in ["A", "B", "C", "D"]:
            btn_frame = ctk.CTkFrame(
                self.answers_frame,
                fg_color="#1E222D",
                corner_radius=12,
                border_width=1,
                border_color="#2B303C"
            )
            btn_frame.pack(fill="x", pady=5)

            badge = ctk.CTkLabel(
                btn_frame,
                text=lettre,
                font=("Arial", 12, "bold"),
                width=32,
                height=32,
                corner_radius=8,
                fg_color="#2B2D42",
                text_color="#FFFFFF"
            )
            badge.pack(side="left", padx=10, pady=8)

            bouton = ctk.CTkButton(
                btn_frame,
                text="",
                font=("Arial", 13),
                anchor="w",
                fg_color="transparent",
                hover_color="#252A37",
                text_color="#FFFFFF",
                command=lambda l=lettre: self.check_answer(l)
            )
            bouton.pack(side="left", fill="both", expand=True, padx=(0, 10))

            self.buttons[lettre] = bouton
            self.button_frames[lettre] = (btn_frame, badge)

        # -------------------------------------
        # 5. BOUTON SUIVANT
        # -------------------------------------
        self.next_button = ctk.CTkButton(
            self.container,
            text="QUESTION SUIVANTE →",
            font=("Arial", 13, "bold"),
            height=42,
            corner_radius=10,
            fg_color="#1F6AA5",
            hover_color="#144870",
            command=self.next_question
        )
        self.next_button.pack(fill="x", pady=(15, 0))

    # =========================================
    # Logique du temps & Questions
    # =========================================
    def calculate_time(self, question):
        texte = (
            question.get("question", "")
            + question.get("A", "")
            + question.get("B", "")
            + question.get("C", "")
            + question.get("D", "")
        )
        temps = 15
        if len(texte) > 200:
            temps += 10
        elif len(texte) > 100:
            temps += 5

        difficulte = question.get("difficulty", "medium")
        if difficulte == "hard":
            temps += 10
        elif difficulte == "easy":
            temps -= 3

        return max(10, min(60, temps))

    def calculate_live_rank(self):
        accuracy = (self.score / (self.index + 1)) if self.index >= 0 else 1.0
        
        if accuracy >= 0.85 and self.combo >= 2:
            return "🥇 1er"
        elif accuracy >= 0.60:
            return "🥈 2ème"
        elif accuracy >= 0.40:
            return "🥉 3ème"
        else:
            return "📊 4ème"

    def load_question(self):
        self.answered = False

        if self.quiz_finished:
            return

        if self.index >= len(self.quiz):
            self.finish_quiz()
            return

        question = self.quiz[self.index]

        self.counter.configure(text=f"Question {self.index + 1} / {len(self.quiz)}")
        self.combo_label.configure(text=f"🔥 x{self.combo}")
        self.xp_label.configure(text=f"⚡ {self.total_xp} XP")

        for lettre in ["A", "B", "C", "D"]:
            self.buttons[lettre].configure(text="", state="normal")
            frame, badge = self.button_frames[lettre]
            frame.configure(fg_color="#1E222D", border_color="#2B303C")
            badge.configure(fg_color="#2B2D42")

        texte_question = question.get("question", "")
        self.question.configure(text=texte_question)

        self.current_time = self.calculate_time(question)
        self.remaining_time = self.current_time
        self.timer_bar.set(1)
        self.update_timer_display()

        self.can_answer = False
        for btn in self.buttons.values():
            btn.configure(state="disabled")

        self.audio_cache = {
            "A": [("Petit A", 0.4), (question.get("A", ""), 0.4)],
            "B": [("Petit B", 0.4), (question.get("B", ""), 0.4)],
            "C": [("Petit C", 0.4), (question.get("C", ""), 0.4)],
            "D": [("Petit D", 0.4), (question.get("D", ""), 0.4)]
        }

        parler_sequence(
            [(texte_question, 0.3)],
            callback=lambda: self.after(0, self.lire_etape_A)
        )

    def lire_etape_A(self):
        if self.answered or self.quiz_finished: return
        self.buttons["A"].configure(text=self.quiz[self.index].get("A", ""))
        parler_sequence(self.audio_cache["A"], callback=lambda: self.after(0, self.lire_etape_B))

    def lire_etape_B(self):
        if self.answered or self.quiz_finished: return
        self.buttons["B"].configure(text=self.quiz[self.index].get("B", ""))
        parler_sequence(self.audio_cache["B"], callback=lambda: self.after(0, self.lire_etape_C))

    def lire_etape_C(self):
        if self.answered or self.quiz_finished: return
        self.buttons["C"].configure(text=self.quiz[self.index].get("C", ""))
        parler_sequence(self.audio_cache["C"], callback=lambda: self.after(0, self.lire_etape_D))

    def lire_etape_D(self):
        if self.answered or self.quiz_finished: return
        self.buttons["D"].configure(text=self.quiz[self.index].get("D", ""))
        parler_sequence(self.audio_cache["D"], callback=lambda: self.after(0, self.lire_etape_fin))

    def lire_etape_fin(self):
        if self.answered or self.quiz_finished: return
        texte_fin = f"Vous disposez maintenant de {self.current_time} secondes pour répondre"
        parler_sequence([(texte_fin, 0)], callback=lambda: self.after(0, self.start_timer))

    def start_timer(self):
        self.start_sound()
        self.can_answer = True
        for btn in self.buttons.values():
            btn.configure(state="normal")
        self.timer_running = True
        self.count_down()

    def count_down(self):
        if not self.timer_running or self.answered:
            return

        if self.remaining_time <= 0:
            self.timer_running = False
            self.timeout_sound()
            
            # Enregistrement "Non répondue" en cas de timeout
            self.user_answers[self.index] = "Non répondue"
            
            bonne = self.quiz[self.index]["correct"]
            parler(f"Temps écoulé. La bonne réponse était {bonne}.")
            self.time_out += 1
            self.combo = 0
            self.check_timeout()
            return

        self.update_timer_display()

        if 0 < self.remaining_time <= 5:
            self.beep()

        self.remaining_time -= 1
        self.after(1000, self.count_down)

    def check_timeout(self):
        if self.answered:
            return
        self.answered = True

        bonne = self.quiz[self.index]["correct"]
        frame, badge = self.button_frames[bonne]
        frame.configure(fg_color="#1E4620", border_color="#2E7D32")
        badge.configure(fg_color="#2E7D32")

        for btn in self.buttons.values():
            btn.configure(state="disabled")

        if self.index == len(self.quiz) - 1:
            self.after(1000, self.finish_quiz)

    def check_answer(self, lettre):
        stop()
        if not self.can_answer or self.answered:
            return

        self.answered = True
        self.timer_running = False
        self.stop_timer()

        # Enregistrement de la lettre choisie
        self.user_answers[self.index] = lettre

        temps_utilise = self.current_time - self.remaining_time

        ratio = self.remaining_time / self.current_time
        xp = int(200 + (800 * ratio))

        difficulty = self.quiz[self.index].get("difficulty", "medium")
        multiplier = 1.6 if difficulty == "hard" else (1.0 if difficulty == "easy" else 1.3)
        xp = int(xp * multiplier)

        self.total_time += temps_utilise
        self.question_times.append(temps_utilise)

        if temps_utilise <= (self.current_time / 2):
            self.fast_answers += 1

        bonne = self.quiz[self.index]["correct"]

        if lettre == bonne:
            self.score += 1
            self.combo += 1
            if self.combo > self.max_combo:
                self.max_combo = self.combo

            bonus_table = {2: 50, 3: 100, 4: 150, 5: 250, 6: 350, 7: 500}
            bonus = bonus_table.get(self.combo, 700 if self.combo >= 8 else 0)
            self.total_xp += xp + bonus

            frame, badge = self.button_frames[lettre]
            frame.configure(fg_color="#1E4620", border_color="#2E7D32")
            badge.configure(fg_color="#2E7D32")

            self.correct_sound()
            parler("Bonne réponse.")
        else:
            frame_w, badge_w = self.button_frames[lettre]
            frame_w.configure(fg_color="#4A151B", border_color="#C62828")
            badge_w.configure(fg_color="#C62828")

            frame_c, badge_c = self.button_frames[bonne]
            frame_c.configure(fg_color="#1E4620", border_color="#2E7D32")
            badge_c.configure(fg_color="#2E7D32")

            self.combo = 0
            self.wrong_sound()
            parler(f"Mauvaise réponse. La bonne réponse était {bonne}.")

        self.combo_label.configure(text=f"🔥 x{self.combo}")
        self.xp_label.configure(text=f"⚡ {self.total_xp} XP")

        for btn in self.buttons.values():
            btn.configure(state="disabled")

        if self.index == len(self.quiz) - 1:
            self.after(850, self.next_question)

    def next_question(self):
        if not self.answered:
            return
        self.timer_running = False
        self.index += 1

        if self.index >= len(self.quiz):
            self.finish_quiz()
        else:
            self.load_question()

    def build_detailed_questions(self):
        """
        Transforme la liste brute du quiz en objets complets contenant :
        - question
        - options (A, B, C, D avec leur texte)
        - user_answer (Le texte complet choisi par l'utilisateur)
        - correct_answer (Le texte complet de la bonne réponse)
        - is_correct (Booleen)
        """
        formatted = []
        for idx, q in enumerate(self.quiz):
            user_key = self.user_answers.get(idx, "Non répondue")
            correct_key = q.get("correct", "A")

            # Construction de la liste des 4 options
            options = []
            for letter in ["A", "B", "C", "D"]:
                val = q.get(letter, "")
                if val:
                    text_opt = val if val.startswith(f"{letter}.") else f"{letter}. {val}"
                    options.append(text_opt)

            # Récupération des réponses textuelles complètes
            if user_key in ["A", "B", "C", "D"]:
                u_text = q.get(user_key, user_key)
                user_answer = u_text if u_text.startswith(f"{user_key}.") else f"{user_key}. {u_text}"
            else:
                user_answer = "Non répondue"

            c_text = q.get(correct_key, correct_key)
            correct_answer = c_text if c_text.startswith(f"{correct_key}.") else f"{correct_key}. {c_text}"

            is_correct = (user_key == correct_key)

            formatted.append({
                "question": q.get("question", f"Question {idx+1}"),
                "options": options,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

        return formatted

    def finish_quiz(self):
        if self.quiz_finished:
            return

        self.quiz_finished = True
        self.timer_running = False
        total_questions = len(self.quiz)

        average_time = round(self.total_time / total_questions, 1) if total_questions > 0 else 0

        # Construction des questions structurées
        detailed_questions = self.build_detailed_questions()

        # Enregistrement propre dans history.json via HistoryManager (sert à l'anti-répétition IA)
        if history_mgr is not None:
            try:
                hist_data = history_mgr.create_quiz_data(
                    sujet=self.quiz_title,
                    niveau=self.quiz_niveau or "Moyen",
                    score=self.score,
                    total=total_questions,
                    xp=self.total_xp,
                    rank=self.calculate_live_rank(),
                    average_time=average_time,
                    questions=detailed_questions,
                    mode="Solo"
                )
                history_mgr.save_quiz(hist_data)
            except Exception as e:
                print(f"⚠️ Erreur lors de la sauvegarde dans l'historique : {e}")

        # Enregistrement dans LibraryManager — c'est CE fichier que l'écran
        # "Mes Parties" (library_hub.py) lit réellement pour l'affichage.
        details = {"correct": [], "wrong": [], "unanswered": []}
        for q in detailed_questions:
            if q["user_answer"] == "Non répondue":
                details["unanswered"].append({"question": q["question"]})
            elif q["is_correct"]:
                details["correct"].append({
                    "question": q["question"],
                    "your_answer": q["user_answer"],
                })
            else:
                details["wrong"].append({
                    "question": q["question"],
                    "your_answer": q["user_answer"],
                    "correct_answer": q["correct_answer"],
                })

        try:
            LibraryManager.save_game_session({
                "session_id": f"SESSION_{uuid.uuid4().hex[:12]}",
                "quiz_title": self.quiz_title,
                "niveau": self.quiz_niveau,
                "mode": "Solo",
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "score": f"{self.score}/{total_questions}",
                "percentage": int((self.score / total_questions) * 100) if total_questions > 0 else 0,
                "xp": self.total_xp,
                "details": details,
            })
        except Exception as e:
            print(f"⚠️ Erreur lors de l'enregistrement dans Mes Parties : {e}")

        # Crédite l'XP gagnée sur le compte connecté (visible sur le badge de l'accueil,
        # et dans les statistiques des Paramètres).
        if session.est_connecte():
            try:
                session.crediter_xp(self.total_xp, self.score)
            except Exception as e:
                print(f"⚠️ Erreur lors du crédit d'XP : {e}")

        # Inclusion explicite du sujet dans le dictionnaire résultat
        quiz_data = {
            "sujet": self.quiz_title,
            "quiz_title": self.quiz_title,
            "title": self.quiz_title,
            "niveau": self.quiz_niveau,
            "questions": detailed_questions,
            "average_time": average_time,
            "total_time": self.total_time,
            "fast_answers": self.fast_answers,
            "time_out": self.time_out,
            "xp": self.calculate_xp()
        }

        parler(f"Quiz terminé. Vous avez obtenu {self.score} bonnes réponses sur {total_questions}.")

        self.finish_callback(
            self.score,
            total_questions,
            self.total_xp,
            self.max_combo,
            average_time,
            quiz_data
        )

    def calculate_xp(self):
        xp = self.score * 10 + self.fast_answers * 5
        if self.time_out == 0:
            xp += 20
        return xp

    def stop_timer(self):
        self.timer_running = False

    # =========================================
    # Annulation du quiz en cours
    # =========================================
    def demander_annulation(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Annuler le quiz ?")
        dialog.geometry("360x180")
        dialog.configure(fg_color="#1E222D")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Voulez-vous vraiment annuler ce quiz ?",
            font=("Arial", 13, "bold"),
            text_color="#FFFFFF",
            wraplength=300,
        ).pack(pady=(24, 6), padx=20)

        ctk.CTkLabel(
            dialog,
            text="Votre progression et l'XP gagnée ne seront pas enregistrées.",
            font=("Arial", 11),
            text_color="#AAAAAA",
            wraplength=300,
            justify="center",
        ).pack(pady=(0, 18), padx=20)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="Continuer le quiz", fg_color="#2B2D42", hover_color="#3A3D52",
            width=140, command=dialog.destroy,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_row, text="Annuler le quiz", fg_color="#C62828", hover_color="#8E1E1E",
            width=140, command=lambda: self._confirmer_annulation(dialog),
        ).pack(side="left", padx=8)

    def _confirmer_annulation(self, dialog):
        dialog.destroy()

        # Coupe la voix de manière sécurisée pour éviter tout blocage silencieux
        try:
            stop()
        except Exception as e:
            print(f"⚠️ Erreur vocale ignorée lors de l'annulation : {e}")

        # Stoppe la logique du jeu en cours
        self.answered = True
        self.timer_running = False
        self.quiz_finished = True

        # Retourne à l'accueil via un micro-délai (sécurité anti-crash Tkinter)
        if self.cancel_callback:
            self.after(50, self.cancel_callback)

    def update_timer_display(self):
        if self.current_time == 0:
            return

        ratio = max(0, self.remaining_time / self.current_time)
        self.timer_bar.set(ratio)
        self.timer_label.configure(text=f"⏱ {self.remaining_time}s")
        self.update_timer_color(ratio)

    def update_timer_color(self, ratio):
        if ratio <= 0.25:
            self.timer_label.configure(text_color="#FF5252")
            self.timer_bar.configure(progress_color="#FF5252")
        elif ratio <= 0.50:
            self.timer_label.configure(text_color="#FF9800")
            self.timer_bar.configure(progress_color="#FF9800")
        else:
            self.timer_label.configure(text_color="#1F6AA5")
            self.timer_bar.configure(progress_color="#1F6AA5")