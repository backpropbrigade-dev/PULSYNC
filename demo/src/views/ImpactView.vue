<template>
  <div class="max-w-full overflow-x-hidden space-y-6 pb-12">
    <!-- Top Header Banner -->
    <div
      class="rounded-xl border border-blue-500/30 bg-gradient-to-r from-blue-950/40 via-[#0e1424] to-[#0d111a] p-6 shadow-xl backdrop-blur-md"
    >
      <div
        class="flex flex-col justify-between gap-4 md:flex-row md:items-center"
      >
        <div>
          <div class="flex items-center gap-2 mb-2">
            <span
              class="rounded-md bg-blue-500/20 border border-blue-400/30 px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider text-blue-300"
            >
              FEG Innovation Hackathon 2026
            </span>
            <span
              class="rounded-md bg-emerald-500/20 border border-emerald-400/30 px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider text-emerald-300"
            >
              Real FEG Dataset Replay
            </span>
          </div>
          <h1 class="text-2xl font-black tracking-tight text-white md:text-3xl">
            PULSYNC SESSION & ROI INTELLIGENCE
          </h1>
          <p class="mt-1 text-sm text-slate-300">
            Session health, behavioral opportunity, historical replay & scenario
            value
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button
            @click="showMethodology = true"
            class="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition-all shadow-sm"
          >
            <HelpCircle class="size-4 text-blue-400" />
            <span>Methodology & Provenance</span>
          </button>
          <button
            @click="exportImpactCaseJson"
            class="flex items-center gap-1.5 rounded-lg border border-blue-500/40 bg-blue-600/20 px-3 py-2 text-xs font-semibold text-blue-300 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
          >
            <Download class="size-4" />
            <span>Export Case JSON</span>
          </button>
        </div>
      </div>

      <!-- Core Product Principle Notice -->
      <div
        class="mt-4 flex items-center justify-between rounded-lg border border-border/80 bg-black/40 px-4 py-2.5 text-xs text-slate-300"
      >
        <div class="flex items-center gap-2">
          <ShieldCheck class="size-4 text-emerald-400 shrink-0" />
          <span
            ><strong class="text-white font-semibold"
              >Product Principle:</strong
            >
            We do not optimize for another bet. We optimize for the user's next
            valuable action.</span
          >
        </div>
        <div
          class="hidden sm:flex items-center gap-1.5 font-mono text-[11px] text-amber-300 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20"
        >
          <span>OBSERVED CORRELATION -- NOT CAUSAL</span>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div
      class="flex overflow-x-auto border-b border-border/80 pb-px gap-2 text-sm font-medium"
    >
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="setActiveTab(tab.id)"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 rounded-t-lg border-b-2 font-semibold transition-all whitespace-nowrap text-xs md:text-sm',
          activeTab === tab.id
            ? 'border-blue-500 bg-blue-500/10 text-blue-400'
            : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40',
        ]"
      >
        <component :is="tab.icon" class="size-4" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24">
      <div
        class="size-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"
      ></div>
      <p class="mt-4 text-xs font-mono text-slate-400">
        Computing statistical replay and ROI metrics from FEG dataset...
      </p>
    </div>

    <div
      v-else-if="loadError"
      class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm text-amber-200"
    >
      <div class="flex items-center gap-2 font-semibold">
        <AlertTriangle class="size-4 text-amber-400" />
        Impact data is not currently available
      </div>
      <p class="mt-2 text-xs text-amber-100/80">{{ loadError }}</p>
    </div>

    <!-- Content Sections -->
    <div v-else-if="summary && health" class="space-y-6">
      <!-- ============================================== -->
      <!-- TAB 1: OVERVIEW                                -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- Challenge-1 scorecard: supported values are sourced from the live impact payload. -->
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <div
            v-for="card in challengeKpis"
            :key="card.label"
            class="rounded-xl border border-border bg-card/70 p-4 shadow-sm backdrop-blur"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-xs font-bold text-slate-200">{{ card.label }}</p>
                <p class="mt-1 text-[11px] leading-relaxed text-slate-400">
                  {{ card.definition }}
                </p>
              </div>
              <span
                :class="kpiTypeClass(card.type)"
                class="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-mono font-bold uppercase"
              >
                {{ card.type }}
              </span>
            </div>
            <div class="mt-4 text-2xl font-black font-mono text-white">
              {{ card.value }}
            </div>
            <p class="mt-2 text-[10px] text-slate-500">
              {{ card.period }} · {{ card.source }}
            </p>
          </div>
        </div>

        <!-- Dataset facts -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          <div
            v-for="(card, key) in summary?.kpi_cards"
            :key="key"
            class="rounded-xl border border-border bg-card/70 p-4 shadow-sm backdrop-blur transition hover:border-blue-500/40"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-slate-400">{{
                card.label
              }}</span>
              <span
                :class="[
                  'text-[10px] font-mono px-1.5 py-0.5 rounded font-bold uppercase',
                  card.type === 'OBSERVED'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : card.type === 'CALCULATED'
                      ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                      : 'bg-purple-500/20 text-purple-300 border border-purple-500/30',
                ]"
              >
                {{ card.type }}
              </span>
            </div>
            <div class="mt-2 flex items-baseline gap-2">
              <div class="text-2xl font-black text-white font-mono">
                {{ formatKpiValue(key, card.value) }}
              </div>
              <span
                v-if="card.share_pct"
                class="text-xs text-blue-400 font-semibold font-mono"
              >
                ({{ card.share_pct }}%)
              </span>
            </div>
            <div
              v-if="card.badge"
              class="mt-2 flex items-center gap-1 text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20"
            >
              <span>{{ card.badge }}</span>
            </div>
            <p v-else-if="card.period" class="mt-1 text-[11px] text-slate-400">
              {{ card.period }}
            </p>
          </div>
        </div>

        <!-- Executive Summary Cards -->
        <div class="grid gap-6 md:grid-cols-2">
          <!-- The Problem & Solution -->
          <div class="rounded-xl border border-border bg-card p-5 space-y-3">
            <div class="flex items-center gap-2 border-b border-border/60 pb-3">
              <AlertTriangle class="size-4 text-amber-400" />
              <h3 class="text-sm font-bold text-white">The Business Problem</h3>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">
              Traditional sports entertainment platforms treat waning session
              momentum by prompting users to place another bet or wager higher.
              This causes cognitive friction, platform fatigue, and early
              bounce.
            </p>
            <div
              class="rounded-lg border border-blue-500/20 bg-blue-500/10 p-3 text-xs text-blue-300 space-y-1"
            >
              <div class="font-bold flex items-center gap-1 text-blue-200">
                <Sparkles class="size-3.5 text-blue-400" />
                <span>PULSYNC Solution</span>
              </div>
              <p class="text-slate-300 leading-relaxed text-[11px]">
                When transaction intent drops but information exploration
                remains high, PULSYNC shifts into
                <strong class="text-white">VALUE_SEEKING</strong> mode,
                delivering Head-to-Head analytics, team form, and tactical
                insights.
              </p>
            </div>
          </div>

          <!-- Replay Proof Highlight -->
          <div
            class="rounded-xl border border-emerald-500/30 bg-card p-5 space-y-3"
          >
            <div
              class="flex items-center justify-between border-b border-border/60 pb-3"
            >
              <div class="flex items-center gap-2">
                <TrendingUp class="size-4 text-emerald-400" />
                <h3 class="text-sm font-bold text-white">
                  Observed Replay Finding
                </h3>
              </div>
              <span
                class="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded"
              >
                {{ replay?.p_value || "Statistical result unavailable" }}
                <span v-if="replay?.statistically_significant"
                  >(Significant)</span
                >
              </span>
            </div>
            <div class="grid grid-cols-2 gap-3 pt-1">
              <div class="rounded-lg bg-accent/60 p-3 border border-border/60">
                <div class="text-[11px] text-slate-400">
                  VALUE_SEEKING 7d Return
                </div>
                <div class="text-2xl font-bold font-mono text-emerald-400 mt-1">
                  {{ replay?.value_seeking.return_7d_rate }}%
                </div>
                <div class="text-[10px] text-slate-400 mt-0.5">
                  Sample:
                  {{ replay?.value_seeking.sessions.toLocaleString() }} sessions
                </div>
              </div>
              <div class="rounded-lg bg-accent/60 p-3 border border-border/60">
                <div class="text-[11px] text-slate-400">
                  Abandoned-Like 7d Return
                </div>
                <div class="text-2xl font-bold font-mono text-slate-300 mt-1">
                  {{ replay?.comparison_cohort.return_7d_rate }}%
                </div>
                <div class="text-[10px] text-slate-400 mt-0.5">
                  Sample:
                  {{ replay?.comparison_cohort.sessions.toLocaleString() }}
                  sessions
                </div>
              </div>
            </div>
            <div
              class="flex items-center justify-between text-xs pt-1 text-slate-300"
            >
              <span
                >Observed Difference:
                <strong class="text-emerald-400 font-mono text-sm"
                  >+{{ replay?.observed_difference_pp }} pp</strong
                ></span
              >
              <span class="text-slate-400 font-mono text-[11px]"
                >95% CI: [{{ replay?.confidence_interval_95[0] }}%,
                {{ replay?.confidence_interval_95[1] }}%]</span
              >
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 2: SESSION HEALTH                          -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'health'" class="space-y-6">
        <!-- Health Overview Stats -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-lg border border-border bg-card p-3">
            <span class="text-xs text-slate-400">Average Duration</span>
            <div class="text-xl font-bold font-mono text-white mt-1">
              {{ health?.average_duration_sec }}s
            </div>
            <span class="text-[10px] text-slate-400">7.1 min / session</span>
          </div>
          <div class="rounded-lg border border-border bg-card p-3">
            <span class="text-xs text-slate-400">Actions per Session</span>
            <div class="text-xl font-bold font-mono text-blue-400 mt-1">
              {{ health?.actions_per_session }}
            </div>
            <span class="text-[10px] text-slate-400"
              >Exploration intensity</span
            >
          </div>
          <div class="rounded-lg border border-border bg-card p-3">
            <span class="text-xs text-slate-400">Session Quality Score</span>
            <div class="text-xl font-bold font-mono text-emerald-400 mt-1">
              {{ health?.session_quality_avg }}/100
            </div>
            <span class="text-[10px] text-slate-400"
              >Composite health index</span
            >
          </div>
          <div class="rounded-lg border border-border bg-card p-3">
            <span class="text-xs text-slate-400">Friction Score</span>
            <div class="text-xl font-bold font-mono text-amber-400 mt-1">
              {{ health?.friction_score_avg }}/100
            </div>
            <span class="text-[10px] text-slate-400"
              >Loop & rapid drop rate</span
            >
          </div>
        </div>

        <!-- Session Funnel -->
        <div class="rounded-xl border border-border bg-card p-5 space-y-4">
          <div
            class="flex items-center justify-between border-b border-border pb-3"
          >
            <div>
              <h3 class="text-sm font-bold text-white">
                Reconstructed Session Funnel
              </h3>
              <p class="text-xs text-slate-400">
                Progression of user behavior from exploration through
                information engagement to subsequent return.
              </p>
            </div>
            <span
              class="text-xs font-mono text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20"
            >
              N = {{ health?.total_sessions.toLocaleString() }} Sessions
            </span>
          </div>

          <div class="space-y-3">
            <div
              v-for="step in health?.funnel"
              :key="step.stage"
              class="space-y-1"
            >
              <div class="flex justify-between text-xs font-semibold">
                <span class="text-slate-200">{{ step.stage }}</span>
                <div class="flex items-center gap-3">
                  <span class="text-slate-400 font-mono"
                    >{{ step.count.toLocaleString() }} sessions</span
                  >
                  <span class="text-blue-400 font-mono w-12 text-right"
                    >{{ step.rate_pct }}%</span
                  >
                </div>
              </div>
              <div
                class="h-2.5 w-full rounded-full bg-slate-800 overflow-hidden"
              >
                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-500 transition-all duration-500"
                  :style="{ width: step.rate_pct + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Daily Trends Table -->
        <div class="rounded-xl border border-border bg-card p-5 space-y-4">
          <h3 class="text-sm font-bold text-white">
            16-Day Historical Time Series Trend
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
              <thead
                class="border-b border-border text-[11px] font-bold text-slate-400 uppercase bg-accent/40"
              >
                <tr>
                  <th class="py-2 px-3">Date</th>
                  <th class="py-2 px-3">Total Sessions</th>
                  <th class="py-2 px-3">Active Players</th>
                  <th class="py-2 px-3">VALUE_SEEKING</th>
                  <th class="py-2 px-3">Early Abandonment</th>
                  <th class="py-2 px-3 text-right">7d Return Rate</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border/60 font-mono">
                <tr
                  v-for="day in health?.daily_trends"
                  :key="day.date"
                  class="hover:bg-accent/30"
                >
                  <td class="py-2 px-3 font-semibold text-slate-200">
                    {{ day.date }}
                  </td>
                  <td class="py-2 px-3">{{ day.sessions.toLocaleString() }}</td>
                  <td class="py-2 px-3 text-slate-400">
                    {{ day.active_players.toLocaleString() }}
                  </td>
                  <td class="py-2 px-3 text-blue-400 font-semibold">
                    {{ day.value_seeking_sessions }}
                  </td>
                  <td class="py-2 px-3 text-amber-400">
                    {{ day.abandonment_rate }}%
                  </td>
                  <td class="py-2 px-3 text-right font-bold text-emerald-400">
                    {{ day.return_7d_rate }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 3: USER SEGMENTS & 3x3 MATRIX              -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'segments'" class="space-y-6">
        <!-- 3x3 Intent x Information Matrix Visualizer -->
        <div class="rounded-xl border border-border bg-card p-5 space-y-4">
          <div
            class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3"
          >
            <div>
              <h3 class="text-sm font-bold text-white">
                Transaction Intent × Information Interest Matrix
              </h3>
              <p class="text-xs text-slate-400">
                The core PULSYNC opportunity lies in the Low Transaction Intent
                / High Information Interest quadrant.
              </p>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span
                class="size-3 rounded bg-amber-500/20 border border-amber-400"
              ></span>
              <span class="text-amber-300 font-semibold"
                >PULSYNC Opportunity</span
              >
            </div>
          </div>

          <!-- 3x3 Grid Display -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div
              v-for="cell in matrix"
              :key="cell.transaction_intent + cell.information_interest"
              :class="[
                'rounded-xl border p-4 transition-all flex flex-col justify-between space-y-2',
                cell.is_pulsync_opportunity
                  ? 'border-amber-500/80 bg-gradient-to-br from-amber-950/40 via-[#1c1811] to-[#0f1118] shadow-lg shadow-amber-500/10 ring-1 ring-amber-400/40'
                  : 'border-border bg-card/60 hover:border-slate-600',
              ]"
            >
              <div class="flex items-center justify-between">
                <div class="text-xs font-bold text-slate-200">
                  Tx:
                  <span
                    :class="
                      cell.transaction_intent === 'HIGH'
                        ? 'text-blue-400'
                        : cell.transaction_intent === 'LOW'
                          ? 'text-amber-400'
                          : 'text-slate-300'
                    "
                    >{{ cell.transaction_intent }}</span
                  >
                  | Info:
                  <span
                    :class="
                      cell.information_interest === 'HIGH'
                        ? 'text-emerald-400'
                        : 'text-slate-400'
                    "
                    >{{ cell.information_interest }}</span
                  >
                </div>
                <span
                  v-if="cell.is_pulsync_opportunity"
                  class="text-[10px] font-bold uppercase tracking-wider bg-amber-500 text-black px-1.5 py-0.5 rounded shadow"
                >
                  Opportunity
                </span>
              </div>

              <div class="flex items-baseline justify-between pt-1">
                <div class="text-xl font-bold font-mono text-white">
                  {{ cell.sessions.toLocaleString() }}
                </div>
                <span class="text-xs font-mono text-slate-400"
                  >{{ cell.session_share }}% sessions</span
                >
              </div>

              <div
                class="border-t border-border/50 pt-2 flex items-center justify-between text-[11px]"
              >
                <span class="text-slate-400">7-Day Return:</span>
                <span
                  :class="
                    cell.is_pulsync_opportunity
                      ? 'font-bold text-amber-400'
                      : 'text-slate-200'
                  "
                  >{{ cell.return_7d_rate }}%</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 5 Standard Behavioral Segments Table -->
        <div class="rounded-xl border border-border bg-card p-5 space-y-4">
          <h3 class="text-sm font-bold text-white">
            Segment Opportunity Sizing (Full Historical Population)
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
              <thead
                class="border-b border-border text-[11px] font-bold text-slate-400 uppercase bg-accent/40"
              >
                <tr>
                  <th class="py-2.5 px-3">Segment</th>
                  <th class="py-2.5 px-3">Sessions</th>
                  <th class="py-2.5 px-3">Players</th>
                  <th class="py-2.5 px-3">Share %</th>
                  <th class="py-2.5 px-3">Stake Exposure</th>
                  <th class="py-2.5 px-3">7d Return Rate</th>
                  <th class="py-2.5 px-3 text-right">Subsequent Staking</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border/60 font-mono">
                <tr
                  v-for="(seg, key) in segments"
                  :key="key"
                  :class="
                    key === 'VALUE_SEEKING'
                      ? 'bg-amber-500/10 font-bold'
                      : 'hover:bg-accent/30'
                  "
                >
                  <td class="py-3 px-3">
                    <div class="flex items-center gap-1.5">
                      <span
                        v-if="key === 'VALUE_SEEKING'"
                        class="size-2 rounded-full bg-amber-400 animate-ping"
                      ></span>
                      <span
                        :class="
                          key === 'VALUE_SEEKING'
                            ? 'text-amber-300'
                            : 'text-white'
                        "
                        >{{ seg.name }}</span
                      >
                    </div>
                  </td>
                  <td class="py-3 px-3">{{ seg.sessions.toLocaleString() }}</td>
                  <td class="py-3 px-3 text-slate-400">
                    {{ seg.players.toLocaleString() }}
                  </td>
                  <td class="py-3 px-3">{{ seg.session_share }}%</td>
                  <td class="py-3 px-3">
                    €{{ seg.historical_stake_exposure.toLocaleString() }}
                  </td>
                  <td
                    class="py-3 px-3"
                    :class="key === 'VALUE_SEEKING' ? 'text-emerald-400' : ''"
                  >
                    {{ seg.return_7d_rate }}%
                  </td>
                  <td class="py-3 px-3 text-right">
                    {{ seg.subsequent_stake_rate }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 4: HISTORICAL REPLAY                       -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'replay'" class="space-y-6">
        <!-- Replay Methodology Badge Banner -->
        <div
          class="rounded-xl border border-blue-500/30 bg-blue-500/10 p-4 text-xs text-blue-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-3"
        >
          <div class="flex items-center gap-2">
            <Info class="size-4 text-blue-400 shrink-0" />
            <span
              ><strong>Reproducible Historical Replay:</strong> Evaluates cohort
              retention on 30-minute reconstructed sessions. Proxy for
              information interest is labeled
              <em>Historical Information-Interest Proxy</em>.</span
            >
          </div>
          <span
            class="text-[11px] font-mono text-amber-300 bg-amber-500/20 px-2.5 py-1 rounded border border-amber-500/30 whitespace-nowrap"
          >
            OBSERVED CORRELATION -- NOT CAUSAL
          </span>
        </div>

        <!-- Cohort Comparison Cards -->
        <div class="grid gap-6 md:grid-cols-2">
          <!-- VALUE_SEEKING Cohort -->
          <div
            class="rounded-xl border border-emerald-500/40 bg-card p-5 space-y-4"
          >
            <div
              class="flex items-center justify-between border-b border-border pb-3"
            >
              <div class="flex items-center gap-2">
                <CheckCircle2 class="size-4 text-emerald-400" />
                <h3 class="text-sm font-bold text-white">
                  VALUE_SEEKING Cohort
                </h3>
              </div>
              <span
                class="text-xs font-mono text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded font-bold"
              >
                N = {{ replay?.value_seeking.sessions.toLocaleString() }}
              </span>
            </div>

            <div class="grid grid-cols-3 gap-2 font-mono text-center">
              <div class="rounded-lg bg-accent/60 p-2.5">
                <span class="text-[10px] text-slate-400 block"
                  >1-Day Return</span
                >
                <span class="text-base font-bold text-emerald-400"
                  >{{ replay?.value_seeking.return_1d_rate }}%</span
                >
              </div>
              <div class="rounded-lg bg-accent/60 p-2.5">
                <span class="text-[10px] text-slate-400 block"
                  >3-Day Return</span
                >
                <span class="text-base font-bold text-emerald-400"
                  >{{ replay?.value_seeking.return_3d_rate }}%</span
                >
              </div>
              <div class="rounded-lg bg-accent/60 p-2.5">
                <span class="text-[10px] text-slate-400 block"
                  >7-Day Return</span
                >
                <span class="text-base font-bold text-emerald-400"
                  >{{ replay?.value_seeking.return_7d_rate }}%</span
                >
              </div>
            </div>

            <div class="space-y-1.5 text-xs text-slate-300 pt-1">
              <div class="flex justify-between">
                <span class="text-slate-400">Subsequent Session Rate:</span>
                <span class="font-mono text-white"
                  >{{ replay?.value_seeking.subsequent_session_rate }}%</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Subsequent Staking Rate:</span>
                <span class="font-mono text-white"
                  >{{ replay?.value_seeking.subsequent_stake_rate }}%</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Median Time to Return:</span>
                <span class="font-mono text-white"
                  >{{ replay?.value_seeking.avg_time_to_return_days }} day</span
                >
              </div>
            </div>
          </div>

          <!-- Comparison Cohort (RESPECT_EXIT) -->
          <div class="rounded-xl border border-border bg-card p-5 space-y-4">
            <div
              class="flex items-center justify-between border-b border-border pb-3"
            >
              <div class="flex items-center gap-2">
                <LogOut class="size-4 text-slate-400" />
                <h3 class="text-sm font-bold text-white">
                  {{ replay?.comparison_cohort.name }}
                </h3>
              </div>
              <span
                class="text-xs font-mono text-slate-400 bg-accent px-2 py-0.5 rounded font-bold"
              >
                N = {{ replay?.comparison_cohort.sessions.toLocaleString() }}
              </span>
            </div>

            <div class="grid grid-cols-3 gap-2 font-mono text-center">
              <div class="rounded-lg bg-accent/60 p-2.5">
                <span class="text-[10px] text-slate-400 block"
                  >1-Day Return</span
                >
                <span class="text-base font-bold text-slate-300"
                  >{{ replay?.comparison_cohort.return_1d_rate }}%</span
                >
              </div>
              <div class="rounded-lg bg-accent/60 p-2.5">
                <span class="text-[10px] text-slate-400 block"
                  >3-Day Return</span
                >
                <span class="text-base font-bold text-slate-300"
                  >{{ replay?.comparison_cohort.return_3d_rate }}%</span
                >
              </div>
              <div class="rounded-lg bg-accent/60 p-2.5">
                <span class="text-[10px] text-slate-400 block"
                  >7-Day Return</span
                >
                <span class="text-base font-bold text-slate-300"
                  >{{ replay?.comparison_cohort.return_7d_rate }}%</span
                >
              </div>
            </div>

            <div class="space-y-1.5 text-xs text-slate-300 pt-1">
              <div class="flex justify-between">
                <span class="text-slate-400">Subsequent Session Rate:</span>
                <span class="font-mono text-white"
                  >{{
                    replay?.comparison_cohort.subsequent_session_rate
                  }}%</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Subsequent Staking Rate:</span>
                <span class="font-mono text-white"
                  >{{ replay?.comparison_cohort.subsequent_stake_rate }}%</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Median Time to Return:</span>
                <span class="font-mono text-white"
                  >{{
                    replay?.comparison_cohort.avg_time_to_return_days
                  }}
                  day</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Statistical Inference Panel -->
        <div class="rounded-xl border border-border bg-card p-5 space-y-4">
          <h3 class="text-sm font-bold text-white">
            Statistical Discipline & Inference
          </h3>
          <div
            class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono"
          >
            <div class="rounded-lg bg-accent/40 p-3 border border-border/60">
              <span class="text-[10px] text-slate-400 block uppercase"
                >Observed Gap</span
              >
              <span class="text-xl font-bold text-emerald-400"
                >+{{ replay?.observed_difference_pp }} pp</span
              >
            </div>
            <div class="rounded-lg bg-accent/40 p-3 border border-border/60">
              <span class="text-[10px] text-slate-400 block uppercase"
                >95% Confidence Interval</span
              >
              <span class="text-base font-bold text-slate-200"
                >[{{ replay?.confidence_interval_95[0] }}%,
                {{ replay?.confidence_interval_95[1] }}%]</span
              >
            </div>
            <div class="rounded-lg bg-accent/40 p-3 border border-border/60">
              <span class="text-[10px] text-slate-400 block uppercase"
                >Z-Statistic</span
              >
              <span class="text-xl font-bold text-blue-400">{{
                replay?.z_statistic
              }}</span>
            </div>
            <div class="rounded-lg bg-accent/40 p-3 border border-border/60">
              <span class="text-[10px] text-slate-400 block uppercase"
                >p-value</span
              >
              <span class="text-xl font-bold text-purple-400">{{
                replay?.p_value
              }}</span>
            </div>
          </div>
          <p class="text-[11px] text-slate-400 leading-relaxed">
            Two-proportion Z-test over the full eligible historical window (16
            days). The +{{ replay?.observed_difference_pp }} pp gap in 7-day
            retention between users demonstrating information exploration versus
            immediate abandonment has an observed difference (Z =
            {{ replay?.z_statistic }}, p
            {{ replay?.p_value || "unavailable" }}).
          </p>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 5: BUSINESS VALUE WATERFALL                -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'waterfall'" class="space-y-6">
        <div class="rounded-xl border border-border bg-card p-5 space-y-4">
          <div
            class="flex items-center justify-between border-b border-border pb-3"
          >
            <div>
              <h3 class="text-sm font-bold text-white">
                Business Value Waterfall Model
              </h3>
              <p class="text-xs text-slate-400">
                Step-by-step commercial translation from raw sessions to
                scenario ROI.
              </p>
            </div>
            <span
              class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20"
            >
              Base Scenario (50% Realization)
            </span>
          </div>

          <div class="space-y-2">
            <div
              v-for="item in roiResult?.waterfall"
              :key="item.step"
              class="flex items-center justify-between rounded-lg border border-border/60 bg-accent/30 px-4 py-2.5 text-xs transition hover:bg-accent/60"
            >
              <span class="font-medium text-slate-200">{{ item.step }}</span>
              <div class="flex items-center gap-2 font-mono font-bold">
                <span
                  :class="
                    item.step.includes('Net')
                      ? 'text-emerald-400 text-sm'
                      : 'text-slate-100'
                  "
                >
                  {{
                    typeof item.amount === "number"
                      ? item.amount.toLocaleString()
                      : item.amount
                  }}
                </span>
                <span class="text-[10px] text-slate-400 font-normal">{{
                  item.unit
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 6: ROI SIMULATOR                           -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'roi'" class="space-y-6">
        <div class="grid gap-6 lg:grid-cols-12">
          <!-- Left: Inputs (5 cols) -->
          <div
            class="lg:col-span-5 rounded-xl border border-border bg-card p-5 space-y-5"
          >
            <div
              class="flex items-center justify-between border-b border-border pb-3"
            >
              <h3 class="text-sm font-bold text-white">
                Scenario Configuration
              </h3>
              <span
                class="text-[10px] font-mono text-amber-400 bg-amber-500/20 px-2 py-0.5 rounded"
                >Editable Demo Assumptions</span
              >
            </div>

            <!-- Scenario Presets -->
            <div class="flex gap-2">
              <button
                v-for="sc in ['conservative', 'base', 'optimistic']"
                :key="sc"
                @click="applyScenarioPreset(sc)"
                :class="[
                  'flex-1 py-1.5 rounded-lg text-xs font-bold uppercase transition-all',
                  simInputs.scenario === sc
                    ? 'bg-blue-600 text-white shadow'
                    : 'bg-accent/60 text-slate-400 hover:text-white',
                ]"
              >
                {{ sc }}
              </button>
            </div>

            <!-- Sliders & Inputs -->
            <div class="space-y-4 text-xs">
              <div class="space-y-1.5">
                <div class="flex justify-between">
                  <span class="text-slate-300 font-semibold"
                    >Scenario Realization of Observed Gap:</span
                  >
                  <span class="font-mono font-bold text-blue-400"
                    >{{ simInputs.scenario_realization_pct }}%</span
                  >
                </div>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  v-model.number="simInputs.scenario_realization_pct"
                  @input="runSimulation"
                  class="w-full accent-blue-500"
                />
              </div>

              <div class="space-y-1.5">
                <div class="flex justify-between">
                  <span class="text-slate-300 font-semibold"
                    >Monthly Sessions Baseline:</span
                  >
                  <span class="font-mono font-bold text-white">{{
                    simInputs.monthly_sessions.toLocaleString()
                  }}</span>
                </div>
                <input
                  type="range"
                  min="20000"
                  max="500000"
                  step="10000"
                  v-model.number="simInputs.monthly_sessions"
                  @input="runSimulation"
                  class="w-full accent-blue-500"
                />
              </div>

              <div class="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <label class="text-[11px] text-slate-400 block mb-1"
                    >Inference Cost/Call (€)</label
                  >
                  <input
                    type="number"
                    step="0.001"
                    v-model.number="simInputs.inference_cost_per_call"
                    @input="runSimulation"
                    class="w-full rounded bg-accent/80 border border-border px-2.5 py-1.5 font-mono text-white"
                  />
                </div>
                <div>
                  <label class="text-[11px] text-slate-400 block mb-1"
                    >API Cost/Call (€)</label
                  >
                  <input
                    type="number"
                    step="0.001"
                    v-model.number="simInputs.api_cost_per_call"
                    @input="runSimulation"
                    class="w-full rounded bg-accent/80 border border-border px-2.5 py-1.5 font-mono text-white"
                  />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-[11px] text-slate-400 block mb-1"
                    >Hosting Monthly (€)</label
                  >
                  <input
                    type="number"
                    step="50"
                    v-model.number="simInputs.hosting_cost_monthly"
                    @input="runSimulation"
                    class="w-full rounded bg-accent/80 border border-border px-2.5 py-1.5 font-mono text-white"
                  />
                </div>
                <div>
                  <label class="text-[11px] text-slate-400 block mb-1"
                    >Engineering Cost (€)</label
                  >
                  <input
                    type="number"
                    step="5000"
                    v-model.number="simInputs.engineering_cost"
                    @input="runSimulation"
                    class="w-full rounded bg-accent/80 border border-border px-2.5 py-1.5 font-mono text-white"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Outputs & Sensitivity (7 cols) -->
          <div class="lg:col-span-7 space-y-5">
            <!-- Output Cards -->
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div class="rounded-xl border border-border bg-card p-4">
                <span class="text-[11px] text-slate-400"
                  >Annual Scenario Value</span
                >
                <div class="text-xl font-bold font-mono text-blue-400 mt-1">
                  €{{
                    roiResult?.outputs.annual_scenario_value_eur.toLocaleString()
                  }}
                </div>
                <span class="text-[10px] text-slate-400"
                  >Incremental stake opp.</span
                >
              </div>
              <div class="rounded-xl border border-border bg-card p-4">
                <span class="text-[11px] text-slate-400"
                  >Annual Operating Cost</span
                >
                <div class="text-xl font-bold font-mono text-slate-200 mt-1">
                  €{{
                    roiResult?.outputs.annual_operating_cost_eur.toLocaleString()
                  }}
                </div>
                <span class="text-[10px] text-slate-400"
                  >Inference, API & infra</span
                >
              </div>
              <div class="rounded-xl border border-emerald-500/40 bg-card p-4">
                <span class="text-[11px] text-slate-400">Annual Net Value</span>
                <div class="text-xl font-bold font-mono text-emerald-400 mt-1">
                  €{{
                    roiResult?.outputs.annual_net_value_eur.toLocaleString()
                  }}
                </div>
                <span class="text-[10px] text-emerald-400 font-semibold"
                  >Net Business Value</span
                >
              </div>
              <div class="rounded-xl border border-purple-500/40 bg-card p-4">
                <span class="text-[11px] text-slate-400">Scenario ROI</span>
                <div class="text-2xl font-black font-mono text-purple-400 mt-1">
                  {{ roiResult?.outputs.roi_percent }}%
                </div>
                <span class="text-[10px] text-purple-300 font-semibold"
                  >Modeled ROI Ratio</span
                >
              </div>
              <div
                class="rounded-xl border border-border bg-card p-4 col-span-2"
              >
                <span class="text-[11px] text-slate-400">Payback Period</span>
                <div class="text-xl font-bold font-mono text-white mt-1">
                  {{ roiResult?.outputs.payback_status }}
                </div>
                <span class="text-[10px] text-slate-400"
                  >Against €{{
                    simInputs.engineering_cost.toLocaleString()
                  }}
                  implementation</span
                >
              </div>
            </div>

            <!-- Sensitivity Analysis Table -->
            <div class="rounded-xl border border-border bg-card p-4 space-y-3">
              <div class="flex items-center justify-between">
                <h4
                  class="text-xs font-bold text-white uppercase tracking-wider"
                >
                  Realization Sensitivity Table
                </h4>
                <span class="text-[10px] text-slate-400 font-mono"
                  >Impact of realization assumptions</span
                >
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs text-slate-300">
                  <thead
                    class="border-b border-border text-[10px] font-bold text-slate-400 uppercase bg-accent/30"
                  >
                    <tr>
                      <th class="py-1.5 px-2">Realization %</th>
                      <th class="py-1.5 px-2">Annual Value</th>
                      <th class="py-1.5 px-2">Annual Net Value</th>
                      <th class="py-1.5 px-2 text-right">ROI %</th>
                    </tr>
                  </thead>
                  <tbody
                    class="divide-y divide-border/60 font-mono text-[11px]"
                  >
                    <tr
                      v-for="item in roiResult?.sensitivity"
                      :key="item.realization_pct"
                      :class="
                        item.realization_pct ===
                        simInputs.scenario_realization_pct
                          ? 'bg-blue-500/10 font-bold'
                          : ''
                      "
                    >
                      <td class="py-2 px-2">{{ item.realization_pct }}%</td>
                      <td class="py-2 px-2">
                        €{{ item.annual_value_eur.toLocaleString() }}
                      </td>
                      <td
                        class="py-2 px-2"
                        :class="
                          item.is_positive ? 'text-emerald-400' : 'text-red-400'
                        "
                      >
                        €{{ item.annual_net_value_eur.toLocaleString() }}
                      </td>
                      <td
                        class="py-2 px-2 text-right font-bold"
                        :class="
                          item.is_positive ? 'text-purple-400' : 'text-red-400'
                        "
                      >
                        {{ item.roi_percent }}%
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 7: METRICS TO FOLLOW & GUARDRAILS          -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'metrics'" class="space-y-6">
        <!-- 4-Level Framework -->
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="lvl in frameworkLevels"
            :key="lvl.level"
            class="rounded-xl border border-border bg-card p-4 space-y-3"
          >
            <div
              class="flex items-center justify-between border-b border-border pb-2"
            >
              <div class="text-xs font-bold text-blue-400 uppercase">
                Level {{ lvl.level }}
              </div>
              <span class="text-[10px] text-slate-400 font-mono">{{
                lvl.name
              }}</span>
            </div>

            <div class="space-y-2">
              <div
                v-for="m in lvl.metrics"
                :key="m.name"
                class="rounded bg-accent/40 p-2 text-xs space-y-1"
              >
                <div class="text-[11px] font-medium text-slate-200">
                  {{ m.name }}
                </div>
                <div
                  class="flex justify-between items-center font-mono text-[10px]"
                >
                  <span
                    :class="
                      m.current === 'Not currently measurable'
                        ? 'text-amber-300'
                        : 'text-emerald-400'
                    "
                    class="font-bold"
                    >{{ m.current }}</span
                  >
                  <span class="text-slate-400">Target: {{ m.target }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Management Signals & Responsible Guardrails -->
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Positive & Monitored Signals -->
          <div class="rounded-xl border border-border bg-card p-5 space-y-4">
            <h3 class="text-sm font-bold text-white">
              Management Growth & Friction Signals
            </h3>
            <div class="space-y-3 text-xs">
              <div>
                <span
                  class="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block mb-1"
                  >Positive Growth Signals</span
                >
                <ul class="space-y-1 text-slate-300">
                  <li
                    v-for="s in metricsChain?.signals.positive"
                    :key="s"
                    class="flex items-center gap-1.5"
                  >
                    <Check class="size-3 text-emerald-400 shrink-0" />
                    <span>{{ s }}</span>
                  </li>
                </ul>
              </div>
              <div class="border-t border-border pt-2">
                <span
                  class="text-[11px] font-bold text-amber-400 uppercase tracking-wider block mb-1"
                  >Monitored Friction Signals</span
                >
                <ul class="space-y-1 text-slate-300">
                  <li
                    v-for="s in metricsChain?.signals.negative_monitored"
                    :key="s"
                    class="flex items-center gap-1.5"
                  >
                    <AlertTriangle class="size-3 text-amber-400 shrink-0" />
                    <span>{{ s }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Responsible Business Guardrails -->
          <div
            class="rounded-xl border border-emerald-500/30 bg-card p-5 space-y-4"
          >
            <div
              class="flex items-center justify-between border-b border-border pb-3"
            >
              <div class="flex items-center gap-2">
                <ShieldCheck class="size-4 text-emerald-400" />
                <h3 class="text-sm font-bold text-white">
                  Responsible Business Guardrails
                </h3>
              </div>
              <span
                class="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded"
              >
                Instrumentation status: not currently measured
              </span>
            </div>

            <div class="space-y-2">
              <div
                v-for="g in metricsChain?.signals.compliance_guardrails"
                :key="g.rule"
                class="flex items-center justify-between rounded bg-accent/40 p-2.5 text-xs"
              >
                <span class="text-slate-300">{{ g.rule }}</span>
                <div
                  class="flex items-center gap-2 font-mono font-bold text-[11px]"
                >
                  <span class="text-amber-300">Not currently instrumented</span>
                  <span
                    class="bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded text-[9px]"
                    >DATA GAP</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- TAB 8: ONE-PAGE IMPACT CASE                    -->
      <!-- ============================================== -->
      <div v-if="activeTab === 'case'" class="space-y-6">
        <!-- Case Header & Action Toolbar -->
        <div
          class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-border pb-4"
        >
          <div>
            <h2 class="text-lg font-bold text-white">
              {{ impactCase?.title }}
            </h2>
            <p class="text-xs text-slate-400">{{ impactCase?.tagline }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="copyCaseSummary"
              class="flex items-center gap-1 rounded bg-accent px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700"
            >
              <Copy class="size-3.5" />
              <span>{{ copyStatus }}</span>
            </button>
            <button
              @click="windowPrint"
              class="flex items-center gap-1 rounded bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500"
            >
              <Printer class="size-3.5" />
              <span>Print Friendly</span>
            </button>
          </div>
        </div>

        <!-- 9-Section Case Document Body -->
        <div class="grid gap-4 md:grid-cols-2">
          <div
            v-for="sec in impactCase?.sections"
            :key="sec.number"
            class="rounded-xl border border-border bg-card p-4 space-y-2"
          >
            <div class="flex items-center gap-2 border-b border-border/60 pb-2">
              <span
                class="flex size-5 items-center justify-center rounded-full bg-blue-500/20 text-[10px] font-bold text-blue-400"
              >
                {{ sec.number }}
              </span>
              <h4
                class="text-xs font-bold text-slate-200 uppercase tracking-wider"
              >
                {{ sec.title }}
              </h4>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">
              {{ sec.content }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Methodology Modal -->
    <div
      v-if="showMethodology"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
    >
      <div
        class="w-full max-w-2xl rounded-xl border border-blue-500/40 bg-[#0d121d] p-6 shadow-2xl space-y-4"
      >
        <div
          class="flex items-center justify-between border-b border-border pb-3"
        >
          <div class="flex items-center gap-2">
            <ShieldCheck class="size-5 text-blue-400" />
            <h3 class="text-base font-bold text-white">
              PULSYNC Methodology & Data Provenance
            </h3>
          </div>
          <button
            @click="showMethodology = false"
            class="text-slate-400 hover:text-white"
          >
            <X class="size-5" />
          </button>
        </div>

        <div
          class="space-y-3 text-xs text-slate-300 leading-relaxed max-h-[65vh] overflow-y-auto pr-2"
        >
          <div>
            <strong class="text-white block mb-0.5">Session Definition:</strong>
            <p>{{ methodology?.session_definition }}</p>
          </div>
          <div>
            <strong class="text-white block mb-0.5">Session Type:</strong>
            <p>{{ methodology?.session_type }}</p>
          </div>
          <div>
            <strong class="text-white block mb-0.5"
              >Information Interest Proxy:</strong
            >
            <p>{{ methodology?.information_interest_proxy }}</p>
          </div>
          <div>
            <strong class="text-white block mb-0.5"
              >Target Segment Definition:</strong
            >
            <p>{{ methodology?.target_segment_definition }}</p>
          </div>
          <div>
            <strong class="text-white block mb-0.5">Comparison Cohort:</strong>
            <p>{{ methodology?.comparison_cohort }}</p>
          </div>
          <div>
            <strong class="text-white block mb-0.5"
              >Statistical Significance Test:</strong
            >
            <p>{{ methodology?.statistical_test }}</p>
          </div>
          <div
            class="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-amber-300"
          >
            <strong class="text-amber-200 block mb-0.5"
              >Causal Limitation Disclaimer:</strong
            >
            <p>{{ methodology?.causal_disclaimer }}</p>
          </div>
        </div>

        <div class="flex justify-end pt-2 border-t border-border">
          <button
            @click="showMethodology = false"
            class="rounded bg-blue-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-blue-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import {
  BarChart3,
  Activity,
  Layers,
  Repeat,
  GitFork,
  Calculator,
  FileText,
  HelpCircle,
  Download,
  ShieldCheck,
  AlertTriangle,
  TrendingUp,
  Sparkles,
  CheckCircle2,
  LogOut,
  Info,
  Check,
  Copy,
  Printer,
  X,
} from "lucide-vue-next";
import {
  fetchImpactSummary,
  fetchImpactSessionHealth,
  fetchImpactMatrix,
  fetchImpactSegments,
  fetchImpactReplay,
  fetchImpactOpportunity,
  simulateROI,
  fetchImpactCase,
  fetchImpactMethodology,
  fetchImpactMetricsChain,
  type ImpactSummary,
  type SessionHealthData,
  type MatrixCell,
  type SegmentInfo,
  type ReplayData,
  type OpportunityData,
  type ROISimulationResult,
  type ImpactCaseData,
  type MethodologyData,
  type MetricsChainData,
} from "@/services/api";

const activeTab = ref("overview");
const loading = ref(true);
const loadError = ref("");
const showMethodology = ref(false);
const copyStatus = ref("Copy Summary");

const tabs = [
  { id: "overview", label: "Executive Overview", icon: BarChart3 },
  { id: "health", label: "Session Health", icon: Activity },
  { id: "segments", label: "Segments & Matrix", icon: Layers },
  { id: "replay", label: "Historical Replay", icon: Repeat },
  { id: "waterfall", label: "Value Waterfall", icon: GitFork },
  { id: "roi", label: "ROI Simulator", icon: Calculator },
  { id: "metrics", label: "Metrics to Follow", icon: CheckCircle2 },
  { id: "case", label: "Impact Case", icon: FileText },
];

const summary = ref<ImpactSummary | null>(null);
const health = ref<SessionHealthData | null>(null);
const matrix = ref<MatrixCell[]>([]);
const segments = ref<Record<string, SegmentInfo>>({});
const replay = ref<ReplayData | null>(null);
const opportunity = ref<OpportunityData | null>(null);
const roiResult = ref<ROISimulationResult | null>(null);
const impactCase = ref<ImpactCaseData | null>(null);
const methodology = ref<MethodologyData | null>(null);
const metricsChain = ref<MetricsChainData | null>(null);

type ChallengeKpi = {
  label: string;
  definition: string;
  value: string;
  type: "OBSERVED" | "CALCULATED" | "SCENARIO";
  period: string;
  source: string;
};

const challengeKpis = computed<ChallengeKpi[]>(() => {
  const dataset = summary.value?.dataset;
  const sessionHealth = health.value;
  const sessions = dataset?.sessions ?? sessionHealth?.total_sessions ?? 0;
  const players = dataset?.players ?? sessionHealth?.active_players ?? 0;

  return [
    {
      label: "Value per Session",
      definition: "Business value or revenue attributable to one session.",
      value: "Not currently measurable",
      type: "CALCULATED",
      period: "Production telemetry required",
      source: "No revenue/value attribution in current API",
    },
    {
      label: "Session Conversion Rate",
      definition: "Share of sessions reaching a confirmed valuable action.",
      value: "Not currently measurable",
      type: "CALCULATED",
      period: "Confirmation telemetry required",
      source: "No confirmed conversion event in current API",
    },
    {
      label: "Actions per Session",
      definition: "Average instrumented actions in a reconstructed session.",
      value: sessionHealth
        ? `${sessionHealth.actions_per_session}`
        : "Not currently measurable",
      type: "CALCULATED",
      period: "Historical reconstructed sessions",
      source: "GET /api/impact/session-health",
    },
    {
      label: "Final-step Conversion",
      definition: "Share reaching the final confirmation step.",
      value: "Not currently measurable",
      type: "CALCULATED",
      period: "Confirmation telemetry required",
      source: "No final-step event in current API",
    },
    {
      label: "Sessions per User",
      definition: "Reconstructed sessions divided by observed players.",
      value:
        players > 0
          ? (sessions / players).toFixed(2)
          : "Not currently measurable",
      type: "CALCULATED",
      period: "Historical dataset window",
      source: "GET /api/impact/summary dataset",
    },
    {
      label: "Time to First Action",
      definition:
        "Elapsed time from session start to the first meaningful action.",
      value: "Not currently measurable",
      type: "CALCULATED",
      period: "First-action timestamp required",
      source: "No reliable first-action measure in current API",
    },
  ];
});

const frameworkLevels = computed(() => {
  const sessionHealth = health.value;
  const replayData = replay.value;
  const opportunityData = opportunity.value;
  const roiData = roiResult.value;
  const unavailable = "Not currently measurable";

  return [
    {
      level: 1,
      name: "Session Health",
      metrics: [
        {
          name: "Session Completion Rate",
          current: sessionHealth
            ? `${sessionHealth.session_completion_rate}%`
            : unavailable,
          target: "No target supplied",
        },
        {
          name: "Abandonment Rate",
          current: sessionHealth
            ? `${sessionHealth.abandonment_rate}%`
            : unavailable,
          target: "No target supplied",
        },
        {
          name: "Actions per Session",
          current: sessionHealth
            ? `${sessionHealth.actions_per_session}`
            : unavailable,
          target: "No target supplied",
        },
        {
          name: "Session Quality Score",
          current: sessionHealth
            ? `${sessionHealth.session_quality_avg}/100`
            : unavailable,
          target: "No target supplied",
        },
      ],
    },
    {
      level: 2,
      name: "PULSYNC Effectiveness",
      metrics: [
        {
          name: "VALUE_SEEKING Detection Rate",
          current: opportunityData
            ? `${opportunityData.session_share_pct}%`
            : unavailable,
          target: "Observed share",
        },
        {
          name: "Information Recommendation CTR",
          current: unavailable,
          target: "Production telemetry required",
        },
        {
          name: "Contextual Guidance Acceptance",
          current: unavailable,
          target: "Production telemetry required",
        },
        {
          name: "Recommendation Dismissal Rate",
          current: unavailable,
          target: "Production telemetry required",
        },
      ],
    },
    {
      level: 3,
      name: "Customer Outcome",
      metrics: [
        {
          name: "1-Day Return Rate",
          current: replayData
            ? `${replayData.value_seeking.return_1d_rate}%`
            : unavailable,
          target: "Observed cohort rate",
        },
        {
          name: "7-Day Return Rate",
          current: replayData
            ? `${replayData.value_seeking.return_7d_rate}%`
            : unavailable,
          target: "Observed cohort rate",
        },
        {
          name: "Observed Gap vs Comparison",
          current: replayData
            ? `+${replayData.observed_difference_pp} pp`
            : unavailable,
          target: "Correlation only",
        },
        {
          name: "Subsequent Session Rate",
          current: replayData
            ? `${replayData.value_seeking.subsequent_session_rate}%`
            : unavailable,
          target: "Observed cohort rate",
        },
      ],
    },
    {
      level: 4,
      name: "Business Outcome",
      metrics: [
        {
          name: "Historical Stake Exposure",
          current: opportunityData
            ? `€${opportunityData.historical_stake_exposure_eur.toLocaleString()}`
            : unavailable,
          target: "Observed exposure, not revenue",
        },
        {
          name: "Scenario Value",
          current: roiData
            ? `€${roiData.outputs.annual_scenario_value_eur.toLocaleString()}`
            : unavailable,
          target: "Scenario output",
        },
        {
          name: "Scenario Net Value",
          current: roiData
            ? `€${roiData.outputs.annual_net_value_eur.toLocaleString()}`
            : unavailable,
          target: "Scenario output",
        },
        {
          name: "Scenario ROI",
          current: roiData ? `${roiData.outputs.roi_percent}%` : unavailable,
          target: "Scenario output",
        },
      ],
    },
  ];
});

const simInputs = ref({
  scenario: "base",
  scenario_realization_pct: 50,
  monthly_sessions: 100000,
  inference_cost_per_call: 0.005,
  api_cost_per_call: 0.002,
  hosting_cost_monthly: 500,
  storage_cost_monthly: 200,
  engineering_cost: 25000,
});

onMounted(async () => {
  try {
    const [
      summaryData,
      healthData,
      matrixData,
      segmentsData,
      replayData,
      oppData,
      roiData,
      caseData,
      methData,
      chainData,
    ] = await Promise.all([
      fetchImpactSummary(),
      fetchImpactSessionHealth(),
      fetchImpactMatrix(),
      fetchImpactSegments(),
      fetchImpactReplay(),
      fetchImpactOpportunity(),
      simulateROI(simInputs.value),
      fetchImpactCase("base"),
      fetchImpactMethodology(),
      fetchImpactMetricsChain(),
    ]);

    summary.value = summaryData;
    health.value = healthData;
    matrix.value = matrixData;
    segments.value = segmentsData;
    replay.value = replayData;
    opportunity.value = oppData;
    roiResult.value = roiData;
    impactCase.value = caseData;
    methodology.value = methData;
    metricsChain.value = chainData;
  } catch (err) {
    console.error("Failed loading impact dashboard data:", err);
    loadError.value =
      "The impact service did not return a complete dataset. Retry after the backend is available.";
  } finally {
    loading.value = false;
  }
});

async function runSimulation() {
  try {
    roiResult.value = await simulateROI(simInputs.value);
  } catch (e) {
    console.error("Simulation error:", e);
  }
}

function applyScenarioPreset(preset: string) {
  simInputs.value.scenario = preset;
  if (preset === "conservative") {
    simInputs.value.scenario_realization_pct = 25;
  } else if (preset === "optimistic") {
    simInputs.value.scenario_realization_pct = 75;
  } else {
    simInputs.value.scenario_realization_pct = 50;
  }
  runSimulation();
}

function formatKpiValue(key: string, val: any): string {
  if (typeof val === "number") {
    if (key.includes("roi")) return val + "%";
    if (key.includes("diff")) return "+" + val + " pp";
    if (key.includes("rate")) return val + "%";
    return val.toLocaleString();
  }
  return String(val);
}

function setActiveTab(tabId: string) {
  activeTab.value = tabId;
}

function kpiTypeClass(type: ChallengeKpi["type"]): string {
  if (type === "OBSERVED")
    return "border border-emerald-500/30 bg-emerald-500/20 text-emerald-300";
  if (type === "CALCULATED")
    return "border border-blue-500/30 bg-blue-500/20 text-blue-300";
  return "border border-amber-500/30 bg-amber-500/20 text-amber-300";
}

function copyCaseSummary() {
  if (!impactCase.value) return;
  const text = impactCase.value.sections
    .map((s) => `${s.number}. ${s.title}\n${s.content}`)
    .join("\n\n");
  navigator.clipboard.writeText(text);
  copyStatus.value = "Copied!";
  setTimeout(() => {
    copyStatus.value = "Copy Summary";
  }, 2500);
}

function windowPrint() {
  window.print();
}

function exportImpactCaseJson() {
  if (!impactCase.value) return;
  const blob = new Blob([JSON.stringify(impactCase.value, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "pulsync_impact_case.json";
  a.click();
  URL.revokeObjectURL(url);
}
</script>
