<template>
  <header class="sticky top-0 z-50 flex items-center justify-between border-b border-border bg-[#0d111a]/95 px-4 py-2.5 backdrop-blur-md">
    <!-- Left Navigation -->
    <div class="flex items-center gap-6">
      <router-link to="/" class="flex items-center gap-2 font-black tracking-wider text-white">
        <span class="rounded bg-blue-600 px-2 py-0.5 text-xs text-white">PS</span>
        <span class="text-base">PULSYNC</span>
      </router-link>

      <nav class="hidden items-center gap-1 md:flex">
        <router-link 
          to="/sport" 
          class="rounded px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="$route.path === '/sport' || $route.path === '/' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-accent hover:text-white'"
        >
          Sport
        </router-link>
        <router-link 
          to="/live" 
          class="flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="$route.path === '/live' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-accent hover:text-white'"
        >
          <span class="relative flex size-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
            <span class="relative inline-flex size-2 rounded-full bg-red-500"></span>
          </span>
          Live
        </router-link>
        <router-link 
          to="/promotions" 
          class="rounded px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="$route.path === '/promotions' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-accent hover:text-white'"
        >
          Promotions
        </router-link>
        <router-link 
          to="/impact" 
          class="rounded px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="$route.path.startsWith('/impact') ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-accent hover:text-white'"
        >
          Impact & ROI
        </router-link>
      </nav>
    </div>

    <!-- Right Controls -->
    <div class="hidden items-center gap-3 lg:flex">
      <router-link 
        to="/profile" 
        class="flex items-center gap-2 rounded border border-border bg-card px-3 py-1.5 text-xs font-medium text-slate-200 transition-colors hover:bg-accent"
      >
        <User class="size-3.5 text-blue-400" />
        <span>Sports Enthusiast</span>
      </router-link>

      <router-link 
        to="/portal" 
        class="flex items-center gap-1.5 rounded border border-blue-500/30 bg-blue-500/10 px-3 py-1.5 text-xs font-semibold text-blue-400 transition-colors hover:bg-blue-500/20"
      >
        <Activity class="size-3.5" />
        <span>Analytics Portal</span>
      </router-link>

      <router-link 
        to="/impact" 
        class="flex items-center gap-1.5 rounded border border-emerald-500/40 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-400 transition-colors hover:bg-emerald-500/20"
      >
        <TrendingUp class="size-3.5" />
        <span>Impact & ROI</span>
      </router-link>
    </div>

    <!-- Mobile Menu Toggle -->
    <button @click="mobileMenuOpen = !mobileMenuOpen" class="block rounded p-1.5 text-slate-300 hover:bg-accent hover:text-white lg:hidden">
      <Menu class="size-5" />
    </button>
  </header>

  <!-- Mobile Menu Dropdown -->
  <div v-if="mobileMenuOpen" class="lg:hidden border-b border-border bg-[#0d111a] px-4 py-3 space-y-2">
    <router-link to="/sport" @click="mobileMenuOpen = false" class="block rounded px-3 py-2 text-sm font-semibold text-slate-300 hover:bg-accent hover:text-white">Sport</router-link>
    <router-link to="/live" @click="mobileMenuOpen = false" class="block rounded px-3 py-2 text-sm font-semibold text-slate-300 hover:bg-accent hover:text-white">Live</router-link>
    <router-link to="/impact" @click="mobileMenuOpen = false" class="block rounded px-3 py-2 text-sm font-semibold text-emerald-400 hover:bg-accent hover:text-white">Impact & ROI</router-link>
    <router-link to="/portal" @click="mobileMenuOpen = false" class="block rounded px-3 py-2 text-sm font-semibold text-blue-400 hover:bg-accent hover:text-white">Analytics Portal</router-link>
    <router-link to="/profile" @click="mobileMenuOpen = false" class="block rounded px-3 py-2 text-sm font-semibold text-slate-300 hover:bg-accent hover:text-white">Profile</router-link>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Activity, TrendingUp, Menu } from 'lucide-vue-next'

const mobileMenuOpen = ref(false)
</script>
