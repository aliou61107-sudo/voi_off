import whisper
import asyncio
import edge_tts
from deep_translator import GoogleTranslator
from pydub import AudioSegment
import os
import re

VOIX_MAP = {
    'microsoft_henri': 'fr-FR-HenriNeural',
    'microsoft_denise': 'fr-FR-DeniseNeural',
    'microsoft_antoine': 'fr-CA-AntoineNeural',
    'microsoft_sylvie': 'fr-CA-SylvieNeural'
}

def nettoyer_texte(texte):
    texte = re.sub(r'\s+', ' ', texte)
    return texte.strip()

def traduire_segment(texte):
    try:
        traducteur = GoogleTranslator(source='en', target='fr')
        return traducteur.translate(texte)
    except:
        return texte

async def _generer_segment_async(texte, voix_nom, chemin):
    communicate = edge_tts.Communicate(texte, voix_nom)
    await communicate.save(chemin)

def transcrire_et_traduire(chemin_audio, voix, chemin_sortie):
    nom_voix = VOIX_MAP.get(voix, 'fr-FR-HenriNeural')

    # Etape 1 — Transcription avec timestamps
    print("Transcription en cours...")
    model = whisper.load_model("tiny")
    result = model.transcribe(
        chemin_audio,
        language="en",
        word_timestamps=False,
        verbose=False
    )

    segments = result["segments"]
    print(f"{len(segments)} segments detectes")

    if not segments:
        raise ValueError("Aucun segment detecte dans l'audio")

    # Etape 2 — Traduction et generation par segment
    audio_final = AudioSegment.silent(duration=0)
    derniere_fin = 0

    for i, segment in enumerate(segments):
        debut_ms = int(segment["start"] * 1000)
        fin_ms = int(segment["end"] * 1000)
        duree_ms = fin_ms - debut_ms
        texte_en = nettoyer_texte(segment["text"])

        if not texte_en:
            # Segment vide — ajouter silence
            silence = AudioSegment.silent(duration=duree_ms)
            audio_final += silence
            derniere_fin = fin_ms
            continue

        # Traduire le segment
        texte_fr = traduire_segment(texte_en)
        print(f"Segment {i+1}/{len(segments)}: {texte_fr[:50]}...")

        # Generer la voix pour ce segment
        chemin_temp = chemin_sortie.replace('.mp3', f'_seg{i}.mp3')
        asyncio.run(_generer_segment_async(texte_fr, nom_voix, chemin_temp))

        # Charger l'audio genere
        segment_audio = AudioSegment.from_mp3(chemin_temp)
        os.remove(chemin_temp)

        # Ajouter silence avant ce segment si necessaire
        if debut_ms > derniere_fin:
            silence = AudioSegment.silent(duration=debut_ms - derniere_fin)
            audio_final += silence

        # Ajuster la vitesse du segment pour correspondre a la duree originale
        if len(segment_audio) > 0 and duree_ms > 0:
            ratio = len(segment_audio) / duree_ms
            if ratio > 1.3:
                # Audio trop long — accelerer legerement
                segment_audio = segment_audio.speedup(playback_speed=min(ratio, 1.5))

        audio_final += segment_audio
        derniere_fin = debut_ms + len(segment_audio)

    # Sauvegarder l'audio final
    audio_final.export(chemin_sortie, format="mp3")
    print("Audio synchronise genere avec succes !")