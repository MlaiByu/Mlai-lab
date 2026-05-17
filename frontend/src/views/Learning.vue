<template>
  <div class="learning-page">
    <div class="page-header">
      <h1>漏洞学习中心</h1>
      <p>深入理解各类Web安全漏洞的原理与防御方法</p>
    </div>

    <div class="learning-container">
      <aside class="category-sidebar">
        <h3>漏洞分类</h3>
        <div
          v-for="category in categories"
          :key="category.id"
          :class="['category-item', { active: selectedCategory === category.id }]"
          @click="selectCategory(category.id)"
        >
          <span class="category-name">{{ category.name }}</span>
          <span class="category-count">{{ category.count }}</span>
        </div>
      </aside>

      <main class="content-area">
        <div class="vulnerabilities-grid">
          <div
            v-for="vuln in filteredVulnerabilities"
            :key="vuln.id"
            :class="['vuln-card', getDifficultyClass(vuln.difficulty)]"
            @click="openVulnDetail(vuln)"
          >
            <div class="vuln-header">
              <h4>{{ vuln.name }}</h4>
              <span :class="['difficulty-badge', getDifficultyClass(vuln.difficulty)]">
                {{ getDifficultyLabel(vuln.difficulty) }}
              </span>
            </div>
            <p class="vuln-summary">{{ vuln.summary }}</p>
            <div class="vuln-tags">
              <span v-for="tag in vuln.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </main>
    </div>

    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="detail-modal">
        <div class="modal-header">
          <div class="header-info">
            <h2>{{ selectedVuln?.name }}</h2>
            <span :class="['difficulty-badge', getDifficultyClass(selectedVuln?.difficulty)]">
              {{ getDifficultyLabel(selectedVuln?.difficulty) }}
            </span>
          </div>
          <button class="close-btn" @click="closeDetailModal">×</button>
        </div>

        <div class="modal-body">
          <div class="modal-section">
            <h3>漏洞简介</h3>
            <p>{{ currentVulnType?.description }}</p>
          </div>

          <div class="modal-section">
            <h3>漏洞原理</h3>
            <ul class="principle-list">
              <li v-for="(item, index) in currentVulnType?.principles" :key="index">
                <span class="step-number">{{ index + 1 }}</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>

          <div class="modal-section">
            <h3>危害影响</h3>
            <div class="impact-list">
              <div v-for="(impact, index) in currentVulnType?.impacts" :key="index" class="impact-item">
                {{ impact }}
              </div>
            </div>
          </div>

          <div class="modal-section">
            <h3>攻击向量</h3>
            <div class="attack-vectors">
              <div v-for="vector in currentVulnType?.attackVectors" :key="vector.name" class="vector-item">
                <strong>{{ vector.name }}</strong>
                <p>{{ vector.description }}</p>
              </div>
            </div>
          </div>

          <div class="modal-section">
            <h3>代码示例</h3>
            <div v-if="currentVulnType?.examples" class="examples-list">
              <div v-for="example in currentVulnType?.examples" :key="example.title">
                <h4>{{ example.title }}</h4>
                <div class="code-block">
                  <span class="code-label">漏洞代码</span>
                  <pre><code>{{ example.vulnerable }}</code></pre>
                </div>
                <div class="code-block">
                  <span class="code-label">攻击Payload</span>
                  <pre class="payload"><code>{{ example.payload }}</code></pre>
                </div>
                <div class="code-block">
                  <span class="code-label">执行结果</span>
                  <pre><code>{{ example.result }}</code></pre>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-section">
            <h3>防御策略</h3>
            <div class="defense-list">
              <div v-for="(defense, index) in currentVulnType?.defenses" :key="index" class="defense-item">
                <span class="check-icon">✓</span>
                {{ defense }}
              </div>
            </div>
          </div>

          <div class="modal-section">
            <h3>真实案例</h3>
            <div class="cases-list">
              <div v-for="(caseItem, index) in currentVulnType?.realCases" :key="index" class="case-item">
                {{ caseItem }}
              </div>
            </div>
          </div>

          <div class="modal-section collapsible">
            <div class="collapsible-header" @click="toggleSolution">
              <h3>解题思路</h3>
              <span :class="['collapse-icon', { rotated: showSolution }]">▼</span>
            </div>
            <div v-show="showSolution" class="collapsible-content">
              <div class="solution-list">
                <div v-for="(step, index) in selectedVuln?.solution" :key="index" class="solution-item">
                  <span class="step-num">{{ index + 1 }}</span>
                  <span class="step-text">{{ step }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-section">
            <h3>实验信息</h3>
            <div class="practice-info">
              <div class="info-row">
                <strong>场景：</strong>{{ selectedVuln?.scenario }}
              </div>
              <div class="info-row">
                <strong>目标：</strong>{{ selectedVuln?.objective }}
              </div>
              <div class="info-row">
                <strong>Flag：</strong><code>{{ selectedVuln?.flag }}</code>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="footer-btn" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { categories, vulnTypes, vulnerabilities } from '../data/vulnerabilities.js'

const selectedCategory = ref('all')
const selectedVuln = ref(null)
const showDetailModal = ref(false)
const showSolution = ref(false)

const filteredVulnerabilities = computed(() => {
  if (selectedCategory.value === 'all') {
    return vulnerabilities
  }
  return vulnerabilities.filter(v => v.type === selectedCategory.value)
})

const currentVulnType = computed(() => {
  if (!selectedVuln.value) return null
  return vulnTypes[selectedVuln.value.type]
})

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

const openVulnDetail = (vuln) => {
  selectedVuln.value = vuln
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedVuln.value = null
  showSolution.value = false
}

const toggleSolution = () => {
  showSolution.value = !showSolution.value
}

const getDifficultyClass = (difficulty) => {
  const classes = {
    easy: 'easy',
    medium: 'medium',
    hard: 'hard'
  }
  return classes[difficulty] || 'easy'
}

const getDifficultyLabel = (difficulty) => {
  const labels = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return labels[difficulty] || '简单'
}
</script>

<style scoped>
.learning-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.page-header h1 {
  font-size: 36px;
  margin-bottom: 10px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.page-header p {
  font-size: 16px;
  opacity: 0.9;
}

.learning-container {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  gap: 20px;
}

.category-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.category-sidebar h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: white;
  padding-left: 10px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  margin-bottom: 10px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateX(5px);
}

.category-item.active {
  background: white;
  color: #667eea;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.category-name {
  font-weight: 600;
  font-size: 15px;
}

.category-count {
  background: rgba(0, 0, 0, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.category-item.active .category-count {
  background: rgba(102, 126, 234, 0.2);
}

.content-area {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  min-height: 500px;
}

.vulnerabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.vuln-card {
  background: white;
  border-radius: 16px;
  padding: 22px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border-top: 4px solid #667eea;
}

.vuln-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.vuln-card.easy {
  border-top-color: #10b981;
}

.vuln-card.medium {
  border-top-color: #f59e0b;
}

.vuln-card.hard {
  border-top-color: #ef4444;
}

.vuln-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.vuln-header h4 {
  font-size: 18px;
  color: #1a1a2e;
  margin: 0;
}

.difficulty-badge {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.difficulty-badge.easy {
  background: #d1fae5;
  color: #065f46;
}

.difficulty-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.difficulty-badge.hard {
  background: #fee2e2;
  color: #991b1b;
}

.vuln-summary {
  color: #666;
  font-size: 14px;
  margin-bottom: 14px;
  line-height: 1.6;
}

.vuln-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 5px 12px;
  background: #f0f2f5;
  border-radius: 6px;
  font-size: 12px;
  color: #555;
  transition: all 0.2s;
}

.tag:hover {
  background: #e0e2e5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.detail-modal {
  background: white;
  border-radius: 20px;
  max-width: 900px;
  max-height: 85vh;
  width: 90%;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #f0f2f5;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 20px 20px 0 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-info h2 {
  margin: 0;
  font-size: 24px;
  color: #1a1a2e;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.2);
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px 30px;
  overflow-y: auto;
  flex: 1;
}

.modal-section {
  margin-bottom: 25px;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.collapsible {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.collapsible-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  cursor: pointer;
  transition: all 0.3s;
}

.collapsible-header:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
}

.collapsible-header h3 {
  margin: 0;
  padding: 0;
  border: none;
}

.collapse-icon {
  font-size: 12px;
  color: #667eea;
  transition: transform 0.3s ease;
}

.collapse-icon.rotated {
  transform: rotate(180deg);
}

.collapsible-content {
  padding: 20px;
  background: white;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

.modal-section h3 {
  font-size: 17px;
  margin: 0 0 15px 0;
  color: #1a1a2e;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f2f5;
}

.modal-section p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.7;
}

.principle-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.principle-list li {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
  border-left: 4px solid #667eea;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.impact-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.impact-item {
  padding: 12px 15px;
  background: #fef3c7;
  border-radius: 10px;
  font-size: 14px;
  color: #92400e;
  border-left: 4px solid #f59e0b;
}

.attack-vectors {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.vector-item {
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
}

.vector-item strong {
  color: #1a1a2e;
  display: block;
  margin-bottom: 6px;
}

.vector-item p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.examples-list h4 {
  margin: 0 0 15px 0;
  color: #1a1a2e;
  font-size: 16px;
}

.code-block {
  margin-bottom: 15px;
}

.code-block:last-child {
  margin-bottom: 0;
}

.code-label {
  display: inline-block;
  padding: 4px 12px;
  background: #667eea;
  color: white;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 8px;
}

.code-block pre {
  margin: 0;
  padding: 16px;
  background: #0f172a;
  color: #e2e8f0;
  border-radius: 10px;
  overflow-x: auto;
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.code-block .payload {
  background: #1e1b4b;
  border: 1px solid #4f46e5;
}

.defense-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.defense-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background: #d1fae5;
  border-radius: 10px;
  font-size: 14px;
  color: #065f46;
}

.check-icon {
  margin-right: 10px;
  font-weight: bold;
}

.cases-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.case-item {
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
  font-size: 14px;
  color: #555;
  border-left: 4px solid #3b82f6;
}

.solution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.solution-item {
  display: flex;
  align-items: flex-start;
  padding: 14px 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
  margin-right: 14px;
  flex-shrink: 0;
}

.step-text {
  font-size: 14px;
  line-height: 1.6;
}

.practice-info {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
}

.info-row {
  font-size: 14px;
  margin-bottom: 10px;
  color: #333;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row code {
  background: #e8f5e9;
  padding: 4px 10px;
  border-radius: 6px;
  color: #065f46;
  font-family: 'Fira Code', monospace;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: flex-end;
}

.footer-btn {
  padding: 12px 30px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.footer-btn:hover {
  background: #5a6fd6;
  transform: translateY(-2px);
}
</style>
