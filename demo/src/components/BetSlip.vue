<template>
  <aside class="flex w-full flex-col gap-3 rounded-lg border border-border bg-card p-3.5">
    <div class="flex items-center justify-between border-b border-border pb-2.5">
      <div class="flex items-center gap-2">
        <Ticket class="size-4 text-blue-400" />
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200">Selection Slip</h3>
      </div>
      <span class="rounded bg-accent px-2 py-0.5 font-mono text-[11px] font-bold text-slate-300">
        {{ selections.length }} Selected
      </span>
    </div>

    <!-- Empty Slip -->
    <div v-if="selections.length === 0" class="flex flex-col items-center justify-center py-10 text-center">
      <Receipt class="size-10 text-slate-600 mb-2" />
      <p class="text-xs font-semibold text-slate-300">Your slip is empty</p>
      <p class="mt-1 text-[11px] text-slate-500 max-w-[200px]">
        Click odds on any match fixture to add a selection. DEMO CREDITS ONLY.
      </p>
    </div>

    <!-- Active Selections -->
    <div v-else class="flex flex-col gap-2.5">
      <div 
        v-for="(sel, idx) in selections" 
        :key="idx" 
        class="flex flex-col gap-1.5 rounded-md border border-border/80 bg-accent/40 p-2.5"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-blue-400">{{ sel.selection.name }}</span>
          <button @click="$emit('remove-selection', idx)" class="text-slate-500 hover:text-red-400">
            <X class="size-3.5" />
          </button>
        </div>
        <div class="text-[11px] text-slate-300">
          {{ sel.event.home }} vs {{ sel.event.away }}
        </div>
        <div class="flex items-center justify-between font-mono text-xs">
          <span class="text-slate-400">Odds</span>
          <span class="font-bold text-slate-100">{{ sel.selection.odds.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Stake Input & Total -->
      <div class="mt-2 flex flex-col gap-2 border-t border-border pt-3">
        <div class="flex items-center justify-between text-xs">
          <span class="text-slate-400">Demo Stake</span>
          <div class="flex items-center gap-1">
            <span class="text-slate-500 font-mono">EUR</span>
            <input 
              v-model.number="stake" 
              type="number" 
              min="1" 
              class="w-20 rounded border border-border bg-background px-2 py-1 font-mono text-xs text-right text-slate-100 focus:border-blue-500 focus:outline-none" 
            />
          </div>
        </div>

        <div class="flex items-center justify-between font-mono text-xs">
          <span class="text-slate-400">Total Odds</span>
          <span class="font-bold text-slate-100">{{ totalOdds.toFixed(2) }}</span>
        </div>

        <div class="flex items-center justify-between font-mono text-xs">
          <span class="text-slate-400">Potential Return</span>
          <span class="font-bold text-emerald-400">€{{ potentialPayout.toFixed(2) }}</span>
        </div>

        <button 
          @click="handlePlaceBet" 
          class="mt-2 w-full rounded bg-blue-600 py-2 text-xs font-bold text-white transition-colors hover:bg-blue-500 active:scale-[0.99]"
        >
          Confirm Demo Selection
        </button>
      </div>
    </div>

    <!-- Compliance Gate Modal -->
    <ComplianceGateModal 
      :show="showComplianceGate" 
      @close="showComplianceGate = false" 
      @eligibility-granted="onEligibilityGranted" 
    />
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Ticket, Receipt, X } from 'lucide-vue-next'
import { checkBettingEligibilityApi, getActiveSessionId, placeBetApi, trackSessionEvent, type EventItem, type SelectionItem } from '@/services/api'
import ComplianceGateModal from './ComplianceGateModal.vue'

const props = defineProps<{
  selections: { event: EventItem; selection: SelectionItem }[]
}>()

const emit = defineEmits(['remove-selection', 'clear-slip'])

const stake = ref(10)
const showComplianceGate = ref(false)

const totalOdds = computed(() => {
  if (props.selections.length === 0) return 0
  return props.selections.reduce((acc, s) => acc * s.selection.odds, 1)
})

const potentialPayout = computed(() => {
  return stake.value * totalOdds.value
})

async function handlePlaceBet() {
  const userId = 'usr_demo'
  const sessionId = getActiveSessionId()
  if (sessionId) {
    await trackSessionEvent(sessionId, 'betslip_view', '/betslip', 'review_selection')
    await trackSessionEvent(sessionId, 'place_bet_clicked', '/betslip', 'place_bet')
  }
  const eligibility = await checkBettingEligibilityApi(userId, sessionId || undefined)
  
  if (!eligibility.eligible) {
    showComplianceGate.value = true
    return
  }

  await executeBetPlacement(userId, sessionId)
}

async function onEligibilityGranted() {
  await executeBetPlacement('usr_demo', getActiveSessionId())
}

async function executeBetPlacement(userId: string, sessionId: string | null) {
  try {
    const result = await placeBetApi(userId, props.selections, stake.value, sessionId || undefined)
    alert(`Demo Selection Placed! Bet ID: ${result.betId}. Potential return: €${potentialPayout.value.toFixed(2)}`)
    emit('clear-slip')
  } catch (err: any) {
    alert(`Betting Blocked by Gate: ${err.reason || err.message || 'Ineligible user account.'}`)
    showComplianceGate.value = true
  }
}
</script>
