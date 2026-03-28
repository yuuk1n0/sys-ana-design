<script setup>
import { computed, h, onMounted, ref } from 'vue'
import { NInput, NSelect, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import api from '@/api'

defineOptions({ name: '库存余额' })

const $table = ref(null)
const queryItems = ref({})
const categoryOptions = ref([])
const tableRows = ref([])

onMounted(async () => {
  await getCategories()
  $table.value?.handleSearch()
})

async function getCategories() {
  const res = await api.getProductCategoryList({ status: 1 })
  categoryOptions.value = (res.data || []).map((item) => ({ label: item.name, value: item.id }))
}

function getCategoryName(categoryId) {
  return categoryOptions.value.find((item) => item.value === categoryId)?.label || '-'
}

function handleTableDataChange(rows) {
  tableRows.value = rows || []
}

const summaryCards = computed(() => {
  const rows = tableRows.value || []
  const lowStockRows = rows.filter((item) => item.is_low_stock)
  const outOfStockRows = rows.filter((item) => !item.stock_status)
  const totalQty = rows.reduce((sum, item) => sum + Number(item.available_qty || 0), 0)
  return [
    { title: '在库SKU', value: rows.length, type: 'neutral' },
    { title: '低库存商品', value: lowStockRows.length, type: 'warning' },
    { title: '缺货商品', value: outOfStockRows.length, type: 'danger' },
    { title: '可用总库存', value: totalQty, type: 'success' },
  ]
})

const stockStatusOptions = [
  { label: '有货', value: 1 },
  { label: '缺货', value: 0 },
]

const columns = [
  { title: '商品编码', key: 'product_code', width: 130, align: 'center' },
  { title: '商品名称', key: 'name', width: 160, align: 'center' },
  {
    title: '商品分类',
    key: 'category_id',
    width: 120,
    align: 'center',
    render(row) {
      return h('span', {}, getCategoryName(row.category_id))
    },
  },
  { title: '可用库存', key: 'available_qty', width: 100, align: 'center' },
  { title: '预警阈值', key: 'low_stock_threshold', width: 100, align: 'center' },
  {
    title: '库存状态',
    key: 'stock_status',
    width: 100,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { type: row.stock_status ? 'success' : 'warning' },
        { default: () => (row.stock_status ? '有货' : '缺货') }
      )
    },
  },
  {
    title: '预警',
    key: 'is_low_stock',
    width: 80,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { type: row.is_low_stock ? 'error' : 'success' },
        { default: () => (row.is_low_stock ? '低库存' : '正常') }
      )
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="库存余额">
    <section class="store-summary">
      <div
        v-for="item in summaryCards"
        :key="item.title"
        class="store-summary-item"
        :class="item.type"
      >
        <div class="store-summary-label">{{ item.title }}</div>
        <div class="store-summary-value">{{ item.value }}</div>
      </div>
    </section>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getInventoryBalanceList"
      @on-data-change="handleTableDataChange"
    >
      <template #queryBar>
        <QueryBarItem label="商品名称" :label-width="70">
          <NInput
            v-model:value="queryItems.name"
            clearable
            placeholder="请输入商品名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="库存状态" :label-width="70">
          <NSelect
            v-model:value="queryItems.stock_status"
            :options="stockStatusOptions"
            clearable
            placeholder="请选择库存状态"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="商品分类" :label-width="70">
          <NSelect
            v-model:value="queryItems.category_id"
            :options="categoryOptions"
            clearable
            placeholder="请选择分类"
            style="width: 180px"
          />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template>

<style scoped lang="scss">
.store-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.store-summary-item {
  border: 1px solid #e9efdd;
  border-radius: 10px;
  background: #f8fbf2;
  padding: 12px 14px;
}

.store-summary-label {
  color: #7a8a72;
  font-size: 13px;
  line-height: 1.4;
}

.store-summary-value {
  margin-top: 6px;
  color: #2f3a1f;
  font-size: 22px;
  font-weight: 600;
  line-height: 1;
}

.store-summary-item.success {
  background: #f2fbf5;
  border-color: #deefe3;
}

.store-summary-item.warning {
  background: #fff8ec;
  border-color: #f5e7c9;
}

.store-summary-item.danger {
  background: #fff2f0;
  border-color: #f6d9d2;
}
</style>
