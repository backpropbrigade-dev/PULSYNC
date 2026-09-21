<template>
  <div class="flex flex-col gap-4 max-w-4xl mx-auto py-4">
    <div class="flex items-center gap-2 border-b border-border pb-3">
      <Gift class="size-5 text-blue-400" />
      <h1 class="text-lg font-bold text-slate-100">Platform Features & Intelligence Tools</h1>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="font-bold text-sm text-blue-400">PULSYNC Real-Time Session Telemetry</h3>
        <p class="mt-1 text-xs text-slate-300 leading-relaxed">
          Continuously monitors user interaction velocity, oscillation, and friction loops to offer timely informational guidance.
        </p>
      </div>

      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="font-bold text-sm text-emerald-400">Non-Gambling Value-Seeking Strategy</h3>
        <p class="mt-1 text-xs text-slate-300 leading-relaxed">
          Recommends head-to-head statistics, player form comparisons, and official match rules without promoting betting.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Gift } from 'lucide-vue-next'
</script>
