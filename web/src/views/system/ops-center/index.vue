<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpin, NTag } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

defineOptions({ name: '运维中心' })

const router = useRouter()
const loading = ref(false)
const overview = ref({})
const audits = ref([])

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const [overviewRes, auditRes] = await Promise.all([
      api.getCourseDesignOverview(),
      api.getAuditLogList({ page: 1, page_size: 6 }),
    ])
    overview.value = overviewRes.data?.platform_metrics || {}
    audits.value = auditRes.data || []
  } finally {
    loading.value = false
  }
}

const cards = computed(() => [
  { title: '系统用户', value: overview.value.user_count || 0, type: 'success' },
  { title: '角色数量', value: overview.value.role_count || 0, type: 'success' },
  { title: '菜单数量', value: overview.value.menu_count || 0, type: 'neutral' },
  { title: '接口数量', value: overview.value.api_count || 0, type: 'warning' },
  { title: '日志记录', value: overview.value.audit_count || 0, type: 'danger' },
  { title: '门店数量', value: overview.value.dept_count || 0, type: 'neutral' },
])

const opsBoards = [
  {
    title: '用户权限管理',
    desc: '基于用户、角色、菜单、API 四层能力完成权限授权，适合课程演示 RBAC 设计。',
    path: '/system/role',
  },
  {
    title: '系统日志管理',
    desc: '审计日志已记录接口访问轨迹，可用于展示登录后操作留痕与系统安全能力。',
    path: '/system/auditlog',
  },
  {
    title: '数据备份与恢复',
    desc: '当前提供运维入口与流程说明，可在数据库脚本或对象存储方案基础上补充正式备份任务。',
    path: '/system/api',
  },
  {
    title: '系统基础设置与维护',
    desc: '可通过部门、菜单、接口等配置维护系统基础参数，并为后续升级维护保留入口。',
    path: '/system/menu',
  },
]

function openPage(path) {
  router.push(path)
}
</script>

<template>
  <CommonPage show-footer title="运维中心">
    <NSpin :show="loading">
      <section class="card-grid">
        <div v-for="item in cards" :key="item.title" class="metric-card" :class="item.type">
          <div class="metric-label">{{ item.title }}</div>
          <div class="metric-value">{{ item.value }}</div>
        </div>
      </section>

      <section class="board-grid">
        <div v-for="item in opsBoards" :key="item.title" class="board-card">
          <div class="board-head">
            <div class="board-title">{{ item.title }}</div>
            <NTag size="small" type="info">系统管理</NTag>
          </div>
          <div class="board-desc">{{ item.desc }}</div>
          <NButton class="mt-12" secondary type="primary" @click="openPage(item.path)">进入配置</NButton>
        </div>
      </section>

      <section class="audit-card">
        <div class="board-title">最近审计日志</div>
        <div v-if="audits.length" class="audit-grid">
          <div v-for="item in audits" :key="item.id" class="audit-item">
            <div>
              <div class="audit-summary">{{ item.summary || item.module || '系统操作' }}</div>
              <div class="audit-meta">{{ item.username || '-' }} / {{ item.path || '-' }}</div>
            </div>
            <NTag size="small" :type="item.method === 'GET' ? 'default' : 'warning'">{{ item.method }}</NTag>
          </div>
        </div>
        <div v-else class="empty-text">暂无审计日志</div>
      </section>
    </NSpin>
  </CommonPage>
</template>

<style scoped lang="scss">
.card-grid,
.board-grid {
  display: grid;
  gap: 12px;
}

.card-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
  margin-bottom: 16px;
}

.metric-card,
.board-card,
.audit-card {
  border: 1px solid #e8eef6;
  border-radius: 12px;
  background: #fff;
}

.metric-card {
  padding: 14px 16px;
}

.metric-card.success {
  background: #f2fbf5;
}

.metric-card.warning {
  background: #fff8ec;
}

.metric-card.danger {
  background: #fff2f0;
}

.metric-label,
.board-desc,
.audit-meta {
  color: #6b7280;
  font-size: 13px;
}

.metric-value {
  margin-top: 8px;
  font-size: 22px;
  font-weight: 600;
  color: #111827;
}

.board-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 16px;
}

.board-card,
.audit-card {
  padding: 16px;
}

.board-head,
.audit-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.board-title,
.audit-summary {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.board-desc {
  margin-top: 10px;
  line-height: 1.7;
}

.audit-grid {
  display: grid;
  gap: 12px;
  margin-top: 12px;
}

.audit-item {
  padding: 10px 0;
  border-bottom: 1px solid #eef2f7;
}

.audit-item:last-child {
  border-bottom: none;
}

.empty-text {
  margin-top: 12px;
  color: #9ca3af;
  font-size: 13px;
}
</style>
