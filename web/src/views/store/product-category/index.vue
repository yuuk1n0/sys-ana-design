<script setup>
import { computed, h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NPopconfirm,
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

defineOptions({ name: '商品分类' })

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
  name: '分类',
  initForm: { sort: 0, status: true },
  doCreate: api.createProductCategory,
  doUpdate: api.updateProductCategory,
  doDelete: api.deleteProductCategory,
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
  const enabledCount = rows.filter((item) => item.status).length
  return [
    { title: '分类总数', value: rows.length, type: 'neutral' },
    { title: '启用分类', value: enabledCount, type: 'success' },
  ]
})

const rules = {
  name: [
    {
      required: true,
      message: '请输入分类名称',
      trigger: ['input', 'blur'],
    },
  ],
}

const columns = [
  { title: 'ID', key: 'id', width: 60, align: 'center' },
  { title: '分类名称', key: 'name', width: 200, align: 'center' },
  { title: '排序', key: 'sort', width: 120, align: 'center' },
  {
    title: '状态',
    key: 'status',
    width: 120,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { bordered: false, type: row.status ? 'success' : 'warning' },
        { default: () => (row.status ? '启用' : '停用') }
      )
    },
  },
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
          [[vPermission, 'post/api/v1/product-category/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ id: row.id }, false) },
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
                [[vPermission, 'delete/api/v1/product-category/delete']]
              ),
            default: () => h('div', {}, '确定删除该分类吗?'),
          }
        ),
      ]
    },
  },
]
</script>

<template>
  <CommonPage show-footer title="商品分类">
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
      <NButton
        v-permission="'post/api/v1/product-category/create'"
        type="primary"
        @click="handleAdd"
      >
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建分类
      </NButton>
    </template>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getProductCategoryList"
      :is-pagination="false"
      @on-data-change="handleTableDataChange"
    >
      <template #queryBar>
        <QueryBarItem label="分类名称" :label-width="70">
          <NInput
            v-model:value="queryItems.name"
            clearable
            placeholder="请输入分类名称"
            @keypress.enter="$table?.handleSearch()"
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
        :label-width="80"
      >
        <NFormItem label="分类名称" path="name">
          <NInput v-model:value="modalForm.name" placeholder="请输入分类名称" />
        </NFormItem>
        <NFormItem label="排序" path="sort">
          <NInputNumber v-model:value="modalForm.sort" :min="0" />
        </NFormItem>
        <NFormItem label="状态" path="status">
          <NSwitch v-model:value="modalForm.status" />
        </NFormItem>
      </NForm>
    </CrudModal>
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
</style>
