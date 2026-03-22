<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import { NButton, NForm, NFormItem, NInput, NInputNumber, NPopconfirm, NSwitch } from 'naive-ui'

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
      return h(NSwitch, { value: row.status, disabled: true })
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
