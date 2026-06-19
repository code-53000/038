<template>
  <div class="pickups-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>回收管理</span>
          <div class="filter-bar">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="待接单" value="scheduled" />
              <el-option label="已接单" value="assigned" />
              <el-option label="已完成" value="completed" />
            </el-select>
            <el-button type="primary" @click="loadData">查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="pickups" v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="donation_id" label="捐赠编号" width="100" />
        <el-table-column prop="contact_name" label="联系人" width="120" />
        <el-table-column prop="contact_phone" label="联系电话" width="130" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column label="预约时间" width="180">
          <template #default="{ row }">
            {{ row.scheduled_date }} {{ row.scheduled_time || '' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'scheduled'"
              type="primary"
              link
              @click="handleAssign(row)"
            >
              接单
            </el-button>
            <el-button
              v-if="row.status === 'assigned'"
              type="success"
              link
              @click="openCompleteDialog(row)"
            >
              完成回收
            </el-button>
            <el-button type="info" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="completeDialogVisible" title="完成回收 - 登记车辆" width="600px">
      <el-form
        ref="bikeForm"
        :model="bikeForm"
        :rules="bikeRules"
        label-width="100px"
      >
        <el-form-item label="品牌">
          <el-input v-model="bikeForm.brand" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="型号">
          <el-input v-model="bikeForm.model" placeholder="请输入型号" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-input v-model="bikeForm.color" placeholder="请输入颜色" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="bikeForm.bike_type" placeholder="请选择类型" style="width: 100%;">
            <el-option label="城市车" value="城市车" />
            <el-option label="山地车" value="山地车" />
            <el-option label="公路车" value="公路车" />
            <el-option label="折叠车" value="折叠车" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input v-model="bikeForm.frame_size" placeholder="请输入车架尺寸" />
        </el-form-item>
        <el-form-item label="回收时车况">
          <el-input
            v-model="bikeForm.condition_on_receipt"
            type="textarea"
            :rows="3"
            placeholder="请描述回收时车辆状况"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="completeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="completing" @click="handleComplete">确认完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPickupsApi, assignPickupApi, completePickupApi } from '@/api/donation'

const loading = ref(false)
const pickups = ref([])
const statusFilter = ref('')
const completeDialogVisible = ref(false)
const currentPickup = ref(null)
const completing = ref(false)

const bikeForm = reactive({
  brand: '',
  model: '',
  color: '',
  bike_type: '',
  frame_size: '',
  condition_on_receipt: ''
})

const bikeRules = {
  condition_on_receipt: [{ required: true, message: '请输入回收时车况', trigger: 'blur' }]
}

const bikeFormRef = ref(null)

const getStatusType = (status) => {
  const map = {
    scheduled: 'warning',
    assigned: 'primary',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    scheduled: '待接单',
    assigned: '已接单',
    completed: '已完成'
  }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await getPickupsApi(params)
    pickups.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleAssign = async (row) => {
  ElMessageBox.confirm('确定要接这个回收单吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await assignPickupApi(row.id)
      ElMessage.success('接单成功')
      loadData()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
}

const openCompleteDialog = (row) => {
  currentPickup.value = row
  Object.assign(bikeForm, {
    brand: '',
    model: '',
    color: '',
    bike_type: '',
    frame_size: '',
    condition_on_receipt: ''
  })
  completeDialogVisible.value = true
}

const handleComplete = async () => {
  try {
    await bikeFormRef.value.validate()
    completing.value = true
    await completePickupApi(currentPickup.value.id, bikeForm)
    ElMessage.success('回收完成，车辆已登记')
    completeDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    completing.value = false
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
