import threading
import time
import pygame

pygame.mixer.init()

MUSIC = "assets/music/menu.mp3"


def start_music():
    try:
        pygame.mixer.music.load(MUSIC)
        pygame.mixer.music.set_volume(0.03)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Erreur musique :", e)


def stop_music():
    try:
        pygame.mixer.music.stop()
    except:
        pass


def resume_music():
    def _play():
        try:
            # Petite pause pour laisser le canal audio se libérer de la voix
            time.sleep(0.9)

            # Re-initialiser le mixer au cas où la voix l'a fermé
            pygame.mixer.quit()
            pygame.mixer.init()

            pygame.mixer.music.load(MUSIC)
            pygame.mixer.music.set_volume(0.03)
            pygame.mixer.music.play(-1)
            print("🎵 Musique de résultat lancée avec succès !")
        except Exception as e:
            print("Erreur relance musique :", e)

    # On lance la musique dans un thread séparé pour ne pas bloquer l'interface
    threading.Thread(target=_play, daemon=True).start()