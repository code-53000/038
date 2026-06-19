<template>
  <div class="refurbishments-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>翻新工序</span>
          <div class="filter-bar">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
            <el-button type="primary" @click="loadData">查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="refurbishments" v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="bike_id" label="车辆ID" width="100" />
        <el-table-column prop="stage" label="工序" width="120" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
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
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'in_progress'"
              type="success"
              link
              @click="handleComplete(row)"
            >
              完成工序
            </el-button>
            <el-button type="primary" link @click="addPartUsage(row)">
              登记零件
            </el-button>
            <el-button type="info" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="partDialogVisible" title="登记零件使用" width="600px">
      <el-form
        ref="partForm"
        :model="partForm"
        :rules="partRules"
        label-width="100px"
      >
        <el-form-item label="零件" prop="part_id">
          <el-select
            v-model="partForm.part_id"
            placeholder="请选择零件"
            style="width: 100%;"
            filterable
            @change="onPartChange"
          >
            <el-option
              v-for="part in partsList"
              :key="part.id"
              :label="`${part.name} (库存: ${part.stock_quantity}${part.unit})`"
              :value="part.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="partForm.quantity" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="partForm.notes"
            type="textarea"
            :rows="2"
            placeholder="备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="partDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submittingPart" @click="handleAddPart">确认登记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getRefurbishmentsApi,
  completeRefurbishmentApi,
  createPartUsageApi
} from '@/api/refurbishment'
import { getPartsApi } from '@/api/part'
import dayjs from 'dayjs'

const loading = ref(false)
const refurbishments = ref([])
const statusFilter = ref('')
const partDialogVisible = ref(false)
const currentRefurbishment = ref(null)
const submittingPart = ref(false)

const partsList = ref([])

const partForm = reactive({
  part_id: null,
  quantity: 1,
  notes: ''
})

const partRules = {
  part_id: [{ required: true, message: '请选择零件', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const partFormRef = ref(null)

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
    const res = await getRefurbishmentsApi(params)
    refurbishments.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadParts = async () => {
  try {
    const res = await getPartsApi()
    partsList.value = res
  } catch (e) {
    console.error(e)
  }
}

const onPartChange = () => {
  // 可以在这里做一些逻辑
}

const handleComplete = async (row) => {
  ElMessageBox.confirm('确定要完成这个工序吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await completeRefurbishmentApi(row.id)
      ElMessage.success('工序已完成')
      loadData()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
}

const addPartUsage = (row) => {
  currentRefurbishment.value = row
  Object.assign(partForm, {
    part_id: null,
    quantity: 1,
    notes: ''
  })
  partDialogVisible.value = true
}

const handleAddPart = async () => {
  try {
    await partFormRef.value.validate()
    submittingPart.value = true
    await createPartUsageApi({
      part_id: partForm.part_id,
      bike_id: currentRefurbishment.value.bike_id,
      refurbishment_id: currentRefurbishment.value.id,
      quantity: partForm.quantity,
      notes: partForm.notes
    })
    ElMessage.success('零件使用已登记')
    partDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    submittingPart.value = false
  }
}

const viewDetail = (row) => {
  // TODO: 详情
}

onMounted(() => {
  loadData()
  loadParts()
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
