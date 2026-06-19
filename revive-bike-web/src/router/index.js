import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'donate',
        name: 'Donate',
        component: () => import('@/views/donation/Donate.vue'),
        meta: { title: '我要捐赠', icon: 'Present', roles: ['donor', 'admin', 'volunteer'] }
      },
      {
        path: 'my-donations',
        name: 'MyDonations',
        component: () => import('@/views/donation/MyDonations.vue'),
        meta: { title: '我的捐赠', icon: 'List', roles: ['donor', 'admin', 'volunteer'] }
      },
      {
        path: 'trace/:id',
        name: 'Trace',
        component: () => import('@/views/donation/Trace.vue'),
        meta: { title: '捐赠追溯', icon: 'View' }
      },
      {
        path: 'pickups',
        name: 'Pickups',
        component: () => import('@/views/donation/Pickups.vue'),
        meta: { title: '回收管理', icon: 'Van', roles: ['volunteer', 'admin'] }
      },
      {
        path: 'bikes',
        name: 'Bikes',
        component: () => import('@/views/refurbishment/Bikes.vue'),
        meta: { title: '车辆管理', icon: 'Bicycle', roles: ['volunteer', 'admin'] }
      },
      {
        path: 'refurbishments',
        name: 'Refurbishments',
        component: () => import('@/views/refurbishment/Refurbishments.vue'),
        meta: { title: '翻新工序', icon: 'Tools', roles: ['volunteer', 'admin'] }
      },
      {
        path: 'parts',
        name: 'Parts',
        component: () => import('@/views/part/Parts.vue'),
        meta: { title: '零件管理', icon: 'Setting', roles: ['volunteer', 'admin'] }
      },
      {
        path: 'recipient-apply',
        name: 'RecipientApply',
        component: () => import('@/views/recipient/Apply.vue'),
        meta: { title: '申请受赠', icon: 'Postcard', roles: ['donor', 'admin', 'volunteer'] }
      },
      {
        path: 'my-applications',
        name: 'MyApplications',
        component: () => import('@/views/recipient/MyApplications.vue'),
        meta: { title: '我的申请', icon: 'Document', roles: ['donor', 'admin', 'volunteer'] }
      },
      {
        path: 'recipients',
        name: 'Recipients',
        component: () => import('@/views/recipient/Recipients.vue'),
        meta: { title: '受赠管理', icon: 'User', roles: ['volunteer', 'admin'] }
      },
      {
        path: 'matches',
        name: 'Matches',
        component: () => import('@/views/recipient/Matches.vue'),
        meta: { title: '匹配管理', icon: 'Connection', roles: ['volunteer', 'admin'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false

  document.title = `${to.meta.title || '自行车翻新捐赠平台'}`

  if (requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.roles && userStore.isLoggedIn) {
    if (to.meta.roles.includes(userStore.role)) {
      next()
    } else {
      next('/dashboard')
    }
  } else {
    next()
  }
})

export default router
