<template>
  <CommonPage show-footer>
    <template #action>
      <NButton type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
        {{ t('common.create') }}
      </NButton>
    </template>

    <CrudTable
      ref="crudTableRef"
      :columns="columns"
      :get-data="api.fetchOrders"
      :query-items="queryItems"
      :scroll-x="1200"
    >
      <template #queryBar>
        <QueryBarItem :label="t('views.order.order_number')" :content-style="{ width: '200px' }">
          <NInput
            v-model:value="queryItems.order_no"
            type="text"
            :placeholder="t('views.order.placeholder.order_number')"
            clearable
          />
        </QueryBarItem>
        <QueryBarItem :label="t('views.order.tracking_number')" :content-style="{ width: '200px' }">
          <NInput
            v-model:value="queryItems.tracking_no"
            type="text"
            :placeholder="t('views.order.placeholder.tracking_number')"
            clearable
          />
        </QueryBarItem>
        <QueryBarItem :label="t('views.order.item_name')" :content-style="{ width: '200px' }">
          <NInput
            v-model:value="queryItems.item_name"
            type="text"
            :placeholder="t('views.order.placeholder.item_name')"
            clearable
          />
        </QueryBarItem>
        <QueryBarItem :label="t('views.order.username')" :content-style="{ width: '200px' }">
          <NInput
            v-model:value="queryItems.username"
            type="text"
            :placeholder="t('views.order.placeholder.username')"
            clearable
          />
       </QueryBarItem>
       <QueryBarItem :label="t('views.order.items_received_status')" :content-style="{ width: '200px' }">
         <NSelect
           v-model:value="queryItems.items_received_status"
           :options="statusOptions"
           clearable
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
       label-placement="left"
       label-align="left"
       :label-width="80"
       :model="modalForm"
       :rules="orderFormRules"
     >
       <OrderForm :form="modalForm" />
     </NForm>
   </CrudModal>
 </CommonPage>
</template>

<script setup>
import { NButton, NInput, NForm, NSelect } from 'naive-ui'
import TheIcon from '@/components/icon/TheIcon.vue'
import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import OrderForm from './OrderForm.vue'
import { useCRUD } from '@/composables'
import api from '@/api'
import { computed, reactive, ref, h } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// const shippingFeeTitle = t('views.order.shipping_fee')
// const remarksTitle = t('views.order.remarks')
// const itemQuantityTitle = t('views.order.item_quantity')

const crudTableRef = ref(null)
const queryItems = reactive({
 order_no: '',
 tracking_no: '',
 item_name: '',
 username: '',
 items_received_status: 'all',
})

const statusOptions = computed(() => [
 { label: t('views.order.items_received_status_all'), value: 'all' },
 { label: t('views.order.items_received_status_received'), value: '1' },
 { label: t('views.order.items_received_status_not_received'), value: '0' },
])

const {
 modalVisible,
  modalAction,
  modalTitle,
  modalLoading,
  handleAdd,
  handleDelete,
  handleEdit,
  handleSave,
  modalForm,
  modalFormRef,
} = useCRUD({
  name: t('views.order.label_order'),
  initForm: { order_no: '', tracking_no: '', item_name: '', username: '', items_received: false, item_quantity: null, shipping_fee: 0, remarks: '' },
  doCreate: api.createOrder, // 确保 api.createOrder 已在 api/order.js 或 api/index.js 中定义和导出
  doDelete: api.deleteOrder, // 确保 api.deleteOrder 已定义和导出
  doUpdate: api.updateOrder, // 确保 api.updateOrder 已定义和导出
  refresh: () => crudTableRef.value?.refresh(),
})

const orderFormRules = {
  order_no: [{ required: true, message: t('views.order.placeholder.order_number_required'), trigger: ['input', 'blur'] }],
  tracking_no: [{ required: true, message: t('views.order.placeholder.tracking_number_required'), trigger: ['input', 'blur'] }],
  item_name: [{ required: true, message: t('views.order.placeholder.item_name_required'), trigger: ['input', 'blur'] }],
  username: [{ required: true, message: t('views.order.placeholder.username_required'), trigger: ['input', 'blur'] }],
  item_quantity: [
    { required: true, type: 'number', message: t('views.order.placeholder.item_quantity_required'), trigger: ['input', 'blur'] },
    { type: 'number', min: 1, message: t('views.order.placeholder.item_quantity_gt_zero'), trigger: ['input', 'blur'] },
  ],
  shipping_fee: [
    { type: 'number', min: 0, message: t('views.order.placeholder.shipping_fee_gte_zero'), trigger: ['input', 'blur'] },
  ],
  remarks: [
    { type: 'string', maxlength: 200, message: t('views.order.placeholder.remarks_max_length'), trigger: ['input', 'blur'] },
  ],
}

const columns = computed(() => [
  { type: 'selection', fixed: 'left' },
  {
    title: t('common.id'),
    key: 'id',
    width: 80,
    ellipsis: { tooltip: true },
  },
  {
    title: t('views.order.order_number'),
    key: 'order_no',
    width: 150,
    ellipsis: { tooltip: true },
  },
  {
    title: t('views.order.tracking_number'),
    key: 'tracking_no',
    width: 150,
    ellipsis: { tooltip: true },
  },
  {
    title: t('views.order.item_name'),
    key: 'item_name',
    width: 200,
    ellipsis: { tooltip: true },
  },
  {
    title: t('views.order.username'),
    key: 'username',
    width: 150,
    ellipsis: { tooltip: true },
  },
  {
    title: t('views.order.itemsReceived'),
    key: 'items_received',
    width: 100,
    align: 'center',
    render(row) {
      return row.items_received ? t('common.text.yes') : t('common.text.no')
    },
  },
  {
    title: '物品数量',
    key: 'item_quantity',
    width: 120,
    ellipsis: { tooltip: true },
  },
  {
    title: '运费',
    key: 'shipping_fee',
    width: 120,
    ellipsis: { tooltip: true },
  },
  {
    title: '备注',
    key: 'remarks',
    width: 200,
    ellipsis: { tooltip: true },
  },
  {
    title: t('common.created_at'),
    key: 'created_at',
    width: 180,
    render(row) {
      return new Date(row.created_at).toLocaleString()
    },
  },
  {
    title: t('common.updated_at'),
    key: 'updated_at',
    width: 180,
    render(row) {
      return new Date(row.updated_at).toLocaleString()
    },
  },
  {
    title: t('common.action'),
    key: 'action',
    width: 220,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            style: 'margin-right: 8px;',
            onClick: () => handleEdit(row),
          },
          { default: () => t('common.edit') }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'error',
            onClick: () => handleDelete(row.id),
          },
          { default: () => t('common.delete') }
        ),
      ]
    },
  },
])

// 添加一些缺失的翻译，确保在 setup 中调用以加载
t('common.create')
t('views.order.label_order')
t('views.order.placeholder.order_number')
t('views.order.placeholder.tracking_number')
t('views.order.placeholder.item_name')
t('views.order.placeholder.order_number_required')
t('views.order.placeholder.tracking_number_required')
t('views.order.placeholder.item_name_required')
t('views.order.placeholder.username')
t('views.order.placeholder.username_required')
t('views.order.placeholder.item_quantity_required')
t('views.order.placeholder.item_quantity_gt_zero')
t('views.order.placeholder.shipping_fee_gte_zero')
t('views.order.placeholder.remarks_max_length')
t('views.order.username')
t('views.order.itemsReceived')
t('common.text.yes') // 需要在国际化文件中添加 common.text.yes 和 common.text.no
t('common.text.no')
// t('views.order.item_quantity') // Column title is now hardcoded
// t('views.order.shipping_fee') // Column title is now hardcoded
// t('views.order.remarks') // Column title is now hardcoded
t('common.edit')
t('common.delete')
t('common.created_at')
t('common.updated_at')
t('common.action')
t('common.id')

</script>