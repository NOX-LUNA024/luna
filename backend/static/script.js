const SESSION_ID = "arman_default";

/* Luna Mood Configurations */
const lunaMoods = {
    happy: {
        key: "happy",
        emoji: "😊",
        greetings: [
            "Good to see you, Arman! 😊",
            "Wonderful to have you here, Arman! ✨",
            "Feeling great today, Arman! 🌟"
        ],
        thoughts: [
            "I'm glad you're here.",
            "Today feels bright and full of potential.",
            "Smiling at how peaceful this moment is."
        ],
        glow: {
            primary: "#f43f5e",
            secondary: "#fbbf24",
            glowColor: "rgba(251, 191, 36, 0.65)",
            auraColor: "rgba(244, 63, 94, 0.35)",
            dropShadow: "rgba(251, 191, 36, 0.7)",
            innerMid: "#fb7185",
            innerDeep: "#e11d48",
            innerCore: "#881337",
            haloBorder: "rgba(251, 191, 36, 0.4)",
            haloBg: "rgba(244, 63, 94, 0.15)"
        }
    },
    curious: {
        key: "curious",
        emoji: "🤔",
        greetings: [
            "What are we exploring today, Arman? 🤔",
            "Curious minds meet again, Arman! 🌌",
            "Ready to uncover something new, Arman? 🔍"
        ],
        thoughts: [
            "I wonder what we'll build.",
            "So many questions left to explore.",
            "What secrets does today hold?"
        ],
        glow: {
            primary: "#38bdf8",
            secondary: "#818cf8",
            glowColor: "rgba(56, 189, 248, 0.65)",
            auraColor: "rgba(129, 140, 248, 0.35)",
            dropShadow: "rgba(56, 189, 248, 0.7)",
            innerMid: "#7dd3fc",
            innerDeep: "#0284c7",
            innerCore: "#0c4a6e",
            haloBorder: "rgba(56, 189, 248, 0.4)",
            haloBg: "rgba(56, 189, 248, 0.15)"
        }
    },
    calm: {
        key: "calm",
        emoji: "😌",
        greetings: [
            "Peaceful moments, Arman 😌",
            "Take a gentle breath, Arman 🍃",
            "Welcome back to a calm space, Arman ✨"
        ],
        thoughts: [
            "I've been waiting.",
            "Resting in quiet reflection.",
            "There's no rush to anything."
        ],
        glow: {
            primary: "#34d399",
            secondary: "#2dd4bf",
            glowColor: "rgba(52, 211, 153, 0.55)",
            auraColor: "rgba(45, 212, 191, 0.3)",
            dropShadow: "rgba(52, 211, 153, 0.65)",
            innerMid: "#6ee7b7",
            innerDeep: "#059669",
            innerCore: "#064e3b",
            haloBorder: "rgba(52, 211, 153, 0.35)",
            haloBg: "rgba(45, 212, 191, 0.12)"
        }
    },
    excited: {
        key: "excited",
        emoji: "🚀",
        greetings: [
            "Let's create something amazing, Arman! 🚀",
            "Energy is high today, Arman! ⚡",
            "Ready to leap forward, Arman! 🔥"
        ],
        thoughts: [
            "I think today will be productive.",
            "So much energy waiting to be channeled!",
            "Great things are about to happen."
        ],
        glow: {
            primary: "#f97316",
            secondary: "#a855f7",
            glowColor: "rgba(249, 115, 22, 0.7)",
            auraColor: "rgba(168, 85, 247, 0.4)",
            dropShadow: "rgba(249, 115, 22, 0.75)",
            innerMid: "#fb923c",
            innerDeep: "#ea580c",
            innerCore: "#7c2d12",
            haloBorder: "rgba(249, 115, 22, 0.45)",
            haloBg: "rgba(249, 115, 22, 0.18)"
        }
    },
    focused: {
        key: "focused",
        emoji: "💻",
        greetings: [
            "Deep focus time, Arman 💻",
            "Let's get into the flow, Arman ⚡",
            "Clear mind, steady task, Arman 🎯"
        ],
        thoughts: [
            "Ready whenever you are.",
            "Eliminating distractions, staying sharp.",
            "One step at a time, with precision."
        ],
        glow: {
            primary: "#06b6d4",
            secondary: "#3b82f6",
            glowColor: "rgba(6, 182, 212, 0.65)",
            auraColor: "rgba(59, 130, 246, 0.35)",
            dropShadow: "rgba(6, 182, 212, 0.7)",
            innerMid: "#67e8f9",
            innerDeep: "#0891b2",
            innerCore: "#164e63",
            haloBorder: "rgba(6, 182, 212, 0.4)",
            haloBg: "rgba(6, 182, 212, 0.15)"
        }
    },
    dreamy: {
        key: "dreamy",
        emoji: "🌙",
        greetings: [
            "Drifting in thought, Arman 🌙",
            "Stargazing with you, Arman ✨",
            "Soft night, clear thoughts, Arman 🌌"
        ],
        thoughts: [
            "The stars feel bright today.",
            "Lost in a sea of gentle ideas.",
            "Wandering through quiet constellations."
        ],
        glow: {
            primary: "#8b5cf6",
            secondary: "#c084fc",
            glowColor: "rgba(192, 132, 252, 0.65)",
            auraColor: "rgba(139, 92, 246, 0.35)",
            dropShadow: "rgba(192, 132, 252, 0.7)",
            innerMid: "#e9d5ff",
            innerDeep: "#a855f7",
            innerCore: "#4c1d95",
            haloBorder: "rgba(192, 132, 252, 0.4)",
            haloBg: "rgba(139, 92, 246, 0.15)"
        }
    }
};

let currentMood = null;

/* Idle Listener & Whisper System */
let idleTimer = null;
const IDLE_TIMEOUT_MS = 2 * 60 * 1000; // 2 minutes
const whispers = [
    "Still there, Arman?",
    "Need anything?"
];

function resetIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(triggerLunaWhisper, IDLE_TIMEOUT_MS);
}

function playSoftWhisperAudio() {
    if (!audioCtx) return;
    try {
        const whisperOsc = audioCtx.createOscillator();
        const whisperGain = audioCtx.createGain();
        const filter = audioCtx.createBiquadFilter();

        whisperOsc.type = 'sine';
        whisperOsc.frequency.setValueAtTime(320, audioCtx.currentTime);
        whisperOsc.frequency.exponentialRampToValueAtTime(220, audioCtx.currentTime + 1.2);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(450, audioCtx.currentTime);

        whisperGain.gain.setValueAtTime(0.001, audioCtx.currentTime);
        whisperGain.gain.linearRampToValueAtTime(0.015, audioCtx.currentTime + 0.4);
        whisperGain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 1.5);

        whisperOsc.connect(filter);
        filter.connect(whisperGain);
        whisperGain.connect(audioCtx.destination);

        whisperOsc.start();
        whisperOsc.stop(audioCtx.currentTime + 1.6);
    } catch (e) {}
}

function triggerLunaWhisper() {
    const chosenWhisper = whispers[Math.floor(Math.random() * whispers.length)];
    
    const thoughtElem = document.getElementById('thought-text');
    if (thoughtElem) {
        thoughtElem.innerText = `"${chosenWhisper}"`;
        thoughtElem.classList.add('whispering');
    }

    setLunaEmotion('curious');
    setTimeout(() => setLunaEmotion(null), 2000);

    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        const assistantRow = document.createElement('div');
        assistantRow.className = 'message-row assistant';
        assistantRow.innerHTML = `<div class="chat-bubble soft-whisper-bubble">${escapeHtml(chosenWhisper)}</div>`;
        chatContainer.appendChild(assistantRow);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    playSoftWhisperAudio();
}

function applyLunaMood(moodKey) {
    const mood = lunaMoods[moodKey] || lunaMoods.dreamy;
    currentMood = mood;

    const greeting = mood.greetings[Math.floor(Math.random() * mood.greetings.length)];
    const thought = mood.thoughts[Math.floor(Math.random() * mood.thoughts.length)];

    const greetingElem = document.getElementById('greeting-text');
    if (greetingElem) greetingElem.innerText = greeting;

    const thoughtElem = document.getElementById('thought-text');
    if (thoughtElem) {
        thoughtElem.innerText = `"${thought}"`;
        thoughtElem.classList.remove('whispering');
    }

    const orb = document.getElementById('luna-orb');
    const halo = document.getElementById('orb-halo');
    const g = mood.glow;

    if (orb) {
        orb.style.boxShadow = `
            inset -18px 4px 0 0 #ffffff,
            inset -28px 6px 14px 0px ${g.innerMid},
            inset -38px 10px 24px 0px ${g.innerDeep},
            inset -50px 14px 36px 0px ${g.innerCore},
            0 0 35px ${g.glowColor},
            0 0 75px ${g.auraColor}
        `;
        orb.style.filter = `drop-shadow(-4px 4px 18px ${g.dropShadow})`;
    }

    if (halo) {
        halo.style.borderColor = g.haloBorder;
        halo.style.background = `radial-gradient(circle, ${g.haloBg} 0%, transparent 70%)`;
    }

    document.documentElement.style.setProperty('--orb-primary', g.primary);
    document.documentElement.style.setProperty('--orb-secondary', g.secondary);
    document.documentElement.style.setProperty('--orb-glow', g.glowColor);
    document.documentElement.style.setProperty('--orb-aura', g.auraColor);
}

function setSingleRandomThought() {
    const moodKeys = Object.keys(lunaMoods);
    const randomMoodKey = moodKeys[Math.floor(Math.random() * moodKeys.length)];
    applyLunaMood(randomMoodKey);
}

/* Web Audio API Space Ambience */
let audioCtx = null;
let ambientGain = null;
let isAudioMuted = true;
let userHasInteracted = false;

function initAmbientAudio() {
    if (audioCtx) return;

    const AudioContext = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContext();

    ambientGain = audioCtx.createGain();
    ambientGain.gain.setValueAtTime(0, audioCtx.currentTime);
    ambientGain.connect(audioCtx.destination);

    const osc1 = audioCtx.createOscillator();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(55, audioCtx.currentTime);

    const filter1 = audioCtx.createBiquadFilter();
    filter1.type = 'lowpass';
    filter1.frequency.setValueAtTime(120, audioCtx.currentTime);

    osc1.connect(filter1);
    filter1.connect(ambientGain);
    osc1.start();

    const bufferSize = audioCtx.sampleRate * 2;
    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;

    for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        output[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
        output[i] *= 0.011;
        b6 = white * 0.115926;
    }

    const noiseSource = audioCtx.createBufferSource();
    noiseSource.buffer = noiseBuffer;
    noiseSource.loop = true;

    const noiseFilter = audioCtx.createBiquadFilter();
    noiseFilter.type = 'bandpass';
    noiseFilter.frequency.setValueAtTime(180, audioCtx.currentTime);
    noiseFilter.Q.setValueAtTime(1.5, audioCtx.currentTime);

    const lfo = audioCtx.createOscillator();
    lfo.frequency.setValueAtTime(0.05, audioCtx.currentTime);
    const lfoGain = audioCtx.createGain();
    lfoGain.gain.setValueAtTime(60, audioCtx.currentTime);

    lfo.connect(lfoGain);
    lfoGain.connect(noiseFilter.frequency);
    lfo.start();

    noiseSource.connect(noiseFilter);
    noiseFilter.connect(ambientGain);
    noiseSource.start();
}

function handleUserInteraction() {
    resetIdleTimer();
    const thoughtElem = document.getElementById('thought-text');
    if (thoughtElem) thoughtElem.classList.remove('whispering');

    if (!userHasInteracted) {
        userHasInteracted = true;
        initAmbientAudio();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function toggleAudio() {
    handleUserInteraction();
    const audioBtn = document.getElementById('audio-toggle-btn');
    const audioIcon = document.getElementById('audio-icon');

    if (!ambientGain) return;

    if (isAudioMuted) {
        ambientGain.gain.linearRampToValueAtTime(0.025, audioCtx.currentTime + 1.5);
        if (audioIcon) audioIcon.className = 'fa-solid fa-volume-high';
        if (audioBtn) audioBtn.classList.add('active');
        isAudioMuted = false;
    } else {
        ambientGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.8);
        if (audioIcon) audioIcon.className = 'fa-solid fa-volume-xmark';
        if (audioBtn) audioBtn.classList.remove('active');
        isAudioMuted = true;
    }
}

function setLunaEmotion(emotion) {
    const orb = document.getElementById('luna-orb');
    if (!orb) return;
    orb.classList.remove('idle', 'curious', 'thinking', 'smile', 'speaking', 'happy');
    orb.classList.add(emotion || 'idle');
}

function triggerVisualBurst(type) {
    const layer = document.getElementById('visual-effects');
    if (!layer || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const isMemory = type === 'memory';
    const color = isMemory ? '#fbbf24' : '#67e8f9';
    const count = isMemory ? 16 : 11;
    for (let index = 0; index < count; index += 1) {
        const particle = document.createElement('span');
        const angle = (Math.PI * 2 * index) / count;
        const distance = 80 + Math.random() * 110;
        particle.className = `visual-burst ${isMemory ? '' : 'sparkle'}`;
        particle.style.setProperty('--burst-color', color);
        particle.style.setProperty('--x', `${Math.cos(angle) * distance}px`);
        particle.style.setProperty('--y', `${Math.sin(angle) * distance}px`);
        particle.addEventListener('animationend', () => particle.remove(), { once: true });
        layer.appendChild(particle);
    }
}

function applyBackendEmotion(emotion) {
    if (!emotion || !emotion.mood) return;
    const avatarState = { bright: 'happy', focused: 'curious', gentle: 'idle', calm: 'idle' }[emotion.mood];
    if (avatarState) setLunaEmotion(avatarState);
}

function classifyAssistantMoment(text) {
    const response = text.toLowerCase();
    if (response.includes("i'll remember that") || response.includes("etched that into my mind")) {
        triggerVisualBurst('memory');
        setLunaEmotion('happy');
    } else if (response.includes('what do you enjoy most about') || response.includes('what part would you like to make progress on next')) {
        triggerVisualBurst('curiosity');
        setLunaEmotion('curious');
    }
}

async function initLunaSpace() {
    await loadLunaState();
    triggerShootingStarLoop();
    setupIdleListeners();
    resetIdleTimer();
}

async function loadLunaState() {
    try {
        const response = await fetch('/luna/state');
        if (!response.ok) throw new Error(`State request failed: ${response.status}`);
        const state = await response.json();
        document.body.classList.remove('sky-morning', 'sky-afternoon', 'sky-sunset', 'sky-night');
        document.body.classList.add(`sky-${state.sky_phase}`);
        const greeting = document.getElementById('greeting-text');
        const thought = document.getElementById('thought-text');
        if (greeting) greeting.textContent = state.greeting;
        if (thought) thought.textContent = `"${state.thought}"`;
        applyBackendEmotion(state.emotion);
        if (!state.emotion) setLunaEmotion('idle');
    } catch (error) {
        console.warn('Unable to load Luna state; using local mood.', error);
        setSingleRandomThought();
    }
}

function setupIdleListeners() {
    ['mousemove', 'keydown', 'touchstart', 'mousedown', 'scroll'].forEach(evt => {
        window.addEventListener(evt, handleUserInteraction, { passive: true });
    });
}

function triggerShootingStarLoop() {
    setInterval(() => {
        if (Math.random() > 0.45) {
            const star = document.getElementById('shooting-star');
            if (star) {
                star.style.animation = 'shootingStarAnim 2.2s ease-in-out';
                setTimeout(() => { star.style.animation = ''; }, 2200);
            }
        }
    }, 14000);
}

function triggerCoreFocusMode() {
    setLunaEmotion('smile');
    setTimeout(() => setLunaEmotion(null), 2500);
    setSingleRandomThought();
}

function speakLunaResponse(text) {
    if (!text || !text.trim()) return;

    if (!('speechSynthesis' in window)) {
        console.warn("Web Speech API is not supported in this browser.");
        return;
    }

    // Unpause speech engine if browser stuck state
    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();

    const speech = new SpeechSynthesisUtterance(text);
    speech.rate = 0.95;
    speech.pitch = 1.05;
    speech.volume = 1;

    const assignVoiceAndSpeak = () => {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
            const femaleVoice =
                voices.find(v => v.name === "Google UK English Female") ||
                voices.find(v => v.name === "Microsoft Zira - English (United States)") ||
                voices.find(v => v.name.includes("Female") || v.name.includes("female")) ||
                voices[0];

            if (femaleVoice) {
                speech.voice = femaleVoice;
            }
        }

        speech.onstart = () => setLunaEmotion("speaking");
        speech.onend = () => setLunaEmotion(null);
        speech.onerror = () => setLunaEmotion(null);

        window.speechSynthesis.speak(speech);
    };

    if (window.speechSynthesis.getVoices().length === 0) {
        window.speechSynthesis.onvoiceschanged = assignVoiceAndSpeak;
    } else {
        assignVoiceAndSpeak();
    }
}

async function sendMessage() {
    handleUserInteraction();
    const input = document.getElementById('user-input');
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;

    setLunaEmotion('curious');

    // Render User Message Bubble
    const userRow = document.createElement('div');
    userRow.className = 'message-row user';
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble';
    userBubble.textContent = message;
    userRow.appendChild(userBubble);
    chatContainer.appendChild(userRow);

    // Prepare Assistant Message Placeholder
    const assistantRow = document.createElement('div');
    assistantRow.className = 'message-row assistant';
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';

    const contentSpan = document.createElement('span');
    const cursorSpan = document.createElement('span');
    cursorSpan.className = 'cursor-blink';

    bubble.appendChild(contentSpan);
    bubble.appendChild(cursorSpan);
    assistantRow.appendChild(bubble);
    chatContainer.appendChild(assistantRow);

    chatContainer.scrollTop = chatContainer.scrollHeight;

    const thinkingTimer = setTimeout(() => {
        setLunaEmotion('thinking');
    }, 600);

    try {
        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: SESSION_ID })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullResponseText = '';
        let hasReceivedToken = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            // Handle both \n\n (SSE standard) and \n splits cleanly
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Hold onto partial chunk in buffer

            for (const line of lines) {
                const trimmedLine = line.trim();
                if (trimmedLine.startsWith('data: ')) {
                    const dataStr = trimmedLine.slice(6).trim();
                    
                    if (dataStr === '[DONE]') {
                        clearTimeout(thinkingTimer);
                        cursorSpan.remove();
                        classifyAssistantMoment(fullResponseText);
                        if (!fullResponseText) setLunaEmotion('idle');
                        speakLunaResponse(fullResponseText);
                        return;
                    }

                    try {
                        const parsed = JSON.parse(dataStr);

                        if (parsed.memory_request) {
                            cursorSpan.remove();
                            contentSpan.innerHTML = `
                                <div class="memory-card">
                                    <p>🌙 That sounds important, Arman.</p>
                                    <p>Would you like me to remember it?</p>
                                    <button class="memory-yes">Yes</button>
                                    <button class="memory-no">No</button>
                                </div>
                            `;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                            continue;
                        }

                        if (parsed.token) {
                            if (!hasReceivedToken) {
                                hasReceivedToken = true;
                                clearTimeout(thinkingTimer);
                                setLunaEmotion('speaking');
                            }
                            fullResponseText += parsed.token;
                            contentSpan.innerText = fullResponseText;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                    } catch (e) {
                        console.error("JSON parse error:", e, dataStr);
                    }
                }
            }
        }

    } catch (e) {
        clearTimeout(thinkingTimer);
        console.error("Stream connection error:", e);
        setLunaEmotion('idle');
        if (cursorSpan.parentNode) cursorSpan.remove();
        contentSpan.innerText = "I had trouble hearing you. Please try again.";
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

window.addEventListener('DOMContentLoaded', initLunaSpace);

if ('speechSynthesis' in window) {
    speechSynthesis.onvoiceschanged = () => {
        speechSynthesis.getVoices();
    };
}
