<script setup>
import { computed, h, onMounted, ref } from 'vue'
import { NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import api from '@/api'

defineOptions({ name: '库存预警' })

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
  const totalGap = rows.reduce((sum, item) => {
    const gap = Number(item.low_stock_threshold || 0) - Number(item.available_qty || 0)
    return sum + (gap > 0 ? gap : 0)
  }, 0)
  return [
    { title: '预警商品数', value: rows.length, type: 'warning' },
    { title: '待补货缺口', value: totalGap, type: 'danger' },
  ]
})

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
    title: '状态',
    key: 'is_low_stock',
    width: 120,
    align: 'center',
    render() {
      return h(NTag, { type: 'error' }, { default: () => '低库存' })
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="库存预警">
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
      :get-data="api.getInventoryWarningList"
      @on-data-change="handleTableDataChange"
    />
  </CommonPage>
</template>

<style scoped lang="scss">
.store-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.store-summary-item {
  border: 1px solid #f5e7c9;
  border-radius: 10px;
  background: #fff8ec;
  padding: 12px 14px;
}

.store-summary-item.danger {
  border-color: #f6d9d2;
  background: #fff2f0;
}

.store-summary-label {
  color: #8b7448;
  font-size: 13px;
  line-height: 1.4;
}

.store-summary-value {
  margin-top: 6px;
  color: #5c3d2e;
  font-size: 22px;
  font-weight: 600;
  line-height: 1;
}
</style>
