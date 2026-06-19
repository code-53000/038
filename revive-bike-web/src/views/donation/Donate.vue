<template>
  <div class="donate-page">
    <el-card class="donate-card">
      <template #header>
        <div class="card-header">
        <h3>捐赠旧自行车</h3>
        <p>让您的旧自行车重获新生，帮助有需要的人</p>
        </div>
      </template>

      <el-form
        ref="donateForm"
        :model="donateForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="车辆描述" prop="description">
          <el-input
            v-model="donateForm.description"
            type="textarea"
            :rows="4"
            placeholder="请描述您的自行车情况，如品牌、型号、使用年限、车况等"
          />
        </el-form-item>

        <el-divider content-position="left">预约上门回收</el-divider>

        <el-form-item label="预约日期" prop="scheduled_date">
          <el-date-picker
            v-model="donateForm.scheduled_date"
            type="date"
            placeholder="选择回收日期"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="预约时间" prop="scheduled_time">
          <el-select v-model="donateForm.scheduled_time" placeholder="选择时间段" style="width: 100%;">
            <el-option label="上午 9:00-11:00" value="上午 9:00-11:00" />
            <el-option label="下午 14:00-17:00" value="下午 14:00-17:00" />
            <el-option label="周末全天" value="周末全天" />
          </el-select>
        </el-form-item>

        <el-form-item label="回收地址" prop="address">
          <el-input v-model="donateForm.address" placeholder="请输入详细地址" />
        </el-form-item>

        <el-form-item label="联系人" prop="contact_name">
          <el-input v-model="donateForm.contact_name" placeholder="请输入联系人姓名" />
        </el-form-item>

        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="donateForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="donateForm.notes"
            type="textarea"
            :rows="2"
            placeholder="其他需要说明的情况"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
            提交捐赠
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
import { createDonationApi, schedulePickupApi } from '@/api/donation'

const router = useRouter()

const donateForm = reactive({
  description: '',
  scheduled_date: null,
  scheduled_time: '',
  address: '',
  contact_name: '',
  contact_phone: '',
  notes: ''
})

const rules = {
  description: [{ required: true, message: '请输入车辆描述', trigger: 'blur' }],
  address: [{ required: true, message: '请输入回收地址', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const donateFormRef = ref(null)
const loading = ref(false)

const handleSubmit = async () => {
  try {
    await donateFormRef.value.validate()
    loading.value = true

    const donationRes = await createDonationApi({
      description: donateForm.description
    })

    if (donateForm.address) {
      await schedulePickupApi(donationRes.id, {
        donation_id: donationRes.id,
        address: donateForm.address,
        contact_name: donateForm.contact_name,
        contact_phone: donateForm.contact_phone,
        scheduled_date: donateForm.scheduled_date,
        scheduled_time: donateForm.scheduled_time,
        notes: donateForm.notes
      })
    }

    ElMessage.success('捐赠登记成功！')
    router.push('/my-donations')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  donateFormRef.value.resetFields()
}
</script>

<style scoped>
.donate-page {
  max-width: 700px;
  margin: 0 auto;
}

.donate-card {
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
