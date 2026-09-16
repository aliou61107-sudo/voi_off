// ═══════════════════════════════════════════
// COMPOSANTS HTML
// ═══════════════════════════════════════════

function renderHeader() {
    return `
        <div class="header">
            <span class="crown">👑</span>
            <div class="brand-name">VOIXOFF PRO</div>
            <div class="brand-line"></div>
            <div class="brand-sub">Studio de voix professionnelle</div>
        </div>
    `;
}

function renderTabs() {
    return `
        <div class="tabs-header">
            <button class="tab-btn active" onclick="switchTab('voix', this)">
                <span class="tab-icon">🎙️</span>Voix Off
            </button>
            <button class="tab-btn" onclick="switchTab('livre', this)">
                <span class="tab-icon">📖</span>Livre Audio
            </button>
            <button class="tab-btn" onclick="switchTab('video', this)">
                <span class="tab-icon">🎬</span>Traduction Video
            </button>
            <button class="tab-btn" onclick="switchTab('audio', this)">
                <span class="tab-icon">🎵</span>Extraire Audio
            </button>
            <button class="tab-btn" onclick="switchTab('remplacer', this)">
                <span class="tab-icon">🎭</span>Remplacer Voix
            </button>
            <button class="tab-btn" onclick="switchTab('et', this)">
            <span class="tab-icon">🌍</span>Extraire et Traduire
            </button>
        </div>
    `;
}

function renderVoiceCard(name, value, icon, desc, checked = false) {
    return `
        <label class="voice-option">
            <input type="radio" name="${name}" value="${value}" ${checked ? 'checked' : ''}>
            <div class="voice-card">
                <span class="voice-icon">${icon}</span>
                <div class="voice-info">
                    <strong>${value.split('_').pop().charAt(0).toUpperCase() + value.split('_').pop().slice(1)}</strong>
                    <span>${desc}</span>
                </div>
            </div>
        </label>
    `;
}

function renderVoiceSection(name, defaultVoix) {
    return `
        <div class="mb-4">
            <label class="field-label">Choisissez votre voix</label>

            <div class="voice-section-title">Google TTS</div>
            <div class="voice-grid mb-3">
                ${renderVoiceCard(name, 'gtts_masculin', '👨', 'Ton grave', defaultVoix === 'gtts_masculin')}
                ${renderVoiceCard(name, 'gtts_feminin', '👩', 'Ton doux', defaultVoix === 'gtts_feminin')}
            </div>

            <div class="voice-section-title">Microsoft Edge</div>
            <div class="voice-grid mb-3">
                ${renderVoiceCard(name, 'microsoft_henri', '🎤', 'Masculin FR', defaultVoix === 'microsoft_henri')}
                ${renderVoiceCard(name, 'microsoft_denise', '🎙️', 'Feminin FR', defaultVoix === 'microsoft_denise')}
                ${renderVoiceCard(name, 'microsoft_antoine', '🎤', 'Masculin CA', defaultVoix === 'microsoft_antoine')}
                ${renderVoiceCard(name, 'microsoft_sylvie', '🎙️', 'Feminin CA', defaultVoix === 'microsoft_sylvie')}
            </div>

            <div class="voice-section-title">ElevenLabs IA</div>
            <div class="voice-grid">
                ${renderVoiceCard(name, 'eleven_adam', '🎭', 'Autoritaire', defaultVoix === 'eleven_adam')}
                ${renderVoiceCard(name, 'eleven_rachel', '🌟', 'Expressive', defaultVoix === 'eleven_rachel')}
                ${renderVoiceCard(name, 'eleven_sage', '🧙', 'Grave et pose', defaultVoix === 'eleven_sage')}
                ${renderVoiceCard(name, 'eleven_daniel', '📖', 'Livre audio', defaultVoix === 'eleven_daniel')}
            </div>
        </div>
    `;
}

function renderResultCard(id, titre) {
    return `
        <div id="loading-bar-${id}" class="loading-bar"></div>
        <div id="result-card-${id}" class="result-card">
            <div class="result-header">
                <div class="result-dot"></div>
                <span class="result-title">${titre}</span>
            </div>
            <audio id="audio-${id}" controls></audio>
            <a id="btn-download-${id}" class="btn-download" href="#">
                Telecharger le fichier
            </a>
        </div>
    `;
}

function renderUploadZone(id, texte, sous_texte, accept, onchange) {
    return `
        <div class="upload-zone" onclick="document.getElementById('${id}').click()">
            <span class="upload-icon">📄</span>
            <div class="upload-text">${texte}</div>
            <div class="upload-sub">${sous_texte}</div>
            <input type="file" id="${id}" accept="${accept}" style="display:none"
                onchange="${onchange}">
            <div id="nom-${id}" class="upload-filename"></div>
        </div>
    `;
}

// ═══════════════════════════════════════════
// ONGLETS
// ═══════════════════════════════════════════

function renderTabVoix() {
    return `
        <div class="mb-4">
            <label class="field-label">Votre texte</label>
            <textarea id="texte" class="text-input"
                placeholder="Ecrivez ou collez votre texte ici..."
                oninput="document.getElementById('compteur').textContent = this.value.length"></textarea>
            <div class="char-count"><span id="compteur">0</span> caracteres</div>
        </div>
        ${renderVoiceSection('voix', 'microsoft_henri')}
        <button class="btn-main" onclick="genererVoix()">Generer la voix off</button>
        ${renderResultCard('voix', 'Voix generee avec succes')}
    `;
}

function renderTabLivre() {
    return `
        <div class="mb-4">
            <label class="field-label">Importez votre document</label>
            ${renderUploadZone('document', 'Cliquez pour importer', 'PDF ou DOCX acceptes', '.pdf,.docx', "afficherNom('document')")}
        </div>
        ${renderVoiceSection('voix-livre', 'microsoft_henri')}
        <button class="btn-main" onclick="convertirLivreAudio()">Convertir en livre audio</button>
        ${renderResultCard('livre', 'Livre audio genere')}
    `;
}

function renderTabVideo() {
    return `
        <div class="mb-4">
            <label class="field-label">Lien YouTube</label>
            <input type="text" id="youtube-url" class="text-field"
                placeholder="https://www.youtube.com/watch?v=...">
        </div>
        <div class="divider-or"><span>ou</span></div>
        <div class="mb-4">
            <label class="field-label">Importez une video</label>
            ${renderUploadZone('video-file', 'Cliquez pour importer', 'MP4 AVI MOV acceptes', '.mp4,.avi,.mov', "afficherNom('video-file')")}
        </div>
        <div class="mb-4">
            <label class="field-label">Format de sortie</label>
            <div class="format-grid">
                <label class="format-option">
                    <input type="radio" name="format" value="mp4" checked>
                    <div class="format-card">🎬 Video MP4</div>
                </label>
                <label class="format-option">
                    <input type="radio" name="format" value="mp3">
                    <div class="format-card">🎵 Audio MP3</div>
                </label>
            </div>
        </div>
        ${renderVoiceSection('voix-video', 'microsoft_henri')}
        <button class="btn-main" onclick="traduireVideo()">Traduire la video en francais</button>
        ${renderResultCard('video', 'Traduction terminee')}
    `;
}

function renderTabAudio() {
    return `
        <div class="mb-4">
            <label class="field-label">Lien YouTube</label>
            <input type="text" id="youtube-url-audio" class="text-field"
                placeholder="https://www.youtube.com/watch?v=...">
        </div>
        <div class="divider-or"><span>ou</span></div>
        <div class="mb-4">
            <label class="field-label">Importez une video</label>
            ${renderUploadZone('video-audio', 'Cliquez pour importer', 'MP4 AVI MOV acceptes', '.mp4,.avi,.mov', "afficherNom('video-audio')")}
        </div>
        <button class="btn-main" onclick="extraireAudio()">🎵 Extraire l'audio en MP3</button>
        ${renderResultCard('audio', 'Audio extrait avec succes')}
    `;
}

function renderTabRemplacer() {
    return `
        <div class="mb-4">
            <label class="field-label">Lien YouTube</label>
            <input type="text" id="youtube-url-remplacer" class="text-field"
                placeholder="https://www.youtube.com/watch?v=...">
        </div>
        <div class="divider-or"><span>ou</span></div>
        <div class="mb-4">
            <label class="field-label">Importez une video ou audio</label>
            ${renderUploadZone('video-remplacer', 'Cliquez pour importer', 'MP4 MP3 WAV acceptes', '.mp4,.mp3,.wav', "afficherNom('video-remplacer')")}
        </div>
        ${renderVoiceSection('voix-remplacer', 'microsoft_henri')}
        <button class="btn-main" onclick="remplacerVoix()">
            🎭 Remplacer la voix
        </button>
        ${renderResultCard('remplacer', 'Voix remplacee avec succes')}
    `;
}

// ═══════════════════════════════════════════
// UTILITAIRES
// ═══════════════════════════════════════════

function switchTab(tab, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    if (btn) btn.classList.add('active');
}

function afficherNom(id) {
    const input = document.getElementById(id);
    const el = document.getElementById('nom-' + id);
    if (input && input.files[0] && el) {
        el.textContent = '✓ ' + input.files[0].name;
        el.style.display = 'block';
    }
}

function setLoading(id, loading, texte) {
    const bar = document.getElementById('loading-bar-' + id);
    if (loading) bar.classList.add('active');
    else bar.classList.remove('active');
}

function afficherResultat(id, fichier) {
    const audio = document.getElementById('audio-' + id);
    const download = document.getElementById('btn-download-' + id);
    const card = document.getElementById('result-card-' + id);
    audio.src = '/static/audio/' + fichier;
    audio.load();
    download.href = '/telecharger/' + fichier;
    card.classList.add('show');
}

function surveiller(tache_id, id) {
    const interval = setInterval(() => {
        fetch('/statut/' + tache_id)
        .then(r => r.json())
        .then(statut => {
            if (statut.statut === 'termine') {
                clearInterval(interval);
                setLoading(id, false);
                afficherResultat(id, statut.fichier);
            } else if (statut.statut === 'erreur') {
                clearInterval(interval);
                setLoading(id, false);
                alert('Erreur : ' + statut.erreur);
            }
        });
    }, 5000);
}

// ═══════════════════════════════════════════
// ACTIONS
// ═══════════════════════════════════════════

function genererVoix() {
    const texte = document.getElementById('texte').value;
    const voix = document.querySelector('input[name="voix"]:checked').value;
    if (!texte.trim()) { alert('Ecrivez du texte avant de generer.'); return; }

    setLoading('voix', true);
    document.getElementById('result-card-voix').classList.remove('show');

    const formData = new FormData();
    formData.append('texte', texte);
    formData.append('voix', voix);

    fetch('/generer', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        setLoading('voix', false);
        if (data.erreur) { alert(data.erreur); return; }
        afficherResultat('voix', data.fichier);
    })
    .catch(() => { setLoading('voix', false); alert('Erreur.'); });
}

function convertirLivreAudio() {
    const fichier = document.getElementById('document').files[0];
    const voix = document.querySelector('input[name="voix-livre"]:checked').value;
    if (!fichier) { alert('Importez un document.'); return; }

    setLoading('livre', true);
    document.getElementById('result-card-livre').classList.remove('show');

    const formData = new FormData();
    formData.append('document', fichier);
    formData.append('voix', voix);

    fetch('/livre-audio', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        setLoading('livre', false);
        if (data.erreur) { alert(data.erreur); return; }
        afficherResultat('livre', data.fichier);
    })
    .catch(() => { setLoading('livre', false); alert('Erreur.'); });
}

function traduireVideo() {
    const youtubeUrl = document.getElementById('youtube-url').value;
    const videoFile = document.getElementById('video-file').files[0];
    const voix = document.querySelector('input[name="voix-video"]:checked').value;
    const format = document.querySelector('input[name="format"]:checked').value;

    if (!youtubeUrl && !videoFile) { alert('Fournissez un lien YouTube ou une video.'); return; }

    setLoading('video', true);
    document.getElementById('result-card-video').classList.remove('show');

    const formData = new FormData();
    if (videoFile) formData.append('video', videoFile);
    if (youtubeUrl) formData.append('youtube_url', youtubeUrl);
    formData.append('voix', voix);
    formData.append('format', format);

    fetch('/traduire-video', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        if (data.erreur) { setLoading('video', false); alert(data.erreur); return; }
        surveiller(data.tache_id, 'video');
    })
    .catch(() => { setLoading('video', false); alert('Erreur.'); });
}

function extraireAudio() {
    const youtubeUrl = document.getElementById('youtube-url-audio').value;
    const videoFile = document.getElementById('video-audio').files[0];

    if (!youtubeUrl && !videoFile) { alert('Fournissez un lien YouTube ou une video.'); return; }

    setLoading('audio', true);
    document.getElementById('result-card-audio').classList.remove('show');

    const formData = new FormData();
    if (videoFile) formData.append('video', videoFile);
    if (youtubeUrl) formData.append('youtube_url', youtubeUrl);

    fetch('/extraire-audio', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        if (data.erreur) { setLoading('audio', false); alert(data.erreur); return; }
        surveiller(data.tache_id, 'audio');
    })
    .catch(() => { setLoading('audio', false); alert('Erreur.'); });
}

function remplacerVoix() {
    const youtubeUrl = document.getElementById('youtube-url-remplacer').value;
    const videoFile = document.getElementById('video-remplacer').files[0];
    const voix = document.querySelector('input[name="voix-remplacer"]:checked').value;

    if (!youtubeUrl && !videoFile) {
        alert('Fournissez un lien YouTube ou importez un fichier.');
        return;
    }

    setLoading('remplacer', true);
    document.getElementById('result-card-remplacer').classList.remove('show');

    const formData = new FormData();
    if (videoFile) formData.append('video', videoFile);
    if (youtubeUrl) formData.append('youtube_url', youtubeUrl);
    formData.append('voix', voix);

    fetch('/remplacer-voix', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        if (data.erreur) { setLoading('remplacer', false); alert(data.erreur); return; }
        surveiller(data.tache_id, 'remplacer');
    })
    .catch(() => { setLoading('remplacer', false); alert('Erreur.'); });
}


function renderTabExtraireTraduire() {
    return `
        <div class="mb-4">
            <label class="field-label">Lien YouTube (en anglais)</label>
            <input type="text" id="youtube-url-et" class="text-field"
                placeholder="https://www.youtube.com/watch?v=...">
        </div>
        <div class="divider-or"><span>ou</span></div>
        <div class="mb-4">
            <label class="field-label">Importez une video en anglais</label>
            ${renderUploadZone('video-et', 'Cliquez pour importer', 'MP4 AVI MOV acceptes', '.mp4,.avi,.mov', "afficherNom('video-et')")}
        </div>
        ${renderVoiceSection('voix-et', 'microsoft_henri')}
        <button class="btn-main" onclick="extraireEtTraduire()">
            🌍 Extraire et traduire en francais
        </button>
        ${renderResultCard('et', 'Audio traduit en francais')}
    `;
}


function extraireEtTraduire() {
    const youtubeUrl = document.getElementById('youtube-url-et').value;
    const videoFile = document.getElementById('video-et').files[0];
    const voix = document.querySelector('input[name="voix-et"]:checked').value;

    if (!youtubeUrl && !videoFile) {
        alert('Fournissez un lien YouTube ou importez une video.');
        return;
    }

    setLoading('et', true);
    document.getElementById('result-card-et').classList.remove('show');

    const formData = new FormData();
    if (videoFile) formData.append('video', videoFile);
    if (youtubeUrl) formData.append('youtube_url', youtubeUrl);
    formData.append('voix', voix);

    fetch('/extraire-traduire', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        if (data.erreur) { setLoading('et', false); alert(data.erreur); return; }
        surveiller(data.tache_id, 'et');
    })
    .catch(() => { setLoading('et', false); alert('Erreur.'); });
}

// ═══════════════════════════════════════════
// INITIALISATION
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('header').innerHTML = renderHeader();
    document.getElementById('tabs-header').innerHTML = renderTabs();
    document.getElementById('tab-voix').innerHTML = renderTabVoix();
    document.getElementById('tab-livre').innerHTML = renderTabLivre();
    document.getElementById('tab-video').innerHTML = renderTabVideo();
    document.getElementById('tab-audio').innerHTML = renderTabAudio();
    document.getElementById('tab-remplacer').innerHTML = renderTabRemplacer();
    document.getElementById('tab-et').innerHTML = renderTabExtraireTraduire();
});