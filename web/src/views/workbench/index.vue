<template>
  <AppPage :show-footer="false">
    <div flex-1>
      <n-card rounded-10>
        <div flex items-center justify-between>
          <div flex items-center>
            <img rounded-full width="60" :src="userStore.avatar" />
            <div ml-10>
              <p text-20 font-semibold>
                {{ $t('views.workbench.text_hello', { username: userStore.name }) }}
              </p>
              <p mt-5 text-14 op-60>{{ $t('views.workbench.text_welcome') }}</p>
            </div>
          </div>
          <n-space :size="12" :wrap="false">
            <n-statistic v-for="item in statisticData" :key="item.id" v-bind="item"></n-statistic>
          </n-space>
        </div>
      </n-card>

      <n-card
        :title="$t('views.workbench.label_dashboard')"
        size="small"
        :segmented="true"
        mt-15
        rounded-10
      >
        <template #header-extra>
          <n-button text type="primary">{{ $t('views.workbench.label_more') }}</n-button>
        </template>

        <n-grid cols="4" :x-gap="12" :y-gap="12">
          <n-gi v-for="item in kpiData" :key="item.id">
            <n-card size="small" hoverable>
              <div text-13 op-70>{{ item.label }}</div>
              <div mt-8 text-24 font-semibold>{{ item.value }}</div>
              <div mt-8 text-12 :class="item.trendClass">{{ item.trend }}</div>
            </n-card>
          </n-gi>
        </n-grid>

        <n-grid mt-15 cols="1 l:2" :x-gap="12" :y-gap="12">
          <n-gi>
            <n-card size="small" :title="$t('views.workbench.label_sales_trend_7d')">
              <div ref="salesTrendRef" class="chart-container"></div>
            </n-card>
          </n-gi>

          <n-gi>
            <n-card size="small" :title="$t('views.workbench.label_inventory_distribution')">
              <div ref="inventoryPieRef" class="chart-container"></div>
            </n-card>
          </n-gi>
        </n-grid>

        <n-card mt-15 size="small" :title="$t('views.workbench.label_store_sales_ranking')">
          <div v-for="(item, index) in storeRankingData" :key="item.store" mb-12>
            <div mb-4 flex items-center justify-between text-13>
              <span>{{ index + 1 }}. {{ item.store }}</span>
              <span font-medium>{{ item.amount }}</span>
            </div>
            <n-progress
              type="line"
              :percentage="item.percent"
              :show-indicator="false"
              :height="8"
            />
          </div>
        </n-card>

        <n-card mt-15 size="small" :title="$t('views.workbench.kpi_hot_goods_top5')">
          <div
            v-for="(item, index) in hotGoodsTop5"
            :key="item.name"
            class="hot-item"
            flex
            items-center
            justify-between
          >
            <div flex items-center>
              <span class="hot-rank">{{ index + 1 }}</span>
              <span>{{ item.name }}</span>
            </div>
            <div text-right>
              <div font-medium>{{ item.sales }}</div>
              <div text-12 op-65>{{ item.stock }}</div>
            </div>
          </div>
        </n-card>
      </n-card>
    </div>
  </AppPage>
</template>

<script setup>
import * as echarts from 'echarts'
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })

const statisticData = computed(() => [
  {
    id: 0,
    label: t('views.workbench.label_number_of_items'),
    value: '25',
  },
  {
    id: 1,
    label: t('views.workbench.label_upcoming'),
    value: '4/16',
  },
  {
    id: 2,
    label: t('views.workbench.label_information'),
    value: '12',
  },
])

const kpiData = computed(() => [
  {
    id: 0,
    label: t('views.workbench.kpi_today_sales'),
    value: '¥128,560',
    trend: '+8.6%',
    trendClass: 'text-#18a058',
  },
  {
    id: 1,
    label: t('views.workbench.kpi_yesterday_compare'),
    value: '+¥10,180',
    trend: t('views.workbench.label_vs_yesterday'),
    trendClass: 'text-#18a058',
  },
  {
    id: 2,
    label: t('views.workbench.kpi_gross_margin'),
    value: '23.4%',
    trend: '+1.2%',
    trendClass: 'text-#18a058',
  },
  {
    id: 3,
    label: t('views.workbench.kpi_inventory_alert'),
    value: '18',
    trend: '-3',
    trendClass: 'text-#d03050',
  },
])

const salesTrendData = ref([
  { day: 'Mon', value: 86 },
  { day: 'Tue', value: 92 },
  { day: 'Wed', value: 88 },
  { day: 'Thu', value: 104 },
  { day: 'Fri', value: 112 },
  { day: 'Sat', value: 126 },
  { day: 'Sun', value: 119 },
])

const inventoryDistributionData = ref([
  { label: '生鲜', value: 42, color: '#18a058' },
  { label: '日配', value: 32, color: '#2080f0' },
  { label: '粮油', value: 17, color: '#f0a020' },
  { label: '其他', value: 9, color: '#d03050' },
])

const storeRankingData = ref([
  { store: '汉阳店', amount: '¥32,840', percent: 100 },
  { store: '汉口店', amount: '¥29,310', percent: 89 },
  { store: '武昌店', amount: '¥25,460', percent: 78 },
  { store: '关谷店', amount: '¥20,990', percent: 64 },
  { store: '蔡甸店', amount: '¥18,720', percent: 57 },
])

const hotGoodsTop5 = ref([
  { name: '精品鸡蛋 30 枚装', sales: '2,480 件', stock: '库存 320 件' },
  { name: '巴氏鲜牛奶 950ml', sales: '2,160 件', stock: '库存 280 件' },
  { name: '东北大米 5kg', sales: '1,940 件', stock: '库存 410 件' },
  { name: '可口可乐 330ml*24', sales: '1,780 件', stock: '库存 260 件' },
  { name: '冰鲜三文鱼切片 250g', sales: '1,350 件', stock: '库存 120 件' },
])

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
      data: salesTrendData.value.map((item) => item.day),
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
        lineStyle: { width: 3, color: '#2080f0' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(32,128,240,0.25)' },
            { offset: 1, color: 'rgba(32,128,240,0.04)' },
          ]),
        },
        data: salesTrendData.value.map((item) => item.value),
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
        data: inventoryDistributionData.value.map((item) => ({
          name: item.label,
          value: item.value,
          itemStyle: { color: item.color },
        })),
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
  nextTick(initCharts)
  window.addEventListener('resize', resizeCharts)
})

watch(
  salesTrendData,
  () => {
    salesTrendChart?.setOption(getSalesTrendOption())
  },
  { deep: true }
)

watch(
  inventoryDistributionData,
  () => {
    inventoryPieChart?.setOption(getInventoryPieOption())
  },
  { deep: true }
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  salesTrendChart?.dispose()
  inventoryPieChart?.dispose()
  salesTrendChart = null
  inventoryPieChart = null
})

const userStore = useUserStore()
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 260px;
}

.hot-item {
  border-bottom: 1px solid rgb(236 245 255 / 90%);
  padding: 10px 0;
}

.hot-item:last-child {
  border-bottom: none;
  padding-bottom: 4px;
}

.hot-rank {
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  border-radius: 50%;
  margin-right: 8px;
  color: #fff;
  background: #2080f0;
  font-size: 12px;
}
</style>
