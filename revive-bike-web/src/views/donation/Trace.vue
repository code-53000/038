<template>
  <div class="trace-page">
    <el-card v-if="traceData.donation">
      <template #header>
        <div class="card-header">
          <span>捐赠追溯 - 编号 #{{ traceData.donation.id }}</span>
          <el-tag :type="getStatusType(traceData.donation.status)" size="large">
            {{ getStatusText(traceData.donation.status) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="捐赠编号">{{ traceData.donation.id }}</el-descriptions-item>
        <el-descriptions-item label="捐赠时间">{{ formatDate(traceData.donation.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="车辆描述" :span="2">{{ traceData.donation.description }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>流转时间线</el-divider>

      <el-timeline>
        <el-timeline-item
          v-for="(item, index) in timelineItems"
          :key="index"
          :timestamp="formatDate(item.created_at)"
          :type="item.type"
          placement="top"
        >
          <el-card shadow="hover">
            <h4>{{ item.title }}</h4>
            <p>{{ item.description }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-divider v-if="traceData.bike">车辆信息</el-divider>

      <el-descriptions v-if="traceData.bike" :column="2" border>
        <el-descriptions-item label="车辆编号">{{ traceData.bike.bike_code }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ traceData.bike.brand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="型号">{{ traceData.bike.model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="颜色">{{ traceData.bike.color || '-' }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ traceData.bike.bike_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="尺寸">{{ traceData.bike.frame_size || '-' }}</el-descriptions-item>
        <el-descriptions-item label="回收时车况" :span="2">{{ traceData.bike.condition_on_receipt || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider v-if="traceData.pickup">回收信息</el-divider>

      <el-descriptions v-if="traceData.pickup" :column="2" border>
        <el-descriptions-item label="回收地址">{{ traceData.pickup.address }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ traceData.pickup.contact_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ traceData.pickup.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="预约时间">{{ traceData.pickup.scheduled_date }} {{ traceData.pickup.scheduled_time || '' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider v-if="traceData.refurbishments.length > 0">翻新工序</el-divider>

      <el-table v-if="traceData.refurbishments.length > 0" :data="traceData.refurbishments" border>
        <el-table-column prop="stage" label="工序" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="labor_hours" label="工时(小时)" width="120" />
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">{{ formatDate(row.started_at) }}</template>
        </el-table-column>
      </el-table>

      <el-divider v-if="traceData.part_usages.length > 0">零件消耗</el-divider>

      <el-table v-if="traceData.part_usages.length > 0" :data="traceData.part_usages" border>
        <el-table-column prop="part.name" label="零件名称" width="200" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="part.unit" label="单位" width="80" />
        <el-table-column prop="notes" label="备注" />
        <el-table-column prop="used_at" label="使用时间" width="180">
          <template #default="{ row }">{{ formatDate(row.used_at) }}</template>
        </el-table-column>
      </el-table>

      <el-divider v-if="traceData.match">受赠信息</el-divider>

      <el-descriptions v-if="traceData.match" :column="2" border>
        <el-descriptions-item label="受赠人">{{ traceData.match.recipient?.full_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ traceData.match.recipient?.phone }}</el-descriptions-item>
        <el-descriptions-item label="申请人类型">{{ getApplicantTypeText(traceData.match.recipient?.applicant_type) }}</el-descriptions-item>
        <el-descriptions-item label="匹配时间">{{ formatDate(traceData.match.match_date) }}</el-descriptions-item>
        <el-descriptions-item label="申请原因" :span="2">{{ traceData.match.recipient?.reason }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-empty v-else description="加载中..." />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { traceDonationApi } from '@/api/donation'
import dayjs from 'dayjs'

const route = useRoute()

const loading = ref(false)
const traceData = ref({
  donation: null,
  donation_history: [],
  bike: null,
  pickup: null,
  refurbishments: [],
  part_usages: [],
  match: null
})

const timelineItems = computed(() => {
  const items = []
  const history = traceData.value.donation_history || []
  const typeMap = {
    pending: 'primary',
    scheduled: 'warning',
    assigned: 'warning',
    received: 'primary',
    refurbishing: 'primary',
    refurbished: 'success',
    matched: 'success',
    completed: 'success'
  }

  history.forEach(item => {
    items.push({
      title: getStatusText(item.status),
      description: item.description,
      created_at: item.created_at,
      type: typeMap[item.status] || 'primary'
    })
  })

  return items
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

const getApplicantTypeText = (type) => {
  const map = {
    student: '学生',
    '外来务工人员': '外来务工人员'
  }
  return map[type] || type
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await traceDonationApi(route.params.id)
    traceData.value = res
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
.trace-page {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #303133;
}

p {
  margin: 0;
  color: #606266;
  font-size: 13px;
}
</style>
