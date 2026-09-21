<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 flex flex-col font-sans">
    <Header />
    <main class="flex-1 px-4 py-4 max-w-[1600px] w-full mx-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import Header from './components/Header.vue'
</script>
