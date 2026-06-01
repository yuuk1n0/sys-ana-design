<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpin, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

defineOptions({ name: '课程总览' })

const router = useRouter()
const loading = ref(false)
const dashboard = ref({
  current_store: {},
  platform_metrics: {},
  phase_plan: [],
  phase_one_modules: [],
  phase_two_modules: [],
})

onMounted(loadDashboard)

async function loadDashboard() {
  loading.value = true
  try {
    const res = await api.getCourseDesignOverview()
    dashboard.value = res.data || dashboard.value
  } finally {
    loading.value = false
  }
}

const heroCards = computed(() => {
  const store = dashboard.value.current_store || {}
  const platform = dashboard.value.platform_metrics || {}
  return [
    { title: '当前门店', value: store.store_name || '-', type: 'neutral' },
    { title: '商品/分类', value: `${store.product_count || 0} / ${store.category_count || 0}`, type: 'success' },
    { title: '业务闭环', value: `${store.sales_order_count || 0} 单`, type: 'warning' },
    { title: '净销售额', value: `¥${Number(store.net_sales_amount || 0).toFixed(2)}`, type: 'danger' },
    { title: '平台账号', value: `${platform.user_count || 0} 人`, type: 'success' },
    { title: '日志记录', value: `${platform.audit_count || 0} 条`, type: 'neutral' },
  ]
})

function openModule(route) {
  if (!route) return
  router.push(route)
}
</script>

<template>
  <CommonPage show-footer title="课程设计总览">
    <NSpin :show="loading">
      <section class="hero-grid">
        <div
          v-for="item in heroCards"
          :key="item.title"
          class="hero-card"
          :class="item.type"
        >
          <div class="hero-label">{{ item.title }}</div>
          <div class="hero-value">{{ item.value }}</div>
        </div>
      </section>

      <section class="plan-board">
        <div class="section-title">开发阶段建议</div>
        <div class="plan-grid">
          <div v-for="item in dashboard.phase_plan" :key="item.stage" class="plan-item">
            <div class="plan-stage">{{ item.stage }}</div>
            <div class="plan-name">{{ item.name }}</div>
            <div class="plan-duration">{{ item.duration }}</div>
          </div>
        </div>
      </section>

      <section class="module-board">
        <div class="section-title">一期工程</div>
        <div class="module-grid">
          <div v-for="module in dashboard.phase_one_modules" :key="module.name" class="module-card">
            <div class="module-head">
              <div>
                <div class="module-name">{{ module.name }}</div>
                <div class="module-route">{{ module.route }}</div>
              </div>
              <NTag type="success" size="small">{{ module.status }}</NTag>
            </div>
            <div class="module-features">
              <div v-for="item in module.features" :key="item" class="feature-item">{{ item }}</div>
            </div>
            <NButton secondary type="primary" @click="openModule(module.route)">进入模块</NButton>
          </div>
        </div>
      </section>

      <section class="module-board">
        <div class="section-title">二期工程</div>
        <div class="module-grid">
          <div v-for="module in dashboard.phase_two_modules" :key="module.name" class="module-card">
            <div class="module-head">
              <div>
                <div class="module-name">{{ module.name }}</div>
                <div class="module-route">{{ module.route }}</div>
              </div>
              <NTag type="info" size="small">{{ module.status }}</NTag>
            </div>
            <div class="module-features">
              <div v-for="item in module.features" :key="item" class="feature-item">{{ item }}</div>
            </div>
            <NButton secondary type="primary" @click="openModule(module.route)">进入模块</NButton>
          </div>
        </div>
      </section>
    </NSpin>
  </CommonPage>
</template>

<style scoped lang="scss">
.hero-grid,
.plan-grid,
.module-grid {
  display: grid;
  gap: 12px;
}

.hero-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
  margin-bottom: 16px;
}

.hero-card,
.plan-item,
.module-card {
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e8eef6;
}

.hero-card {
  padding: 14px 16px;
}

.hero-card.success {
  background: #f2fbf5;
}

.hero-card.warning {
  background: #fff8ec;
}

.hero-card.danger {
  background: #fff2f0;
}

.hero-label,
.module-route,
.plan-stage {
  color: #7b8794;
  font-size: 13px;
}

.hero-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.section-title {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.plan-board,
.module-board {
  margin-bottom: 16px;
}

.plan-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.plan-item {
  padding: 14px 16px;
}

.plan-name {
  margin-top: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.plan-duration {
  margin-top: 6px;
  color: #2563eb;
  font-size: 13px;
}

.module-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.module-card {
  padding: 16px;
}

.module-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.module-name {
  font-size: 17px;
  font-weight: 600;
  color: #111827;
}

.module-features {
  margin: 14px 0 16px;
  display: grid;
  gap: 8px;
}

.feature-item {
  padding: 8px 10px;
  border-radius: 8px;
  background: #f8fafc;
  color: #374151;
  font-size: 13px;
}
</style>
