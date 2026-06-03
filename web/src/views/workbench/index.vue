<template>
  <AppPage :show-footer="false">
    <div flex-1 class="workbench-wrap">
      <n-card class="hero-card" :bordered="false">
        <div class="hero">
          <div class="hero-left">
            <img class="hero-avatar" :src="userStore.avatar" />
            <div class="hero-text">
              <div class="hero-title">
                {{ $t('views.workbench.text_hello', { username: userStore.name }) }}
              </div>
              <div class="hero-subtitle">{{ $t('views.workbench.text_welcome') }}</div>
              <div class="hero-meta">
                <n-tag size="small" type="success" :bordered="false">
                  {{ dashboardStoreName }}
                </n-tag>
                <span v-if="generatedAt" class="hero-time">数据更新时间：{{ generatedAt }}</span>
              </div>
            </div>
          </div>

          <div class="hero-right">
            <div class="stat-grid">
              <div v-for="item in statisticData" :key="item.id" class="stat-item">
                <div class="stat-label">{{ item.label }}</div>
                <div class="stat-value">{{ item.value }}</div>
              </div>
            </div>
          </div>
        </div>
      </n-card>

      <n-spin :show="loading" size="large">
        <n-alert v-if="error" type="error" class="alert-card" :bordered="false">
          {{ error }}
        </n-alert>

        <n-alert v-else-if="!dashboardStoreId" type="warning" class="alert-card" :bordered="false">
          当前账号未绑定门店，无法生成经营驾驶舱与 AI 分析数据。
        </n-alert>

        <n-card
          v-else
          :title="$t('views.workbench.label_dashboard')"
          class="dash-card"
          :bordered="false"
          size="small"
          :segmented="true"
          mt-15
        >
          <template #header-extra>
            <n-space :size="10" :wrap="false">
              <n-button secondary type="primary" @click="loadDashboard">刷新</n-button>
              <n-button text type="primary">{{ $t('views.workbench.label_more') }}</n-button>
            </n-space>
          </template>

          <n-grid cols="1 s:2 l:4" :x-gap="12" :y-gap="12">
            <n-gi>
              <div class="kpi-card kpi-primary">
                <div class="kpi-label">{{ $t('views.workbench.kpi_today_sales') }}</div>
                <div class="kpi-value">¥{{ formatAmount(kpis.today_sales_amount) }}</div>
                <div class="kpi-trend">
                  <span class="kpi-trend-label">
                    {{ $t('views.workbench.label_vs_yesterday') }}
                  </span>
                  <span :class="salesTrendClass">{{ salesTrendText }}</span>
                </div>
              </div>
            </n-gi>
            <n-gi>
              <div class="kpi-card kpi-surface">
                <div class="kpi-label">{{ $t('views.workbench.kpi_yesterday_compare') }}</div>
                <div class="kpi-value">¥{{ formatAmount(kpis.yesterday_sales_amount) }}</div>
                <div class="kpi-trend">
                  <span class="kpi-trend-label">订单数</span>
                  <span class="kpi-trend-value">{{ store.sales_order_count || 0 }}</span>
                </div>
              </div>
            </n-gi>
            <n-gi>
              <div class="kpi-card kpi-surface">
                <div class="kpi-label">{{ $t('views.workbench.kpi_gross_margin') }}</div>
                <div class="kpi-value">{{ grossMarginText }}</div>
                <div class="kpi-trend">
                  <span class="kpi-trend-label">会员数</span>
                  <span class="kpi-trend-value">{{ store.member_count || 0 }}</span>
                </div>
              </div>
            </n-gi>
            <n-gi>
              <div class="kpi-card kpi-warning">
                <div class="kpi-label">{{ $t('views.workbench.kpi_inventory_alert') }}</div>
                <div class="kpi-value">{{ kpis.inventory_warning_count ?? 0 }}</div>
                <div class="kpi-trend">
                  <span class="kpi-trend-label">可用库存</span>
                  <span class="kpi-trend-value">{{ store.inventory_qty || 0 }}</span>
                </div>
              </div>
            </n-gi>
          </n-grid>

          <n-grid mt-15 cols="1 l:2" :x-gap="12" :y-gap="12">
            <n-gi>
              <n-card
                size="small"
                class="inner-card"
                :bordered="false"
                :title="$t('views.workbench.label_sales_trend_7d')"
              >
                <div ref="salesTrendRef" class="chart-container"></div>
              </n-card>
            </n-gi>

            <n-gi>
              <n-card
                size="small"
                class="inner-card"
                :bordered="false"
                :title="$t('views.workbench.label_inventory_distribution')"
              >
                <div ref="inventoryPieRef" class="chart-container"></div>
              </n-card>
            </n-gi>
          </n-grid>

          <n-grid mt-15 cols="1 l:2" :x-gap="12" :y-gap="12">
            <n-gi>
              <n-card
                size="small"
                class="inner-card"
                :bordered="false"
                :title="$t('views.workbench.label_store_sales_ranking')"
              >
                <div v-if="storeSalesRanking.length === 0" class="empty-block">暂无排行数据</div>
                <div
                  v-for="(item, index) in storeSalesRanking"
                  :key="item.store_id"
                  class="rank-item"
                >
                  <div class="rank-head">
                    <span class="rank-title">{{ index + 1 }}. {{ item.store_name }}</span>
                    <span class="rank-value">¥{{ formatAmount(item.net_sales_amount) }}</span>
                  </div>
                  <n-progress
                    type="line"
                    :percentage="item.percent"
                    :show-indicator="false"
                    :height="8"
                  />
                </div>
              </n-card>
            </n-gi>

            <n-gi>
              <n-card
                size="small"
                class="inner-card"
                :bordered="false"
                :title="$t('views.workbench.kpi_hot_goods_top5')"
              >
                <div v-if="hotGoodsTop5.length === 0" class="empty-block">暂无热销数据</div>
                <div v-for="(item, index) in hotGoodsTop5" :key="item.product_id" class="hot-item">
                  <div class="hot-left">
                    <span class="hot-rank">{{ index + 1 }}</span>
                    <div class="hot-name">{{ item.name || '-' }}</div>
                  </div>
                  <div class="hot-right">
                    <div class="hot-metric">销量 {{ item.sale_qty }}</div>
                    <div class="hot-sub">库存 {{ item.stock_qty }}</div>
                  </div>
                </div>
              </n-card>
            </n-gi>
          </n-grid>

          <n-card mt-15 class="ai-card" size="small" :bordered="false" title="AI 智能经营分析">
            <div class="ai-grid">
              <div class="ai-insight">
                <div class="ai-summary">{{ aiPanel.summary }}</div>
                <div class="ai-section">
                  <div class="ai-section-title">异常预警</div>
                  <div v-if="aiPanel.warnings.length === 0" class="ai-empty">暂无异常预警</div>
                  <div v-for="(item, idx) in aiPanel.warnings" :key="idx" class="ai-item">
                    {{ item }}
                  </div>
                </div>
                <div class="ai-section">
                  <div class="ai-section-title">智能建议</div>
                  <div v-if="aiPanel.suggestions.length === 0" class="ai-empty">暂无建议</div>
                  <div v-for="(item, idx) in aiPanel.suggestions" :key="idx" class="ai-item">
                    {{ item }}
                  </div>
                </div>
              </div>

              <div class="ai-chat">
                <div ref="chatScrollRef" class="chat-history">
                  <div
                    v-for="(msg, idx) in chatMessages"
                    :key="idx"
                    class="chat-row"
                    :class="msg.role"
                  >
                    <div class="chat-bubble">
                      <div
                        v-if="msg.role === 'assistant'"
                        class="chat-markdown"
                        v-html="renderAssistantMarkdown(msg.content)"
                      ></div>
                      <div v-else class="chat-text">{{ msg.content }}</div>
                    </div>
                  </div>
                </div>

                <div class="chat-input">
                  <n-input
                    v-model:value="chatInput"
                    type="textarea"
                    :autosize="{ minRows: 2, maxRows: 4 }"
                    placeholder="例如：今天销售下降的原因可能是什么？我应该先做哪些动作？"
                    :disabled="chatLoading"
                  />
                  <n-button
                    type="primary"
                    :loading="chatLoading"
                    :disabled="!chatInput.trim() || chatLoading"
                    @click="sendChat"
                  >
                    发送
                  </n-button>
                </div>
              </div>
            </div>
          </n-card>
        </n-card>
      </n-spin>
    </div>
  </AppPage>
</template>

<script setup>
import * as echarts from 'echarts'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import api from '@/api'
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })

marked.setOptions({ gfm: true, breaks: true })

const loading = ref(false)
const error = ref('')
const generatedAt = ref('')
const dashboardStoreId = ref(null)
const dashboardStoreName = ref('-')

const store = ref({})
const statistics = ref({ store_count: 0, pending_audit_count: 0, system_message_count: 0 })
const kpis = ref({})
const salesTrendData = ref([])
const inventoryDistributionData = ref([])
const storeSalesRanking = ref([])
const hotGoodsTop5 = ref([])
const aiPanel = ref({ summary: '', warnings: [], suggestions: [] })

const statisticData = computed(() => [
  {
    id: 0,
    label: t('views.workbench.label_number_of_items'),
    value: String(statistics.value.store_count ?? 0),
  },
  {
    id: 1,
    label: t('views.workbench.label_upcoming'),
    value: String(statistics.value.pending_audit_count ?? 0),
  },
  {
    id: 2,
    label: t('views.workbench.label_information'),
    value: String(statistics.value.system_message_count ?? 0),
  },
])

const grossMarginText = computed(() => {
  const value = kpis.value?.gross_margin_rate
  if (value === null || value === undefined) return '—'
  return `${(Number(value) * 100).toFixed(2)}%`
})

const salesTrendText = computed(() => {
  const rate = kpis.value?.today_vs_yesterday_rate
  if (rate === null || rate === undefined) return '—'
  const pct = Number(rate) * 100
  const sign = pct > 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
})

const salesTrendClass = computed(() => {
  const rate = Number(kpis.value?.today_vs_yesterday_rate)
  if (!Number.isFinite(rate) || rate === 0) return 'trend-neutral'
  return rate > 0 ? 'trend-up' : 'trend-down'
})

const userStore = useUserStore()

function renderAssistantMarkdown(content) {
  const raw = marked.parse(String(content || ''))
  return DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } })
}

function formatAmount(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '0.00'
  return num.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.getWorkbenchDashboard({ days: 7 })
    const payload = res.data || {}
    generatedAt.value = payload.generated_at || ''
    dashboardStoreId.value = payload.store_id ?? null
    dashboardStoreName.value = payload.store_name || '-'

    const data = payload.data || {}
    store.value = data.store || {}
    statistics.value = data.statistics || statistics.value
    kpis.value = data.kpis || {}
    salesTrendData.value = data.sales_trend || []
    inventoryDistributionData.value = data.inventory_distribution || []
    storeSalesRanking.value = data.store_sales_ranking || []
    hotGoodsTop5.value = data.hot_goods_top5 || []
    aiPanel.value = data.ai_panel || { summary: '', warnings: [], suggestions: [] }

    nextTick(initCharts)
    syncWelcomeMessage()
  } catch (e) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const salesTrendRef = ref()
const inventoryPieRef = ref()
let salesTrendChart = null
let inventoryPieChart = null

function getSalesTrendOption() {
  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 30, right: 18, bottom: 20, left: 36 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: salesTrendData.value.map((item) => item.date?.slice?.(5) || item.date),
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#e8eef6' } },
    },
    series: [
      {
        type: 'line',
        smooth: true,
        showSymbol: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#2d7a4b' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(45,122,75,0.22)' },
            { offset: 1, color: 'rgba(45,122,75,0.04)' },
          ]),
        },
        data: salesTrendData.value.map((item) => item.amount),
      },
    ],
  }
}

function getInventoryPieOption() {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { bottom: 0, left: 'center' },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '45%'],
        label: { formatter: '{d}%' },
        labelLine: { length: 12, length2: 10 },
        data: inventoryDistributionData.value.map((item, index) => {
          const colors = ['#2d7a4b', '#2080f0', '#f0a020', '#d03050', '#7a9a4f', '#3f6212']
          return {
            name: item.category,
            value: item.qty,
            itemStyle: { color: colors[index % colors.length] },
          }
        }),
      },
    ],
  }
}

function initCharts() {
  if (salesTrendRef.value) {
    salesTrendChart?.dispose()
    salesTrendChart = echarts.init(salesTrendRef.value)
    salesTrendChart.setOption(getSalesTrendOption())
  }
  if (inventoryPieRef.value) {
    inventoryPieChart?.dispose()
    inventoryPieChart = echarts.init(inventoryPieRef.value)
    inventoryPieChart.setOption(getInventoryPieOption())
  }
}

function resizeCharts() {
  salesTrendChart?.resize()
  inventoryPieChart?.resize()
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('resize', resizeCharts)
})

watch(salesTrendData, () => salesTrendChart?.setOption(getSalesTrendOption()), {
  deep: true,
})
watch(inventoryDistributionData, () => inventoryPieChart?.setOption(getInventoryPieOption()), {
  deep: true,
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  salesTrendChart?.dispose()
  inventoryPieChart?.dispose()
  salesTrendChart = null
  inventoryPieChart = null
})

const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatScrollRef = ref()

function syncWelcomeMessage() {
  if (chatMessages.value.length) return
  const preset = aiPanel.value?.summary
  chatMessages.value = [
    {
      role: 'assistant',
      content: preset || '我可以基于门店经营数据进行分析，你可以直接问我：销售/库存/会员等问题。',
    },
  ]
  nextTick(scrollChatToBottom)
}

function scrollChatToBottom() {
  const el = chatScrollRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

async function sendChat() {
  if (!dashboardStoreId.value) return
  const question = chatInput.value.trim()
  if (!question) return

  chatLoading.value = true
  chatInput.value = ''
  chatMessages.value.push({ role: 'user', content: question })
  nextTick(scrollChatToBottom)

  try {
    const history = chatMessages.value
      .slice(-12)
      .filter((item) => item.role === 'user' || item.role === 'assistant')
      .map((item) => ({ role: item.role, content: item.content }))
    const res = await api.operateAIChat({
      question,
      messages: history,
      store_id: dashboardStoreId.value,
    })
    const reply = res.data?.reply || '未返回内容'
    chatMessages.value.push({ role: 'assistant', content: reply })
    if (res.data?.analysis) aiPanel.value = res.data.analysis
  } catch (e) {
    chatMessages.value.push({ role: 'assistant', content: e?.message || '请求失败，请稍后重试。' })
  } finally {
    chatLoading.value = false
    nextTick(scrollChatToBottom)
  }
}
</script>

<style scoped>
.workbench-wrap {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.hero-card {
  border-radius: 16px;
  background: radial-gradient(
    1200px 420px at 10% 0%,
    rgba(142, 197, 96, 0.26) 0%,
    rgba(142, 197, 96, 0.06) 38%,
    rgba(255, 255, 255, 0.6) 100%
  );
  box-shadow: 0 14px 40px rgba(45, 122, 75, 0.12);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.hero-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 260px;
}

.hero-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 20px rgba(45, 122, 75, 0.18);
}

.hero-title {
  font-size: 22px;
  font-weight: 650;
  color: #1f2a1b;
}

.hero-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: rgba(47, 58, 31, 0.72);
}

.hero-meta {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-time {
  font-size: 12px;
  color: rgba(47, 58, 31, 0.62);
}

.hero-right {
  flex: 1;
  min-width: 260px;
  display: flex;
  justify-content: flex-end;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  width: min(520px, 100%);
}

.stat-item {
  border-radius: 14px;
  padding: 12px 12px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(227, 234, 210, 0.8);
  box-shadow: 0 10px 26px rgba(45, 122, 75, 0.08);
}

.stat-label {
  font-size: 12px;
  color: rgba(47, 58, 31, 0.65);
}

.stat-value {
  margin-top: 8px;
  font-size: 20px;
  font-weight: 700;
  color: #1f2a1b;
}

.alert-card {
  border-radius: 14px;
}

.dash-card {
  border-radius: 16px;
  background: rgba(248, 251, 242, 0.74);
  box-shadow: 0 12px 34px rgba(45, 122, 75, 0.1);
}

.kpi-card {
  border-radius: 16px;
  padding: 14px 14px;
  border: 1px solid rgba(227, 234, 210, 0.9);
  box-shadow: 0 12px 24px rgba(45, 122, 75, 0.08);
  min-height: 106px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.kpi-primary {
  background: linear-gradient(
    135deg,
    rgba(142, 197, 96, 0.42) 0%,
    rgba(248, 251, 242, 0.92) 60%,
    rgba(255, 255, 255, 0.8) 100%
  );
}

.kpi-warning {
  background: linear-gradient(
    135deg,
    rgba(240, 160, 32, 0.16) 0%,
    rgba(255, 248, 236, 0.78) 70%,
    rgba(255, 255, 255, 0.75) 100%
  );
}

.kpi-surface {
  background: rgba(255, 255, 255, 0.7);
}

.kpi-label {
  font-size: 12px;
  color: rgba(47, 58, 31, 0.68);
}

.kpi-value {
  margin-top: 10px;
  font-size: 22px;
  font-weight: 760;
  color: #1f2a1b;
}

.kpi-trend {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 12px;
}

.kpi-trend-label {
  color: rgba(47, 58, 31, 0.6);
}

.kpi-trend-value {
  color: rgba(47, 58, 31, 0.82);
  font-weight: 600;
}

.trend-up {
  color: #18a058;
  font-weight: 700;
}

.trend-down {
  color: #d03050;
  font-weight: 700;
}

.trend-neutral {
  color: rgba(47, 58, 31, 0.72);
  font-weight: 600;
}

.inner-card {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 10px 22px rgba(45, 122, 75, 0.08);
}

.chart-container {
  width: 100%;
  height: 260px;
}

.empty-block {
  padding: 10px 0;
  color: rgba(47, 58, 31, 0.55);
  font-size: 12px;
}

.rank-item {
  padding: 10px 0;
  border-bottom: 1px solid rgba(227, 234, 210, 0.8);
}

.rank-item:last-child {
  border-bottom: none;
}

.rank-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.rank-title {
  color: rgba(47, 58, 31, 0.9);
}

.rank-value {
  color: rgba(47, 58, 31, 0.9);
  font-weight: 650;
}

.hot-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(227, 234, 210, 0.8);
}

.hot-item:last-child {
  border-bottom: none;
  padding-bottom: 4px;
}

.hot-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.hot-name {
  color: rgba(47, 58, 31, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.hot-right {
  text-align: right;
  flex-shrink: 0;
}

.hot-metric {
  font-weight: 650;
  color: rgba(47, 58, 31, 0.9);
}

.hot-sub {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(47, 58, 31, 0.62);
}

.hot-rank {
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 999px;
  color: #fff;
  background: #2d7a4b;
  font-size: 12px;
  font-weight: 700;
}

.ai-card {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 10px 22px rgba(45, 122, 75, 0.08);
}

.ai-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 12px;
}

.ai-summary {
  padding: 12px 12px;
  border-radius: 12px;
  background: rgba(142, 197, 96, 0.12);
  border: 1px solid rgba(227, 234, 210, 0.9);
  color: rgba(47, 58, 31, 0.9);
  font-size: 13px;
}

.ai-section {
  margin-top: 12px;
}

.ai-section-title {
  font-size: 13px;
  font-weight: 650;
  color: rgba(47, 58, 31, 0.92);
  margin-bottom: 8px;
}

.ai-item {
  padding: 10px 10px;
  border-radius: 12px;
  border: 1px solid rgba(227, 234, 210, 0.9);
  background: rgba(248, 251, 242, 0.7);
  color: rgba(47, 58, 31, 0.86);
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.ai-empty {
  padding: 10px 0;
  color: rgba(47, 58, 31, 0.55);
  font-size: 12px;
}

.ai-chat {
  display: flex;
  flex-direction: column;
  min-height: 340px;
}

.chat-history {
  flex: 1;
  overflow: auto;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(227, 234, 210, 0.9);
  background: rgba(248, 251, 242, 0.58);
}

.chat-row {
  display: flex;
  margin-bottom: 10px;
}

.chat-row.user {
  justify-content: flex-end;
}

.chat-row.assistant {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 92%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(227, 234, 210, 0.9);
  background: rgba(255, 255, 255, 0.74);
  color: rgba(47, 58, 31, 0.9);
  font-size: 13px;
  line-height: 1.55;
  overflow: hidden;
}

.chat-text {
  white-space: pre-wrap;
}

.chat-markdown {
  color: rgba(47, 58, 31, 0.9);
}

.chat-markdown :deep(p) {
  margin: 0 0 8px;
  white-space: normal;
}

.chat-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.chat-markdown :deep(h1),
.chat-markdown :deep(h2),
.chat-markdown :deep(h3) {
  margin: 10px 0 8px;
  font-weight: 700;
  color: rgba(31, 42, 27, 0.95);
}

.chat-markdown :deep(h1) {
  font-size: 16px;
}

.chat-markdown :deep(h2) {
  font-size: 15px;
}

.chat-markdown :deep(h3) {
  font-size: 14px;
}

.chat-markdown :deep(ul),
.chat-markdown :deep(ol) {
  margin: 0 0 8px 18px;
  padding: 0;
}

.chat-markdown :deep(li) {
  margin: 4px 0;
}

.chat-markdown :deep(code) {
  font-family:
    ui-monospace,
    SFMono-Regular,
    Menlo,
    Monaco,
    Consolas,
    'Liberation Mono',
    'Courier New',
    monospace;
  font-size: 12px;
  background: rgba(142, 197, 96, 0.14);
  border: 1px solid rgba(227, 234, 210, 0.9);
  padding: 1px 6px;
  border-radius: 8px;
}

.chat-markdown :deep(pre) {
  margin: 0 0 10px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(248, 251, 242, 0.78);
  border: 1px solid rgba(227, 234, 210, 0.9);
  overflow: auto;
}

.chat-markdown :deep(pre code) {
  background: transparent;
  border: none;
  padding: 0;
}

.chat-markdown :deep(blockquote) {
  margin: 0 0 10px;
  padding: 8px 10px;
  border-left: 3px solid rgba(45, 122, 75, 0.5);
  background: rgba(142, 197, 96, 0.08);
  border-radius: 10px;
}

.chat-markdown :deep(a) {
  color: #2d7a4b;
  text-decoration: underline;
}

.chat-row.user .chat-bubble {
  background: rgba(142, 197, 96, 0.16);
}

.chat-input {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: start;
}

@media (max-width: 992px) {
  .ai-grid {
    grid-template-columns: 1fr;
  }
  .stat-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
