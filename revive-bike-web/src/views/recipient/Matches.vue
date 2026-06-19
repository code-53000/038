<template>
  <div class="matches-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>匹配管理</span>
          <div class="action-bar">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="已匹配" value="matched" />
              <el-option label="已交付" value="delivered" />
            </el-select>
            <el-button type="primary" @click="openMatchDialog">
              <el-icon><Plus /></el-icon>
              新建匹配
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="matches" v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column label="车辆信息" width="200">
          <template #default="{ row }">
            <div v-if="row.bike">
              <div>{{ row.bike.bike_code }}</div>
              <div style="color: #909399; font-size: 12px;">
                {{ row.bike.brand }} {{ row.bike.model }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="受赠人" width="150">
          <template #default="{ row }">
            <div v-if="row.recipient">
              <div>{{ row.recipient.full_name }}</div>
              <div style="color: #909399; font-size: 12px;">{{ row.recipient.phone }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'delivered' ? 'success' : 'primary'">
              {{ row.status === 'delivered' ? '已交付' : '已匹配' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="match_date" label="匹配时间" width="180">
          <template #default="{ row }">{{ formatDate(row.match_date) }}</template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'matched'"
              type="success"
              link
              @click="handleDeliver(row)"
            >
              确认交付
            </el-button>
            <el-button type="info" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="matchDialogVisible" title="新建匹配" width="600px">
      <el-form
        ref="matchForm"
        :model="matchForm"
        :rules="matchRules"
        label-width="100px"
      >
        <el-form-item label="选择车辆" prop="bike_id">
          <el-select
            v-model="matchForm.bike_id"
            placeholder="请选择可匹配的车辆"
            style="width: 100%;"
            filterable
          >
            <el-option
              v-for="bike in availableBikes"
              :key="bike.id"
              :label="`${bike.bike_code} - ${bike.brand || ''} ${bike.model || ''}`"
              :value="bike.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择受赠人" prop="recipient_id">
          <el-select
            v-model="matchForm.recipient_id"
            placeholder="请选择已审核通过的受赠人"
            style="width: 100%;"
            filterable
          >
            <el-option
              v-for="recipient in approvedRecipients"
              :key="recipient.id"
              :label="`${recipient.full_name} - ${recipient.applicant_type}`"
              :value="recipient.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="matchForm.notes"
            type="textarea"
            :rows="2"
            placeholder="备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="matchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateMatch">确认匹配</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMatchesApi, createMatchApi, deliverMatchApi, getRecipientsApi } from '@/api/recipient'
import { getBikesApi } from '@/api/refurbishment'
import dayjs from 'dayjs'

const loading = ref(false)
const matches = ref([])
const statusFilter = ref('')
const matchDialogVisible = ref(false)
const submitting = ref(false)

const availableBikes = ref([])
const approvedRecipients = ref([])

const matchForm = reactive({
  bike_id: null,
  recipient_id: null,
  notes: ''
})

const matchRules = {
  bike_id: [{ required: true, message: '请选择车辆', trigger: 'change' }],
  recipient_id: [{ required: true, message: '请选择受赠人', trigger: 'change' }]
}

const matchFormRef = ref(null)

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await getMatchesApi(params)
    matches.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadAvailableBikes = async () => {
  try {
    const res = await getBikesApi({ status: 'refurbished' })
    availableBikes.value = res
  } catch (e) {
    console.error(e)
  }
}

const loadApprovedRecipients = async () => {
  try {
    const res = await getRecipientsApi({ status: 'approved' })
    approvedRecipients.value = res
  } catch (e) {
    console.error(e)
  }
}

const openMatchDialog = () => {
  Object.assign(matchForm, {
    bike_id: null,
    recipient_id: null,
    notes: ''
  })
  loadAvailableBikes()
  loadApprovedRecipients()
  matchDialogVisible.value = true
}

const handleCreateMatch = async () => {
  try {
    await matchFormRef.value.validate()
    submitting.value = true
    await createMatchApi(matchForm)
    ElMessage.success('匹配成功')
    matchDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const handleDeliver = async (row) => {
  ElMessageBox.confirm('确定车辆已交付给受赠人了吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await deliverMatchApi(row.id)
      ElMessage.success('交付成功')
      loadData()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
}

const viewDetail = (row) => {
  // TODO: 详情
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

.action-bar {
  display: flex;
  align-items: center;
}
</style>
