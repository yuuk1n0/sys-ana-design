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

defineOptions({ name: '供应商管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')
const tableRows = ref([])

const {
  modalVisible,
  modalTitle,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '供应商',
  initForm: { settlement_cycle: 30, status: true },
  doCreate: api.createSupplier,
  doUpdate: api.updateSupplier,
  doDelete: api.deleteSupplier,
  refresh: () => $table.value?.handleSearch(),
})

onMounted(() => {
  $table.value?.handleSearch()
})

function handleTableDataChange(rows) {
  tableRows.value = rows || []
}

const summaryCards = computed(() => {
  const rows = tableRows.value || []
  const activeCount = rows.filter((item) => item.status).length
  const avgSettlement = rows.length
    ? Math.round(rows.reduce((sum, item) => sum + Number(item.settlement_cycle || 0), 0) / rows.length)
    : 0
  const hasContactCount = rows.filter((item) => item.contact_name || item.phone).length
  return [
    { title: '供应商总数', value: rows.length, type: 'neutral' },
    { title: '合作中', value: activeCount, type: 'success' },
    { title: '已建联系人', value: hasContactCount, type: 'warning' },
    { title: '平均账期(天)', value: avgSettlement, type: 'danger' },
  ]
})

const rules = {
  supplier_code: [{ required: true, message: '请输入供应商编码', trigger: ['input', 'blur'] }],
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: ['input', 'blur'] }],
  settlement_cycle: [{ required: true, type: 'number', message: '请输入结算周期', trigger: ['input', 'blur'] }],
}

const columns = [
  { title: '供应商编码', key: 'supplier_code', width: 130, align: 'center' },
  { title: '供应商名称', key: 'supplier_name', width: 180, align: 'center' },
  { title: '联系人', key: 'contact_name', width: 120, align: 'center' },
  { title: '联系电话', key: 'phone', width: 130, align: 'center' },
  { title: '结算周期', key: 'settlement_cycle', width: 110, align: 'center' },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      return h(NTag, { bordered: false, type: row.status ? 'success' : 'warning' }, () =>
        row.status ? '启用' : '停用'
      )
    },
  },
  { title: '地址', key: 'address', width: 180, align: 'center', ellipsis: { tooltip: true } },
  {
    title: '操作',
    key: 'actions',
    width: 180,
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
          [[vPermission, 'post/api/v1/supplier/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ id: row.id }) },
          {
            trigger: () =>
              withDirectives(
                h(
                  NButton,
                  { size: 'small', type: 'error' },
                  {
                    default: () => '删除',
                    icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
                  }
                ),
                [[vPermission, 'delete/api/v1/supplier/delete']]
              ),
            default: () => h('div', {}, '确定删除该供应商吗?'),
          }
        ),
      ]
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="供应商管理">
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
      <NButton v-permission="'post/api/v1/supplier/create'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新增供应商
      </NButton>
    </template>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getSupplierList"
      @on-data-change="handleTableDataChange"
    >
      <template #queryBar>
        <QueryBarItem label="供应商名称" :label-width="80">
          <NInput
            v-model:value="queryItems.supplier_name"
            clearable
            placeholder="请输入供应商名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="供应商编码" :label-width="80">
          <NInput
            v-model:value="queryItems.supplier_code"
            clearable
            placeholder="请输入供应商编码"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="40">
          <NSelect
            v-model:value="queryItems.status"
            :options="[
              { label: '启用', value: 1 },
              { label: '停用', value: 0 },
            ]"
            clearable
            placeholder="请选择状态"
            style="width: 140px"
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
        :label-width="100"
      >
        <NFormItem label="供应商编码" path="supplier_code">
          <NInput v-model:value="modalForm.supplier_code" placeholder="请输入供应商编码" />
        </NFormItem>
        <NFormItem label="供应商名称" path="supplier_name">
          <NInput v-model:value="modalForm.supplier_name" placeholder="请输入供应商名称" />
        </NFormItem>
        <NFormItem label="联系人" path="contact_name">
          <NInput v-model:value="modalForm.contact_name" placeholder="请输入联系人(可选)" />
        </NFormItem>
        <NFormItem label="联系电话" path="phone">
          <NInput v-model:value="modalForm.phone" placeholder="请输入联系电话(可选)" />
        </NFormItem>
        <NFormItem label="结算周期" path="settlement_cycle">
          <NInputNumber v-model:value="modalForm.settlement_cycle" :min="1" />
        </NFormItem>
        <NFormItem label="地址" path="address">
          <NInput v-model:value="modalForm.address" placeholder="请输入地址(可选)" />
        </NFormItem>
        <NFormItem label="状态" path="status">
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
