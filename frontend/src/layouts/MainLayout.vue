<template>
  <div class="app-container">
    <el-container class="main-layout">
      <Navbar />
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import { onMounted } from 'vue'
import store from '../store'

onMounted(() => {
  store.actions.loadExperimentRecords()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f5f5;
  width: 100%;
}

.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 0;
  margin: 0;
  width: 100%;
}
</style>
