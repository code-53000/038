<template>
  <div class="my-donations">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的捐赠</span>
          <el-button type="primary" @click="$router.push('/donate')">
            <el-icon><Plus /></el-icon>
            新增捐赠
          </el-button>
        </div>
      </template>

      <el-table :data="donations" v-loading="loading" @row-click="goToDetail">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="viewTrace(row)">查看追溯</el-button>
            <el-button type="success" link @click.stop="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDonationsApi } from '@/api/donation'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const donations = ref([])

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    scheduled: 'warning',
    assigned: 'warning',
    received: 'primary',
    refurbishing: 'primary',
    refurbished: 'success',
    matched: 'success',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待预约',
    scheduled: '已预约',
    assigned: '已接单',
    received: '已回收',
    refurbishing: '翻新中',
    refurbished: '翻新完成',
    matched: '已匹配',
    completed: '已完成'
  }
  return map[status] || status
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDonationsApi()
    donations.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goToDetail = (row) => {
  router.push(`/trace/${row.id}`)
}

const viewTrace = (row) => {
  router.push(`/trace/${row.id}`)
}

const viewDetail = (row) => {
  router.push(`/trace/${row.id}`)
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
