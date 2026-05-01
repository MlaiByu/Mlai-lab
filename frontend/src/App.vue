<template>
  <div class="app-container">
    <Navbar v-if="showNavbar" />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

const route = useRoute()

const excludedPaths = ['/', '/login', '/register']

const showNavbar = computed(() => {
  return !excludedPaths.includes(route.path)
})

watch(() => route.path, () => {
  // Navbar visibility is handled by computed property
})

onMounted(() => {
  // Initial check is handled by computed property
})
</script>

<style>
:root {
  --primary-color: #0ea5e9;
  --primary-light: #38bdf8;
  --primary-dark: #0284c7;
  --secondary-color: #06b6d4;
  --success-color: #22c55e;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --info-color: #3b82f6;
  --bg-light: #f8fafc;
  --bg-card: #ffffff;
  --border-color: #e2e8f0;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.el-header {
  background: #ffffff !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  box-shadow: none !important;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  color: var(--text-primary);
  margin: 0;
  padding: 0;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4f8 50%, #f0fdf4 100%);
}

.main-content {
  flex: 1;
  padding: 2rem;
  padding-top: calc(2rem + 70px);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  color: var(--text-secondary);
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: #f8fafc;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-input option {
  background: white;
  color: var(--text-primary);
}

.btn {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  letter-spacing: 0.3px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(14, 165, 233, 0.4);
}

.btn-secondary {
  background: #f1f5f9;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.alert {
  padding: 1rem 1.25rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.alert-success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.25);
  color: var(--success-color);
}

.alert-danger {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: var(--danger-color);
}

.alert-info {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.25);
  color: var(--info-color);
}

.alert-warning {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.25);
  color: var(--warning-color);
}

pre {
  background: #1e293b;
  padding: 1.25rem;
  border-radius: 12px;
  overflow-x: auto;
  color: #e2e8f0;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}

code {
  background: rgba(14, 165, 233, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  color: var(--primary-color);
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

.result-box {
  background: #f8fafc;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.25rem;
  margin-top: 1rem;
  min-height: 120px;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-primary);
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
}

.vulnerability-type {
  display: inline-block;
  padding: 0.375rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.vuln-low {
  background: rgba(34, 197, 94, 0.1);
  color: var(--success-color);
}

.vuln-medium {
  background: rgba(234, 179, 8, 0.1);
  color: #ca8a04;
}

.vuln-high {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.card-small {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 1.75rem;
  cursor: pointer;
  transition: all 0.35s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
}

.card-small:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.15);
}

.card-small h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.card-small p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-box-shadow: 0 0 0 30px white inset;
  -webkit-text-fill-color: var(--text-primary);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.875rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background: #f8fafc;
  font-weight: 600;
  color: var(--text-primary);
}

tr:hover {
  background: #f8fafc;
}
</style>