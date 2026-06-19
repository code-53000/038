<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="32" color="#409eff"><Bicycle /></el-icon>
        <span class="logo-text">自行车翻新捐赠</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        :collapse="false"
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409eff"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ $route.meta.title }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.userInfo?.full_name || userStore.userInfo?.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const menuItems = computed(() => {
  const role = userStore.role
  const allMenus = [
    { path: '/dashboard', title: '首页', icon: 'HomeFilled', roles: ['donor', 'volunteer', 'admin'] },
    { path: '/donate', title: '我要捐赠', icon: 'Present', roles: ['donor', 'volunteer', 'admin'] },
    { path: '/my-donations', title: '我的捐赠', icon: 'List', roles: ['donor', 'volunteer', 'admin'] },
    { path: '/pickups', title: '回收管理', icon: 'Van', roles: ['volunteer', 'admin'] },
    { path: '/bikes', title: '车辆管理', icon: 'Bicycle', roles: ['volunteer', 'admin'] },
    { path: '/refurbishments', title: '翻新工序', icon: 'Tools', roles: ['volunteer', 'admin'] },
    { path: '/parts', title: '零件管理', icon: 'Setting', roles: ['volunteer', 'admin'] },
    { path: '/recipient-apply', title: '申请受赠', icon: 'Postcard', roles: ['donor', 'volunteer', 'admin'] },
    { path: '/my-applications', title: '我的申请', icon: 'Document', roles: ['donor', 'volunteer', 'admin'] },
    { path: '/recipients', title: '受赠管理', icon: 'User', roles: ['volunteer', 'admin'] },
    { path: '/matches', title: '匹配管理', icon: 'Connection', roles: ['volunteer', 'admin'] }
  ]
  return allMenus.filter(item => item.roles.includes(role))
})

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
    }).catch(() => {})
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #001529;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid #1f3a56;
}

.logo-text {
  color: white;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.menu {
  border-right: none;
  flex: 1;
}

.header {
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #606266;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
