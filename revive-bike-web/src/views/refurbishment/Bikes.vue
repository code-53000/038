<template>
  <div class="bikes-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>车辆管理</span>
          <div class="filter-bar">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="已回收" value="donated" />
              <el-option label="翻新中" value="refurbishing" />
              <el-option label="翻新完成" value="refurbished" />
              <el-option label="已匹配" value="matched" />
              <el-option label="已捐赠" value="donated_completed" />
            </el-select>
            <el-button type="primary" @click="loadData">查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="bikes" v-loading="loading">
        <el-table-column prop="bike_code" label="车辆编号" width="150" />
        <el-table-column prop="brand" label="品牌" width="120" />
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="color" label="颜色" width="100" />
        <el-table-column prop="bike_type" label="类型" width="100" />
        <el-table-column prop="frame_size" label="尺寸" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="received_at" label="回收时间" width="180">
          <template #default="{ row }">{{ formatDate(row.received_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="startRefurbishment(row)">开始翻新</el-button>
            <el-button type="info" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="refurbishDialogVisible" title="开始翻新工序" width="500px">
      <el-form
        ref="refurbishForm"
        :model="refurbishForm"
        :rules="refurbishRules"
        label-width="100px"
      >
        <el-form-item label="工序">
          <el-select v-model="refurbishForm.stage" placeholder="请选择工序" style="width: 100%;">
            <el-option label="清洁除锈" value="清洁除锈" />
            <el-option label="轮胎更换" value="轮胎更换" />
            <el-option label="刹车系统检修" value="刹车系统检修" />
            <el-option label="传动系统检修" value="传动系统检修" />
            <el-option label="整车调试" value="整车调试" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="refurbishForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工序描述"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="refurbishForm.notes"
            type="textarea"
            :rows="2"
            placeholder="备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="refurbishDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleStartRefurbishment">确认开始</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getBikesApi, createRefurbishmentApi } from '@/api/refurbishment'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const bikes = ref([])
const statusFilter = ref('')
const refurbishDialogVisible = ref(false)
const currentBike = ref(null)
const submitting = ref(false)

const refurbishForm = reactive({
  stage: '',
  description: '',
  notes: ''
})

const refurbishRules = {
  stage: [{ required: true, message: '请选择工序', trigger: 'change' }]
}

const refurbishFormRef = ref(null)

const getStatusType = (status) => {
  const map = {
    donated: 'info',
    refurbishing: 'warning',
    refurbished: 'success',
    matched: 'primary',
    donated_completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    donated: '已回收',
    refurbishing: '翻新中',
    refurbished: '翻新完成',
    matched: '已匹配',
    donated_completed: '已捐赠完成'
  }
  return map[status] || status
}

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
    const res = await getBikesApi(params)
    bikes.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const startRefurbishment = (row) => {
  currentBike.value = row
  Object.assign(refurbishForm, {
    stage: '',
    description: '',
    notes: ''
  })
  refurbishDialogVisible.value = true
}

const handleStartRefurbishment = async () => {
  try {
    await refurbishFormRef.value.validate()
    submitting.value = true
    await createRefurbishmentApi({
      bike_id: currentBike.value.id,
      stage: refurbishForm.stage,
      description: refurbishForm.description,
      notes: refurbishForm.notes
    })
    ElMessage.success('翻新工序已开始')
    refurbishDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const viewDetail = (row) => {
  // TODO: 详情
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

.filter-bar {
  display: flex;
  align-items: center;
}
</style>
