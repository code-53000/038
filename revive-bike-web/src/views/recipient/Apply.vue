<template>
  <div class="apply-page">
    <el-card class="apply-card">
      <template #header>
        <div class="card-header">
          <h3>申请受赠自行车</h3>
          <p>请如实填写您的信息，我们会尽快审核</p>
        </div>
      </template>

      <el-form
        ref="applyForm"
        :model="applyForm"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="applyForm.full_name" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="applyForm.phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="applyForm.id_card" placeholder="请输入身份证号" />
        </el-form-item>

        <el-form-item label="居住地址" prop="address">
          <el-input v-model="applyForm.address" placeholder="请输入详细地址" />
        </el-form-item>

        <el-form-item label="申请人类型" prop="applicant_type">
          <el-radio-group v-model="applyForm.applicant_type">
            <el-radio value="学生">学生</el-radio>
            <el-radio value="外来务工人员">外来务工人员</el-radio>
            <el-radio value="困难家庭">困难家庭</el-radio>
            <el-radio value="其他">其他</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="所属单位/学校" prop="organization">
          <el-input v-model="applyForm.organization" placeholder="请输入单位或学校名称" />
        </el-form-item>

        <el-form-item label="申请理由" prop="reason">
          <el-input
            v-model="applyForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您的情况和申请理由"
          />
        </el-form-item>

        <el-form-item label="车辆类型偏好">
          <el-select v-model="applyForm.bike_type_preference" placeholder="请选择" style="width: 100%;">
            <el-option label="城市车" value="城市车" />
            <el-option label="山地车" value="山地车" />
            <el-option label="折叠车" value="折叠车" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>

        <el-form-item label="车架尺寸偏好">
          <el-select v-model="applyForm.frame_size_preference" placeholder="请选择" style="width: 100%;">
            <el-option label="20寸" value="20寸" />
            <el-option label="24寸" value="24寸" />
            <el-option label="26寸" value="26寸" />
            <el-option label="28寸" value="28寸" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
            提交申请
          </el-button>
          <el-button size="large" @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createRecipientApi } from '@/api/recipient'

const router = useRouter()

const applyForm = reactive({
  full_name: '',
  phone: '',
  id_card: '',
  address: '',
  applicant_type: '',
  organization: '',
  reason: '',
  bike_type_preference: '',
  frame_size_preference: ''
})

const rules = {
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  applicant_type: [{ required: true, message: '请选择申请人类型', trigger: 'change' }],
  reason: [{ required: true, message: '请输入申请理由', trigger: 'blur' }]
}

const applyFormRef = ref(null)
const loading = ref(false)

const handleSubmit = async () => {
  try {
    await applyFormRef.value.validate()
    loading.value = true
    await createRecipientApi(applyForm)
    ElMessage.success('申请提交成功，请等待审核')
    router.push('/my-applications')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  applyFormRef.value.resetFields()
}
</script>

<style scoped>
.apply-page {
  max-width: 700px;
  margin: 0 auto;
}

.apply-card {
  border-radius: 8px;
}

.card-header h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
</style>
