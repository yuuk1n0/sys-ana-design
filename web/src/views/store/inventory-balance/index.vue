<script setup>
import { h, onMounted, ref } from 'vue'
import { NInput, NSelect, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import api from '@/api'

defineOptions({ name: '库存余额' })

const $table = ref(null)
const queryItems = ref({})

onMounted(() => {
  $table.value?.handleSearch()
})

const stockStatusOptions = [
  { label: '有货', value: 1 },
  { label: '缺货', value: 0 },
]

const columns = [
  { title: '商品编码', key: 'product_code', width: 130, align: 'center' },
  { title: '商品名称', key: 'name', width: 160, align: 'center' },
  { title: '分类ID', key: 'category_id', width: 90, align: 'center' },
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
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getInventoryBalanceList"
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
      </template>
    </CrudTable>
  </CommonPage>
</template>
