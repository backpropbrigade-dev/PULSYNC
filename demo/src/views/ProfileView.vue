<template>
  <div class="flex flex-col gap-4 max-w-4xl mx-auto py-2">
    <div class="flex items-center gap-2 border-b border-border pb-3">
      <User class="size-5 text-blue-400" />
      <h1 class="text-lg font-bold text-slate-100">My Profile & FEG Dataset Intelligence</h1>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="text-xs font-bold uppercase text-slate-400">User Summary</h3>
        <p class="mt-2 text-base font-bold text-slate-100">Sports Enthusiast</p>
        <p class="text-xs text-slate-400">fan@pulsync.ai</p>
        <div class="mt-3 flex items-center gap-1.5">
          <span class="rounded bg-blue-500/20 px-2 py-0.5 text-[10px] font-bold text-blue-400">Customer</span>
          <span class="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400">Active</span>
        </div>
      </div>

      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="text-xs font-bold uppercase text-slate-400">Demo Wallet</h3>
        <p class="mt-2 font-mono text-2xl font-black text-emerald-400">€1,000.00</p>
        <p class="mt-1 text-xs text-slate-400">Bonus: €50.00</p>
      </div>

      <div class="rounded-lg border border-border bg-card p-4">
        <h3 class="text-xs font-bold uppercase text-slate-400">Historical Intelligence Profile</h3>
        <div v-if="profile" class="mt-2 flex flex-col gap-1.5 text-xs">
          <div class="flex justify-between">
            <span class="text-slate-400">Preferred Sport:</span>
            <span class="font-bold text-slate-100">{{ profile.preferred_sport }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Activity Level:</span>
            <span class="font-bold text-emerald-400">{{ profile.activity_level }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Dataset Actions:</span>
            <span class="font-mono font-bold text-slate-100">
              {{ profile.historical_activity?.total_actions || 2540 }}
            </span>
          </div>
        </div>
        <div v-else class="mt-2 text-xs text-slate-500">Loading dataset profile...</div>
      </div>
    </div>

    <!-- Sports Affinity Breakdown -->
    <div v-if="profile?.sports_interest" class="rounded-lg border border-border bg-card p-4">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">
        FEG Dataset Sport Affinity Distribution
      </h3>
      <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-5">
        <div 
          v-for="(val, sport) in profile.sports_interest" 
          :key="sport" 
          class="flex flex-col gap-1 rounded border border-border bg-background p-2.5"
        >
          <span class="text-xs font-semibold text-slate-300">{{ sport }}</span>
          <span class="font-mono text-sm font-bold text-blue-400">
            {{ (val * 100).toFixed(1) }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User } from 'lucide-vue-next'
import { fetchUserProfile, type PlayerProfileData } from '@/services/api'

const profile = ref<PlayerProfileData | null>(null)

onMounted(async () => {
  profile.value = await fetchUserProfile('usr_demo')
})
</script>
