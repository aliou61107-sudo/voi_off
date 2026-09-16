from gtts import gTTS

VOIX = {
    'gtts_masculin': 'ca',
    'gtts_feminin': 'fr'
}

def generer(texte, voix, chemin):
    tld = VOIX[voix]
    tts = gTTS(text=texte, lang='fr', tld=tld)
    tts.save(chemin)