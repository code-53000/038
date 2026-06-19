<template>
  <div class="my-applications">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的申请</span>
          <el-button type="primary" @click="$router.push('/recipient-apply')">
            <el-icon><Plus /></el-icon>
            新增申请
          </el-button>
        </div>
      </template>

      <el-table :data="applications" v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="applicant_type" label="类型" width="120" />
        <el-table-column prop="reason" label="申请理由" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecipientsApi } from '@/api/recipient'
import dayjs from 'dayjs'

const loading = ref(false)
const applications = ref([])

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    matched: 'primary',
    received: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    matched: '已匹配',
    received: '已领取'
  }
  return map[status] || status
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getRecipientsApi()
    applications.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
