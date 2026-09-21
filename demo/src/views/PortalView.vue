<template>
  <div class="flex flex-col gap-5 max-w-6xl mx-auto py-2">
    <div class="flex items-center justify-between border-b border-border pb-3">
      <div class="flex items-center gap-2">
        <Activity class="size-5 text-blue-400" />
        <h1 class="text-lg font-bold text-slate-100">Analytics & FEG Dataset Portal</h1>
      </div>
      <span class="rounded bg-blue-500/10 px-2.5 py-1 text-xs font-semibold text-blue-400">
        Live Telemetry Active
      </span>
    </div>

    <!-- FEG Dataset Summary Banner -->
    <DatasetSummaryCard />

    <!-- KPIs Grid -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-lg border border-border bg-card p-3.5">
        <span class="text-xs text-slate-400">Total Preprocessed Sessions</span>
        <p class="mt-1 font-mono text-2xl font-black text-slate-100">
          {{ (analytics?.kpis?.totalBets || 15738).toLocaleString() }}
        </p>
      </div>

      <div class="rounded-lg border border-border bg-card p-3.5">
        <span class="text-xs text-slate-400">Active Customers</span>
        <p class="mt-1 font-mono text-2xl font-black text-slate-100">
          {{ (analytics?.kpis?.activeCustomers || 15738).toLocaleString() }}
        </p>
      </div>

      <div class="rounded-lg border border-border bg-card p-3.5">
        <span class="text-xs text-slate-400">DEMO Turnover</span>
        <p class="mt-1 font-mono text-2xl font-black text-emerald-400">
          €{{ (analytics?.kpis?.turnover || 70500).toLocaleString() }}
        </p>
      </div>

      <div class="rounded-lg border border-border bg-card p-3.5">
        <span class="text-xs text-slate-400">Live Fixtures Tracked</span>
        <p class="mt-1 font-mono text-2xl font-black text-blue-400">
          {{ analytics?.kpis?.liveEvents || 60 }}
        </p>
      </div>
    </div>

    <!-- Sports Distribution & Daily Trend -->
    <div class="grid gap-4 md:grid-cols-2">
      <!-- Activity by Sport -->
      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
          Top Sports Activity Breakdown (Dataset)
        </h3>
        <div class="flex flex-col gap-2">
          <div 
            v-for="s in analytics?.betsBySport || defaultSports" 
            :key="s.name"
            class="flex items-center justify-between rounded bg-accent/40 px-3 py-2 text-xs"
          >
            <span class="font-semibold text-slate-200">{{ s.name }}</span>
            <span class="font-mono font-bold text-blue-400">{{ s.value.toLocaleString() }} actions</span>
          </div>
        </div>
      </div>

      <!-- Daily Trend -->
      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
          Daily Action Volume (Last 7 Days)
        </h3>
        <div class="flex flex-col gap-2">
          <div 
            v-for="d in analytics?.byDay || defaultDays" 
            :key="d.day"
            class="flex items-center justify-between rounded bg-accent/40 px-3 py-2 text-xs"
          >
            <span class="font-semibold text-slate-200">{{ d.day }}</span>
            <div class="flex items-center gap-3 font-mono">
              <span class="text-slate-400">{{ d.bets }} actions</span>
              <span class="font-bold text-emerald-400">€{{ d.turnover }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Activity } from 'lucide-vue-next'
import DatasetSummaryCard from '@/components/DatasetSummaryCard.vue'
import { fetchAnalytics } from '@/services/api'

const analytics = ref<any>(null)

const defaultSports = [
  { name: 'Football', value: 2765432 },
  { name: 'Tennis', value: 124530 },
  { name: 'Basketball', value: 52140 },
  { name: 'Baseball', value: 32100 },
  { name: 'Ice Hockey', value: 20120 },
]

const defaultDays = [
  { day: 'Mon', bets: 120, turnover: 4500 },
  { day: 'Tue', bets: 180, turnover: 6200 },
  { day: 'Wed', bets: 210, turnover: 7800 },
  { day: 'Thu', bets: 190, turnover: 6900 },
  { day: 'Fri', bets: 310, turnover: 11200 },
  { day: 'Sat', bets: 450, turnover: 18500 },
  { day: 'Sun', bets: 380, turnover: 15400 },
]

onMounted(async () => {
  analytics.value = await fetchAnalytics()
})
</script>
