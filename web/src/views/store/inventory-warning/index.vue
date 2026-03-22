<script setup>
import { h, onMounted, ref } from 'vue'
import { NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import api from '@/api'

defineOptions({ name: '库存预警' })

const $table = ref(null)
const queryItems = ref({})

onMounted(() => {
  $table.value?.handleSearch()
})

const columns = [
  { title: '商品编码', key: 'product_code', width: 130, align: 'center' },
  { title: '商品名称', key: 'name', width: 160, align: 'center' },
  { title: '分类ID', key: 'category_id', width: 90, align: 'center' },
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
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getInventoryWarningList"
    />
  </CommonPage>
</template>
