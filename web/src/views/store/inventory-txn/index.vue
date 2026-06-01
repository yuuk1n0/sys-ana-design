<script setup>
import {
  NButton,
  NDatePicker,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSelect,
  NTag,
} from 'naive-ui'
import { computed, h, onMounted, ref } from 'vue'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import api from '@/api'

defineOptions({ name: '库存流水' })

const $table = ref(null)
const queryItems = ref({})
const datetimeRange = ref(null)
const tableRows = ref([])
const operateModalVisible = ref(false)
const operateSaving = ref(false)
const operateType = ref('STOCK_IN')
const operateFormRef = ref(null)
const productOptions = ref([])
const operateForm = ref({
  remark: '',
  items: [{ product_id: null, qty: 1 }],
})

const operateRules = {
  items: {
    validator: () => {
      const items = operateForm.value.items || []
      if (!items.length) {
        return new Error('请至少添加一条作业明细')
      }
      const invalid = items.some((item) => !item.product_id || !Number(item.qty))
      if (invalid) {
        return new Error('请完整填写商品和数量')
      }
      return true
    },
    trigger: ['change', 'blur'],
  },
}

onMounted(async () => {
  await loadProducts()
  $table.value?.handleSearch()
})

const bizTypeOptions = [
  { label: '初始化', value: 'INIT' },
  { label: '采购入库', value: 'STOCK_IN' },
  { label: '业务出库', value: 'STOCK_OUT' },
  { label: '销售扣减', value: 'SALE' },
  { label: '退货回补', value: 'RETURN' },
  { label: '盘盈', value: 'STOCKTAKE_GAIN' },
  { label: '盘亏', value: 'STOCKTAKE_LOSS' },
  { label: '人工调整', value: 'MANUAL' },
]

const bizTypeMap = {
  INIT: { label: '初始化', type: 'info' },
  STOCK_IN: { label: '采购入库', type: 'success' },
  STOCK_OUT: { label: '业务出库', type: 'error' },
  SALE: { label: '销售扣减', type: 'warning' },
  RETURN: { label: '退货回补', type: 'success' },
  STOCKTAKE_GAIN: { label: '盘盈', type: 'success' },
  STOCKTAKE_LOSS: { label: '盘亏', type: 'error' },
  MANUAL: { label: '人工调整', type: 'default' },
}

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

async function loadProducts() {
  const res = await api.getProductList({ page: 1, page_size: 9999, status: 1 })
  productOptions.value = (res.data || []).map((item) => ({
    label: `${item.name} (${item.product_code})`,
    value: item.id,
  }))
}

function handleTableDataChange(rows) {
  tableRows.value = rows || []
}

function resetOperateForm() {
  operateForm.value = {
    remark: '',
    items: [{ product_id: null, qty: 1 }],
  }
}

function openOperateModal(type) {
  operateType.value = type
  resetOperateForm()
  operateModalVisible.value = true
}

function addOperateItem() {
  operateForm.value.items.push({ product_id: null, qty: 1 })
}

function removeOperateItem(index) {
  if (operateForm.value.items.length === 1) return
  operateForm.value.items.splice(index, 1)
}

function submitOperateForm() {
  operateFormRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      operateSaving.value = true
      await api.createInventoryOperation({
        biz_type: operateType.value,
        remark: operateForm.value.remark,
        items: operateForm.value.items,
      })
      $message.success(operateType.value === 'STOCK_IN' ? '入库登记成功' : '出库登记成功')
      operateModalVisible.value = false
      $table.value?.handleSearch()
    } finally {
      operateSaving.value = false
    }
  })
}

const summaryCards = computed(() => {
  const rows = tableRows.value || []
  const saleCount = rows.filter((item) => item.biz_type === 'SALE').length
  const stocktakeCount = rows.filter((item) => item.biz_type?.startsWith('STOCKTAKE')).length
  const positiveChange = rows
    .filter((item) => Number(item.change_qty) > 0)
    .reduce((sum, item) => sum + Number(item.change_qty || 0), 0)
  const negativeChange = rows
    .filter((item) => Number(item.change_qty) < 0)
    .reduce((sum, item) => sum + Math.abs(Number(item.change_qty || 0)), 0)
  return [
    { title: '流水条数', value: rows.length, type: 'neutral' },
    { title: '销售扣减', value: saleCount, type: 'warning' },
    { title: '盘点调整', value: stocktakeCount, type: 'success' },
    { title: '入库/回补', value: positiveChange, type: 'success' },
    { title: '出库/扣减', value: negativeChange, type: 'danger' },
  ]
})

const columns = [
  { title: '时间', key: 'created_at', width: 160, align: 'center' },
  { title: '商品编码', key: 'product_code', width: 120, align: 'center' },
  { title: '商品名称', key: 'product_name', width: 160, align: 'center' },
  {
    title: '业务类型',
    key: 'biz_type',
    width: 120,
    align: 'center',
    render(row) {
      const bizType = bizTypeMap[row.biz_type] || { label: row.biz_type || '-', type: 'default' }
      return h(NTag, { bordered: false, type: bizType.type }, { default: () => bizType.label })
    },
  },
  { title: '业务单号', key: 'biz_no', width: 140, align: 'center' },
  { title: '变更前', key: 'before_qty', width: 90, align: 'center' },
  {
    title: '变更量',
    key: 'change_qty',
    width: 90,
    align: 'center',
    render(row) {
      const qty = Number(row.change_qty || 0)
      const text = qty > 0 ? `+${qty}` : `${qty}`
      const color = qty > 0 ? '#18a058' : qty < 0 ? '#d03050' : '#666'
      return h('span', { style: { color, fontWeight: 600 } }, text)
    },
  },
  { title: '变更后', key: 'after_qty', width: 90, align: 'center' },
  { title: '操作人', key: 'operator_id', width: 90, align: 'center' },
]
</script>

<template>
  <CommonPage show-footer title="库存流水">
    <template #action>
      <div class="inventory-actions">
        <NButton v-permission="'post/api/v1/inventory/operate'" type="primary" @click="openOperateModal('STOCK_IN')">
          <TheIcon icon="material-symbols:add-box-outline" :size="18" class="mr-5" />入库登记
        </NButton>
        <NButton v-permission="'post/api/v1/inventory/operate'" type="warning" ghost @click="openOperateModal('STOCK_OUT')">
          <TheIcon icon="material-symbols:outbox-outline" :size="18" class="mr-5" />出库登记
        </NButton>
      </div>
    </template>
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
      :get-data="api.getInventoryTxnList"
      @on-data-change="handleTableDataChange"
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

    <CrudModal
      v-model:visible="operateModalVisible"
      :title="operateType === 'STOCK_IN' ? '入库登记' : '出库登记'"
      :loading="operateSaving"
      width="860px"
      @save="submitOperateForm"
    >
      <NForm
        ref="operateFormRef"
        :model="operateForm"
        :rules="operateRules"
        label-placement="left"
        :label-width="90"
      >
        <NFormItem label="备注" path="remark">
          <NInput v-model:value="operateForm.remark" type="textarea" placeholder="请输入备注(可选)" />
        </NFormItem>
        <NFormItem label="作业明细" path="items">
          <div class="operate-lines">
            <div
              v-for="(item, index) in operateForm.items"
              :key="index"
              class="operate-line"
            >
              <NSelect
                v-model:value="item.product_id"
                :options="productOptions"
                filterable
                placeholder="请选择商品"
              />
              <NInputNumber v-model:value="item.qty" :min="1" placeholder="数量" />
              <NButton quaternary type="error" :disabled="operateForm.items.length === 1" @click="removeOperateItem(index)">
                删除
              </NButton>
            </div>
            <NButton dashed type="primary" @click="addOperateItem">
              <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />添加商品
            </NButton>
          </div>
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped lang="scss">
.inventory-actions {
  display: flex;
  gap: 12px;
}

.store-summary {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
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
}

.store-summary-value {
  margin-top: 6px;
  color: #2f3a1f;
  font-size: 20px;
  font-weight: 600;
}

.store-summary-item.warning {
  background: #fff8ec;
  border-color: #f5e7c9;
}

.store-summary-item.danger {
  background: #fff2f0;
  border-color: #f6d9d2;
}

.store-summary-item.success {
  background: #f2fbf5;
  border-color: #deefe3;
}

.operate-lines {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.operate-line {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px 80px;
  gap: 10px;
  align-items: center;
}
</style>
