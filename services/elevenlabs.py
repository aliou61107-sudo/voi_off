from elevenlabs.client import ElevenLabs
from elevenlabs import save

VOIX = {
    'eleven_adam': {
        'voice_id': 'pNInz6obpgDQGcFmaJgB',
        'stability': 0.75,
        'similarity_boost': 0.85,
        'style': 0.40
    },
    'eleven_rachel': {
        'voice_id': '21m00Tcm4TlvDq8ikWAM',
        'stability': 0.65,
        'similarity_boost': 0.80,
        'style': 0.35
    },
    'eleven_sage': {
        'voice_id': 'onwK4e9ZLuTAKqWW03F9',
        'stability': 0.85,
        'similarity_boost': 0.90,
        'style': 0.20
    }
}

def generer(texte, voix, chemin, api_key):
    config = VOIX[voix]
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id=config['voice_id'],
        text=texte,
        model_id="eleven_multilingual_v2",
        voice_settings={
            "stability": config['stability'],
            "similarity_boost": config['similarity_boost'],
            "style": config['style'],
            "use_speaker_boost": True
        }
    )
    save(audio, chemin)