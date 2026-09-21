<template>
  <div class="flex flex-col gap-3">
    <!-- Day Filters Bar -->
    <div class="flex items-center gap-1.5 rounded-lg border border-border bg-card p-1.5">
      <button
        v-for="d in days"
        :key="d.key"
        @click="selectDay(d.key)"
        class="rounded px-3 py-1 text-xs font-semibold transition-colors"
        :class="activeDay === d.key ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-accent hover:text-white'"
      >
        {{ d.label }}
      </button>

      <span class="ml-auto pr-2 text-xs font-mono text-slate-400">
        {{ totalEvents }} fixtures
      </span>
    </div>

    <!-- Loading Skeletons -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 4" :key="i" class="h-28 w-full animate-pulse rounded-lg border border-border bg-card/60"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="events.length === 0" class="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card p-10 text-center">
      <CalendarX class="size-10 text-slate-500 mb-2" />
      <h3 class="text-sm font-bold text-slate-200">No events available</h3>
      <p class="mt-1 text-xs text-slate-400">Try selecting a different sport or day filter.</p>
    </div>

    <!-- Grouped Events by Competition -->
    <div v-else v-for="(groupEvents, compName) in groupedEvents" :key="compName" class="overflow-hidden rounded-lg border border-border bg-card">
      <!-- Competition Header -->
      <div class="flex items-center justify-between border-b border-border bg-accent/40 px-3.5 py-2">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-300">{{ compName }}</span>
        <div class="flex items-center gap-4 text-[11px] font-bold text-slate-400">
          <span class="w-16 text-center">1</span>
          <span class="w-16 text-center">X</span>
          <span class="w-16 text-center">2</span>
        </div>
      </div>

      <!-- Match Rows -->
      <div class="divide-y divide-border/60">
        <div 
          v-for="ev in groupEvents" 
          :key="ev.id" 
          class="flex flex-col gap-2 p-3 transition-colors hover:bg-accent/30 sm:flex-row sm:items-center sm:justify-between"
        >
          <!-- Match Info -->
          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <span v-if="ev.status === 'LIVE'" class="flex items-center gap-1 rounded bg-red-500/20 px-1.5 py-0.5 text-[10px] font-bold text-red-400">
                <span class="size-1.5 rounded-full bg-red-500 animate-pulse"></span>
                LIVE {{ ev.clockSeconds ? `${Math.floor(ev.clockSeconds / 60)}'` : '' }}
              </span>
              <span v-else class="text-[11px] font-medium text-slate-400">
                {{ formatDate(ev.startsAt) }}
              </span>
              <span class="text-[10px] text-slate-500">| {{ ev.sport.name }}</span>
            </div>

            <div class="flex items-center gap-3 font-semibold text-sm text-slate-100">
              <span class="hover:text-blue-400 transition-colors cursor-pointer">{{ ev.home }}</span>
              <span v-if="ev.status === 'LIVE'" class="font-mono text-xs text-red-400 font-bold">
                {{ ev.homeScore }} - {{ ev.awayScore }}
              </span>
              <span v-else class="text-slate-500 text-xs">vs</span>
              <span class="hover:text-blue-400 transition-colors cursor-pointer">{{ ev.away }}</span>
            </div>
          </div>

          <!-- Odds Buttons -->
          <div class="flex items-center gap-2">
            <button
              v-for="sel in ev.primarySelections"
              :key="sel.id"
              @click="toggleOdd(ev, sel)"
              class="flex h-9 w-20 flex-col items-center justify-center rounded border px-2 py-1 transition-all active:scale-95 shadow-sm"
              :class="selectedIds.has(sel.id) 
                ? 'border-blue-400 bg-blue-600 text-white shadow-blue-500/20' 
                : 'border-border bg-accent/60 text-slate-400 hover:border-blue-500/50 hover:bg-blue-600/20'"
            >
              <span class="text-[10px] truncate max-w-full" :class="selectedIds.has(sel.id) ? 'text-blue-100 font-semibold' : 'text-slate-400'">
                {{ sel.name }}
              </span>
              <span class="font-mono text-xs font-bold" :class="selectedIds.has(sel.id) ? 'text-white' : 'text-blue-400'">
                {{ sel.odds.toFixed(2) }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { CalendarX } from 'lucide-vue-next'
import { fetchEvents, type EventItem, type SelectionItem } from '@/services/api'

const props = defineProps<{
  sport?: string
  liveOnly?: boolean
}>()

const emit = defineEmits(['select-odd'])

const days = [
  { key: 'all', label: 'All' },
  { key: 'today', label: 'Today' },
  { key: 'tomorrow', label: 'Tomorrow' },
]

const activeDay = ref('all')
const events = ref<EventItem[]>([])
const loading = ref(true)
const selectedIds = ref<Set<string>>(new Set())

const totalEvents = computed(() => events.value.length)

const groupedEvents = computed(() => {
  const groups: Record<string, EventItem[]> = {}
  for (const ev of events.value) {
    const comp = ev.competition?.name || 'Other Competition'
    if (!groups[comp]) groups[comp] = []
    groups[comp].push(ev)
  }
  return groups
})

function toggleOdd(ev: EventItem, sel: SelectionItem) {
  if (selectedIds.value.has(sel.id)) {
    selectedIds.value.delete(sel.id)
  } else {
    // Clear other selections for the same event
    for (const s of ev.primarySelections) {
      selectedIds.value.delete(s.id)
    }
    selectedIds.value.add(sel.id)
  }
  emit('select-odd', { event: ev, selection: sel })
}

async function loadEvents() {
  loading.value = true
  events.value = await fetchEvents(props.sport || 'all', activeDay.value, props.liveOnly ? 'live' : '')
  loading.value = false
}

function selectDay(dayKey: string) {
  activeDay.value = dayKey
  loadEvents()
}

function formatDate(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return 'Upcoming'
  }
}

watch(() => props.sport, () => loadEvents())
watch(() => props.liveOnly, () => loadEvents())

onMounted(() => loadEvents())
</script>
