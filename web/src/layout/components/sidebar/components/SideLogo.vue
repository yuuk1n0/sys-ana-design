<template>
  <router-link class="store-side-logo" to="/">
    <icon-custom-logo text-34 color-primary></icon-custom-logo>
    <h2 v-show="!appStore.collapsed" class="store-side-logo-title">
      {{ title }}
    </h2>
  </router-link>
</template>

<script setup>
import { useAppStore } from '@/store'
const title = import.meta.env.VITE_TITLE

const appStore = useAppStore()
</script>

<style scoped lang="scss">
.store-side-logo {
  height: 60px;
  margin: 8px;
  border-radius: 10px;
  background: #eef5e2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.store-side-logo-title {
  margin-left: 8px;
  margin-right: 8px;
  max-width: 150px;
  flex-shrink: 0;
  color: #3f6e2a;
  font-size: 16px;
  font-weight: 700;
}
</style>
