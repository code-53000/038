<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #ecf5ff;">
              <el-icon size="28" color="#409eff"><Present /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalDonations }}</div>
              <div class="stat-label">总捐赠数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f0f9eb;">
              <el-icon size="28" color="#67c23a"><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.refurbishing }}</div>
              <div class="stat-label">翻新中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #fdf6ec;">
              <el-icon size="28" color="#e6a23c"><Bicycle /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.availableBikes }}</div>
              <div class="stat-label">可捐赠车辆</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #fef0f0;">
              <el-icon size="28" color="#f56c6c"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingRecipients }}</div>
              <div class="stat-label">待审核申请</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近捐赠</span>
              <el-button type="primary" link @click="$router.push('/my-donations')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentDonations" v-loading="loading">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近翻新</span>
              <el-button type="primary" link @click="$router.push('/refurbishments')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentRefurbishments" v-loading="loading">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="stage" label="工序" width="120" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
                  {{ row.status === 'completed' ? '已完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="$router.push('/donate')">
              <el-icon size="32" color="#409eff"><Present /></el-icon>
              <span>我要捐赠</span>
            </div>
            <div class="action-item" @click="$router.push('/my-donations')">
              <el-icon size="32" color="#67c23a"><List /></el-icon>
              <span>我的捐赠</span>
            </div>
            <div class="action-item" v-if="isVolunteerOrAdmin" @click="$router.push('/pickups')">
              <el-icon size="32" color="#e6a23c"><Van /></el-icon>
              <span>回收管理</span>
            </div>
            <div class="action-item" v-if="isVolunteerOrAdmin" @click="$router.push('/refurbishments')">
              <el-icon size="32" color="#f56c6c"><Tools /></el-icon>
              <span>翻新工序</span>
            </div>
            <div class="action-item" @click="$router.push('/recipient-apply')">
              <el-icon size="32" color="#909399"><Postcard /></el-icon>
              <span>申请受赠</span>
            </div>
            <div class="action-item" v-if="isVolunteerOrAdmin" @click="$router.push('/matches')">
              <el-icon size="32" color="#8e44ad"><Connection /></el-icon>
              <span>匹配管理</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getDonationsApi } from '@/api/donation'
import { getRefurbishmentsApi } from '@/api/refurbishment'
import { getRecipientsApi } from '@/api/recipient'
import { getBikesApi } from '@/api/refurbishment'
import dayjs from 'dayjs'

const userStore = useUserStore()

const loading = ref(false)
const recentDonations = ref([])
const recentRefurbishments = ref([])

const stats = reactive({
  totalDonations: 0,
  refurbishing: 0,
  availableBikes: 0,
  pendingRecipients: 0
})

const isVolunteerOrAdmin = computed(() => {
  return ['volunteer', 'admin'].includes(userStore.role)
})

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
    const [donations, refurbishments, bikes, recipients] = await Promise.all([
      getDonationsApi({ limit: 5 }),
      getRefurbishmentsApi({ limit: 5 }),
      getBikesApi(),
      getRecipientsApi({ status: 'pending' })
    ])
    recentDonations.value = donations
    recentRefurbishments.value = refurbishments
    stats.totalDonations = donations.length
    stats.refurbishing = refurbishments.filter(r => r.status === 'in_progress').length
    stats.availableBikes = bikes.filter(b => b.status === 'refurbished').length
    stats.pendingRecipients = recipients.length
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
.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.mt-20 {
  margin-top: 20px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.action-item {
  width: 140px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: #ecf5ff;
  transform: translateY(-2px);
}

.action-item span {
  font-size: 14px;
  color: #606266;
}
</style>
