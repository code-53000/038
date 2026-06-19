<template>
  <div class="parts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>零件管理</span>
          <div class="action-bar">
            <el-input
              v-model="keyword"
              placeholder="搜索零件名称"
              style="width: 200px; margin-right: 10px;"
              clearable
              @input="loadData"
            />
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon>
              新增零件
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="parts" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="零件名称" width="150" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="stock_quantity" label="库存数量" width="120">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.stock_quantity < 10 }">
              {{ row.stock_quantity }} {{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑零件' : '新增零件'" width="500px">
      <el-form
        ref="partForm"
        :model="partForm"
        :rules="partRules"
        label-width="100px"
      >
        <el-form-item label="零件名称" prop="name">
          <el-input v-model="partForm.name" placeholder="请输入零件名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="partForm.category" placeholder="请选择分类" style="width: 100%;">
            <el-option label="轮胎" value="轮胎" />
            <el-option label="刹车系统" value="刹车系统" />
            <el-option label="传动系统" value="传动系统" />
            <el-option label="配件" value="配件" />
            <el-option label="养护" value="养护" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="SKU" prop="sku">
          <el-input v-model="partForm.sku" placeholder="请输入SKU编码" />
        </el-form-item>
        <el-form-item label="库存数量" prop="stock_quantity">
          <el-input-number v-model="partForm.stock_quantity" :min="0" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="partForm.unit" placeholder="请输入单位" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="partForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPartsApi, createPartApi, updatePartApi, deletePartApi } from '@/api/part'
import dayjs from 'dayjs'

const loading = ref(false)
const parts = ref([])
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentPart = ref(null)
const submitting = ref(false)

const partForm = reactive({
  name: '',
  category: '',
  sku: '',
  stock_quantity: 0,
  unit: '个',
  description: ''
})

const partRules = {
  name: [{ required: true, message: '请输入零件名称', trigger: 'blur' }]
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
    if (keyword.value) {
      params.keyword = keyword.value
    }
    const res = await getPartsApi(params)
    parts.value = res
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  currentPart.value = null
  Object.assign(partForm, {
    name: '',
    category: '',
    sku: '',
    stock_quantity: 0,
    unit: '个',
    description: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  currentPart.value = row
  Object.assign(partForm, {
    name: row.name,
    category: row.category,
    sku: row.sku,
    stock_quantity: row.stock_quantity,
    unit: row.unit,
    description: row.description
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await partFormRef.value.validate()
    submitting.value = true
    if (isEdit.value) {
      await updatePartApi(currentPart.value.id, partForm)
      ElMessage.success('更新成功')
    } else {
      await createPartApi(partForm)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除零件"${row.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deletePartApi(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {})
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

.low-stock {
  color: #f56c6c;
  font-weight: 600;
}
</style>
