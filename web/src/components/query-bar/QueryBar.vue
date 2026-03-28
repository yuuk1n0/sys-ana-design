<template>
  <div class="store-query-bar">
    <n-space wrap :size="[35, 15]">
      <slot />
      <div>
        <n-button secondary type="primary" @click="emit('reset')">重置</n-button>
        <n-button ml-20 type="primary" @click="emit('search')">搜索</n-button>
      </div>
    </n-space>
  </div>
</template>

<script setup>
const emit = defineEmits(['search', 'reset'])
</script>

<style scoped lang="scss">
.store-query-bar {
  min-height: 60px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border: 1px solid #e7edd7;
  border-radius: 10px;
  padding: 15px;
  background: #f8fbf2;
}
</style>
