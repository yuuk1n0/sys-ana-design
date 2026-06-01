<script setup>
import { computed, onMounted, ref } from 'vue'
import { NButton, NSpin, NTag } from 'naive-ui'
import { useRouter } from 'vue-router'

import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

defineOptions({ name: '仓库中心' })

const router = useRouter()
const loading = ref(false)
const overview = ref({})
const warningRows = ref([])
const txnRows = ref([])

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const [overviewRes, warningRes, txnRes] = await Promise.all([
      api.getCourseDesignOverview(),
      api.getInventoryWarningList({ page: 1, page_size: 5 }),
      api.getInventoryTxnList({ page: 1, page_size: 6 }),
    ])
    overview.value = overviewRes.data?.current_store || {}
    warningRows.value = warningRes.data || []
    txnRows.value = txnRes.data || []
  } finally {
    loading.value = false
  }
}

const cards = computed(() => [
  { title: '门店仓库', value: overview.value.store_name || '-', type: 'neutral' },
  { title: '库存 SKU', value: overview.value.inventory_sku_count || 0, type: 'success' },
  { title: '可用库存', value: overview.value.inventory_qty || 0, type: 'success' },
  { title: '预警商品', value: overview.value.inventory_warning_count || 0, type: 'danger' },
])

const taskBoards = [
  {
    title: '仓库信息管理',
    desc: '维护门店仓储对象、货位规则与商品承载范围，作为入库、出库和盘点的统一入口。',
  },
  {
    title: '入库出库管理',
    desc: '当前已接入库存作业与业务流水，可从库存流水页执行采购入库、业务出库与销售扣减。',
  },
  {
    title: '库存盘点管理',
    desc: '提供盘点能力预留位，可按库存流水中的盘盈、盘亏类型扩展正式盘点单据。',
  },
  {
    title: '库存报警管理',
    desc: '基于库存阈值自动识别低库存商品，并在预警区展示待补货缺口。',
  },
]

function openPage(path) {
  router.push(path)
}
</script>

<template>
  <CommonPage show-footer title="仓库中心">
    <template #action>
      <div class="actions">
        <NButton type="primary" @click="openPage('/store/inventory-txn')">去做入库/出库</NButton>
        <NButton secondary type="warning" @click="openPage('/store/inventory-warning')">查看库存预警</NButton>
      </div>
    </template>
    <NSpin :show="loading">
      <section class="card-grid">
        <div v-for="item in cards" :key="item.title" class="metric-card" :class="item.type">
          <div class="metric-label">{{ item.title }}</div>
          <div class="metric-value">{{ item.value }}</div>
        </div>
      </section>

      <section class="board-grid">
        <div v-for="item in taskBoards" :key="item.title" class="board-card">
          <div class="board-title">{{ item.title }}</div>
          <div class="board-desc">{{ item.desc }}</div>
        </div>
      </section>

      <section class="panel-grid">
        <div class="panel-card">
          <div class="panel-title">低库存商品</div>
          <div v-if="warningRows.length" class="list-grid">
            <div v-for="row in warningRows" :key="row.id" class="list-item">
              <div>
                <div class="item-name">{{ row.name }}</div>
                <div class="item-meta">{{ row.product_code }} / 当前库存 {{ row.available_qty }}</div>
              </div>
              <NTag type="error" size="small">阈值 {{ row.low_stock_threshold }}</NTag>
            </div>
          </div>
          <div v-else class="empty-text">当前没有低库存商品</div>
        </div>

        <div class="panel-card">
          <div class="panel-title">最近库存流水</div>
          <div v-if="txnRows.length" class="list-grid">
            <div v-for="row in txnRows" :key="row.id" class="list-item">
              <div>
                <div class="item-name">{{ row.product_name || row.product_code }}</div>
                <div class="item-meta">{{ row.biz_no }} / {{ row.created_at }}</div>
              </div>
              <NTag :type="Number(row.change_qty) >= 0 ? 'success' : 'warning'" size="small">
                {{ Number(row.change_qty) >= 0 ? `+${row.change_qty}` : row.change_qty }}
              </NTag>
            </div>
          </div>
          <div v-else class="empty-text">暂无库存流水</div>
        </div>
      </section>
    </NSpin>
  </CommonPage>
</template>

<style scoped lang="scss">
.actions,
.card-grid,
.board-grid,
.panel-grid,
.list-grid {
  display: grid;
  gap: 12px;
}

.actions {
  display: flex;
}

.card-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 16px;
}

.metric-card,
.board-card,
.panel-card {
  border: 1px solid #e8eef6;
  border-radius: 12px;
  background: #fff;
}

.metric-card {
  padding: 14px 16px;
}

.metric-card.success {
  background: #f2fbf5;
}

.metric-card.danger {
  background: #fff2f0;
}

.metric-label,
.item-meta,
.board-desc {
  color: #6b7280;
  font-size: 13px;
}

.metric-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
}

.board-grid,
.panel-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 16px;
}

.board-card,
.panel-card {
  padding: 16px;
}

.board-title,
.panel-title,
.item-name {
  color: #111827;
  font-weight: 600;
}

.board-desc {
  margin-top: 10px;
  line-height: 1.7;
}

.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #eef2f7;
}

.list-item:last-child {
  border-bottom: none;
}

.empty-text {
  color: #9ca3af;
  font-size: 13px;
}
</style>
