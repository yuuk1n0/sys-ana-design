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

defineOptions({ name: '会员管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')
const tableRows = ref([])

const levelOptions = [
  { label: '普通会员', value: 'NORMAL' },
  { label: '银卡会员', value: 'SILVER' },
  { label: '金卡会员', value: 'GOLD' },
  { label: '钻石会员', value: 'DIAMOND' },
]

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
  name: '会员',
  initForm: { level: 'NORMAL', points: 0, status: true },
  doCreate: api.createMember,
  doUpdate: api.updateMember,
  doDelete: api.deleteMember,
  refresh: () => $table.value?.handleSearch(),
})

onMounted(() => {
  $table.value?.handleSearch()
})

function handleTableDataChange(rows) {
  tableRows.value = rows || []
}

function getLevelMeta(level) {
  const meta = {
    NORMAL: { label: '普通会员', type: 'default' },
    SILVER: { label: '银卡会员', type: 'info' },
    GOLD: { label: '金卡会员', type: 'warning' },
    DIAMOND: { label: '钻石会员', type: 'success' },
  }
  return meta[level] || { label: level || '-', type: 'default' }
}

const summaryCards = computed(() => {
  const rows = tableRows.value || []
  const activeCount = rows.filter((item) => item.status).length
  const highLevelCount = rows.filter((item) => ['GOLD', 'DIAMOND'].includes(item.level)).length
  const totalPoints = rows.reduce((sum, item) => sum + Number(item.points || 0), 0)
  return [
    { title: '会员总数', value: rows.length, type: 'neutral' },
    { title: '活跃会员', value: activeCount, type: 'success' },
    { title: '高等级会员', value: highLevelCount, type: 'warning' },
    { title: '累计积分', value: totalPoints, type: 'danger' },
  ]
})

const rules = {
  member_no: [{ required: true, message: '请输入会员编号', trigger: ['input', 'blur'] }],
  name: [{ required: true, message: '请输入会员姓名', trigger: ['input', 'blur'] }],
  level: [{ required: true, message: '请选择会员等级', trigger: ['change'] }],
  points: [{ required: true, type: 'number', message: '请输入会员积分', trigger: ['input', 'blur'] }],
}

const columns = [
  { title: '会员编号', key: 'member_no', width: 120, align: 'center' },
  { title: '会员姓名', key: 'name', width: 120, align: 'center' },
  { title: '手机号', key: 'phone', width: 130, align: 'center' },
  {
    title: '会员等级',
    key: 'level',
    width: 120,
    align: 'center',
    render(row) {
      const level = getLevelMeta(row.level)
      return h(NTag, { bordered: false, type: level.type }, { default: () => level.label })
    },
  },
  { title: '积分', key: 'points', width: 100, align: 'center' },
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
          [[vPermission, 'post/api/v1/member/update']]
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
                [[vPermission, 'delete/api/v1/member/delete']]
              ),
            default: () => h('div', {}, '确定删除该会员吗?'),
          }
        ),
      ]
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="会员管理">
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
      <NButton v-permission="'post/api/v1/member/create'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新增会员
      </NButton>
    </template>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getMemberList"
      @on-data-change="handleTableDataChange"
    >
      <template #queryBar>
        <QueryBarItem label="会员姓名" :label-width="70">
          <NInput
            v-model:value="queryItems.name"
            clearable
            placeholder="请输入会员姓名"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="会员编号" :label-width="70">
          <NInput
            v-model:value="queryItems.member_no"
            clearable
            placeholder="请输入会员编号"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="手机号" :label-width="60">
          <NInput
            v-model:value="queryItems.phone"
            clearable
            placeholder="请输入手机号"
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
        :label-width="90"
      >
        <NFormItem label="会员编号" path="member_no">
          <NInput v-model:value="modalForm.member_no" placeholder="请输入会员编号" />
        </NFormItem>
        <NFormItem label="会员姓名" path="name">
          <NInput v-model:value="modalForm.name" placeholder="请输入会员姓名" />
        </NFormItem>
        <NFormItem label="手机号" path="phone">
          <NInput v-model:value="modalForm.phone" placeholder="请输入手机号(可选)" />
        </NFormItem>
        <NFormItem label="会员等级" path="level">
          <NSelect v-model:value="modalForm.level" :options="levelOptions" placeholder="请选择会员等级" />
        </NFormItem>
        <NFormItem label="积分" path="points">
          <NInputNumber v-model:value="modalForm.points" :min="0" />
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

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.feature-card {
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

.feature-desc {
  margin-top: 8px;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.7;
}
</style>
