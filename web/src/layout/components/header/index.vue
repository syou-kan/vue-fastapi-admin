<template>
  <div flex items-center>
    <MenuCollapse />
    <BreadCrumb ml-15 hidden sm:block />
  </div>
  <div ml-auto flex items-center>
    <div class="flex items-center h-full px-12">
      <n-button size="small" tertiary @click="contactSupportModalRef?.open()">
        {{ t('common.contactSupport') }}
      </n-button>
    </div>
    <Languages />
    <ThemeMode />
    <GithubSite />
    <FullScreen />
    <UserAvatar />
  </div>
  <ContactSupportModal ref="contactSupportModalRef" />
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { NButton } from 'naive-ui'
import BreadCrumb from './components/BreadCrumb.vue'
import MenuCollapse from './components/MenuCollapse.vue'
import FullScreen from './components/FullScreen.vue'
import UserAvatar from './components/UserAvatar.vue'
import GithubSite from './components/GithubSite.vue'
import ThemeMode from './components/ThemeMode.vue'
import Languages from './components/Languages.vue'
import ContactSupportModal from '@/components/common/ContactSupportModal.vue'

const { t } = useI18n()

const contactSupportModalRef = ref(null)
</script>
