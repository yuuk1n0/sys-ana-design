<script setup>
import { NDatePicker, NInput, NSelect } from 'naive-ui'
import { onMounted, ref } from 'vue'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import api from '@/api'

defineOptions({ name: '库存流水' })

const $table = ref(null)
const queryItems = ref({})
const datetimeRange = ref(null)

onMounted(() => {
  $table.value?.handleSearch()
})

const bizTypeOptions = [
  { label: '初始化', value: 'INIT' },
  { label: '销售扣减', value: 'SALE' },
  { label: '退货回补', value: 'RETURN' },
  { label: '盘盈', value: 'STOCKTAKE_GAIN' },
  { label: '盘亏', value: 'STOCKTAKE_LOSS' },
  { label: '人工调整', value: 'MANUAL' },
]

function formatTimestamp(timestamp) {
  const date = new Date(timestamp)
  const pad = (num) => num.toString().padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  const seconds = pad(date.getSeconds())
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

function handleDateRangeChange(value) {
  if (!value || value.length !== 2) {
    queryItems.value.start_time = null
    queryItems.value.end_time = null
    return
  }
  queryItems.value.start_time = formatTimestamp(value[0])
  queryItems.value.end_time = formatTimestamp(value[1])
}

const columns = [
  { title: '时间', key: 'created_at', width: 160, align: 'center' },
  { title: '商品编码', key: 'product_code', width: 120, align: 'center' },
  { title: '商品名称', key: 'product_name', width: 160, align: 'center' },
  { title: '业务类型', key: 'biz_type', width: 120, align: 'center' },
  { title: '业务单号', key: 'biz_no', width: 140, align: 'center' },
  { title: '变更前', key: 'before_qty', width: 90, align: 'center' },
  { title: '变更量', key: 'change_qty', width: 90, align: 'center' },
  { title: '变更后', key: 'after_qty', width: 90, align: 'center' },
  { title: '操作人', key: 'operator_id', width: 90, align: 'center' },
]
</script>

<template>
  <CommonPage show-footer title="库存流水">
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getInventoryTxnList"
    >
      <template #queryBar>
        <QueryBarItem label="商品ID" :label-width="60">
          <NInput
            v-model:value="queryItems.product_id"
            clearable
            placeholder="请输入商品ID"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="业务类型" :label-width="70">
          <NSelect
            v-model:value="queryItems.biz_type"
            :options="bizTypeOptions"
            clearable
            placeholder="请选择业务类型"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="时间范围" :label-width="70">
          <NDatePicker
            v-model:value="datetimeRange"
            type="datetimerange"
            clearable
            @update:value="handleDateRangeChange"
          />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template>
