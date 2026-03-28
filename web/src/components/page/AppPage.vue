<template>
  <transition name="fade-slide" mode="out-in" appear>
    <section class="cus-scroll-y store-page-wrap wh-full flex-col p-15">
      <slot />
      <AppFooter v-if="showFooter" mt-15 />
      <n-back-top :bottom="20" />
    </section>
  </transition>
</template>

<script setup>
defineProps({
  showFooter: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped lang="scss">
.store-page-wrap {
  background: linear-gradient(180deg, #f3f8ea 0%, #f6f8f4 56%, #f7f8f4 100%);
}
</style>
