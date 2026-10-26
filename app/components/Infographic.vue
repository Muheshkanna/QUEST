<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

export interface InfographicStep {
  label: string
  detail: string
  math: string
}

export interface InfographicData {
  title: string
  steps: InfographicStep[]
  example?: string
  image_url?: string
  image_prompt?: string
  fallback_image?: string
}

const props = defineProps<{
  infographic: InfographicData
  topicId: string
}>()

// ── Image State & 8-Second Fallback Handling ──────────────────────────────
const imageLoading = ref(true)
const imageError = ref(false)
const showBuiltinSvg = ref(false)
const currentImgSrc = ref('')
const triedLocalPng = ref(false)
let timeoutTimer: ReturnType<typeof setTimeout> | null = null

function initImage() {
  imageLoading.value = true
  imageError.value = false
  showBuiltinSvg.value = false
  triedLocalPng.value = false

  if (timeoutTimer) clearTimeout(timeoutTimer)

  const primaryUrl = props.infographic?.image_url || ''
  if (!primaryUrl) {
    switchToFallback()
    return
  }

  currentImgSrc.value = primaryUrl

  // 8-second timeout requirement
  timeoutTimer = setTimeout(() => {
    if (imageLoading.value) {
      switchToFallback()
    }
  }, 8000)
}

function onImageLoad() {
  if (timeoutTimer) clearTimeout(timeoutTimer)
  imageLoading.value = false
  imageError.value = false
}

function onImageError() {
  if (timeoutTimer) clearTimeout(timeoutTimer)
  switchToFallback()
}

function switchToFallback() {
  if (!triedLocalPng.value) {
    triedLocalPng.value = true
    // Try local /fallback/<topic_id>.png
    currentImgSrc.value = `/fallback/${props.topicId}.png`
    return
  }
  // If local png failed or already tried, render the built-in code SVG
  imageLoading.value = false
  imageError.value = true
  showBuiltinSvg.value = true
}

// ── Animated Steps Diagram State ──────────────────────────────────────────
const svgContainerRef = ref<SVGSVGElement | null>(null)
const prefersReduced = ref(false)
const activeStepCount = ref(0)
let stepTimer: ReturnType<typeof setInterval> | null = null
const isDownloading = ref(false)

const steps = computed(() => props.infographic?.steps || [])

function startStepAnimation() {
  if (stepTimer) clearInterval(stepTimer)

  if (prefersReduced.value) {
    activeStepCount.value = steps.value.length
    return
  }

  activeStepCount.value = 1
  stepTimer = setInterval(() => {
    if (activeStepCount.value < steps.value.length) {
      activeStepCount.value++
    } else {
      if (stepTimer) clearInterval(stepTimer)
    }
  }, 1200)
}

function replayAnimation() {
  activeStepCount.value = 0
  setTimeout(() => {
    startStepAnimation()
  }, 150)
}

// ── Download Diagram as PNG ───────────────────────────────────────────────
async function downloadAsPng() {
  if (!svgContainerRef.value || isDownloading.value) return
  isDownloading.value = true

  try {
    const svgEl = svgContainerRef.value
    const serializer = new XMLSerializer()
    let svgString = serializer.serializeToString(svgEl)

    // Ensure xmlns is present
    if (!svgString.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      svgString = svgString.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"')
    }

    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)

    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      // 2x resolution for crisp high-DPI output
      const width = 800
      const height = 620
      canvas.width = width * 2
      canvas.height = height * 2
      const ctx = canvas.getContext('2d')

      if (ctx) {
        ctx.scale(2, 2)
        // Background fill matching Midnight Navy
        ctx.fillStyle = '#101B35'
        ctx.fillRect(0, 0, width, height)
        ctx.drawImage(img, 0, 0, width, height)

        const pngUrl = canvas.toDataURL('image/png')
        const downloadLink = document.createElement('a')
        downloadLink.download = `infographic-${props.topicId}.png`
        downloadLink.href = pngUrl
        downloadLink.click()
      }

      URL.revokeObjectURL(url)
      isDownloading.value = false
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      isDownloading.value = false
    }

    img.src = url
  } catch (err) {
    console.error('Failed to export infographic as PNG:', err)
    isDownloading.value = false
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    prefersReduced.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }
  initImage()
  startStepAnimation()
})

watch(() => props.topicId, () => {
  initImage()
  replayAnimation()
})

onBeforeUnmount(() => {
  if (timeoutTimer) clearTimeout(timeoutTimer)
  if (stepTimer) clearInterval(stepTimer)
})
</script>

<template>
  <div class="infographic-container" role="region" aria-label="Visual Mathematical Infographic">
    <!-- Top / Left: AI-generated visual or fallback illustration -->
    <div class="illustration-panel">
      <div class="image-wrapper quest-surface-card">
        <!-- Skeleton Loader -->
        <div v-if="imageLoading" class="image-skeleton" aria-hidden="true">
          <div class="skeleton-shimmer"></div>
          <div class="skeleton-rune">✧</div>
          <p class="skeleton-text">Summoning arcane illustration…</p>
        </div>

        <!-- Real Image -->
        <img
          v-if="!showBuiltinSvg"
          :src="currentImgSrc"
          :alt="infographic.title || 'Mathematical Infographic Illustration'"
          class="generated-image"
          :class="{ 'is-hidden': imageLoading }"
          @load="onImageLoad"
          @error="onImageError"
        />

        <!-- Code-Drawn Built-in SVG Fallback -->
        <div v-else class="builtin-svg-fallback" role="img" aria-label="Geometric Mathematical Illustration">
          <svg viewBox="0 0 600 400" class="fallback-svg" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="abyssGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#0B1327" />
                <stop offset="50%" stop-color="#193D65" />
                <stop offset="100%" stop-color="#101B35" />
              </linearGradient>
              <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#D9B66F" />
                <stop offset="100%" stop-color="#8E743F" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            <!-- Background Stratum -->
            <rect width="600" height="400" fill="url(#abyssGrad)" rx="12" />

            <!-- Arcane Mathematical Geometries -->
            <g opacity="0.35">
              <circle cx="300" cy="200" r="140" fill="none" stroke="#D9B66F" stroke-width="1.5" stroke-dasharray="6 6" />
              <circle cx="300" cy="200" r="100" fill="none" stroke="#9C8AD6" stroke-width="1" />
              <circle cx="300" cy="200" r="60" fill="none" stroke="#28745B" stroke-width="1.5" stroke-dasharray="4 4" />
              <line x1="160" y1="200" x2="440" y2="200" stroke="#D9B66F" stroke-width="1" stroke-opacity="0.4" />
              <line x1="300" y1="60" x2="300" y2="340" stroke="#D9B66F" stroke-width="1" stroke-opacity="0.4" />
            </g>

            <!-- Topic-adaptive central icon -->
            <g v-if="topicId.includes('fraction')" transform="translate(300, 200)" filter="url(#glow)">
              <rect x="-80" y="-30" width="60" height="60" rx="8" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
              <text x="-50" y="8" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" text-anchor="middle" font-weight="700">1/4</text>
              <text x="0" y="8" fill="#D9B66F" font-family="'Cinzel', serif" font-size="28" text-anchor="middle" font-weight="800">+</text>
              <rect x="20" y="-30" width="60" height="60" rx="8" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
              <text x="50" y="8" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" text-anchor="middle" font-weight="700">2/4</text>
            </g>
            <g v-else-if="topicId.includes('volume')" transform="translate(300, 200)" filter="url(#glow)">
              <!-- Isometric unit cube cluster -->
              <polygon points="0,-40 40,-20 0,0 -40,-20" fill="#235288" stroke="#D9B66F" stroke-width="1.5" />
              <polygon points="-40,-20 0,0 0,40 -40,20" fill="#193D65" stroke="#D9B66F" stroke-width="1.5" />
              <polygon points="0,0 40,-20 40,20 0,40" fill="#0B1327" stroke="#D9B66F" stroke-width="1.5" />
              <text x="0" y="65" fill="#D9B66F" font-family="'Cinzel', serif" font-size="16" text-anchor="middle" font-weight="700">L × W × H = V</text>
            </g>
            <g v-else transform="translate(300, 200)" filter="url(#glow)">
              <!-- Balanced Ratio Scales -->
              <circle cx="-60" cy="0" r="32" fill="#193D65" stroke="#28745B" stroke-width="2" />
              <circle cx="60" cy="0" r="48" fill="#193D65" stroke="#D9B66F" stroke-width="2" />
              <text x="-60" y="6" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="18" text-anchor="middle" font-weight="700">2 : 3</text>
              <text x="60" y="6" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="20" text-anchor="middle" font-weight="700">6 : 9</text>
            </g>

            <!-- Bottom Title Inscription -->
            <text x="300" y="365" fill="#F1E8D6" font-family="'Cinzel', serif" font-size="15" text-anchor="middle" letter-spacing="1">
              {{ infographic.title || 'Axiom of Arcane Mathematics' }}
            </text>
          </svg>
        </div>
      </div>

      <figcaption class="ai-caption">
        AI-generated illustration. The math below is drawn by code so it is always correct.
      </figcaption>
    </div>

    <!-- Bottom / Right: Animated SVG step diagram from structured InfographicData -->
    <div class="diagram-panel quest-surface-card">
      <div class="diagram-toolbar">
        <h3 class="diagram-title font-display">{{ infographic.title }}</h3>
        <div class="toolbar-actions">
          <button
            type="button"
            class="quest-btn-secondary"
            aria-label="Replay animated step diagram"
            @click="replayAnimation"
          >
            ↻ Replay
          </button>
          <button
            type="button"
            class="quest-btn-secondary"
            aria-label="Download infographic step diagram as PNG image"
            :disabled="isDownloading"
            @click="downloadAsPng"
          >
            <span v-if="isDownloading">Saving…</span>
            <span v-else>⤓ PNG</span>
          </button>
        </div>
      </div>

      <!-- Crisp SVG Step Diagram -->
      <div class="svg-stage-wrapper">
        <svg
          ref="svgContainerRef"
          viewBox="0 0 800 580"
          class="step-diagram-svg"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#193D65" stop-opacity="0.9" />
              <stop offset="100%" stop-color="#0B1327" stop-opacity="0.95" />
            </linearGradient>
            <linearGradient id="arrowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#D9B66F" />
              <stop offset="100%" stop-color="#28745B" />
            </linearGradient>
            <filter id="stepShadow" x="-10%" y="-10%" width="120%" height="130%">
              <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#050A16" flood-opacity="0.7" />
            </filter>
            <marker
              id="goldArrow"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#D9B66F" />
            </marker>
          </defs>

          <!-- Steps Loop: 4 stacked cards with connecting animated flow arrows -->
          <g v-for="(step, idx) in steps" :key="idx">
            <!-- Step Card Node -->
            <g
              class="step-node"
              :class="{
                'node-visible': idx < activeStepCount,
                'node-reduced': prefersReduced
              }"
              :transform="`translate(50, ${30 + idx * 125})`"
            >
              <!-- Card Background -->
              <rect
                x="0"
                y="0"
                width="700"
                height="92"
                rx="10"
                fill="url(#cardGrad)"
                stroke="rgba(217, 182, 111, 0.4)"
                stroke-width="1.5"
                filter="url(#stepShadow)"
              />

              <!-- Step Index Badge -->
              <circle cx="45" cy="46" r="22" fill="#0B1327" stroke="#D9B66F" stroke-width="2" />
              <text
                x="45"
                y="52"
                fill="#D9B66F"
                font-family="'Cinzel', Georgia, serif"
                font-size="16"
                font-weight="700"
                text-anchor="middle"
              >
                {{ idx + 1 }}
              </text>

              <!-- Step Label -->
              <text
                x="85"
                y="36"
                fill="#F1E8D6"
                font-family="'Cinzel', Georgia, serif"
                font-size="17"
                font-weight="700"
              >
                {{ step.label }}
              </text>

              <!-- Step Detail Text -->
              <text
                x="85"
                y="62"
                fill="#B8B0A2"
                font-family="'Plus Jakarta Sans', system-ui, sans-serif"
                font-size="13"
              >
                {{ step.detail }}
              </text>

              <!-- Crisp Math Formula Plaque -->
              <rect
                x="460"
                y="18"
                width="220"
                height="56"
                rx="6"
                fill="#0B1327"
                stroke="rgba(40, 116, 91, 0.6)"
                stroke-width="1.2"
              />
              <text
                x="570"
                y="52"
                fill="#D9B66F"
                font-family="'JetBrains Mono', monospace"
                font-size="17"
                font-weight="700"
                text-anchor="middle"
              >
                {{ step.math }}
              </text>
            </g>

            <!-- Connecting Arrow to Next Step -->
            <path
              v-if="idx < steps.length - 1"
              :d="`M 400 ${122 + idx * 125} L 400 ${150 + idx * 125}`"
              fill="none"
              stroke="#D9B66F"
              stroke-width="2.5"
              marker-end="url(#goldArrow)"
              class="flow-arrow"
              :class="{
                'arrow-drawn': idx < activeStepCount - 1,
                'arrow-reduced': prefersReduced
              }"
            />
          </g>

          <!-- Overall Worked Example Footer inside SVG -->
          <g v-if="infographic.example" transform="translate(50, 535)">
            <text
              x="0"
              y="18"
              fill="#D9B66F"
              font-family="'Cinzel', Georgia, serif"
              font-size="14"
              font-weight="700"
            >
              COMPLETE FORMULA:
            </text>
            <text
              x="170"
              y="18"
              fill="#F1E8D6"
              font-family="'JetBrains Mono', monospace"
              font-size="15"
              font-weight="700"
            >
              {{ infographic.example }}
            </text>
          </g>
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.infographic-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  width: 100%;
}

.illustration-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-medium);
  background: var(--surface-sunken);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-skeleton {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  background: linear-gradient(135deg, rgba(16, 27, 53, 0.95), rgba(25, 61, 101, 0.7));
  overflow: hidden;
}

.skeleton-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(217, 182, 111, 0.08) 50%,
    transparent 100%
  );
  animation: shimmer 1.8s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.skeleton-rune {
  font-size: 32px;
  color: var(--quest-gold);
  animation: pulseRune 2s infinite ease-in-out;
}

@keyframes pulseRune {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; filter: drop-shadow(0 0 12px var(--quest-gold)); }
}

.skeleton-text {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--quest-parchment-muted);
  letter-spacing: 0.05em;
  z-index: 1;
}

.generated-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.4s ease;
}

.generated-image.is-hidden {
  opacity: 0;
  position: absolute;
}

.builtin-svg-fallback {
  width: 100%;
  height: 100%;
  display: flex;
}

.fallback-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.ai-caption {
  font-size: 12px;
  color: var(--quest-parchment-faint);
  line-height: 1.4;
  font-style: italic;
  padding: 0 var(--space-2xs);
}

/* Diagram Panel */
.diagram-panel {
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-medium);
  background: var(--surface-card);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.diagram-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.diagram-title {
  font-size: 17px;
  color: var(--quest-gold);
  letter-spacing: 0.04em;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.quest-btn-secondary {
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

.quest-btn-secondary:hover:not(:disabled) {
  background: rgba(35, 82, 136, 0.9);
  border-color: var(--quest-gold);
  color: var(--quest-gold);
}

.quest-btn-secondary:focus-visible {
  outline: 2px solid var(--quest-gold);
  outline-offset: 2px;
}

.quest-btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.svg-stage-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.step-diagram-svg {
  width: 100%;
  height: auto;
  min-width: 440px;
  display: block;
}

/* Step Node Animation */
.step-node {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.step-node.node-visible,
.step-node.node-reduced {
  opacity: 1;
  transform: translateY(0);
}

/* Arrow stroke-dashoffset animation */
.flow-arrow {
  stroke-dasharray: 40;
  stroke-dashoffset: 40;
  transition: stroke-dashoffset 0.6s ease 0.3s;
}

.flow-arrow.arrow-drawn,
.flow-arrow.arrow-reduced {
  stroke-dashoffset: 0;
}

@media (prefers-reduced-motion: reduce) {
  .step-node,
  .flow-arrow {
    transition: none !important;
  }
}

@media (max-width: 640px) {
  .infographic-container {
    gap: var(--space-md);
  }
  .image-wrapper {
    aspect-ratio: 4 / 3;
  }
  .diagram-panel {
    padding: var(--space-sm);
  }
  .diagram-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .diagram-title {
    font-size: 15px;
  }
  .svg-stage-wrapper {
    margin: 0 -4px;
    width: calc(100% + 8px);
  }
  .step-diagram-svg {
    min-width: 360px;
  }
}
</style>
