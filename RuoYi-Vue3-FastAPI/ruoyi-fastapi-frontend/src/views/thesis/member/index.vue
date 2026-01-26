<template>
  <component :is="currentComponent" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PackageView from './package.vue'
import UserView from './user.vue'
import QuotaView from './quota.vue'

const route = useRoute()
const currentComponent = ref(PackageView)

// 根据路由参数或默认显示套餐管理
onMounted(() => {
  // 默认显示套餐管理页面
  currentComponent.value = PackageView
})
</script>
