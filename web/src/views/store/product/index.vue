<script setup>
import { computed, h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NPopconfirm,
  NSelect,
  NSwitch,
  NTag,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '商品管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')
const categoryOptions = ref([])
const tableRows = ref([])

const {
  modalVisible,
  modalTitle,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleAdd,
} = useCRUD({
  name: '商品',
  initForm: { status: true, stock_status: true, low_stock_threshold: 0 },
  doCreate: api.createProduct,
  doUpdate: api.updateProduct,
  doDelete: () => Promise.resolve(),
  refresh: () => $table.value?.handleSearch(),
})

onMounted(async () => {
  await getCategories()
  $table.value?.handleSearch()
})

async function getCategories() {
  const res = await api.getProductCategoryList({ status: 1 })
  categoryOptions.value = (res.data || []).map((item) => ({ label: item.name, value: item.id }))
}

async function handleToggleStatus(row) {
  await api.changeProductStatus({ id: row.id, status: !row.status })
  $message.success('状态更新成功')
  $table.value?.handleSearch()
}

function getCategoryName(categoryId) {
  return categoryOptions.value.find((item) => item.value === categoryId)?.label || '-'
}

const rules = {
  category_id: [{ required: true, message: '请选择分类', trigger: ['change'] }],
  product_code: [{ required: true, message: '请输入商品编码', trigger: ['input', 'blur'] }],
  name: [{ required: true, message: '请输入商品名称', trigger: ['input', 'blur'] }],
  unit: [{ required: true, message: '请输入单位', trigger: ['input', 'blur'] }],
  sale_price: [{ required: true, message: '请输入售价', trigger: ['input', 'blur'] }],
  low_stock_threshold: [{ required: true, message: '请输入预警阈值', trigger: ['input', 'blur'] }],
}

const summaryCards = computed(() => {
  const rows = tableRows.value || []
  const total = rows.length
  const onShelf = rows.filter((item) => item.status).length
  const lowStock = rows.filter((item) => item.is_low_stock).length
  const noStock = rows.filter((item) => !item.stock_status).length
  return [
    { title: '在管商品', value: total, type: 'neutral' },
    { title: '上架中', value: onShelf, type: 'success' },
    { title: '低库存', value: lowStock, type: 'warning' },
    { title: '缺货', value: noStock, type: 'danger' },
  ]
})

function handleTableDataChange(rows) {
  tableRows.value = rows || []
}

const columns = [
  { title: '编码', key: 'product_code', width: 120, align: 'center' },
  { title: '名称', key: 'name', width: 140, align: 'center' },
  {
    title: '分类',
    key: 'category_id',
    width: 120,
    align: 'center',
    render(row) {
      return h('span', {}, getCategoryName(row.category_id))
    },
  },
  { title: '单位', key: 'unit', width: 80, align: 'center' },
  {
    title: '售价',
    key: 'sale_price',
    width: 100,
    align: 'center',
    render(row) {
      return h('span', {}, `¥${Number(row.sale_price || 0).toFixed(2)}`)
    },
  },
  { title: '可用库存', key: 'available_qty', width: 100, align: 'center' },
  {
    title: '库存状态',
    key: 'stock_status',
    width: 100,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { bordered: false, type: row.stock_status ? 'success' : 'warning' },
        { default: () => (row.stock_status ? '有货' : '缺货') }
      )
    },
  },
  {
    title: '上架状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      return h(NTag, { bordered: false, type: row.status ? 'success' : 'default' }, () =>
        row.status ? '已上架' : '已下架'
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    align: 'center',
    render(row) {
      return [
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              style: 'margin-right: 8px;',
              onClick: () => handleEdit(row),
            },
            { default: () => '编辑', icon: renderIcon('material-symbols:edit', { size: 16 }) }
          ),
          [[vPermission, 'post/api/v1/product/update']]
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleToggleStatus(row),
          },
          {
            trigger: () =>
              withDirectives(
                h(
                  NButton,
                  { size: 'small', type: row.status ? 'warning' : 'success' },
                  { default: () => (row.status ? '下架' : '上架') }
                ),
                [[vPermission, 'post/api/v1/product/change_status']]
              ),
            default: () => h('div', {}, `确定${row.status ? '下架' : '上架'}该商品吗?`),
          }
        ),
      ]
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="商品管理">
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
    <template #action>
      <NButton v-permission="'post/api/v1/product/create'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建商品
      </NButton>
    </template>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getProductList"
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
        <QueryBarItem label="分类" :label-width="40">
          <NSelect
            v-model:value="queryItems.category_id"
            :options="categoryOptions"
            clearable
            placeholder="请选择分类"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="上架" :label-width="40">
          <NSelect
            v-model:value="queryItems.status"
            :options="[
              { label: '上架', value: 1 },
              { label: '下架', value: 0 },
            ]"
            clearable
            placeholder="请选择"
            style="width: 120px"
          />
        </QueryBarItem>
        <QueryBarItem label="库存" :label-width="40">
          <NSelect
            v-model:value="queryItems.stock_status"
            :options="[
              { label: '有货', value: 1 },
              { label: '缺货', value: 0 },
            ]"
            clearable
            placeholder="请选择"
            style="width: 120px"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NForm
        ref="modalFormRef"
        :model="modalForm"
        :rules="rules"
        label-placement="left"
        :label-width="90"
      >
        <NFormItem label="分类" path="category_id">
          <NSelect
            v-model:value="modalForm.category_id"
            :options="categoryOptions"
            placeholder="请选择分类"
          />
        </NFormItem>
        <NFormItem label="商品编码" path="product_code">
          <NInput v-model:value="modalForm.product_code" placeholder="请输入商品编码" />
        </NFormItem>
        <NFormItem label="商品名称" path="name">
          <NInput v-model:value="modalForm.name" placeholder="请输入商品名称" />
        </NFormItem>
        <NFormItem label="单位" path="unit">
          <NInput v-model:value="modalForm.unit" placeholder="例如: 件/瓶/盒" />
        </NFormItem>
        <NFormItem label="售价" path="sale_price">
          <NInputNumber v-model:value="modalForm.sale_price" :min="0" :precision="2" />
        </NFormItem>
        <NFormItem label="条码" path="barcode">
          <NInput v-model:value="modalForm.barcode" placeholder="请输入条码(可选)" />
        </NFormItem>
        <NFormItem label="预警阈值" path="low_stock_threshold">
          <NInputNumber v-model:value="modalForm.low_stock_threshold" :min="0" />
        </NFormItem>
        <NFormItem label="上架状态" path="status">
          <NSwitch v-model:value="modalForm.status" />
        </NFormItem>
        <NFormItem label="备注" path="remark">
          <NInput v-model:value="modalForm.remark" placeholder="请输入备注(可选)" />
        </NFormItem>
      </NForm>
    </CrudModal>
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
