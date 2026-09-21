<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-md">
    <div class="w-full max-w-xl rounded-xl border border-blue-500/40 bg-[#0d121d] p-5 shadow-2xl">
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-border pb-3">
        <div class="flex items-center gap-2">
          <ShieldCheck class="size-5 text-blue-400" />
          <h3 class="text-sm font-bold text-slate-100">PULSYNC Player Protection & Compliance Gate</h3>
        </div>
        <button @click="$emit('close')" class="rounded p-1 text-slate-400 hover:bg-accent hover:text-white">
          <X class="size-4" />
        </button>
      </div>

      <!-- Demo Environment Banner -->
      <div class="mt-3 flex items-center justify-between rounded-md border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-300">
        <span class="font-bold">DEMO / MOCK ENVIRONMENT</span>
        <span class="text-[11px] text-amber-200/80">EU & Croatia Responsible Gambling Prototype</span>
      </div>

      <!-- Quick Demo Scenario Switcher -->
      <div class="mt-3 flex items-center gap-1.5 rounded-lg border border-border bg-card p-1.5">
        <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 pl-1">Test Persona:</span>
        <button
          @click="selectPersona('valid')"
          class="rounded px-2.5 py-1 text-[11px] font-semibold transition-colors"
          :class="activePersona === 'valid' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-accent'"
        >
          Valid 18+
        </button>
        <button
          @click="selectPersona('underage')"
          class="rounded px-2.5 py-1 text-[11px] font-semibold transition-colors"
          :class="activePersona === 'underage' ? 'bg-red-600 text-white' : 'text-slate-400 hover:bg-accent'"
        >
          Under 18
        </button>
        <button
          @click="selectPersona('excluded')"
          class="rounded px-2.5 py-1 text-[11px] font-semibold transition-colors"
          :class="activePersona === 'excluded' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:bg-accent'"
        >
          Self-Excluded
        </button>
      </div>

      <!-- Wizard Progress Indicators -->
      <div class="mt-4 flex items-center justify-between border-b border-border/60 pb-3">
        <div 
          v-for="(st, idx) in steps" 
          :key="st.key" 
          class="flex items-center gap-1.5 text-xs"
          :class="currentStep === idx ? 'font-bold text-blue-400' : (currentStep > idx ? 'text-emerald-400 font-semibold' : 'text-slate-500')"
        >
          <span class="flex size-5 items-center justify-center rounded-full text-[10px]"
            :class="currentStep === idx ? 'bg-blue-600 text-white' : (currentStep > idx ? 'bg-emerald-500/20 text-emerald-400' : 'bg-accent text-slate-400')"
          >
            {{ idx + 1 }}
          </span>
          <span class="hidden sm:inline">{{ st.title }}</span>
        </div>
      </div>

      <!-- Step 1: Demo Registration -->
      <div v-if="currentStep === 0" class="mt-4 flex flex-col gap-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">Step 1: Demo Registration</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Browsing sports information is open to everyone. Registration is required only when entering the demo betting flow.
        </p>

        <div class="flex flex-col gap-2">
          <label class="text-xs text-slate-400">Display Name</label>
          <input v-model="displayName" type="text" class="rounded border border-border bg-background px-3 py-1.5 text-xs text-slate-100 focus:border-blue-500 focus:outline-none" />

          <label class="text-xs text-slate-400 mt-1">Demo Email Identifier</label>
          <input v-model="email" type="email" class="rounded border border-border bg-background px-3 py-1.5 text-xs text-slate-100 focus:border-blue-500 focus:outline-none" />
        </div>

        <button @click="continueRegistration" class="mt-2 w-full rounded bg-blue-600 py-2 text-xs font-bold text-white hover:bg-blue-500">
          Continue to 18+ Age Verification →
        </button>
      </div>

      <!-- Step 2: 18+ Age Verification -->
      <div v-if="currentStep === 1" class="mt-4 flex flex-col gap-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">Step 2: 18+ Age Verification</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Confirm your age attribute. (Forward-looking eIDAS 2.0 / EUDI 18+ attribute proof pattern).
        </p>

        <div class="flex flex-col gap-2">
          <label class="text-xs text-slate-400">Date of Birth (YYYY-MM-DD)</label>
          <input v-model="birthDate" type="date" class="rounded border border-border bg-background px-3 py-1.5 text-xs text-slate-100 focus:border-blue-500 focus:outline-none" />

          <div class="mt-2 flex items-center gap-2 rounded bg-accent/40 p-2.5 text-xs text-slate-300">
            <input v-model="confirm18" type="checkbox" id="confirm18" class="size-4 accent-blue-600" />
            <label for="confirm18" class="cursor-pointer">I confirm I am 18 years of age or older.</label>
          </div>
        </div>

        <div class="flex gap-2 mt-2">
          <button @click="currentStep = 0" class="w-1/3 rounded border border-border py-2 text-xs font-semibold text-slate-400 hover:bg-accent">
            ← Back
          </button>
          <button @click="submitAge" class="w-2/3 rounded bg-blue-600 py-2 text-xs font-bold text-white hover:bg-blue-500">
            Verify Age Attribute →
          </button>
        </div>
      </div>

      <!-- Step 3: Conceptual KYC -->
      <div v-if="currentStep === 2" class="mt-4 flex flex-col gap-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">Step 3: Conceptual Identity Verification (KYC)</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Select a dummy document type to perform synthetic verification. No real document data is processed or stored.
        </p>

        <div class="flex flex-col gap-2">
          <label class="text-xs text-slate-400">Select Document Type (Synthetic Demo)</label>
          <select v-model="docType" class="rounded border border-border bg-background px-3 py-1.5 text-xs text-slate-100 focus:border-blue-500 focus:outline-none">
            <option value="National ID">National ID Card</option>
            <option value="Passport">Passport</option>
            <option value="Driving Licence">Driving Licence</option>
          </select>

          <div class="rounded border border-blue-500/30 bg-blue-500/10 p-2.5 text-[11px] text-blue-300">
            Demo verification — no real identity data processed.
          </div>
        </div>

        <div class="flex gap-2 mt-2">
          <button @click="currentStep = 1" class="w-1/3 rounded border border-border py-2 text-xs font-semibold text-slate-400 hover:bg-accent">
            ← Back
          </button>
          <button @click="submitKyc" class="w-2/3 rounded bg-blue-600 py-2 text-xs font-bold text-white hover:bg-blue-500">
            Perform Demo Identity Verification →
          </button>
        </div>
      </div>

      <!-- Step 4: Player Protection Exclusion Check -->
      <div v-if="currentStep === 3" class="mt-4 flex flex-col gap-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">Step 4: Excluded-Player Register Check</h4>
        <p class="text-xs text-slate-400 leading-relaxed">
          Performing deterministic check against synthetic responsible gambling register.
        </p>

        <div class="flex flex-col items-center justify-center py-6 border border-border bg-accent/30 rounded-lg">
          <RefreshCw v-if="checkingExclusion" class="size-8 text-blue-400 animate-spin mb-2" />
          <span v-if="checkingExclusion" class="text-xs text-slate-300 font-mono">Querying DEMO_REGISTER...</span>
          
          <template v-else>
            <CheckCircle2 v-if="!exclusionResult?.excluded" class="size-10 text-emerald-400 mb-2" />
            <AlertTriangle v-else class="size-10 text-red-400 mb-2" />
            
            <span class="text-sm font-bold text-slate-100">
              {{ exclusionResult?.excluded ? 'SELF-EXCLUDED RECORD DETECTED' : 'NO SELF-EXCLUSION RECORD FOUND' }}
            </span>
            <span class="text-xs text-slate-400 mt-1 font-mono">
              Source: {{ exclusionResult?.source || 'DEMO_REGISTER' }}
            </span>
          </template>
        </div>

        <button @click="evaluateFinalGate" :disabled="checkingExclusion" class="mt-2 w-full rounded bg-blue-600 py-2 text-xs font-bold text-white hover:bg-blue-500 disabled:opacity-50">
          Evaluate Final Betting Eligibility →
        </button>
      </div>

      <!-- Step 5: Final Decision Gate -->
      <div v-if="currentStep === 4" class="mt-4 flex flex-col gap-3">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">Final Eligibility Decision</h4>

        <!-- ELIGIBLE Screen -->
        <div v-if="eligibilityResult?.eligible" class="flex flex-col items-center justify-center p-6 border border-emerald-500/40 bg-emerald-500/10 rounded-lg text-center">
          <CheckCircle2 class="size-12 text-emerald-400 mb-2" />
          <h3 class="text-base font-black text-emerald-400 uppercase tracking-wider">BETTING ELIGIBILITY GRANTED</h3>
          <p class="text-xs text-slate-200 mt-1">
            Age Verified (18+) ✓ | Identity Verified (KYC) ✓ | Exclusion Check Passed ✓
          </p>
          <span class="mt-3 rounded bg-emerald-500/20 px-3 py-1 font-mono text-xs font-bold text-emerald-300 border border-emerald-500/30">
            STATUS: ELIGIBLE
          </span>

          <button @click="proceedBetting" class="mt-4 w-full rounded bg-emerald-600 py-2.5 text-xs font-bold text-white hover:bg-emerald-500 shadow-lg">
            Proceed to Demo Betting Flow →
          </button>
        </div>

        <!-- BLOCKED ACCESS Screen -->
        <div v-else class="flex flex-col items-center justify-center p-6 border border-red-500/40 bg-red-500/10 rounded-lg text-center">
          <AlertTriangle class="size-12 text-red-400 mb-2" />
          <h3 class="text-base font-black text-red-400 uppercase tracking-wider">ACCESS BLOCKED — INELIGIBLE</h3>
          <p class="text-xs text-slate-200 mt-2 max-w-md font-semibold">
            {{ eligibilityResult?.reason || 'Betting access is unavailable for this account.' }}
          </p>

          <div class="mt-3 flex flex-wrap gap-2 justify-center">
            <span class="rounded px-2.5 py-1 text-[11px] font-bold font-mono" :class="eligibilityResult?.age_verified ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'">
              18+ Age: {{ eligibilityResult?.age_verified ? 'VERIFIED' : 'RESTRICTED' }}
            </span>
            <span class="rounded px-2.5 py-1 text-[11px] font-bold font-mono" :class="!eligibilityResult?.self_excluded ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'">
              Self-Exclusion: {{ eligibilityResult?.self_excluded ? 'EXCLUDED' : 'PASSED' }}
            </span>
          </div>

          <div class="mt-4 p-3 rounded bg-card border border-border text-xs text-slate-400 text-left w-full">
            <span class="font-bold text-slate-200 block mb-1">Responsible Gambling Protection Notice:</span>
            PULSYNC strictly enforces player protection guidelines. Betting access is disabled. You may continue to browse non-gambling sports information and statistics.
          </div>

          <button @click="$emit('close')" class="mt-4 w-full rounded border border-border bg-card py-2 text-xs font-bold text-slate-300 hover:bg-accent">
            Return to Sports Information Browsing
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ShieldCheck, X, RefreshCw, CheckCircle2, AlertTriangle } from 'lucide-vue-next'
import { verifyAgeApi, submitKycDemoApi, checkSelfExclusionApi, checkBettingEligibilityApi, getActiveSessionId, loginApi, type BettingEligibilityResult } from '@/services/api'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'eligibility-granted'])

const steps = [
  { key: 'reg', title: 'Register' },
  { key: 'age', title: '18+ Age' },
  { key: 'kyc', title: 'KYC Demo' },
  { key: 'exclusion', title: 'Exclusion' },
  { key: 'gate', title: 'Decision Gate' },
]

const currentStep = ref(0)
const activePersona = ref('valid')

const displayName = ref('Sports Enthusiast')
const email = ref('fan@pulsync.ai')
const birthDate = ref('2000-05-15')
const confirm18 = ref(true)
const docType = ref('National ID')

const checkingExclusion = ref(false)
const exclusionResult = ref<any>(null)
const eligibilityResult = ref<BettingEligibilityResult | null>(null)

async function continueRegistration() {
  await loginApi(getActiveSessionId() || undefined)
  currentStep.value = 1
}

function selectPersona(type: string) {
  activePersona.value = type
  if (type === 'valid') {
    displayName.value = 'Valid Bettor 18+'
    email.value = 'valid_user@pulsync.ai'
    birthDate.value = '2000-05-15'
    confirm18.value = true
  } else if (type === 'underage') {
    displayName.value = 'Junior Fan (Under 18)'
    email.value = 'junior@pulsync.ai'
    birthDate.value = '2010-08-20'
    confirm18.value = false
  } else if (type === 'excluded') {
    displayName.value = 'Excluded Player Profile'
    email.value = 'excluded_user@pulsync.ai'
    birthDate.value = '1995-03-10'
    confirm18.value = true
  }
  currentStep.value = 0
}

async function submitAge() {
  const userId = activePersona.value === 'excluded' ? 'usr_excluded_demo' : (activePersona.value === 'underage' ? 'usr_underage_demo' : 'usr_demo')
  const calculatedAge = activePersona.value === 'underage' ? 15 : 24
  await verifyAgeApi(userId, calculatedAge, birthDate.value)
  currentStep.value = 2
}

async function submitKyc() {
  const userId = activePersona.value === 'excluded' ? 'usr_excluded_demo' : (activePersona.value === 'underage' ? 'usr_underage_demo' : 'usr_demo')
  await submitKycDemoApi(userId, docType.value)
  currentStep.value = 3
  runExclusionCheck()
}

async function runExclusionCheck() {
  checkingExclusion.value = true
  const userId = activePersona.value === 'excluded' ? 'usr_excluded_demo' : (activePersona.value === 'underage' ? 'usr_underage_demo' : 'usr_demo')
  
  // If demo persona is 'excluded', ensure self_excluded flag is set in backend
  if (activePersona.value === 'excluded') {
    await verifyAgeApi('usr_excluded_demo', 25)
    await submitKycDemoApi('usr_excluded_demo', 'Passport')
  }

  exclusionResult.value = await checkSelfExclusionApi(userId)
  checkingExclusion.value = false
}

async function evaluateFinalGate() {
  currentStep.value = 4
  const userId = activePersona.value === 'excluded' ? 'usr_excluded_demo' : (activePersona.value === 'underage' ? 'usr_underage_demo' : 'usr_demo')
  eligibilityResult.value = await checkBettingEligibilityApi(userId)
}

function proceedBetting() {
  emit('eligibility-granted')
  emit('close')
}
</script>
