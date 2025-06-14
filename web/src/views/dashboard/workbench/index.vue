<template>
  <AppPage>
    <div v-if="loading" class="flex-center h-full">
      <n-spin size="large" />
    </div>
    <div v-else>
      <n-card :bordered="false" size="large" class="mb-16px rounded-16px shadow-sm">
        <div class="flex items-center">
          <img :src="userStore.avatar" alt="avatar" class="h-64px w-64px rounded-full" />
          <div class="ml-12px">
            <h3 class="text-18px font-semibold">
              {{ welcomeMessage }}，{{ userStore.name }}
            </h3>
            <p class="text-12px text-gray-500">今天又是充满活力的一天！</p>
          </div>
        </div>
      </n-card>
      <component :is="currentView" :data="workbenchData" />
    </div>
  </AppPage>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/store';
import { getWorkbenchData } from '@/api/dashboard';
import AdminView from './components/AdminView.vue';
import UserView from './components/UserView.vue';

const userStore = useUserStore();
const loading = ref(true);
const workbenchData = ref(null);

const isAdmin = computed(() => userStore.isSuperUser);
const currentView = computed(() => (isAdmin.value ? AdminView : UserView));

const welcomeMessage = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return '凌晨好';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

onMounted(async () => {
  try {
    const { data } = await getWorkbenchData();
    workbenchData.value = data;
  } catch (error) {
    console.error('Failed to fetch workbench data:', error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped></style>