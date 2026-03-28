<template>
  <AppPage :show-footer="showFooter">
    <header v-if="showHeader" class="store-page-header">
      <slot v-if="$slots.header" name="header" />
      <template v-else>
        <h2 class="store-page-title">{{ title || route.meta?.title }}</h2>
        <slot name="action" />
      </template>
    </header>

    <n-card class="store-page-card" flex-1>
      <slot />
    </n-card>
  </AppPage>
</template>

<script setup>
defineProps({
  showFooter: {
    type: Boolean,
    default: false,
  },
  showHeader: {
    type: Boolean,
    default: true,
  },
  title: {
    type: String,
    default: undefined,
  },
})
const route = useRoute()
</script>

<style scoped lang="scss">
.store-page-header {
  min-height: 46px;
  margin-bottom: 15px;
  padding: 0 2px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.store-page-title {
  margin: 0;
  color: #2f3a1f;
  font-size: 22px;
  font-weight: 500;
}

.store-page-card {
  border-radius: 12px;
  border: 1px solid #e9efdd;
  box-shadow: 0 6px 18px rgba(71, 93, 48, 0.06);
}
</style>
