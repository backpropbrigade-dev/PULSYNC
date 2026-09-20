<template>
  <div>
    <!-- PULSYNC SESSION INTELLIGENCE PANEL -->
    <div class="rounded-lg border border-blue-500/30 bg-gradient-to-r from-blue-950/40 via-card to-slate-900/60 p-4 shadow-lg mb-4">
      <div class="flex items-center justify-between border-b border-blue-500/20 pb-2.5 mb-3">
        <div class="flex items-center gap-2">
          <Sparkles class="size-4 text-blue-400 animate-pulse" />
          <span class="text-xs font-bold uppercase tracking-wider text-blue-400">PULSYNC Session Intelligence</span>
        </div>
        <span class="text-[11px] font-mono text-slate-400">{{ sessionId ? sessionId.slice(0, 14) : '—' }}</span>
      </div>

      <!-- Machine 3 Signal Badges -->
      <div class="grid grid-cols-2 gap-2 mb-3 md:grid-cols-4">
        <!-- Transaction Intent -->
        <div class="rounded-md bg-slate-800/60 border border-slate-700/50 p-2 text-center">
          <div class="text-[10px] uppercase font-semibold text-slate-400 mb-1">Transaction Intent</div>
          <span :class="intentBadgeClass(intel?.transaction_intent)" class="text-xs font-bold px-2 py-0.5 rounded">
            {{ intel?.transaction_intent ?? '…' }}
          </span>
        </div>
        <!-- Information Interest -->
        <div class="rounded-md bg-slate-800/60 border border-slate-700/50 p-2 text-center">
          <div class="text-[10px] uppercase font-semibold text-slate-400 mb-1">Info Interest</div>
          <span :class="infoInterestBadgeClass(intel?.information_interest)" class="text-xs font-bold px-2 py-0.5 rounded">
            {{ intel?.information_interest ?? '…' }}
          </span>
        </div>
        <!-- Intent -->
        <div class="rounded-md bg-slate-800/60 border border-slate-700/50 p-2 text-center">
          <div class="text-[10px] uppercase font-semibold text-slate-400 mb-1">Intent</div>
          <span class="text-xs font-bold text-purple-300 bg-purple-900/40 px-2 py-0.5 rounded">
            {{ intel?.intent ?? '…' }} <span v-if="intel?.intent_confidence">· {{ (intel.intent_confidence * 100).toFixed(0) }}%</span>
          </span>
        </div>
        <!-- Engagement State -->
        <div class="rounded-md bg-slate-800/60 border border-slate-700/50 p-2 text-center">
          <div class="text-[10px] uppercase font-semibold text-slate-400 mb-1">Engagement</div>
          <span :class="engagementBadgeClass(intel?.engagement_state)" class="text-xs font-bold px-2 py-0.5 rounded">
            {{ intel?.engagement_state ?? '…' }}
          </span>
        </div>
      </div>

      <!-- Engagement message -->
      <div v-if="intel?.engagement_message" class="mb-3 rounded-md border border-amber-500/30 bg-amber-900/20 px-3 py-2 text-xs text-amber-200 flex items-center gap-2">
        <MessageCircle class="size-3.5 shrink-0 text-amber-400" />
        <span>{{ intel.engagement_message }}</span>
      </div>

      <!-- RESPECT_EXIT: no content, no prompt -->
      <div v-if="intel?.engagement_state === 'RESPECT_EXIT'" class="text-center text-slate-500 text-xs py-2">
        — No suggestions. Respecting your session exit. —
      </div>

      <!-- Recommendations -->
      <div v-else-if="recommendations.length > 0" class="grid gap-3 md:grid-cols-2">
        <div
          v-for="rec in recommendations.slice(0, 2)"
          :key="rec.id || rec.content_id"
          class="flex flex-col justify-between rounded-md border border-border/80 bg-accent/40 p-3 transition-all hover:border-blue-500/40"
        >
          <div>
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-slate-100">{{ rec.title }}</h4>
              <span class="text-[10px] font-mono text-amber-400 font-semibold">{{ rec.score }}%</span>
            </div>
            <p class="mt-1 text-xs text-slate-300 leading-relaxed">{{ rec.description || rec.reason }}</p>
            <div class="mt-2 flex items-center gap-1.5 text-[11px] text-blue-400">
              <Info class="size-3 shrink-0" />
              <span>{{ rec.reason }}</span>
            </div>
          </div>
          <button
            @click="clickGuidance(rec)"
            class="mt-3 flex items-center justify-center gap-1.5 rounded bg-blue-600/30 border border-blue-500/50 px-3 py-2 text-xs font-bold text-blue-200 transition-all hover:bg-blue-600 hover:text-white active:scale-95 shadow"
          >
            <span>{{ rec.action_label || 'View Details' }}</span>
            <ChevronRight class="size-3.5" />
          </button>
        </div>
      </div>

      <!-- Score bar -->
      <div class="mt-3 flex items-center gap-3 text-[11px] text-slate-400 border-t border-slate-800 pt-2 flex-wrap">
        <span>Session Quality: <b class="text-slate-200">{{ intel?.session_quality ?? intel?.session_quality_score ?? '—' }}</b></span>
        <span>Abandonment Risk: <b class="text-slate-200">{{ ((intel?.abandonment_probability ?? 0) * 100).toFixed(0) }}%</b></span>
        <span v-if="intel?.continuation_probability">Continuation: <b class="text-slate-200">{{ (intel.continuation_probability * 100).toFixed(0) }}%</b></span>
        <span class="ml-auto text-[10px] font-mono text-blue-400 bg-blue-900/30 px-1.5 py-0.5 rounded border border-blue-500/20">
          Model: {{ intel?.model_versions ? 'ML ' + (intel.model_versions.intent || 'v1') : 'Heuristic' }}
        </span>
      </div>
    </div>

    <!-- Interactive modal for clicked recommendation -->
    <div v-if="activeModalRec" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
      <div class="w-full max-w-lg rounded-xl border border-blue-500/40 bg-[#0d121d] p-5 shadow-2xl">
        <div class="flex items-center justify-between border-b border-border pb-3">
          <div class="flex items-center gap-2">
            <BarChart2 class="size-5 text-blue-400" />
            <h3 class="text-sm font-bold text-slate-100">{{ activeModalRec.title }}</h3>
          </div>
          <button @click="closeModal" class="rounded p-1 text-slate-400 hover:bg-accent hover:text-white">
            <X class="size-4" />
          </button>
        </div>

        <div class="mt-4 flex flex-col gap-3">
          <div class="rounded-lg border border-border bg-card p-3">
            <div class="flex items-center justify-between text-xs font-bold text-slate-300 border-b border-border/60 pb-1.5">
              <span>Fixture: Viking vs Dinamo Zagreb</span>
              <span class="text-emerald-400 font-mono">LIVE 24'</span>
            </div>
            <div class="mt-2.5 flex flex-col gap-1.5 text-xs">
              <span class="text-[11px] font-semibold text-slate-400">Head-to-Head Encounters (Last 5 Matches)</span>
              <div class="flex items-center justify-between rounded bg-accent/50 px-2.5 py-1 text-slate-200">
                <span>Aug 2026: Dinamo Zagreb 2 - 1 Viking</span>
                <span class="font-bold text-blue-400">Dinamo Win</span>
              </div>
              <div class="flex items-center justify-between rounded bg-accent/50 px-2.5 py-1 text-slate-200">
                <span>May 2026: Viking 1 - 1 Dinamo Zagreb</span>
                <span class="font-bold text-amber-400">Draw</span>
              </div>
              <div class="flex items-center justify-between rounded bg-accent/50 px-2.5 py-1 text-slate-200">
                <span>Feb 2026: Dinamo Zagreb 0 - 2 Viking</span>
                <span class="font-bold text-emerald-400">Viking Win</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-lg border border-border bg-card p-3">
              <span class="text-[11px] font-bold uppercase text-slate-400">Viking Form</span>
              <div class="mt-1.5 flex items-center gap-1 font-mono text-xs font-bold">
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
                <span class="rounded bg-amber-500/20 px-1.5 py-0.5 text-amber-400">D</span>
                <span class="rounded bg-red-500/20 px-1.5 py-0.5 text-red-400">L</span>
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
              </div>
              <span class="mt-1 text-[10px] text-slate-400 block">Avg Goals Scored: 1.8 / match</span>
            </div>
            <div class="rounded-lg border border-border bg-card p-3">
              <span class="text-[11px] font-bold uppercase text-slate-400">Dinamo Zagreb Form</span>
              <div class="mt-1.5 flex items-center gap-1 font-mono text-xs font-bold">
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
                <span class="rounded bg-amber-500/20 px-1.5 py-0.5 text-amber-400">D</span>
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
                <span class="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-400">W</span>
              </div>
              <span class="mt-1 text-[10px] text-slate-400 block">Avg Goals Scored: 2.2 / match</span>
            </div>
          </div>

          <div class="rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-xs text-blue-300">
            <div class="flex items-center gap-1.5 font-bold mb-1">
              <CheckCircle2 class="size-4 text-blue-400" />
              <span>Feedback Logged to PULSYNC Engine</span>
            </div>
            <p class="text-[11px] text-slate-300 leading-relaxed">
              Interaction recorded. Recommendation scoring model dynamically updated for session {{ sessionId?.slice(0, 12) }}.
            </p>
          </div>
        </div>

        <div class="mt-4 flex justify-end">
          <button @click="closeModal" class="rounded bg-blue-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-blue-500">
            Close Analysis
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Sparkles, Info, ChevronRight, BarChart2, X, CheckCircle2, MessageCircle } from 'lucide-vue-next'
import {
  createSession, fetchSessionIntelligence,
  trackSessionEvent, type RecommendationItem, type SessionIntel
} from '@/services/api'

const sessionId = ref('')
const intel = ref<SessionIntel | null>(null)
const activeModalRec = ref<RecommendationItem | null>(null)

const recommendations = computed(() => intel.value?.recommendations ?? [])

onMounted(async () => {
  const anonId = localStorage.getItem('pulsync_anon_id') || crypto.randomUUID()
  localStorage.setItem('pulsync_anon_id', anonId)

  try {
    sessionId.value = await createSession(anonId)
    await trackSessionEvent(sessionId.value, 'page_view', '/sport', 'browse')
    // Fetch full intelligence (includes recommendations + Machine 3 signals)
    intel.value = await fetchSessionIntelligence(sessionId.value)
  } catch (error) {
    console.error('Unable to initialize PULSYNC session intelligence', error)
  }
  window.addEventListener('pulsync-session-updated', refreshIntelligence)
})

async function refreshIntelligence(event?: Event) {
  const session = (event as CustomEvent<string> | undefined)?.detail
  if (!sessionId.value || (session && session !== sessionId.value)) return
  intel.value = await fetchSessionIntelligence(sessionId.value)
}

onUnmounted(() => {
  window.removeEventListener('pulsync-session-updated', refreshIntelligence)
})

async function clickGuidance(rec: RecommendationItem) {
  activeModalRec.value = rec
  if (sessionId.value) {
    // Fire telemetry for the recommendation click
    const action = (rec.content_type || rec.title || '').toLowerCase().replace(/\s+/g, '_')
    await trackSessionEvent(sessionId.value, `recommendation_click`, '/sport', action)
    // Refresh intelligence after click
    await refreshIntelligence()
  }
}

function closeModal() {
  activeModalRec.value = null
}

// Badge helpers
function intentBadgeClass(val?: string) {
  if (val === 'HIGH') return 'bg-red-900/60 text-red-300'
  if (val === 'MEDIUM') return 'bg-amber-900/60 text-amber-300'
  return 'bg-slate-700 text-slate-300'
}

function infoInterestBadgeClass(val?: string) {
  if (val === 'HIGH') return 'bg-emerald-900/60 text-emerald-300'
  if (val === 'MEDIUM') return 'bg-yellow-900/60 text-yellow-300'
  return 'bg-slate-700 text-slate-300'
}

function engagementBadgeClass(val?: string) {
  if (val === 'VALUE_SEEKING') return 'bg-blue-900/60 text-blue-300'
  if (val === 'RESPECT_EXIT') return 'bg-slate-700 text-slate-400'
  if (val === 'LOW_PRESSURE') return 'bg-purple-900/60 text-purple-300'
  return 'bg-emerald-900/60 text-emerald-300'
}
</script>
