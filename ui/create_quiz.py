import customtkinter as ctk
import json
import os


def ouvrir_fenetre_creation():

    fenetre = ctk.CTkToplevel()

    fenetre.title("Créer un Quiz")

    fenetre.geometry("700x850")


    # -----------------------------
    # Fonction Enregistrer
    # -----------------------------
    def enregistrer_question():

        question = champ_question.get()
        a = reponse_a.get()
        b = reponse_b.get()
        c = reponse_c.get()
        d = reponse_d.get()
        correct = bonne_reponse.get()


        nouvelle_question = {
            "question": question,
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "correct": correct
        }


        # Créer le dossier data s'il n'existe pas
        if not os.path.exists("data"):
            os.makedirs("data")


        # Lire les questions existantes
        try:
            with open(
                "data/quizzes.json",
                "r",
                encoding="utf-8"
            ) as fichier:

                questions = json.load(fichier)

        except:
            questions = []


        # Ajouter la nouvelle question
        questions.append(nouvelle_question)


        # Sauvegarder
        with open(
            "data/quizzes.json",
            "w",
            encoding="utf-8"
        ) as fichier:

            json.dump(
                questions,
                fichier,
                indent=4,
                ensure_ascii=False
            )


        print("Question enregistrée avec succès !")


    # -----------------------------
    # Titre
    # -----------------------------
    titre = ctk.CTkLabel(
        fenetre,
        text="Créer un nouveau Quiz",
        font=("Castellar", 22, "bold")
    )

    titre.pack(pady=20)



    # -----------------------------
    # Question
    # -----------------------------
    label_question = ctk.CTkLabel(
        fenetre,
        text="Question :"
    )

    label_question.pack()


    champ_question = ctk.CTkEntry(
        fenetre,
        width=500
    )

    champ_question.pack(pady=10)



    # -----------------------------
    # Réponse A
    # -----------------------------
    label_a = ctk.CTkLabel(
        fenetre,
        text="Réponse A :"
    )

    label_a.pack()


    reponse_a = ctk.CTkEntry(
        fenetre,
        width=500
    )

    reponse_a.pack(pady=5)



    # -----------------------------
    # Réponse B
    # -----------------------------
    label_b = ctk.CTkLabel(
        fenetre,
        text="Réponse B :"
    )

    label_b.pack()


    reponse_b = ctk.CTkEntry(
        fenetre,
        width=500
    )

    reponse_b.pack(pady=5)



    # -----------------------------
    # Réponse C
    # -----------------------------
    label_c = ctk.CTkLabel(
        fenetre,
        text="Réponse C :"
    )

    label_c.pack()


    reponse_c = ctk.CTkEntry(
        fenetre,
        width=500
    )

    reponse_c.pack(pady=5)



    # -----------------------------
    # Réponse D
    # -----------------------------
    label_d = ctk.CTkLabel(
        fenetre,
        text="Réponse D :"
    )

    label_d.pack()


    reponse_d = ctk.CTkEntry(
        fenetre,
        width=500
    )

    reponse_d.pack(pady=5)



    # -----------------------------
    # Bonne réponse
    # -----------------------------
    label_correct = ctk.CTkLabel(
        fenetre,
        text="Bonne réponse :"
    )

    label_correct.pack(pady=5)


    bonne_reponse = ctk.CTkOptionMenu(
        fenetre,
        values=["A", "B", "C", "D"]
    )

    bonne_reponse.pack(pady=10)



    # -----------------------------
    # Bouton Enregistrer
    # -----------------------------
    bouton_enregistrer = ctk.CTkButton(
        fenetre,
        text="Enregistrer la question",
        command=enregistrer_question
    )

    bouton_enregistrer.pack(pady=25)