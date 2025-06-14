<template>
  <div>
    <n-grid :x-gap="16" :y-gap="16" :cols="4">
      <n-gi v-for="item in cardData" :key="item.title">
        <n-card
          :bordered="false"
          class="cursor-pointer rounded-md"
          hoverable
          :style="{ background: item.bgColor }"
        >
          <div class="wh-full flex-col-center">
            <component :is="item.icon" :size="48" :color="item.color" />
            <p class="py-8px text-16px">{{ item.title }}</p>
            <p class="text-20px font-bold">{{ data[item.field] }}</p>
          </div>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup>
import { h } from 'vue';
import { useThemeVars } from 'naive-ui';
import { UserOutlined, TeamOutlined, MenuOutlined, ApiOutlined } from '@vicons/antd';

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});

const themeVars = useThemeVars();

const cardData = [
  {
    title: '用户数',
    field: 'user_count',
    icon: () => h(UserOutlined),
    color: themeVars.value.primaryColor,
    bgColor: '#f0faff',
  },
  {
    title: '角色数',
    field: 'role_count',
    icon: () => h(TeamOutlined),
    color: themeVars.value.infoColor,
    bgColor: '#f0faff',
  },
  {
    title: '菜单数',
    field: 'menu_count',
    icon: () => h(MenuOutlined),
    color: themeVars.value.successColor,
    bgColor: '#f0faff',
  },
  {
    title: '接口数',
    field: 'api_count',
    icon: () => h(ApiOutlined),
    color: themeVars.value.warningColor,
    bgColor: '#f0faff',
  },
];
</script>

<style scoped></style>