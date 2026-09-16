import whisper
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import os
import uuid
import time


# ═══════════════════════════════════════════
# EXTRACTION DU SAMPLE DE VOIX
# ═══════════════════════════════════════════

def extraire_sample_voix(chemin_audio, duree_secondes=60):
    """
    Extrait un échantillon de voix (~60s) pour le clonage ElevenLabs.
    On évite les 3 premières secondes (souvent musique/intro).
    """
    audio = AudioSegment.from_file(chemin_audio)
    debut_ms = 3000
    fin_ms = min(debut_ms + duree_secondes * 1000, len(audio))
    sample = audio[debut_ms:fin_ms]

    chemin_sample = chemin_audio.replace('.mp3', f'_sample_{uuid.uuid4().hex[:6]}.mp3')
    sample.export(chemin_sample, format='mp3')
    print(f"Sample extrait : {(fin_ms - debut_ms) / 1000:.1f}s → {chemin_sample}")
    return chemin_sample


# ═══════════════════════════════════════════
# CLONAGE ELEVENLABS
# ═══════════════════════════════════════════

def creer_clone_elevenlabs(chemin_sample, api_key):
    """
    Cree un clone de voix temporaire via ElevenLabs Instant Voice Cloning.
    Utilise client.voices.ivc.create() (SDK v2.x).
    Retourne (client, voice_id) pour reutilisation et suppression ulterieure.
    """
    client = ElevenLabs(api_key=api_key)
    nom_clone = f"clone_temp_{uuid.uuid4().hex[:8]}"

    response = client.voices.ivc.create(
        name=nom_clone,
        files=[chemin_sample],
        description="Voix clonee temporaire — traduction automatique"
    )

    print(f"Clone ElevenLabs cree : {response.voice_id}")
    return client, response.voice_id


def supprimer_clone(client, voice_id):
    """Supprime le clone temporaire ElevenLabs après génération."""
    try:
        client.voices.delete(voice_id)
        print(f"Clone {voice_id} supprimé de ElevenLabs")
    except Exception as e:
        print(f"Avertissement : impossible de supprimer le clone {voice_id} : {e}")


# ═══════════════════════════════════════════
# DÉCOUPAGE DE TEXTE (CHUNKS)
# ═══════════════════════════════════════════

def decouper_texte(texte, taille_max=4000):
    """
    Découpe un texte en segments en respectant les frontières de phrase.
    Utilisé pour la traduction et la génération TTS sur longs contenus.
    """
    if len(texte) <= taille_max:
        return [texte]

    morceaux = []
    while len(texte) > taille_max:
        # Chercher la dernière phrase complète avant la limite
        coupure = texte.rfind('. ', 0, taille_max)
        if coupure == -1:
            coupure = texte.rfind(' ', 0, taille_max)
        if coupure == -1:
            coupure = taille_max
        morceaux.append(texte[:coupure + 1].strip())
        texte = texte[coupure + 1:].strip()

    if texte:
        morceaux.append(texte)

    return morceaux


# ═══════════════════════════════════════════
# TRADUCTION EN→FR
# ═══════════════════════════════════════════

def traduire_texte_long(texte, source='en', target='fr'):
    """
    Traduit un texte de n'importe quelle longueur en le découpant en segments
    de 4500 caractères max (limite de deep_translator / Google Translate).
    """
    morceaux = decouper_texte(texte, taille_max=4500)
    print(f"Traduction : {len(morceaux)} segment(s) à traduire ({len(texte)} caractères au total)")

    traduits = []
    for i, morceau in enumerate(morceaux):
        try:
            t = GoogleTranslator(source=source, target=target).translate(morceau)
            traduits.append(t if t else morceau)
            # Pause pour éviter le rate limiting Google
            if len(morceaux) > 1:
                time.sleep(0.6)
        except Exception as e:
            print(f"Erreur traduction segment {i + 1}/{len(morceaux)} : {e}")
            traduits.append(morceau)  # Conserver le texte original si échec

    return ' '.join(traduits)


# ═══════════════════════════════════════════
# GÉNÉRATION TTS AVEC VOIX CLONÉE
# ═══════════════════════════════════════════

def generer_tts_clone_chunks(texte, voice_id, api_key, chemin_sortie):
    """
    Génère l'audio TTS en français avec la voix clonée.
    Gère automatiquement le découpage en chunks pour les longs textes (2h+).
    """
    client = ElevenLabs(api_key=api_key)
    morceaux = decouper_texte(texte, taille_max=3500)
    print(f"TTS : {len(morceaux)} chunk(s) à générer")

    VOICE_SETTINGS = {
        "stability": 0.75,
        "similarity_boost": 0.90,
        "style": 0.25,
        "use_speaker_boost": True
    }

    if len(morceaux) == 1:
        # Texte court — génération directe
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=morceaux[0],
            model_id="eleven_multilingual_v2",
            voice_settings=VOICE_SETTINGS
        )
        save(audio, chemin_sortie)
        return

    # Texte long — génération par chunks puis assemblage
    fichiers_temp = []
    for i, morceau in enumerate(morceaux):
        print(f"  TTS chunk {i + 1}/{len(morceaux)}...")
        chemin_temp = chemin_sortie.replace('.mp3', f'_tts_{i}.mp3')

        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=morceau,
            model_id="eleven_multilingual_v2",
            voice_settings=VOICE_SETTINGS
        )
        save(audio, chemin_temp)
        fichiers_temp.append(chemin_temp)

        # Pause entre les appels API
        if i < len(morceaux) - 1:
            time.sleep(1.2)

    # Assembler tous les chunks en un seul MP3
    print("Assemblage des chunks audio...")
    audio_final = AudioSegment.empty()
    for f in fichiers_temp:
        audio_final += AudioSegment.from_mp3(f)
        os.remove(f)

    audio_final.export(chemin_sortie, format='mp3')
    print(f"Audio final exporté : {chemin_sortie}")


# ═══════════════════════════════════════════
# PIPELINE PRINCIPAL
# ═══════════════════════════════════════════

def cloner_et_traduire(chemin_audio, chemin_sortie, api_key, callback_progression=None):
    """
    Pipeline complet : clone la voix originale, transcrit l'audio en anglais,
    traduit en français et génère le TTS avec la voix clonée.

    Supporte les vidéos de toute durée (2h+) via chunking automatique.

    Args:
        chemin_audio (str): Chemin du fichier audio source (anglais, MP3)
        chemin_sortie (str): Chemin de sortie pour l'audio traduit (MP3)
        api_key (str): Clé API ElevenLabs
        callback_progression (callable): Fonction(etape, message) pour les MAJ de statut
    """
    voice_id = None
    client_eleven = None
    chemin_sample = None

    def progression(etape, message):
        print(f"[{etape.upper()}] {message}")
        if callback_progression:
            callback_progression(etape, message)

    try:
        # ── Étape 1 : Extraction du sample de voix ──────────────────────────
        progression("extraction", "Extraction de l'echantillon vocal (60s)...")
        chemin_sample = extraire_sample_voix(chemin_audio)

        # ── Étape 2 : Clonage ElevenLabs ────────────────────────────────────
        progression("clonage", "Clonage de la voix originale via ElevenLabs...")
        client_eleven, voice_id = creer_clone_elevenlabs(chemin_sample, api_key)

        # ── Étape 3 : Transcription Whisper (modèle base) ───────────────────
        progression("transcription", "Transcription audio en cours (modele Whisper base)...")
        model = whisper.load_model("base")
        result = model.transcribe(
            chemin_audio,
            language="en",
            verbose=False
        )
        texte_en = result["text"].strip()

        if not texte_en:
            raise ValueError("Aucun texte detecte dans l'audio — verifiez que la video contient bien de la parole en anglais.")

        print(f"Transcription terminee : {len(texte_en)} caracteres")

        # ── Étape 4 : Traduction EN→FR ───────────────────────────────────────
        progression("traduction", f"Traduction EN->FR en cours ({len(texte_en)} caracteres)...")
        texte_fr = traduire_texte_long(texte_en)
        print(f"Traduction terminee : {len(texte_fr)} caracteres")

        # ── Étape 5 : Génération TTS avec voix clonée ───────────────────────
        nb_chunks = max(1, len(texte_fr) // 3500)
        progression("generation", f"Generation TTS avec voix clonee (~{nb_chunks} chunk(s))...")
        generer_tts_clone_chunks(texte_fr, voice_id, api_key, chemin_sortie)

        progression("termine", "Traduction terminee avec succes !")

    finally:
        # Nettoyage systématique même en cas d'erreur
        if chemin_sample and os.path.exists(chemin_sample):
            os.remove(chemin_sample)

        if client_eleven and voice_id:
            supprimer_clone(client_eleven, voice_id)
