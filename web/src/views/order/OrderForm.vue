<template>
  <NFormItem :label="t('views.order.order_number')" path="order_no">
    <NInput v-model:value="form.order_no" :placeholder="t('views.order.placeholder.order_number_required')" />
  </NFormItem>
  <NFormItem :label="t('views.order.tracking_number')" path="tracking_no">
    <NInput v-model:value="form.tracking_no" :placeholder="t('views.order.placeholder.tracking_number_required')" />
  </NFormItem>
  <NFormItem :label="t('views.order.item_name')" path="item_name">
    <NInput v-model:value="form.item_name" :placeholder="t('views.order.placeholder.item_name_required')" />
  </NFormItem>
  <NFormItem :label="t('views.order.username')" path="username">
    <NInput v-model:value="form.username" :placeholder="t('views.order.placeholder.username')" />
  </NFormItem>
  <NFormItem :label="t('views.order.itemsReceived')" path="items_received">
    <n-checkbox v-model:checked="form.items_received" />
  </NFormItem>
</template>

<script setup>
import { NFormItem, NInput, NCheckbox } from 'naive-ui'
import { useI18n } from 'vue-i18n'

defineProps({
  form: {
    type: Object,
    required: true,
  },
})

const { t } = useI18n()

// 确保翻译占位符被加载 (如果这些翻译仅在此组件的表单项中使用)
// 如果这些翻译也在 index.vue 中使用（例如用于rules），则在那里加载即可
t('views.order.order_number')
t('views.order.tracking_number')
t('views.order.item_name')
t('views.order.itemsReceived')
t('views.order.username')
t('views.order.placeholder.order_number_required')
t('views.order.placeholder.tracking_number_required')
t('views.order.placeholder.item_name_required')
t('views.order.placeholder.username')
t('views.order.placeholder.username_required')
</script>