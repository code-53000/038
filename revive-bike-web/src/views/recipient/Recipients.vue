<template>
  <div class="recipients-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>受赠管理</span>
          <div class="filter-bar">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="已匹配" value="matched" />
              <el-option label="已领取" value="received" />
            </el-select>
            <el-button type="primary" @click="loadData">查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="recipients" v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="applicant_type" label="类型" width="120" />
        <el-table-column prop="organization" label="单位/学校" width="150" show-overflow-tooltip />
        <el-table-column prop="reason" label="申请理由" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
            </template>
            <el-button type="info" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="rejectDialogVisible" title="拒绝申请" width="500px">
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝理由">
          <el-input
            v-model="rejectForm.review_notes"
            type="textarea"
            :rows="3"
            placeholder="请输入拒绝理由"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="rejecting" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRecipientsApi, approveRecipientApi, rejectRecipientApi } from '@/api/recipient'
import dayjs from 'dayjs'

const loading = ref(false)
const recipients = ref([])
const statusFilter = ref('')
const rejectDialogVisible = ref(false)
const currentRecipient = ref(null)
const rejecting = ref(false)

const rejectForm = reactive({
  review_notes: ''
})

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
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await getRecipientsApi(params)
    recipients.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleApprove = async (row) => {
  ElMessageBox.confirm('确定要通过这个申请吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await approveRecipientApi(row.id)
      ElMessage.success('审核通过')
      loadData()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
}

const handleReject = (row) => {
  currentRecipient.value = row
  rejectForm.review_notes = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.review_notes) {
    ElMessage.warning('请输入拒绝理由')
    return
  }
  try {
    rejecting.value = true
    await rejectRecipientApi(currentRecipient.value.id, rejectForm.review_notes)
    ElMessage.success('已拒绝')
    rejectDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    rejecting.value = false
  }
}

const viewDetail = (row) => {
  // TODO: 详情弹窗
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

.filter-bar {
  display: flex;
  align-items: center;
}
</style>
