import asyncio
import edge_tts
import re
from pydub import AudioSegment
import os

VOIX = {
    'microsoft_denise': 'fr-FR-DeniseNeural',
    'microsoft_henri': 'fr-FR-HenriNeural',
    'microsoft_sylvie': 'fr-CA-SylvieNeural',
    'microsoft_antoine': 'fr-CA-AntoineNeural'
}

def nettoyer_texte(texte):
    texte = texte.replace('...', ',')
    texte = texte.replace('—', ',')
    texte = re.sub(r'\n+', ' ', texte)
    texte = re.sub(r' +', ' ', texte)
    return texte.strip()

def decouper_texte(texte, taille=4500):
    # Decoupe le texte en morceaux en respectant les phrases
    morceaux = []
    while len(texte) > taille:
        # Cherche le dernier point avant la limite
        coupure = texte.rfind('.', 0, taille)
        if coupure == -1:
            coupure = taille
        morceaux.append(texte[:coupure+1].strip())
        texte = texte[coupure+1:].strip()
    if texte:
        morceaux.append(texte)
    return morceaux

async def _generer_async(texte, voix, chemin):
    communicate = edge_tts.Communicate(texte, voix)
    await communicate.save(chemin)

def generer(texte, voix, chemin):
    nom_voix = VOIX[voix]
    texte = nettoyer_texte(texte)
    morceaux = decouper_texte(texte)

    if len(morceaux) == 1:
        # Texte court — generation directe
        asyncio.run(_generer_async(morceaux[0], nom_voix, chemin))
    else:
        # Texte long — generation par morceaux puis assemblage
        fichiers_temp = []
        for i, morceau in enumerate(morceaux):
            chemin_temp = chemin.replace('.mp3', f'_part{i}.mp3')
            asyncio.run(_generer_async(morceau, nom_voix, chemin_temp))
            fichiers_temp.append(chemin_temp)

        # Assembler tous les morceaux en un seul MP3
        audio_final = AudioSegment.empty()
        for f in fichiers_temp:
            audio_final += AudioSegment.from_mp3(f)
            os.remove(f)  # Supprime le fichier temporaire

        audio_final.export(chemin, format="mp3")