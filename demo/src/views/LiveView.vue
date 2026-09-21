<template>
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
    <div class="lg:col-span-3">
      <SportsRail />
    </div>

    <div class="flex flex-col gap-4 lg:col-span-6">
      <div class="flex items-center gap-2">
        <span class="relative flex size-2.5">
          <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
          <span class="relative inline-flex size-2.5 rounded-full bg-red-500"></span>
        </span>
        <h2 class="text-base font-bold text-slate-100">Live Fixtures Now</h2>
      </div>

      <SportFeed :live-only="true" @select-odd="onSelectOdd" />
    </div>

    <div class="lg:col-span-3">
      <BetSlip 
        :selections="selections" 
        @remove-selection="removeSelection" 
        @clear-slip="selections = []" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SportsRail from '@/components/SportsRail.vue'
import SportFeed from '@/components/SportFeed.vue'
import BetSlip from '@/components/BetSlip.vue'
import type { EventItem, SelectionItem } from '@/services/api'

const selections = ref<{ event: EventItem; selection: SelectionItem }[]>([])

function onSelectOdd(item: { event: EventItem; selection: SelectionItem }) {
  const existingIdx = selections.value.findIndex(s => s.event.id === item.event.id)
  if (existingIdx >= 0) {
    selections.value[existingIdx] = item
  } else {
    selections.value.push(item)
  }
}

function removeSelection(idx: number) {
  selections.value.splice(idx, 1)
}
</script>
