<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NProgress, NSpin } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

defineOptions({ name: '财务中心' })

const router = useRouter()
const loading = ref(false)
const overview = ref({})
const statementRows = ref([])

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const [overviewRes, statementRes, dashboardRes] = await Promise.all([
      api.getFinanceOverview(),
      api.getFinanceStatementList({ page: 1, page_size: 7 }),
      api.getCourseDesignOverview(),
    ])
    overview.value = {
      ...(overviewRes.data || {}),
      store_name: dashboardRes.data?.current_store?.store_name || '-',
    }
    statementRows.value = statementRes.data || []
  } finally {
    loading.value = false
  }
}

const cards = computed(() => [
  { title: '门店', value: overview.value.store_name || '-', type: 'neutral' },
  { title: '销售总额', value: `¥${Number(overview.value.sale_amount || 0).toFixed(2)}`, type: 'success' },
  { title: '退货金额', value: `¥${Number(overview.value.return_amount || 0).toFixed(2)}`, type: 'warning' },
  { title: '净销售额', value: `¥${Number(overview.value.net_sales_amount || 0).toFixed(2)}`, type: 'danger' },
  { title: '净销售数量', value: overview.value.net_sales_qty || 0, type: 'success' },
  { title: '收银笔数', value: overview.value.txn_count || 0, type: 'neutral' },
])

function openPage(path) {
  router.push(path)
}
</script>

<template>
  <CommonPage show-footer title="财务中心">
    <template #action>
      <div class="actions">
        <NButton type="primary" @click="openPage('/store/sales')">进入销售与收银</NButton>
      </div>
    </template>
    <NSpin :show="loading">
      <section class="card-grid">
        <div v-for="item in cards" :key="item.title" class="metric-card" :class="item.type">
          <div class="metric-label">{{ item.title }}</div>
          <div class="metric-value">{{ item.value }}</div>
        </div>
      </section>

      <section class="statement-card">
        <div class="board-title">最近财务日报</div>
        <div v-if="statementRows.length" class="statement-grid">
          <div v-for="row in statementRows" :key="row.date" class="statement-item">
            <div>
              <div class="statement-date">{{ row.date }}</div>
              <div class="statement-meta">净销量 {{ row.net_sales_qty }} 件</div>
            </div>
            <div class="statement-amount">¥{{ Number(row.net_sales_amount || 0).toFixed(2) }}</div>
          </div>
        </div>
        <div v-else class="empty-text">暂无财务日报数据</div>
      </section>
    </NSpin>
  </CommonPage>
</template>

<style scoped lang="scss">
.actions {
  display: flex;
}

.card-grid,
.board-grid {
  display: grid;
  gap: 12px;
}

.card-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
  margin-bottom: 16px;
}

.metric-card,
.board-card,
.statement-card {
  border-radius: 12px;
  border: 1px solid #e8eef6;
  background: #fff;
}

.metric-card {
  padding: 14px 16px;
}

.metric-card.success {
  background: #f2fbf5;
}

.metric-card.warning {
  background: #fff8ec;
}

.metric-card.danger {
  background: #fff2f0;
}

.metric-label,
.board-desc,
.statement-meta {
  color: #6b7280;
  font-size: 13px;
}

.metric-value {
  margin-top: 8px;
  font-size: 22px;
  font-weight: 600;
  color: #111827;
}

.board-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 16px;
}

.board-card,
.statement-card {
  padding: 16px;
}

.board-title,
.statement-date {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.board-desc {
  margin-top: 10px;
  line-height: 1.7;
}

.statement-grid {
  display: grid;
  gap: 12px;
  margin-top: 12px;
}

.statement-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #eef2f7;
}

.statement-item:last-child {
  border-bottom: none;
}

.statement-amount {
  font-size: 18px;
  font-weight: 600;
  color: #2563eb;
}

.empty-text {
  margin-top: 12px;
  color: #9ca3af;
  font-size: 13px;
}
</style>
