<template>
  <div class="app-container">
    <h1>任务管理 - 简化测试版</h1>
    <p>如果你能看到这个页面，说明路由和组件加载是正常的。</p>
    <el-button type="primary" @click="testClick">测试按钮</el-button>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup name="TaskSimple">
const message = ref('');

function testClick() {
  message.value = '按钮点击成功！组件功能正常。';
}
</script>
