/* ==========================================================================
   Rohith Fitness centre - Shared Frontend Logic & API Client
   ========================================================================== */

const API_BASE_URL = window.location.origin.includes('http') 
  ? window.location.origin 
  : 'http://127.0.0.1:5000';

// Current User State Management
const Auth = {
  getUser() {
    const userStr = localStorage.getItem('fitness_user');
    if (userStr) {
      try { return JSON.parse(userStr); } catch(e) {}
    }
    return { id: 1, username: 'Guest User', email: 'guest@fitness.app' };
  },

  setUser(user) {
    localStorage.setItem('fitness_user', JSON.stringify(user));
    this.updateUserUI();
  },

  logout() {
    localStorage.removeItem('fitness_user');
    window.location.href = 'login.html';
  },

  isLoggedIn() {
    return localStorage.getItem('fitness_user') !== null;
  },

  updateUserUI() {
    const user = this.getUser();
    const badgeEl = document.getElementById('navUserBadge');
    if (badgeEl) {
      if (this.isLoggedIn()) {
        badgeEl.innerHTML = `
          <span>👤 <strong>${escapeHtml(user.username)}</strong></span>
          <button onclick="Auth.logout()" class="btn btn-outline" style="padding: 0.25rem 0.6rem; font-size: 0.78rem;">Logout</button>
        `;
      } else {
        badgeEl.innerHTML = `
          <a href="login.html" class="btn btn-primary" style="padding: 0.35rem 0.85rem; font-size: 0.82rem;">Login / Register</a>
        `;
      }
    }
  }
};

// Notification Toast System
function showToast(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Utility: HTML Escaper
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Active Page Link Highlighting & Floating Chat Initialization
document.addEventListener('DOMContentLoaded', () => {
  Auth.updateUserUI();

  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Initialize Right-Corner Floating AI Chatbot on all pages except standalone chatbot.html
  if (currentPath !== 'chatbot.html') {
    FloatingChat.init();
  }
});

/* ==========================================================================
   Professional Floating AI Chatbot (Right Corner) Engine
   Camera, Mic, Files, Text-to-Speech & Gemini AI Integration
   ========================================================================== */

const FloatingChat = {
  isOpen: false,
  isMaximized: false,
  ttsEnabled: false,
  activeAttachment: null, // { type: 'image'|'file', data: string, name: string }
  cameraStream: null,
  currentFacingMode: 'user',
  recognition: null,
  isListening: false,

  init() {
    if (document.getElementById('floatingChatBtn')) return;
    this.injectMarkup();
    this.bindEvents();
  },

  injectMarkup() {
    const html = `
      <!-- Right-Corner Floating Launcher Button -->
      <div id="floatingChatBtn" class="floating-chat-btn" title="Open FitBot AI Fitness Assistant">
        <div class="pulse-ring"></div>
        <span id="floatingChatIcon">🤖</span>
        <span class="online-badge"></span>
        <div class="chat-tooltip">Chat with FitBot AI 🏋️</div>
      </div>

      <!-- Right-Corner Floating Chat Drawer Window -->
      <div id="floatingChatWindow" class="floating-chat-window">
        
        <!-- Header -->
        <div class="floating-chat-header">
          <div class="floating-chat-header-info">
            <div class="floating-chat-avatar">
              🤖
              <span class="avatar-dot"></span>
            </div>
            <div>
              <div style="font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; gap: 0.4rem;">
                FitBot AI
                <span style="font-size: 0.65rem; background: rgba(16, 185, 129, 0.2); color: var(--accent-neon); padding: 1px 6px; border-radius: 10px; font-weight: 700;">PRO</span>
              </div>
              <div style="font-size: 0.72rem; color: var(--text-muted);">Personal Fitness & Nutrition Coach</div>
            </div>
          </div>
          <div class="floating-chat-header-actions">
            <button type="button" id="floatingSoundBtn" class="floating-icon-btn" title="Toggle Auto Voice (Read Aloud)" onclick="FloatingChat.toggleTTS()">🔇</button>
            <button type="button" class="floating-icon-btn" title="Clear Chat History" onclick="FloatingChat.clearChat()">🗑️</button>
            <button type="button" class="floating-icon-btn" title="Maximize / Restore" onclick="FloatingChat.toggleMaximize()">⛶</button>
            <button type="button" class="floating-icon-btn" title="Close Chat" onclick="FloatingChat.toggleOpen()">✕</button>
          </div>
        </div>

        <!-- Messages Stream -->
        <div id="floatingChatMessages" class="floating-chat-messages">
          <div class="chat-bubble bot">
            Hello! I'm <strong>FitBot</strong>, your personal AI fitness & nutrition coach. 🏋️<br><br>
            • Ask any fitness, workout routine, or diet questions<br>
            • 📷 <strong>Camera:</strong> Snap a photo of your meal or workout form<br>
            • 🎤 <strong>Mic:</strong> Speak directly to ask questions hands-free<br>
            • 📎 <strong>Files:</strong> Upload progress photos or workout docs
          </div>
        </div>

        <!-- Quick Prompts Chips -->
        <div class="floating-quick-prompts">
          <span class="chip" onclick="FloatingChat.sendQuick('How much protein do I need daily for muscle building?')">💡 Daily Protein</span>
          <span class="chip" onclick="FloatingChat.sendQuick('What is the most effective workout strategy for fat loss?')">🔥 Fat Loss</span>
          <span class="chip" onclick="FloatingChat.sendQuick('Give me a balanced 4-day workout routine split')">💪 4-Day Split</span>
          <span class="chip" onclick="FloatingChat.sendQuick('What should I eat before and after workout?')">🥗 Meal Guide</span>
        </div>

        <!-- Active Attachment Preview Strip -->
        <div id="floatingAttachmentStrip" class="attachment-preview-strip">
          <div class="attachment-preview-info">
            <img id="floatingAttachmentThumb" class="attachment-thumb" src="" alt="preview" style="display:none;" onclick="FloatingChat.previewAttachmentInLightbox()">
            <span id="floatingAttachmentFileIcon" style="font-size:1.2rem; display:none;">📄</span>
            <span id="floatingAttachmentName" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:210px; font-weight:500;"></span>
          </div>
          <button type="button" class="attachment-remove-btn" onclick="FloatingChat.removeAttachment()" title="Remove attachment">✕</button>
        </div>

        <!-- Live Voice Recording Bar -->
        <div id="floatingVoiceBar" class="voice-recording-bar">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <div class="audio-waves">
              <span></span><span></span><span></span><span></span>
            </div>
            <span>Listening... Speak your fitness question</span>
          </div>
          <button type="button" onclick="FloatingChat.stopVoiceRecognition()" style="background:transparent; border:none; color:#fff; cursor:pointer; font-size:0.8rem; text-decoration:underline;">Stop</button>
        </div>

        <!-- Multimodal Input Area -->
        <div class="chat-input-wrapper">
          <form id="floatingChatForm" onsubmit="FloatingChat.handleSend(event)" class="chat-action-row">
            <!-- Hidden File Input -->
            <input type="file" id="floatingFileInput" accept="image/*,.pdf,.doc,.docx,.txt,.csv" style="display:none;" onchange="FloatingChat.handleFileSelected(event)">
            
            <!-- Camera Button -->
            <button type="button" id="floatingCamBtn" class="chat-tool-btn" title="Snap Photo with Camera" onclick="FloatingChat.openCamera()">
              📷
            </button>

            <!-- Mic Button -->
            <button type="button" id="floatingMicBtn" class="chat-tool-btn" title="Voice Input (Microphone)" onclick="FloatingChat.toggleVoice()">
              🎤
            </button>

            <!-- File Button -->
            <button type="button" id="floatingFileBtn" class="chat-tool-btn" title="Attach Image or Document" onclick="document.getElementById('floatingFileInput').click()">
              📎
            </button>

            <!-- Text Input -->
            <input type="text" id="floatingChatInput" class="form-control chat-text-input" placeholder="Ask question or snap photo..." autocomplete="off">

            <!-- Send Button -->
            <button type="submit" id="floatingSendBtn" class="chat-send-btn">
              <span>Send</span> 🚀
            </button>
          </form>
        </div>

        <!-- Camera Capture Modal Viewport -->
        <div id="floatingCameraModal" class="camera-overlay-modal">
          <div class="camera-modal-header">
            <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-main); display:flex; align-items:center; gap:0.4rem;">
              📷 FitBot Camera Access
            </span>
            <button type="button" class="floating-icon-btn" onclick="FloatingChat.closeCamera()" style="font-size: 1.1rem;">✕</button>
          </div>
          
          <div class="camera-viewport-container">
            <video id="floatingCameraVideo" autoplay playsinline muted></video>
            <canvas id="floatingCameraCanvas" style="display:none;"></canvas>
            <div id="floatingCameraGuide" class="camera-guide-box">
              <span>Align Meal or Workout Pose</span>
            </div>
          </div>

          <div class="camera-controls-bar">
            <button type="button" id="floatingCameraSwitchBtn" class="floating-icon-btn" onclick="FloatingChat.switchCamera()" title="Switch Camera" style="width:40px; height:40px; font-size:1.15rem;">
              🔄
            </button>

            <button type="button" id="floatingCameraShutterBtn" class="camera-shutter-btn" onclick="FloatingChat.takeSnapshot()" title="Capture Snapshot">
              📸
            </button>

            <div id="floatingCameraReviewActions" style="display:none; gap:0.5rem;">
              <button type="button" class="btn btn-outline" style="padding:0.4rem 0.8rem; font-size:0.8rem;" onclick="FloatingChat.retakeSnapshot()">↺ Retake</button>
              <button type="button" class="btn btn-primary" style="padding:0.4rem 0.8rem; font-size:0.8rem;" onclick="FloatingChat.confirmSnapshot()">✓ Use Photo</button>
            </div>
          </div>
        </div>

      </div>

      <!-- Photo Lightbox Modal -->
      <div id="chatPhotoLightbox" class="chat-lightbox" onclick="this.classList.remove('show')">
        <img id="chatLightboxImg" src="" alt="Enlarged photo">
      </div>
    `;

    const wrapper = document.createElement('div');
    wrapper.id = 'floatingChatRoot';
    wrapper.innerHTML = html;
    document.body.appendChild(wrapper);
  },

  bindEvents() {
    const btn = document.getElementById('floatingChatBtn');
    if (btn) {
      btn.addEventListener('click', () => this.toggleOpen());
    }
  },

  toggleOpen() {
    this.isOpen = !this.isOpen;
    const windowEl = document.getElementById('floatingChatWindow');
    const iconEl = document.getElementById('floatingChatIcon');
    if (this.isOpen) {
      windowEl.classList.add('active');
      iconEl.textContent = '✕';
      document.getElementById('floatingChatInput').focus();
      this.loadHistory();
    } else {
      windowEl.classList.remove('active');
      iconEl.textContent = '🤖';
      this.closeCamera();
      this.stopVoiceRecognition();
    }
  },

  toggleMaximize() {
    this.isMaximized = !this.isMaximized;
    const windowEl = document.getElementById('floatingChatWindow');
    if (this.isMaximized) {
      windowEl.classList.add('is-maximized');
    } else {
      windowEl.classList.remove('is-maximized');
    }
  },

  toggleTTS() {
    this.ttsEnabled = !this.ttsEnabled;
    const btn = document.getElementById('floatingSoundBtn');
    if (this.ttsEnabled) {
      btn.textContent = '🔊';
      btn.classList.add('active');
      showToast('Voice read-aloud enabled 🔊', 'info');
    } else {
      btn.textContent = '🔇';
      btn.classList.remove('active');
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
      showToast('Voice read-aloud muted 🔇', 'info');
    }
  },

  speakText(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleanText = text
      .replace(/[*_#`~•]/g, '')
      .replace(/<[^>]*>/g, '')
      .replace(/\[Attached:[^\]]*\]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  },

  async loadHistory() {
    const user = Auth.getUser();
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/history?user_id=${user.id}`);
      const data = await res.json();
      if (data.success && data.history && data.history.length > 0) {
        const container = document.getElementById('floatingChatMessages');
        container.innerHTML = '';
        data.history.forEach(item => {
          this.appendMessage(item.message, item.sender === 'user' ? 'user' : 'bot', false);
        });
        this.scrollToBottom();
      }
    } catch(e) {}
  },

  appendMessage(text, sender = 'bot', canSpeak = true, attachment = null) {
    const container = document.getElementById('floatingChatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;

    let attachmentHtml = '';
    if (attachment) {
      if (attachment.type === 'image' || (attachment.data && attachment.data.startsWith('data:image'))) {
        attachmentHtml = `<img src="${attachment.data}" class="bubble-attachment-img" alt="attachment" onclick="FloatingChat.openLightbox('${attachment.data}')">`;
      } else if (attachment.name) {
        attachmentHtml = `<div class="bubble-attachment-file"><span>📎</span><span>${escapeHtml(attachment.name)}</span></div>`;
      }
    }

    const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const speakBtnHtml = sender === 'bot' 
      ? `<button type="button" class="tts-btn" title="Read Aloud" onclick="FloatingChat.speakText(\`${escapeHtml(text.replace(/"/g, '&quot;'))}\`)">🔊</button>` 
      : '';

    bubble.innerHTML = `
      ${attachmentHtml}
      <div>${this.formatMarkdown(text)}</div>
      <div class="chat-bubble-meta">
        ${speakBtnHtml}
        <span>${timeString}</span>
      </div>
    `;

    container.appendChild(bubble);
    this.scrollToBottom();

    if (sender === 'bot' && this.ttsEnabled && canSpeak) {
      this.speakText(text);
    }
  },

  formatMarkdown(str) {
    let formatted = escapeHtml(str);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
  },

  scrollToBottom() {
    const container = document.getElementById('floatingChatMessages');
    if (container) container.scrollTop = container.scrollHeight;
  },

  sendQuick(text) {
    const input = document.getElementById('floatingChatInput');
    input.value = text;
    this.handleSend(new Event('submit'));
  },

  clearChat() {
    const container = document.getElementById('floatingChatMessages');
    container.innerHTML = `
      <div class="chat-bubble bot">
        Chat cleared. Ask me a new fitness question whenever you're ready! 🏋️
      </div>
    `;
    showToast('Chat history cleared', 'info');
  },

  openLightbox(src) {
    const lightbox = document.getElementById('chatPhotoLightbox');
    const img = document.getElementById('chatLightboxImg');
    if (lightbox && img) {
      img.src = src;
      lightbox.classList.add('show');
    }
  },

  previewAttachmentInLightbox() {
    if (this.activeAttachment && this.activeAttachment.data) {
      this.openLightbox(this.activeAttachment.data);
    }
  },

  // ================= CAMERA ACCESS =================
  async openCamera() {
    const modal = document.getElementById('floatingCameraModal');
    const video = document.getElementById('floatingCameraVideo');
    const canvas = document.getElementById('floatingCameraCanvas');
    const shutterBtn = document.getElementById('floatingCameraShutterBtn');
    const reviewActions = document.getElementById('floatingCameraReviewActions');
    const guide = document.getElementById('floatingCameraGuide');

    video.style.display = 'block';
    canvas.style.display = 'none';
    shutterBtn.style.display = 'flex';
    reviewActions.style.display = 'none';
    guide.style.display = 'flex';

    modal.classList.add('show');

    try {
      if (this.cameraStream) {
        this.cameraStream.getTracks().forEach(t => t.stop());
      }
      this.cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: this.currentFacingMode, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      video.srcObject = this.cameraStream;
    } catch (err) {
      modal.classList.remove('show');
      showToast('Camera access permission was not granted or webcam is unavailable.', 'danger');
    }
  },

  switchCamera() {
    this.currentFacingMode = this.currentFacingMode === 'user' ? 'environment' : 'user';
    this.openCamera();
  },

  takeSnapshot() {
    const video = document.getElementById('floatingCameraVideo');
    const canvas = document.getElementById('floatingCameraCanvas');
    const shutterBtn = document.getElementById('floatingCameraShutterBtn');
    const reviewActions = document.getElementById('floatingCameraReviewActions');
    const guide = document.getElementById('floatingCameraGuide');

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    video.style.display = 'none';
    canvas.style.display = 'block';
    shutterBtn.style.display = 'none';
    reviewActions.style.display = 'flex';
    guide.style.display = 'none';
  },

  retakeSnapshot() {
    const video = document.getElementById('floatingCameraVideo');
    const canvas = document.getElementById('floatingCameraCanvas');
    const shutterBtn = document.getElementById('floatingCameraShutterBtn');
    const reviewActions = document.getElementById('floatingCameraReviewActions');
    const guide = document.getElementById('floatingCameraGuide');

    video.style.display = 'block';
    canvas.style.display = 'none';
    shutterBtn.style.display = 'flex';
    reviewActions.style.display = 'none';
    guide.style.display = 'flex';
  },

  confirmSnapshot() {
    const canvas = document.getElementById('floatingCameraCanvas');
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

    this.activeAttachment = {
      type: 'image',
      data: dataUrl,
      name: 'camera-snapshot.jpg'
    };

    this.renderAttachmentStrip();
    this.closeCamera();
    showToast('Photo captured and attached! 📷', 'success');

    const input = document.getElementById('floatingChatInput');
    if (!input.value) {
      input.value = 'Analyze this photo for calories, macros, or exercise form';
    }
    input.focus();
  },

  closeCamera() {
    const modal = document.getElementById('floatingCameraModal');
    if (modal) modal.classList.remove('show');
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(t => t.stop());
      this.cameraStream = null;
    }
  },

  // ================= MIC ACCESS (SPEECH RECOGNITION) =================
  toggleVoice() {
    if (this.isListening) {
      this.stopVoiceRecognition();
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      showToast('Speech recognition is not supported in this browser. Please use Google Chrome or Edge.', 'info');
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      const micBtn = document.getElementById('floatingMicBtn');
      const voiceBar = document.getElementById('floatingVoiceBar');
      const input = document.getElementById('floatingChatInput');

      micBtn.classList.add('active-mic');
      voiceBar.classList.add('show');
      this.isListening = true;

      this.recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        input.value = transcript;
      };

      this.recognition.onerror = (event) => {
        this.stopVoiceRecognition();
        if (event.error === 'not-allowed') {
          showToast('Microphone access denied. Please allow microphone permission in browser.', 'danger');
        }
      };

      this.recognition.onend = () => {
        this.stopVoiceRecognition();
      };

      this.recognition.start();
    } catch (e) {
      this.stopVoiceRecognition();
      showToast('Could not start microphone voice recognition.', 'danger');
    }
  },

  stopVoiceRecognition() {
    if (this.recognition && this.isListening) {
      try { this.recognition.stop(); } catch(e) {}
    }
    this.isListening = false;
    const micBtn = document.getElementById('floatingMicBtn');
    const voiceBar = document.getElementById('floatingVoiceBar');
    if (micBtn) micBtn.classList.remove('active-mic');
    if (voiceBar) voiceBar.classList.remove('show');
  },

  // ================= FILES ACCESS =================
  handleFileSelected(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      showToast('File size exceeds 10MB limit.', 'danger');
      event.target.value = '';
      return;
    }

    const isImg = file.type.startsWith('image/');
    const reader = new FileReader();

    reader.onload = (e) => {
      this.activeAttachment = {
        type: isImg ? 'image' : 'file',
        data: e.target.result,
        name: file.name
      };
      this.renderAttachmentStrip();
      showToast(`Attached: ${file.name} 📎`, 'success');
      event.target.value = '';
    };

    reader.readAsDataURL(file);
  },

  renderAttachmentStrip() {
    const strip = document.getElementById('floatingAttachmentStrip');
    const thumb = document.getElementById('floatingAttachmentThumb');
    const icon = document.getElementById('floatingAttachmentFileIcon');
    const nameEl = document.getElementById('floatingAttachmentName');

    if (!this.activeAttachment) {
      strip.classList.remove('show');
      thumb.style.display = 'none';
      icon.style.display = 'none';
      nameEl.textContent = '';
      return;
    }

    strip.classList.add('show');
    nameEl.textContent = this.activeAttachment.name || 'Attachment';

    if (this.activeAttachment.type === 'image') {
      thumb.src = this.activeAttachment.data;
      thumb.style.display = 'block';
      icon.style.display = 'none';
    } else {
      thumb.style.display = 'none';
      icon.style.display = 'inline-block';
    }
  },

  removeAttachment() {
    this.activeAttachment = null;
    this.renderAttachmentStrip();
  },

  // ================= SEND CHAT =================
  async handleSend(e) {
    if (e && e.preventDefault) e.preventDefault();
    const input = document.getElementById('floatingChatInput');
    const sendBtn = document.getElementById('floatingSendBtn');
    const userMessage = input.value.trim();
    const currentAttachment = this.activeAttachment;

    if (!userMessage && !currentAttachment) return;

    const user = Auth.getUser();

    // Display user message in bubbles
    this.appendMessage(userMessage || (currentAttachment ? `Attached: ${currentAttachment.name}` : ''), 'user', false, currentAttachment);

    // Reset input and attachment
    input.value = '';
    this.removeAttachment();
    sendBtn.disabled = true;

    // Show Typing Indicator
    const container = document.getElementById('floatingChatMessages');
    const typingBubble = document.createElement('div');
    typingBubble.id = 'floatingTypingIndicator';
    typingBubble.className = 'chat-bubble bot';
    typingBubble.innerHTML = '<em>FitBot is analyzing... 💬</em>';
    container.appendChild(typingBubble);
    this.scrollToBottom();

    const payload = {
      message: userMessage,
      user_id: user.id
    };

    if (currentAttachment) {
      payload.file_name = currentAttachment.name;
      if (currentAttachment.type === 'image') {
        payload.image_data = currentAttachment.data;
      }
    }

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      document.getElementById('floatingTypingIndicator')?.remove();

      if (data.success && data.reply) {
        this.appendMessage(data.reply, 'bot', true);
      } else {
        this.appendMessage(data.message || 'Sorry, I encountered an issue processing your request.', 'bot', true);
      }
    } catch (err) {
      document.getElementById('floatingTypingIndicator')?.remove();
      this.appendMessage("I'm currently running in offline fallback mode. For real-time Gemini AI capabilities, ensure the Flask backend is active.", 'bot', true);
    } finally {
      sendBtn.disabled = false;
    }
  }
};

