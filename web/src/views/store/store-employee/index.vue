<script setup>
import { computed, h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import { NButton, NForm, NFormItem, NInput, NPopconfirm, NSelect, NSwitch, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '员工管理' })

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
  name: '员工',
  initForm: { status: true },
  doCreate: api.createStoreEmployee,
  doUpdate: api.updateStoreEmployee,
  doDelete: api.deleteStoreEmployee,
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
  const managerCount = rows.filter((item) => `${item.job_title || ''}`.includes('店长')).length
  const uniqueJobs = new Set(rows.map((item) => item.job_title).filter(Boolean)).size
  return [
    { title: '员工总数', value: rows.length, type: 'neutral' },
    { title: '在岗员工', value: activeCount, type: 'success' },
    { title: '店长/主管', value: managerCount, type: 'warning' },
    { title: '岗位类型', value: uniqueJobs, type: 'danger' },
  ]
})

const rules = {
  employee_no: [{ required: true, message: '请输入员工工号', trigger: ['input', 'blur'] }],
  name: [{ required: true, message: '请输入员工姓名', trigger: ['input', 'blur'] }],
  job_title: [{ required: true, message: '请输入岗位名称', trigger: ['input', 'blur'] }],
}

const columns = [
  { title: '员工工号', key: 'employee_no', width: 120, align: 'center' },
  { title: '员工姓名', key: 'name', width: 120, align: 'center' },
  { title: '手机号', key: 'phone', width: 130, align: 'center' },
  { title: '岗位', key: 'job_title', width: 120, align: 'center' },
  { title: '入职日期', key: 'hire_date', width: 120, align: 'center' },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      return h(NTag, { bordered: false, type: row.status ? 'success' : 'warning' }, () =>
        row.status ? '在岗' : '离岗'
      )
    },
  },
  { title: '备注', key: 'remark', width: 180, align: 'center', ellipsis: { tooltip: true } },
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
          [[vPermission, 'post/api/v1/store-employee/update']]
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
                [[vPermission, 'delete/api/v1/store-employee/delete']]
              ),
            default: () => h('div', {}, '确定删除该员工吗?'),
          }
        ),
      ]
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="员工管理">
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
      <NButton v-permission="'post/api/v1/store-employee/create'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新增员工
      </NButton>
    </template>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getStoreEmployeeList"
      @on-data-change="handleTableDataChange"
    >
      <template #queryBar>
        <QueryBarItem label="员工姓名" :label-width="70">
          <NInput
            v-model:value="queryItems.name"
            clearable
            placeholder="请输入员工姓名"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="员工工号" :label-width="70">
          <NInput
            v-model:value="queryItems.employee_no"
            clearable
            placeholder="请输入员工工号"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="岗位" :label-width="40">
          <NInput
            v-model:value="queryItems.job_title"
            clearable
            placeholder="请输入岗位"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="40">
          <NSelect
            v-model:value="queryItems.status"
            :options="[
              { label: '在岗', value: 1 },
              { label: '离岗', value: 0 },
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
        :label-width="90"
      >
        <NFormItem label="员工工号" path="employee_no">
          <NInput v-model:value="modalForm.employee_no" placeholder="请输入员工工号" />
        </NFormItem>
        <NFormItem label="员工姓名" path="name">
          <NInput v-model:value="modalForm.name" placeholder="请输入员工姓名" />
        </NFormItem>
        <NFormItem label="手机号" path="phone">
          <NInput v-model:value="modalForm.phone" placeholder="请输入手机号(可选)" />
        </NFormItem>
        <NFormItem label="岗位" path="job_title">
          <NInput v-model:value="modalForm.job_title" placeholder="请输入岗位，如店长/收银员" />
        </NFormItem>
        <NFormItem label="入职日期" path="hire_date">
          <NInput v-model:value="modalForm.hire_date" placeholder="请输入入职日期，例如 2026-05-28" />
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
