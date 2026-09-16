
from flask import Flask, render_template, request, send_file, jsonify
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from services import document_service, video_service
import yt_dlp
import os
import uuid
import asyncio
import threading
import edge_tts
from gtts import gTTS

app = Flask(__name__)
import tempfile
tempfile.tempdir = 'D:\\voix_off_v2\\static\\uploads'
taches = {}

AUDIO_DIR = os.path.join('D:\\voix_off_v2', 'static', 'audio')
UPLOAD_DIR = os.path.join('D:\\voix_off_v2', 'static', 'uploads')
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ELEVEN_API_KEY = "sk_98650a8bf3b413fec9d7b00e2f05ee0030cd0978b335d35f"

async def generer_edge_tts(texte, voix, chemin):
    communicate = edge_tts.Communicate(texte, voix)
    await communicate.save(chemin)

def generer_eleven(texte, voice_id, settings, chemin):
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=texte,
        model_id="eleven_multilingual_v2",
        voice_settings=settings
    )
    save(audio, chemin)

def generer_voix(texte, voix, chemin):
    if voix == 'eleven_adam':
        generer_eleven(texte, "pNInz6obpgDQGcFmaJgB",
            {"stability": 0.75, "similarity_boost": 0.85, "style": 0.40, "use_speaker_boost": True}, chemin)
    elif voix == 'eleven_rachel':
        generer_eleven(texte, "21m00Tcm4TlvDq8ikWAM",
            {"stability": 0.65, "similarity_boost": 0.80, "style": 0.35, "use_speaker_boost": True}, chemin)
    elif voix == 'eleven_sage':
        generer_eleven(texte, "onwK4e9ZLuTAKqWW03F9",
            {"stability": 0.85, "similarity_boost": 0.90, "style": 0.20, "use_speaker_boost": True}, chemin)
    elif voix == 'eleven_daniel':
        generer_eleven(texte, "onwK4e9ZLuTAKqWW03F9",
            {"stability": 0.85, "similarity_boost": 0.90, "style": 0.15, "use_speaker_boost": True}, chemin)
    elif voix == 'microsoft_henri':
        asyncio.run(generer_edge_tts(texte, 'fr-FR-HenriNeural', chemin))
    elif voix == 'microsoft_denise':
        asyncio.run(generer_edge_tts(texte, 'fr-FR-DeniseNeural', chemin))
    elif voix == 'microsoft_antoine':
        asyncio.run(generer_edge_tts(texte, 'fr-CA-AntoineNeural', chemin))
    elif voix == 'microsoft_sylvie':
        asyncio.run(generer_edge_tts(texte, 'fr-CA-SylvieNeural', chemin))
    elif voix == 'gtts_masculin':
        tts = gTTS(text=texte, lang='fr', tld='ca')
        tts.save(chemin)
    elif voix == 'gtts_feminin':
        tts = gTTS(text=texte, lang='fr', tld='fr')
        tts.save(chemin)
    else:
        raise ValueError("Voix inconnue !")

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/generer', methods=['POST'])
def generer():
    texte = request.form.get('texte', '')
    voix = request.form.get('voix', 'microsoft_henri')
    if not texte.strip():
        return jsonify({"erreur": "Texte vide !"}), 400
    nom_fichier = f"{uuid.uuid4()}.mp3"
    chemin = os.path.join(AUDIO_DIR, nom_fichier)
    try:
        generer_voix(texte, voix, chemin)
        return jsonify({"fichier": nom_fichier})
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500

@app.route('/livre-audio', methods=['POST'])
def livre_audio():
    if 'document' not in request.files:
        return jsonify({"erreur": "Aucun fichier envoye !"}), 400
    fichier = request.files['document']
    voix = request.form.get('voix', 'microsoft_henri')
    if fichier.filename == '':
        return jsonify({"erreur": "Fichier vide !"}), 400
    try:
        texte = document_service.extraire_texte(fichier, fichier.filename)
        if not texte:
            return jsonify({"erreur": "Document vide ou illisible !"}), 400
        texte = texte[:50000]
        nom_fichier = f"{uuid.uuid4()}.mp3"
        chemin = os.path.join(AUDIO_DIR, nom_fichier)
        generer_voix(texte, voix, chemin)
        return jsonify({"fichier": nom_fichier})
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500

@app.route('/traduire-video', methods=['POST'])
def traduire_video():
    voix = request.form.get('voix', 'microsoft_henri')
    youtube_url = request.form.get('youtube_url', '')
    video_file = request.files.get('video')
    format_sortie = request.form.get('format', 'mp4')

    tache_id = str(uuid.uuid4())
    taches[tache_id] = {"statut": "en_cours", "fichier": None, "erreur": None}

    nom_audio = f"{uuid.uuid4()}.mp3"
    nom_video = f"{uuid.uuid4()}.mp4"
    chemin_audio_final = os.path.join(AUDIO_DIR, nom_audio)
    chemin_video_final = os.path.join(AUDIO_DIR, nom_video)
    chemin_audio_temp = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp3")

    # Sauvegarder le fichier video si uploade
    chemin_video_sauvegarde = None
    if video_file:
        chemin_video_sauvegarde = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_upload.mp4")
        video_file.save(chemin_video_sauvegarde)

    def traiter_en_arriere_plan():
        chemin_video_local = None  # variable locale propre

        try:
            if youtube_url:
                # Telecharger video YouTube
                chemin_video_local = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp4")
                ydl_opts = {
                    'format': 'best[ext=mp4]',
                    'outtmpl': chemin_video_local,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])

                # Extraire audio
                ydl_opts_audio = {
                    'format': 'bestaudio/best',
                    'outtmpl': chemin_audio_temp.replace('.mp3', ''),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                }
                with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                    ydl.download([youtube_url])

            elif chemin_video_sauvegarde:
                from moviepy import VideoFileClip
                chemin_video_local = chemin_video_sauvegarde
                clip = VideoFileClip(chemin_video_local)
                clip.audio.write_audiofile(chemin_audio_temp)
                clip.close()

            else:
                taches[tache_id]["statut"] = "erreur"
                taches[tache_id]["erreur"] = "Aucune source video fournie"
                return

            # Transcrire et traduire
            video_service.transcrire_et_traduire(
                chemin_audio_temp, voix, chemin_audio_final
            )

            if format_sortie == 'mp3':
                taches[tache_id]["statut"] = "termine"
                taches[tache_id]["fichier"] = nom_audio
            else:
                from moviepy import VideoFileClip, AudioFileClip
                video_clip = VideoFileClip(chemin_video_local)
                audio_clip = AudioFileClip(chemin_audio_final)

                if audio_clip.duration > video_clip.duration:
                    audio_clip = audio_clip.subclipped(0, video_clip.duration)

                video_final = video_clip.with_audio(audio_clip)
                video_final.write_videofile(
                    chemin_video_final,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
                video_clip.close()
                audio_clip.close()

                taches[tache_id]["statut"] = "termine"
                taches[tache_id]["fichier"] = nom_video

            # Nettoyer fichiers temporaires
            for f in [chemin_audio_temp, chemin_video_local]:
                if f and os.path.exists(f):
                    os.remove(f)

        except Exception as e:
            taches[tache_id]["statut"] = "erreur"
            taches[tache_id]["erreur"] = str(e)

    thread = threading.Thread(target=traiter_en_arriere_plan)
    thread.start()

    return jsonify({"tache_id": tache_id})

@app.route('/statut/<tache_id>')
def statut_tache(tache_id):
    if tache_id not in taches:
        return jsonify({"erreur": "Tache introuvable"}), 404
    return jsonify(taches[tache_id])

@app.route('/telecharger/<nom_fichier>')
def telecharger(nom_fichier):
    chemin = os.path.join(AUDIO_DIR, nom_fichier)
    if nom_fichier.endswith('.mp4'):
        return send_file(chemin, as_attachment=True, download_name="video_traduite.mp4")
    else:
        return send_file(chemin, as_attachment=True, download_name="voix_off.mp3")



@app.route('/extraire-audio', methods=['POST'])
def extraire_audio():
    youtube_url = request.form.get('youtube_url', '')
    video_file = request.files.get('video')

    tache_id = str(uuid.uuid4())
    taches[tache_id] = {"statut": "en_cours", "fichier": None, "erreur": None}

    nom_audio = f"{uuid.uuid4()}.mp3"
    chemin_audio = os.path.join(AUDIO_DIR, nom_audio)

    def traiter():
        try:
            if youtube_url:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': chemin_audio.replace('.mp3', ''),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])

            elif video_file:
                from moviepy import VideoFileClip
                chemin_video = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp4")
                video_file.save(chemin_video)
                clip = VideoFileClip(chemin_video)
                clip.audio.write_audiofile(chemin_audio)
                clip.close()
                os.remove(chemin_video)

            else:
                taches[tache_id]["statut"] = "erreur"
                taches[tache_id]["erreur"] = "Aucune source fournie"
                return

            taches[tache_id]["statut"] = "termine"
            taches[tache_id]["fichier"] = nom_audio

        except Exception as e:
            taches[tache_id]["statut"] = "erreur"
            taches[tache_id]["erreur"] = str(e)

    threading.Thread(target=traiter).start()
    return jsonify({"tache_id": tache_id})

@app.route('/remplacer-voix', methods=['POST'])
def remplacer_voix():
    youtube_url = request.form.get('youtube_url', '')
    video_file = request.files.get('video')
    voix = request.form.get('voix', 'microsoft_henri')

    tache_id = str(uuid.uuid4())
    taches[tache_id] = {"statut": "en_cours", "fichier": None, "erreur": None}

    nom_audio = f"{uuid.uuid4()}.mp3"
    chemin_audio_final = os.path.join(AUDIO_DIR, nom_audio)
    chemin_audio_temp = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp3")

    chemin_video_sauvegarde = None
    if video_file:
        chemin_video_sauvegarde = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp4")
        video_file.save(chemin_video_sauvegarde)

    def traiter():
        try:
            if youtube_url:
                # Extraire audio depuis YouTube
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': chemin_audio_temp.replace('.mp3', ''),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])

            elif chemin_video_sauvegarde:
                from moviepy import VideoFileClip
                clip = VideoFileClip(chemin_video_sauvegarde)
                clip.audio.write_audiofile(chemin_audio_temp)
                clip.close()

            else:
                taches[tache_id]["statut"] = "erreur"
                taches[tache_id]["erreur"] = "Aucune source fournie"
                return

            # Transcrire le texte (sans traduction — on garde le francais)
            import whisper
            print("Transcription en cours...")
            model = whisper.load_model("tiny")
            result = model.transcribe(chemin_audio_temp, verbose=False)
            texte = result["text"].strip()
            print(f"Transcription terminee : {texte[:100]}...")

            # Regenerer avec la nouvelle voix
            generer_voix(texte, voix, chemin_audio_final)

            # Nettoyer
            if os.path.exists(chemin_audio_temp):
                os.remove(chemin_audio_temp)
            if chemin_video_sauvegarde and os.path.exists(chemin_video_sauvegarde):
                os.remove(chemin_video_sauvegarde)

            taches[tache_id]["statut"] = "termine"
            taches[tache_id]["fichier"] = nom_audio

        except Exception as e:
            taches[tache_id]["statut"] = "erreur"
            taches[tache_id]["erreur"] = str(e)

    threading.Thread(target=traiter).start()
    return jsonify({"tache_id": tache_id})



@app.route('/extraire-traduire', methods=['POST'])
def extraire_traduire():
    youtube_url = request.form.get('youtube_url', '')
    video_file = request.files.get('video')
    voix = request.form.get('voix', 'microsoft_henri')

    tache_id = str(uuid.uuid4())
    taches[tache_id] = {"statut": "en_cours", "fichier": None, "erreur": None}

    nom_audio = f"{uuid.uuid4()}.mp3"
    chemin_audio_final = os.path.join(AUDIO_DIR, nom_audio)
    chemin_audio_temp = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp3")

    chemin_video_sauvegarde = None
    if video_file:
        chemin_video_sauvegarde = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mp4")
        video_file.save(chemin_video_sauvegarde)

    def traiter():
        try:
            if youtube_url:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': chemin_audio_temp.replace('.mp3', ''),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])

            elif chemin_video_sauvegarde:
                from moviepy import VideoFileClip
                clip = VideoFileClip(chemin_video_sauvegarde)
                clip.audio.write_audiofile(chemin_audio_temp)
                clip.close()

            else:
                taches[tache_id]["statut"] = "erreur"
                taches[tache_id]["erreur"] = "Aucune source fournie"
                return

            # Transcrire EN anglais + traduire EN francais + generer voix
            video_service.transcrire_et_traduire(
                chemin_audio_temp, voix, chemin_audio_final
            )

            # Nettoyer
            for f in [chemin_audio_temp, chemin_video_sauvegarde]:
                if f and os.path.exists(f):
                    os.remove(f)

            taches[tache_id]["statut"] = "termine"
            taches[tache_id]["fichier"] = nom_audio

        except Exception as e:
            taches[tache_id]["statut"] = "erreur"
            taches[tache_id]["erreur"] = str(e)

    threading.Thread(target=traiter).start()
    return jsonify({"tache_id": tache_id})

if __name__ == '__main__':
    app.run(debug=True)
