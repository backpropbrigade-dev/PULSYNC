<template>
  <aside class="flex w-full flex-col gap-4 lg:block">
    <!-- Quick Links (Hidden on mobile to save vertical space, already in header) -->
    <nav class="hidden rounded-lg border border-border bg-card lg:block mb-4">
      <div class="border-b border-border px-3.5 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
        Recommended
      </div>
      <div class="flex flex-col p-1.5 gap-0.5">
        <router-link
          to="/sport"
          class="flex items-center gap-2.5 rounded px-2.5 py-2 text-xs font-semibold transition-colors hover:bg-accent"
          :class="!$route.query.sport || $route.query.sport === 'all' ? 'bg-accent text-white font-bold' : 'text-slate-300'"
        >
          <Star class="size-4 text-amber-400" />
          <span>Top offer</span>
        </router-link>

        <router-link
          to="/live"
          class="flex items-center gap-2.5 rounded px-2.5 py-2 text-xs font-semibold transition-colors hover:bg-accent text-slate-300"
        >
          <Zap class="size-4 text-amber-500" />
          <span>Live now</span>
        </router-link>

        <router-link
          to="/promotions"
          class="flex items-center gap-2.5 rounded px-2.5 py-2 text-xs font-semibold transition-colors hover:bg-accent text-slate-300"
        >
          <Gift class="size-4 text-blue-400" />
          <span>Promotions</span>
        </router-link>
      </div>
    </nav>

    <!-- Sports List -->
    <nav class="rounded-lg border border-border bg-card">
      <div class="hidden lg:flex items-center justify-between border-b border-border px-3.5 py-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Sports</span>
        <span class="rounded bg-blue-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-blue-400">
          {{ sports.length }} Available
        </span>
      </div>

      <!-- Horizontal scroll on mobile, vertical list on desktop -->
      <div class="flex overflow-x-auto lg:max-h-[560px] lg:flex-col lg:overflow-y-auto p-1.5 gap-1.5 lg:gap-0.5 no-scrollbar">
        <div v-if="loading" class="flex lg:flex-col gap-2 p-2">
          <div v-for="i in 8" :key="i" class="h-8 w-24 lg:w-full shrink-0 animate-pulse rounded bg-accent/50"></div>
        </div>

        <router-link
          v-for="sport in sports"
          :key="sport.id"
          :to="{ path: '/sport', query: { sport: sport.slug } }"
          class="flex shrink-0 items-center gap-2 rounded px-3 lg:px-2.5 py-2 lg:py-1.5 text-xs transition-colors hover:bg-accent border lg:border-transparent border-border"
          :class="$route.query.sport === sport.slug ? 'bg-blue-600/20 font-bold text-blue-400 border-blue-500/30 lg:border-blue-500/30' : 'text-slate-300 bg-accent/30 lg:bg-transparent'"
        >
          <Trophy class="size-3.5 shrink-0 text-slate-400 hidden lg:block" />
          <span class="truncate whitespace-nowrap">{{ sport.name }}</span>

          <span v-if="sport.liveCount > 0" class="rounded bg-red-500/20 px-1.5 py-0.5 text-[10px] font-bold text-red-400">
            {{ sport.liveCount }}
          </span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Trophy, Star, Zap, Gift } from 'lucide-vue-next'
import { fetchSports, type SportItem } from '@/services/api'

const sports = ref<SportItem[]>([])
const loading = ref(true)

onMounted(async () => {
  sports.value = await fetchSports()
  loading.value = false
})
</script>
