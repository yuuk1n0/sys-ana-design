<script setup>
import { computed, h, onMounted, ref } from 'vue'
import {
  NButton,
  NDataTable,
  NDatePicker,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSelect,
  NTabPane,
  NTabs,
  NTag,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { renderIcon } from '@/utils'
import api from '@/api'

defineOptions({ name: '销售管理' })

const $statementTable = ref(null)
const $orderTable = ref(null)
const statementQueryItems = ref({})
const orderQueryItems = ref({})
const statementDatetimeRange = ref(null)
const orderDatetimeRange = ref(null)
const orderModalVisible = ref(false)
const orderSaving = ref(false)
const orderMode = ref('SALE')
const orderFormRef = ref(null)
const orderDetailVisible = ref(false)
const orderDetail = ref({ lines: [] })
const productOptions = ref([])
const memberOptions = ref([])
const overview = ref({
  sale_amount: 0,
  return_amount: 0,
  net_sales_amount: 0,
  net_sales_qty: 0,
  txn_count: 0,
})
const orderForm = ref({
  member_id: null,
  remark: '',
  items: [{ product_id: null, qty: 1 }],
})

const salesFeatureBoards = [
  { title: '销售订单录入与管理', desc: '当前支持销售开单、业务单据查询和明细回看，满足门店销售台账管理。' },
  { title: '销售退货管理', desc: '退货录入与库存回补已经联通，可直接展示销售退货业务闭环。' },
  { title: '销售统计报表', desc: '销售统计页结合财务日报，输出销售额、退货额、净销量等经营指标。' },
  { title: '商品销售排行榜', desc: '已预留商品销售排行榜区，可基于销售流水继续扩展热销商品榜单。' },
]

const salesRankingPreview = [
  { name: '精品鸡蛋 30 枚装', sales: '2,480 件', note: '高频刚需' },
  { name: '巴氏鲜牛奶 950ml', sales: '2,160 件', note: '乳品热销' },
  { name: '东北大米 5kg', sales: '1,940 件', note: '粮油主力' },
]

const orderRules = {
  items: {
    validator: () => {
      const items = orderForm.value.items || []
      if (!items.length) {
        return new Error('请至少添加一条商品明细')
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
  await Promise.all([loadProducts(), loadMembers()])
  $orderTable.value?.handleSearch()
  $statementTable.value?.handleSearch()
})

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

function updateDateRange(queryItems, value) {
  if (!value || value.length !== 2) {
    queryItems.start_time = null
    queryItems.end_time = null
    return
  }
  queryItems.start_time = formatTimestamp(value[0])
  queryItems.end_time = formatTimestamp(value[1])
}

function handleStatementDateRangeChange(value) {
  updateDateRange(statementQueryItems.value, value)
}

function handleOrderDateRangeChange(value) {
  updateDateRange(orderQueryItems.value, value)
}

async function loadProducts() {
  const res = await api.getProductList({ page: 1, page_size: 9999, status: 1 })
  productOptions.value = (res.data || []).map((item) => ({
    label: `${item.name} (${item.product_code})`,
    value: item.id,
  }))
}

async function loadMembers() {
  const res = await api.getMemberList({ page: 1, page_size: 9999, status: 1 })
  memberOptions.value = (res.data || []).map((item) => ({
    label: `${item.name}${item.member_no ? ` (${item.member_no})` : ''}`,
    value: item.id,
  }))
}

async function fetchOverview(params = {}) {
  const res = await api.getFinanceOverview(params)
  overview.value = {
    sale_amount: Number(res.data?.sale_amount || 0),
    return_amount: Number(res.data?.return_amount || 0),
    net_sales_amount: Number(res.data?.net_sales_amount || 0),
    net_sales_qty: Number(res.data?.net_sales_qty || 0),
    txn_count: Number(res.data?.txn_count || 0),
  }
}

async function getStatementList(params = {}) {
  await fetchOverview(params)
  return api.getFinanceStatementList(params)
}

function getOrderList(params = {}) {
  return api.getSalesOrderList(params)
}

function resetOrderForm() {
  orderForm.value = {
    member_id: null,
    remark: '',
    items: [{ product_id: null, qty: 1 }],
  }
}

function openOrderModal(mode) {
  orderMode.value = mode
  resetOrderForm()
  orderModalVisible.value = true
}

function addOrderItem() {
  orderForm.value.items.push({ product_id: null, qty: 1 })
}

function removeOrderItem(index) {
  if (orderForm.value.items.length === 1) return
  orderForm.value.items.splice(index, 1)
}

async function submitOrder() {
  orderFormRef.value?.validate(async (errors) => {
    if (errors) return
    try {
      orderSaving.value = true
      const handler = orderMode.value === 'SALE' ? api.submitSaleOrder : api.submitReturnOrder
      await handler(orderForm.value)
      $message.success(orderMode.value === 'SALE' ? '销售单提交成功' : '退货单提交成功')
      orderModalVisible.value = false
      await Promise.all([$orderTable.value?.handleSearch(), $statementTable.value?.handleSearch()])
    } finally {
      orderSaving.value = false
    }
  })
}

async function showOrderDetail(row) {
  const res = await api.getSalesOrderDetail({ biz_no: row.biz_no })
  orderDetail.value = res.data || { lines: [] }
  orderDetailVisible.value = true
}

const summaryCards = computed(() => [
  { title: '销售总额', value: `¥${overview.value.sale_amount.toFixed(2)}`, type: 'success' },
  { title: '退货金额', value: `¥${overview.value.return_amount.toFixed(2)}`, type: 'warning' },
  { title: '净销售额', value: `¥${overview.value.net_sales_amount.toFixed(2)}`, type: 'danger' },
  { title: '净销售数量', value: overview.value.net_sales_qty, type: 'neutral' },
  { title: '业务笔数', value: overview.value.txn_count, type: 'neutral' },
])

const orderTypeOptions = [
  { label: '销售单', value: 'SALE' },
  { label: '退货单', value: 'RETURN' },
]

const orderTypeMap = {
  SALE: { label: '销售单', type: 'warning' },
  RETURN: { label: '退货单', type: 'success' },
}

const orderColumns = [
  { title: '单号', key: 'biz_no', width: 190, align: 'center' },
  {
    title: '类型',
    key: 'biz_type',
    width: 100,
    align: 'center',
    render(row) {
      const item = orderTypeMap[row.biz_type] || { label: row.biz_type || '-', type: 'default' }
      return h(NTag, { bordered: false, type: item.type }, { default: () => item.label })
    },
  },
  { title: '会员', key: 'member_name', width: 120, align: 'center' },
  { title: '商品摘要', key: 'line_summary', width: 220, align: 'center', ellipsis: { tooltip: true } },
  { title: '项数', key: 'item_count', width: 80, align: 'center' },
  { title: '总数量', key: 'total_qty', width: 90, align: 'center' },
  {
    title: '总金额',
    key: 'total_amount',
    width: 110,
    align: 'center',
    render(row) {
      return h('span', {}, `¥${Number(row.total_amount || 0).toFixed(2)}`)
    },
  },
  { title: '创建时间', key: 'created_at', width: 160, align: 'center' },
  {
    title: '操作',
    key: 'actions',
    width: 110,
    align: 'center',
    render(row) {
      return h(
        NButton,
        {
          size: 'small',
          type: 'primary',
          onClick: () => showOrderDetail(row),
        },
        {
          default: () => '查看明细',
          icon: renderIcon('material-symbols:visibility-outline', { size: 16 }),
        }
      )
    },
  },
]

const statementColumns = [
  { title: '日期', key: 'date', width: 140, align: 'center' },
  {
    title: '销售额',
    key: 'sale_amount',
    width: 120,
    align: 'center',
    render(row) {
      return h('span', {}, `¥${Number(row.sale_amount || 0).toFixed(2)}`)
    },
  },
  {
    title: '退货额',
    key: 'return_amount',
    width: 120,
    align: 'center',
    render(row) {
      return h('span', {}, `¥${Number(row.return_amount || 0).toFixed(2)}`)
    },
  },
  {
    title: '净销售额',
    key: 'net_sales_amount',
    width: 130,
    align: 'center',
    render(row) {
      return h(
        'span',
        { style: { fontWeight: 600, color: '#2f855a' } },
        `¥${Number(row.net_sales_amount || 0).toFixed(2)}`
      )
    },
  },
  { title: '净销售数量', key: 'net_sales_qty', width: 110, align: 'center' },
]

const detailColumns = [
  { title: '商品编码', key: 'product_code', width: 120, align: 'center' },
  { title: '商品名称', key: 'product_name', width: 160, align: 'center' },
  { title: '数量', key: 'qty', width: 80, align: 'center' },
  {
    title: '单价',
    key: 'unit_price',
    width: 100,
    align: 'center',
    render(row) {
      return h('span', {}, `¥${Number(row.unit_price || 0).toFixed(2)}`)
    },
  },
  {
    title: '金额',
    key: 'amount',
    width: 100,
    align: 'center',
    render(row) {
      return h('span', {}, `¥${Number(row.amount || 0).toFixed(2)}`)
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="销售管理">
    <template #action>
      <div class="sales-actions">
        <NButton
          v-permission="'post/api/v1/sale/submit'"
          type="primary"
          @click="openOrderModal('SALE')"
        >
          <TheIcon icon="material-symbols:point-of-sale-rounded" :size="18" class="mr-5" />销售开单
        </NButton>
        <NButton
          v-permission="'post/api/v1/sale/return'"
          type="warning"
          ghost
          @click="openOrderModal('RETURN')"
        >
          <TheIcon icon="material-symbols:assignment-return" :size="18" class="mr-5" />退货录入
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

    <section class="feature-grid">
      <div v-for="item in salesFeatureBoards" :key="item.title" class="feature-card">
        <div class="feature-title">{{ item.title }}</div>
        <div class="feature-desc">{{ item.desc }}</div>
      </div>
    </section>

    <section class="ranking-card">
      <div class="feature-title">商品销售排行榜</div>
      <div class="ranking-list">
        <div v-for="(item, index) in salesRankingPreview" :key="item.name" class="ranking-item">
          <div class="ranking-name">{{ index + 1 }}. {{ item.name }}</div>
          <div class="ranking-meta">{{ item.sales }} / {{ item.note }}</div>
        </div>
      </div>
    </section>

    <NTabs type="line" animated>
      <NTabPane name="orders" tab="业务单据">
        <CrudTable
          ref="$orderTable"
          v-model:query-items="orderQueryItems"
          :columns="orderColumns"
          :get-data="getOrderList"
        >
          <template #queryBar>
            <QueryBarItem label="单号" :label-width="40">
              <NInput
                v-model:value="orderQueryItems.biz_no"
                clearable
                placeholder="请输入业务单号"
                @keypress.enter="$orderTable?.handleSearch()"
              />
            </QueryBarItem>
            <QueryBarItem label="类型" :label-width="40">
              <NSelect
                v-model:value="orderQueryItems.biz_type"
                :options="orderTypeOptions"
                clearable
                placeholder="请选择类型"
                style="width: 160px"
              />
            </QueryBarItem>
            <QueryBarItem label="时间范围" :label-width="70">
              <NDatePicker
                v-model:value="orderDatetimeRange"
                type="datetimerange"
                clearable
                @update:value="handleOrderDateRangeChange"
              />
            </QueryBarItem>
          </template>
        </CrudTable>
      </NTabPane>

      <NTabPane name="statement" tab="销售统计">
        <CrudTable
          ref="$statementTable"
          v-model:query-items="statementQueryItems"
          :columns="statementColumns"
          :get-data="getStatementList"
        >
          <template #queryBar>
            <QueryBarItem label="统计时间" :label-width="70">
              <NDatePicker
                v-model:value="statementDatetimeRange"
                type="datetimerange"
                clearable
                @update:value="handleStatementDateRangeChange"
              />
            </QueryBarItem>
          </template>
        </CrudTable>
      </NTabPane>
    </NTabs>

    <CrudModal
      v-model:visible="orderModalVisible"
      :title="orderMode === 'SALE' ? '销售开单' : '退货录入'"
      :loading="orderSaving"
      width="860px"
      @save="submitOrder"
    >
      <NForm
        ref="orderFormRef"
        :model="orderForm"
        :rules="orderRules"
        label-placement="left"
        :label-width="90"
      >
        <NFormItem label="关联会员" path="member_id">
          <NSelect
            v-model:value="orderForm.member_id"
            :options="memberOptions"
            clearable
            filterable
            placeholder="可选，未选择则按散客处理"
          />
        </NFormItem>
        <NFormItem label="备注" path="remark">
          <NInput v-model:value="orderForm.remark" type="textarea" placeholder="请输入备注(可选)" />
        </NFormItem>
        <NFormItem label="商品明细" path="items">
          <div class="order-lines">
            <div
              v-for="(item, index) in orderForm.items"
              :key="index"
              class="order-line"
            >
              <NSelect
                v-model:value="item.product_id"
                :options="productOptions"
                filterable
                placeholder="请选择商品"
              />
              <NInputNumber v-model:value="item.qty" :min="1" placeholder="数量" />
              <NButton quaternary type="error" :disabled="orderForm.items.length === 1" @click="removeOrderItem(index)">
                删除
              </NButton>
            </div>
            <NButton dashed type="primary" @click="addOrderItem">
              <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />添加商品
            </NButton>
          </div>
        </NFormItem>
      </NForm>
    </CrudModal>

    <CrudModal
      v-model:visible="orderDetailVisible"
      title="单据详情"
      width="900px"
      :show-footer="false"
    >
      <div class="detail-meta">
        <div>单号：{{ orderDetail.biz_no || '-' }}</div>
        <div>类型：{{ orderTypeMap[orderDetail.biz_type]?.label || orderDetail.biz_type || '-' }}</div>
        <div>会员：{{ orderDetail.member_name || '-' }}</div>
        <div>总数量：{{ orderDetail.total_qty || 0 }}</div>
        <div>总金额：¥{{ Number(orderDetail.total_amount || 0).toFixed(2) }}</div>
        <div>备注：{{ orderDetail.remark || '-' }}</div>
      </div>
      <NDataTable :columns="detailColumns" :data="orderDetail.lines || []" :pagination="false" />
    </CrudModal>
  </CommonPage>
</template>

<style scoped lang="scss">
.sales-actions {
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

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.feature-card,
.ranking-card {
  border-radius: 10px;
  border: 1px solid #e8eef6;
  background: #fff;
  padding: 14px;
}

.feature-title {
  color: #111827;
  font-size: 15px;
  font-weight: 600;
}

.feature-desc,
.ranking-meta {
  margin-top: 8px;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.7;
}

.ranking-card {
  margin-bottom: 14px;
}

.ranking-list {
  display: grid;
  gap: 10px;
  margin-top: 10px;
}

.ranking-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid #eef2f7;
  padding-bottom: 10px;
}

.ranking-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.ranking-name {
  color: #111827;
  font-size: 14px;
}

.order-lines {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-line {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px 80px;
  gap: 10px;
  align-items: center;
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px 16px;
  margin-bottom: 16px;
  color: #4b5563;
}
</style>
