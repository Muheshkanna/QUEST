<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

export interface ExplainerSlide {
  title: string
  visual_hint: string
  narration: string
  highlight?: string
}

export interface ExplainerScript {
  slides: ExplainerSlide[]
}

const props = defineProps<{
  explainer: ExplainerScript
  topicId: string
}>()

const slides = computed(() => props.explainer?.slides || [])
const currentSlideIndex = ref(0)
const currentSlide = computed(() => slides.value[currentSlideIndex.value] || null)

// ── Web Speech API Narration State ────────────────────────────────────────
const isPlaying = ref(false)
const isSpeechSupported = ref(true)
const speechNotice = ref('')
const playbackRate = ref(1.0)
const availableVoices = ref<SpeechSynthesisVoice[]>([])
const selectedVoiceURI = ref<string>('')
const currentSentenceIndex = ref(0)
const showTranscript = ref(false)

let timerAdvanceId: ReturnType<typeof setTimeout> | null = null
let utterance: SpeechSynthesisUtterance | null = null

// Split current narration into sentences
const currentSentences = computed(() => {
  if (!currentSlide.value?.narration) return []
  const matches = currentSlide.value.narration.match(/[^.!?]+[.!?]+|[^.!?]+$/g)
  return matches ? matches.map(s => s.trim()).filter(Boolean) : [currentSlide.value.narration]
})

function loadVoices() {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    isSpeechSupported.value = false
    speechNotice.value = 'Audio narration unavailable in this browser. Running in visual autoplay mode.'
    return
  }

  const voices = window.speechSynthesis.getVoices()
  if (voices.length > 0) {
    // Filter and prioritize English voices
    const english = voices.filter(v => v.lang.startsWith('en'))
    availableVoices.value = english.length > 0 ? english : voices

    // Pick high quality default English voice if not selected yet
    if (!selectedVoiceURI.value && availableVoices.value.length > 0) {
      const preferred = availableVoices.value.find(v =>
        v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('David')
      ) || availableVoices.value[0]
      selectedVoiceURI.value = preferred.voiceURI
    }
  }
}

function stopSpeech() {
  if (timerAdvanceId) {
    clearTimeout(timerAdvanceId)
    timerAdvanceId = null
  }
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
  isPlaying.value = false
}

function speakCurrentSlide() {
  stopSpeech()
  if (!currentSlide.value) return

  currentSentenceIndex.value = 0
  isPlaying.value = true

  // If SpeechSynthesis is not supported, use estimated duration timer
  if (!isSpeechSupported.value || typeof window === 'undefined' || !('speechSynthesis' in window)) {
    startFallbackTimer()
    return
  }

  try {
    const textToSpeak = currentSlide.value.narration
    utterance = new SpeechSynthesisUtterance(textToSpeak)
    utterance.rate = playbackRate.value

    // Assign selected voice
    if (selectedVoiceURI.value) {
      const v = availableVoices.value.find(vox => vox.voiceURI === selectedVoiceURI.value)
      if (v) utterance.voice = v
    }

    // Boundary tracking for sentence highlight
    utterance.onboundary = (event) => {
      if (event.name === 'sentence' || event.name === 'word') {
        const charIndex = event.charIndex
        let cumulative = 0
        for (let i = 0; i < currentSentences.value.length; i++) {
          cumulative += currentSentences.value[i].length + 1
          if (charIndex < cumulative) {
            currentSentenceIndex.value = i
            break
          }
        }
      }
    }

    utterance.onend = () => {
      isPlaying.value = false
      // Auto-advance to next slide if not on the last slide
      if (currentSlideIndex.value < slides.value.length - 1) {
        timerAdvanceId = setTimeout(() => {
          nextSlide()
        }, 1200)
      }
    }

    utterance.onerror = (e) => {
      console.warn('Speech synthesis error or interrupted:', e)
      speechNotice.value = 'Audio narration unavailable in this browser. Running in visual autoplay mode.'
      startFallbackTimer()
    }

    window.speechSynthesis.speak(utterance)
  } catch (err) {
    console.warn('Failed to start speech:', err)
    startFallbackTimer()
  }
}

function startFallbackTimer() {
  isPlaying.value = true
  const wordCount = (currentSlide.value?.narration || '').split(/\s+/).length
  // Approx 130 words per minute scaled by rate
  const durationMs = Math.max(4000, Math.round((wordCount / (130 * playbackRate.value)) * 60 * 1000))

  // Estimate sentence progression across duration
  const sentCount = currentSentences.value.length
  if (sentCount > 1) {
    const stepMs = durationMs / sentCount
    let step = 0
    const stepInterval = setInterval(() => {
      step++
      if (step < sentCount) {
        currentSentenceIndex.value = step
      } else {
        clearInterval(stepInterval)
      }
    }, stepMs)
  }

  timerAdvanceId = setTimeout(() => {
    isPlaying.value = false
    if (currentSlideIndex.value < slides.value.length - 1) {
      nextSlide()
    }
  }, durationMs)
}

function togglePlayPause() {
  if (isPlaying.value) {
    stopSpeech()
  } else {
    speakCurrentSlide()
  }
}

function restartSlide() {
  speakCurrentSlide()
}

function goToSlide(index: number) {
  if (index < 0 || index >= slides.value.length) return
  currentSlideIndex.value = index
  speakCurrentSlide()
}

function prevSlide() {
  if (currentSlideIndex.value > 0) {
    goToSlide(currentSlideIndex.value - 1)
  }
}

function nextSlide() {
  if (currentSlideIndex.value < slides.value.length - 1) {
    goToSlide(currentSlideIndex.value + 1)
  }
}

function setPlaybackRate(rate: number) {
  playbackRate.value = rate
  if (isPlaying.value) {
    speakCurrentSlide()
  }
}

// ── Keyboard Controls ─────────────────────────────────────────────────────
function handleKeyDown(e: KeyboardEvent) {
  // Avoid capturing keystrokes when interacting with text inputs
  const target = e.target as HTMLElement
  if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
    return
  }

  if (e.code === 'Space') {
    e.preventDefault()
    togglePlayPause()
  } else if (e.code === 'ArrowRight' || e.code === 'ArrowDown') {
    e.preventDefault()
    nextSlide()
  } else if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') {
    e.preventDefault()
    prevSlide()
  }
}

// ── Visual Hint Classifier for SVG Scenes ─────────────────────────────────
const visualSceneType = computed(() => {
  const hint = (currentSlide.value?.visual_hint || '').toLowerCase()
  const title = (currentSlide.value?.title || '').toLowerCase()
  const combined = `${hint} ${title}`

  if (combined.includes('fraction') || combined.includes('denominator') || combined.includes('slice') || combined.includes('shield') || combined.includes('quarter') || combined.includes('half')) {
    return 'fractions'
  }
  if (combined.includes('ratio') || combined.includes('scale') || combined.includes('gem') || combined.includes('multiplier') || combined.includes('balance') || combined.includes('pouch')) {
    return 'ratios'
  }
  if (combined.includes('volume') || combined.includes('cube') || combined.includes('layer') || combined.includes('prism') || combined.includes('height') || combined.includes('grid')) {
    return 'volume'
  }
  return 'generic'
})

onMounted(() => {
  if (typeof window !== 'undefined') {
    loadVoices()
    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = loadVoices
    }
    window.addEventListener('keydown', handleKeyDown)
  }
  // Start slide 1 automatically
  speakCurrentSlide()
})

onBeforeUnmount(() => {
  stopSpeech()
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', handleKeyDown)
  }
})

watch(() => props.topicId, () => {
  currentSlideIndex.value = 0
  speakCurrentSlide()
})
</script>

<template>
  <div class="explainer-container" role="region" aria-label="Interactive Narrated Walkthrough">
    <!-- Notice when SpeechSynthesis is unavailable -->
    <div v-if="speechNotice" class="speech-notice" role="status">
      <span>ℹ️ {{ speechNotice }}</span>
    </div>

    <!-- 16:9 Stage -->
    <div class="stage-frame quest-surface-card" :aria-label="`Slide ${currentSlideIndex + 1}: ${currentSlide?.title}`">
      <!-- Top Stage HUD -->
      <div class="stage-hud">
        <span class="hud-pill" aria-live="polite">
          Slide {{ currentSlideIndex + 1 }} of {{ slides.length }}
        </span>
        <h2 class="hud-title font-display" aria-live="polite">
          {{ currentSlide?.title }}
        </h2>
        <span class="hud-topic font-display">{{ topicId.replace(/-/g, ' ') }}</span>
      </div>

      <!-- Stage Visual Canvas (16:9 Animated SVG Scene) -->
      <div class="stage-scene" role="img" :aria-label="currentSlide?.visual_hint || 'Visual illustration of current math concept'">
        <!-- Scene A: Fractions (Fraction bars, pie slices, dividing shields) -->
        <svg v-if="visualSceneType === 'fractions'" viewBox="0 0 800 450" class="scene-svg">
          <defs>
            <linearGradient id="blueElixir" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#235288" />
              <stop offset="100%" stop-color="#193D65" />
            </linearGradient>
            <linearGradient id="goldElixir" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#D9B66F" />
              <stop offset="100%" stop-color="#8E743F" />
            </linearGradient>
            <filter id="sceneGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          <!-- Arcane circle backdrop -->
          <circle cx="400" cy="225" r="170" fill="none" stroke="rgba(217, 182, 111, 0.15)" stroke-width="1.5" stroke-dasharray="8 8" />

          <!-- Left Fraction Bar: 1/4 -->
          <g transform="translate(180, 160)">
            <rect x="0" y="0" width="180" height="50" rx="8" fill="#0B1327" stroke="#D9B66F" stroke-width="2" />
            <rect x="0" y="0" width="45" height="50" rx="8" fill="url(#blueElixir)" />
            <line x1="45" y1="0" x2="45" y2="50" stroke="#D9B66F" stroke-width="1.5" />
            <line x1="90" y1="0" x2="90" y2="50" stroke="#D9B66F" stroke-width="1" stroke-dasharray="3 3" />
            <line x1="135" y1="0" x2="135" y2="50" stroke="#D9B66F" stroke-width="1" stroke-dasharray="3 3" />
            <text x="90" y="80" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" font-weight="700" text-anchor="middle">1 / 4</text>
          </g>

          <text x="400" y="195" fill="#D9B66F" font-family="'Cinzel', serif" font-size="34" font-weight="800" text-anchor="middle">+</text>

          <!-- Right Fraction Bar: 2/4 (renamed from 1/2) -->
          <g transform="translate(440, 160)">
            <rect x="0" y="0" width="180" height="50" rx="8" fill="#0B1327" stroke="#D9B66F" stroke-width="2" />
            <rect x="0" y="0" width="90" height="50" rx="8" fill="url(#goldElixir)" />
            <line x1="45" y1="0" x2="45" y2="50" stroke="#D9B66F" stroke-width="1" stroke-dasharray="3 3" />
            <line x1="90" y1="0" x2="90" y2="50" stroke="#D9B66F" stroke-width="1.5" />
            <line x1="135" y1="0" x2="135" y2="50" stroke="#D9B66F" stroke-width="1" stroke-dasharray="3 3" />
            <text x="90" y="80" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" font-weight="700" text-anchor="middle">2 / 4</text>
          </g>

          <!-- Result Bar underneath -->
          <g transform="translate(310, 275)" filter="url(#sceneGlow)">
            <rect x="0" y="0" width="180" height="50" rx="8" fill="#0B1327" stroke="#28745B" stroke-width="2" />
            <rect x="0" y="0" width="135" height="50" rx="8" fill="#28745B" opacity="0.8" />
            <line x1="45" y1="0" x2="45" y2="50" stroke="#D9B66F" stroke-width="1" stroke-dasharray="3 3" />
            <line x1="90" y1="0" x2="90" y2="50" stroke="#D9B66F" stroke-width="1" stroke-dasharray="3 3" />
            <line x1="135" y1="0" x2="135" y2="50" stroke="#D9B66F" stroke-width="1.5" />
            <text x="90" y="80" fill="#D9B66F" font-family="'Cinzel', serif" font-size="22" font-weight="800" text-anchor="middle">= 3 / 4</text>
          </g>
        </svg>

        <!-- Scene B: Ratios (Balance scale with colored gems, constant multiplier) -->
        <svg v-else-if="visualSceneType === 'ratios'" viewBox="0 0 800 450" class="scene-svg">
          <defs>
            <radialGradient id="sapphireGem" cx="35%" cy="35%" r="65%">
              <stop offset="0%" stop-color="#9C8AD6" />
              <stop offset="60%" stop-color="#235288" />
              <stop offset="100%" stop-color="#0B1327" />
            </radialGradient>
            <radialGradient id="amberGem" cx="35%" cy="35%" r="65%">
              <stop offset="0%" stop-color="#F1E8D6" />
              <stop offset="50%" stop-color="#D9B66F" />
              <stop offset="100%" stop-color="#8E743F" />
            </radialGradient>
          </defs>

          <!-- Scale Fulcrum & Beam -->
          <polygon points="400,320 380,360 420,360" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
          <line x1="220" y1="230" x2="580" y2="230" stroke="#D9B66F" stroke-width="4" stroke-linecap="round" />
          <line x1="400" y1="230" x2="400" y2="320" stroke="#D9B66F" stroke-width="3" />

          <!-- Left Scale Pan (2 Blue Gems) -->
          <line x1="220" y1="230" x2="180" y2="290" stroke="#B8B0A2" stroke-width="1.5" />
          <line x1="220" y1="230" x2="260" y2="290" stroke="#B8B0A2" stroke-width="1.5" />
          <path d="M 170 290 Q 220 310 270 290 Z" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
          <circle cx="205" cy="280" r="14" fill="url(#sapphireGem)" stroke="#D9B66F" stroke-width="1" />
          <circle cx="235" cy="280" r="14" fill="url(#sapphireGem)" stroke="#D9B66F" stroke-width="1" />
          <text x="220" y="340" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" font-weight="700" text-anchor="middle">2 Gems</text>

          <!-- Multiplier Sigil in Center -->
          <g transform="translate(400, 160)">
            <rect x="-45" y="-20" width="90" height="40" rx="8" fill="#0B1327" stroke="#28745B" stroke-width="2" />
            <text x="0" y="6" fill="#D9B66F" font-family="'JetBrains Mono', monospace" font-size="18" font-weight="700" text-anchor="middle">× 3</text>
          </g>

          <!-- Right Scale Pan (3 Amber Gems) -->
          <line x1="580" y1="230" x2="540" y2="290" stroke="#B8B0A2" stroke-width="1.5" />
          <line x1="580" y1="230" x2="620" y2="290" stroke="#B8B0A2" stroke-width="1.5" />
          <path d="M 530 290 Q 580 310 630 290 Z" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
          <circle cx="560" cy="280" r="14" fill="url(#amberGem)" stroke="#D9B66F" stroke-width="1" />
          <circle cx="585" cy="272" r="14" fill="url(#amberGem)" stroke="#D9B66F" stroke-width="1" />
          <circle cx="605" cy="280" r="14" fill="url(#amberGem)" stroke="#D9B66F" stroke-width="1" />
          <text x="580" y="340" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" font-weight="700" text-anchor="middle">3 Gems</text>
        </svg>

        <!-- Scene C: Volume (3D Isometric stacked unit cubes) -->
        <svg v-else-if="visualSceneType === 'volume'" viewBox="0 0 800 450" class="scene-svg">
          <defs>
            <linearGradient id="cubeTop" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#235288" />
              <stop offset="100%" stop-color="#193D65" />
            </linearGradient>
            <linearGradient id="cubeLeft" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#193D65" />
              <stop offset="100%" stop-color="#0B1327" />
            </linearGradient>
            <linearGradient id="cubeRight" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#0B1327" />
              <stop offset="100%" stop-color="#101B35" />
            </linearGradient>
          </defs>

          <!-- 3D Stacked Layers -->
          <g transform="translate(400, 230)">
            <!-- Base Layer Ground Inscription -->
            <ellipse cx="0" cy="110" rx="180" ry="60" fill="rgba(25, 61, 101, 0.4)" stroke="#D9B66F" stroke-width="1" stroke-dasharray="6 6" />

            <!-- Isometric Cubes Cluster -->
            <!-- Layer 1 -->
            <g transform="translate(-60, 50)">
              <polygon points="0,-25 30,-10 0,5 -30,-10" fill="url(#cubeTop)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="-30,-10 0,5 0,35 -30,20" fill="url(#cubeLeft)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="0,5 30,-10 30,20 0,35" fill="url(#cubeRight)" stroke="#D9B66F" stroke-width="1.2" />
            </g>
            <g transform="translate(0, 50)">
              <polygon points="0,-25 30,-10 0,5 -30,-10" fill="url(#cubeTop)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="-30,-10 0,5 0,35 -30,20" fill="url(#cubeLeft)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="0,5 30,-10 30,20 0,35" fill="url(#cubeRight)" stroke="#D9B66F" stroke-width="1.2" />
            </g>
            <g transform="translate(60, 50)">
              <polygon points="0,-25 30,-10 0,5 -30,-10" fill="url(#cubeTop)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="-30,-10 0,5 0,35 -30,20" fill="url(#cubeLeft)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="0,5 30,-10 30,20 0,35" fill="url(#cubeRight)" stroke="#D9B66F" stroke-width="1.2" />
            </g>

            <!-- Layer 2 (Stacked on top) -->
            <g transform="translate(0, 5)">
              <polygon points="0,-25 30,-10 0,5 -30,-10" fill="url(#cubeTop)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="-30,-10 0,5 0,35 -30,20" fill="url(#cubeLeft)" stroke="#D9B66F" stroke-width="1.2" />
              <polygon points="0,5 30,-10 30,20 0,35" fill="url(#cubeRight)" stroke="#D9B66F" stroke-width="1.2" />
            </g>

            <!-- Layer 3 (Top Monolith) -->
            <g transform="translate(0, -40)">
              <polygon points="0,-25 30,-10 0,5 -30,-10" fill="#28745B" stroke="#D9B66F" stroke-width="1.5" />
              <polygon points="-30,-10 0,5 0,35 -30,20" fill="#193D65" stroke="#D9B66F" stroke-width="1.5" />
              <polygon points="0,5 30,-10 30,20 0,35" fill="#0B1327" stroke="#D9B66F" stroke-width="1.5" />
            </g>
          </g>

          <text x="400" y="390" fill="#D9B66F" font-family="'JetBrains Mono', monospace" font-size="20" font-weight="700" text-anchor="middle">
            V = Length × Width × Height
          </text>
        </svg>

        <!-- Scene D: Generic Clean Title & Text Arcana Card -->
        <svg v-else viewBox="0 0 800 450" class="scene-svg">
          <circle cx="400" cy="225" r="160" fill="none" stroke="rgba(217, 182, 111, 0.2)" stroke-width="2" stroke-dasharray="10 10" />
          <circle cx="400" cy="225" r="120" fill="none" stroke="rgba(156, 138, 214, 0.3)" stroke-width="1.5" />
          <polygon points="400,105 504,285 296,285" fill="none" stroke="#D9B66F" stroke-width="1.5" opacity="0.4" />
          <polygon points="400,345 504,165 296,165" fill="none" stroke="#D9B66F" stroke-width="1.5" opacity="0.4" />
          <circle cx="400" cy="225" r="40" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
          <text x="400" y="234" fill="#D9B66F" font-family="'Cinzel', serif" font-size="26" font-weight="800" text-anchor="middle">✧</text>
          <text x="400" y="360" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="18" font-weight="700" text-anchor="middle">
            {{ currentSlide?.visual_hint || 'Mathematical Concept Illumination' }}
          </text>
        </svg>
      </div>

      <!-- Live Caption Subtitles Panel inside Stage -->
      <div class="stage-subtitles" aria-live="polite">
        <p class="subtitle-text">
          <span
            v-for="(sentence, sIdx) in currentSentences"
            :key="sIdx"
            class="sentence-span"
            :class="{ 'is-active-sentence': isPlaying && sIdx === currentSentenceIndex }"
          >
            <!-- Highlight key phrase in gold if present -->
            <template v-if="currentSlide?.highlight && sentence.includes(currentSlide.highlight)">
              <span>{{ sentence.split(currentSlide.highlight)[0] }}</span>
              <strong class="highlight-token">{{ currentSlide.highlight }}</strong>
              <span>{{ sentence.split(currentSlide.highlight)[1] }}</span>
            </template>
            <template v-else>
              {{ sentence }}
            </template>
            &nbsp;
          </span>
        </p>
      </div>

      <!-- Last Slide "Try It" Action Overlay -->
      <div v-if="currentSlideIndex === slides.length - 1" class="try-it-banner">
        <p class="try-it-text font-display">Walkthrough Complete! Test your skills in battle:</p>
        <NuxtLink :to="`/quiz/${topicId}`" class="btn-try-it font-display">
          ⚔️ Try It: Enter the Battle →
        </NuxtLink>
      </div>
    </div>

    <!-- Slide Timeline Progress Bar with Markers -->
    <div class="timeline-bar" role="navigation" aria-label="Slide timeline navigation">
      <div
        v-for="(_, index) in slides"
        :key="index"
        class="timeline-marker"
        :class="{
          'marker-active': index === currentSlideIndex,
          'marker-completed': index < currentSlideIndex
        }"
        :aria-label="`Jump to Slide ${index + 1}`"
        @click="goToSlide(index)"
      >
        <span class="marker-dot"></span>
        <span class="marker-label">{{ index + 1 }}</span>
      </div>
    </div>

    <!-- Media Controls Dock -->
    <div class="controls-dock quest-surface-card">
      <div class="dock-playback">
        <!-- Previous Slide -->
        <button
          type="button"
          class="dock-btn"
          aria-label="Previous slide"
          :disabled="currentSlideIndex === 0"
          @click="prevSlide"
        >
          ⏮ Previous
        </button>

        <!-- Play / Pause -->
        <button
          type="button"
          class="dock-btn dock-btn-primary"
          :aria-label="isPlaying ? 'Pause narration' : 'Play narration'"
          @click="togglePlayPause"
        >
          <span v-if="isPlaying">⏸ Pause</span>
          <span v-else>▶ Play</span>
        </button>

        <!-- Restart Current Slide -->
        <button
          type="button"
          class="dock-btn"
          aria-label="Restart current slide narration"
          @click="restartSlide"
        >
          ↻ Restart
        </button>

        <!-- Next Slide -->
        <button
          type="button"
          class="dock-btn"
          aria-label="Next slide"
          :disabled="currentSlideIndex === slides.length - 1"
          @click="nextSlide"
        >
          Next ⏭
        </button>
      </div>

      <!-- Settings: Speed & Voices & Transcript -->
      <div class="dock-settings">
        <!-- Speed Control (0.75x, 1x, 1.25x) -->
        <div class="speed-toggle" role="radiogroup" aria-label="Playback speed">
          <button
            v-for="rate in [0.75, 1.0, 1.25]"
            :key="rate"
            type="button"
            class="speed-btn"
            :class="{ 'speed-active': playbackRate === rate }"
            :aria-checked="playbackRate === rate"
            role="radio"
            @click="setPlaybackRate(rate)"
          >
            {{ rate }}x
          </button>
        </div>

        <!-- Voice Picker -->
        <div v-if="availableVoices.length > 0" class="voice-picker-wrapper">
          <label for="explainer-voice-select" class="sr-only">Choose Narration Voice</label>
          <select
            id="explainer-voice-select"
            v-model="selectedVoiceURI"
            class="voice-select"
            aria-label="Narration voice"
            @change="restartSlide"
          >
            <option v-for="vox in availableVoices" :key="vox.voiceURI" :value="vox.voiceURI">
              {{ vox.name }} ({{ vox.lang }})
            </option>
          </select>
        </div>

        <!-- Transcript Toggle -->
        <button
          type="button"
          class="dock-btn btn-transcript"
          :aria-expanded="showTranscript"
          aria-label="Toggle full lesson transcript"
          @click="showTranscript = !showTranscript"
        >
          📜 {{ showTranscript ? 'Hide' : 'Show' }} Transcript
        </button>
      </div>
    </div>

    <!-- Expandable Full Transcript Drawer -->
    <div v-if="showTranscript" class="transcript-drawer quest-surface-card" role="region" aria-label="Full Lesson Transcript">
      <h3 class="transcript-title font-display">Arcane Lesson Transcript</h3>
      <ol class="transcript-list">
        <li
          v-for="(slide, sIdx) in slides"
          :key="sIdx"
          class="transcript-item"
          :class="{ 'item-current': sIdx === currentSlideIndex }"
          @click="goToSlide(sIdx)"
        >
          <span class="transcript-slide-badge">Slide {{ sIdx + 1 }}: {{ slide.title }}</span>
          <p class="transcript-narration">{{ slide.narration }}</p>
        </li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
.explainer-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  width: 100%;
}

.speech-notice {
  padding: 10px 16px;
  background: rgba(217, 182, 111, 0.12);
  border: 1px solid rgba(217, 182, 111, 0.3);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-size: 13px;
}

/* 16:9 Stage Frame */
.stage-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1.5px solid var(--border-medium);
  background: radial-gradient(circle at 50% 30%, #193D65 0%, #0B1327 75%, #050A16 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-lg);
}

.stage-hud {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: linear-gradient(180deg, rgba(11, 19, 39, 0.85) 0%, transparent 100%);
  z-index: 2;
}

.hud-pill {
  font-size: 12px;
  font-weight: 700;
  color: var(--quest-gold);
  background: rgba(217, 182, 111, 0.15);
  border: 1px solid rgba(217, 182, 111, 0.35);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  letter-spacing: 0.05em;
}

.hud-title {
  font-size: 18px;
  color: var(--quest-parchment);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  letter-spacing: 0.03em;
}

.hud-topic {
  font-size: 12px;
  color: var(--quest-parchment-muted);
  text-transform: capitalize;
}

.stage-scene {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.scene-svg {
  width: 100%;
  height: 100%;
  max-height: 280px;
  display: block;
}

/* Subtitle Captions inside Stage */
.stage-subtitles {
  padding: 16px 24px;
  background: linear-gradient(0deg, rgba(11, 19, 39, 0.95) 0%, rgba(11, 19, 39, 0.75) 80%, transparent 100%);
  z-index: 2;
  text-align: center;
}

.subtitle-text {
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.6;
  color: var(--quest-parchment-muted);
}

.sentence-span {
  transition: all 0.3s ease;
}

.sentence-span.is-active-sentence {
  color: var(--quest-parchment);
  font-weight: 600;
  text-shadow: 0 0 10px var(--quest-gold-glow);
}

.highlight-token {
  color: var(--quest-gold);
  font-weight: 800;
  text-decoration: underline dotted var(--quest-gold);
}

/* Last Slide "Try It" Banner */
.try-it-banner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 24px 36px;
  background: rgba(11, 19, 39, 0.92);
  border: 1.5px solid var(--quest-gold);
  border-radius: var(--radius-md);
  box-shadow: 0 0 30px var(--quest-gold-glow);
  z-index: 5;
  text-align: center;
}

.try-it-text {
  font-size: 16px;
  color: var(--quest-parchment);
}

.btn-try-it {
  min-height: 44px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #D9B66F, #B8922A);
  color: #0B1327;
  font-size: 15px;
  font-weight: 800;
  border-radius: var(--radius-sm);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(217, 182, 111, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-try-it:hover {
  transform: scale(1.04);
  box-shadow: 0 6px 20px var(--quest-gold-glow);
}

/* Timeline Markers */
.timeline-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 12px;
}

.timeline-marker {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 6px 0;
}

.marker-dot {
  width: 100%;
  height: 4px;
  background: rgba(217, 182, 111, 0.2);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.marker-label {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--quest-parchment-faint);
  transition: color 0.3s ease;
}

.timeline-marker.marker-completed .marker-dot {
  background: var(--quest-emerald);
}

.timeline-marker.marker-active .marker-dot {
  background: var(--quest-gold);
  height: 6px;
  box-shadow: 0 0 8px var(--quest-gold);
}

.timeline-marker.marker-active .marker-label {
  color: var(--quest-gold);
  font-weight: 700;
}

/* Controls Dock */
.controls-dock {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: 12px 18px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: var(--surface-card);
  flex-wrap: wrap;
}

.dock-playback {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

.dock-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 8px 16px;
  background: rgba(25, 61, 101, 0.7);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.dock-btn:hover:not(:disabled) {
  background: rgba(35, 82, 136, 0.9);
  border-color: var(--quest-gold);
  color: var(--quest-gold);
}

.dock-btn:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 2px;
}

.dock-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.dock-btn-primary {
  background: linear-gradient(135deg, rgba(217, 182, 111, 0.25), rgba(40, 116, 91, 0.35));
  border-color: var(--quest-gold);
  color: var(--quest-gold);
  font-weight: 700;
}

.dock-settings {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.speed-toggle {
  display: flex;
  align-items: center;
  background: var(--surface-sunken);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.speed-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 6px 10px;
  background: transparent;
  border: none;
  color: var(--quest-parchment-muted);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.speed-btn:hover {
  color: var(--quest-gold);
}

.speed-btn.speed-active {
  background: rgba(217, 182, 111, 0.2);
  color: var(--quest-gold);
}

.voice-select {
  min-height: 44px;
  padding: 6px 12px;
  background: var(--surface-sunken);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--quest-parchment);
  font-family: var(--font-body);
  font-size: 12px;
  cursor: pointer;
}

.voice-select:focus-visible {
  outline: 2px solid var(--quest-gold);
}

.btn-transcript {
  background: transparent;
  border-color: var(--border-subtle);
}

/* Transcript Drawer */
.transcript-drawer {
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: var(--surface-card);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.transcript-title {
  font-size: 15px;
  color: var(--quest-gold);
}

.transcript-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-left: 18px;
}

.transcript-item {
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-xs);
  transition: background 0.2s ease;
}

.transcript-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.transcript-item.item-current {
  background: rgba(217, 182, 111, 0.12);
  border-left: 3px solid var(--quest-gold);
}

.transcript-slide-badge {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 700;
  color: var(--quest-gold);
  display: block;
  margin-bottom: 4px;
}

.transcript-narration {
  font-size: 13px;
  color: var(--quest-parchment-muted);
  line-height: 1.5;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
