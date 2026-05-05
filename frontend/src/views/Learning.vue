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

    <div v-if="showDetailModal" class="detail-modal-overlay" @click.self="closeDetailModal">
      <div class="detail-modal">
        <div class="modal-header">
          <div class="header-left">
            <div>
              <h2>{{ selectedVuln?.name }}</h2>
              <span :class="['difficulty-badge', getDifficultyClass(selectedVuln?.difficulty)]">
                {{ getDifficultyLabel(selectedVuln?.difficulty) }}
              </span>
            </div>
          </div>
          <button class="modal-close-btn" @click="closeDetailModal">×</button>
        </div>

        <div class="view-toggle">
          <button
            :class="['toggle-btn', { active: viewMode === 'text' }]"
            @click="viewMode = 'text'"
          >
            文本模式
          </button>
          <button
            :class="['toggle-btn', { active: viewMode === 'visual' }]"
            @click="viewMode = 'visual'"
          >
            图解模式
          </button>
        </div>

        <div class="modal-content">
          <div v-if="viewMode === 'text'" class="text-view">
            <section class="content-section">
              <h3>漏洞简介</h3>
              <p>{{ selectedVuln?.description }}</p>
            </section>

            <section class="content-section">
              <h3>危害影响</h3>
              <ul>
                <li v-for="(impact, index) in selectedVuln?.impact" :key="index">{{ impact }}</li>
              </ul>
            </section>

            <section class="content-section">
              <h3>漏洞原理</h3>
              <div v-html="selectedVuln?.principle"></div>
            </section>

            <section class="content-section">
              <h3>防御方法</h3>
              <ul>
                <li v-for="(defense, index) in selectedVuln?.defense" :key="index">{{ defense }}</li>
              </ul>
            </section>

            <section class="content-section">
              <h3>代码示例</h3>
              <div class="code-example">
                <pre>{{ selectedVuln?.codeExample }}</pre>
              </div>
            </section>

            <section class="content-section">
              <h3>实战学习</h3>
              <p>现在去实际操作这个漏洞吧！</p>
              <button class="go-practice-btn" @click="goPractice">去靶场练习</button>
            </section>
          </div>

          <div v-if="viewMode === 'visual'" class="visual-view">
            <div class="diagram-container">
              <h3 class="diagram-title">攻击流程</h3>
              <div class="flow-diagram">
                <div
                  v-for="(step, index) in selectedVuln?.flowDiagram"
                  :key="index"
                  :class="['flow-step', { 'step-active': currentStep === index }]"
                  @click="currentStep = index"
                >
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <h4>{{ step.title }}</h4>
                    <p>{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="compare-section">
              <div class="compare-card attack">
                <h4>有漏洞的代码</h4>
                <pre>{{ selectedVuln?.vulnCode }}</pre>
              </div>
              <div class="compare-card secure">
                <h4>安全的代码</h4>
                <pre>{{ selectedVuln?.secureCode }}</pre>
              </div>
            </div>

            <div class="checklist-section">
              <h3>安全检查清单</h3>
              <div class="checklist">
                <div
                  v-for="(item, index) in selectedVuln?.checklist"
                  :key="index"
                  :class="['check-item', { checked: checkedItems.includes(index) }]"
                  @click="toggleCheck(index)"
                >
                  <span class="check-icon">{{ checkedItems.includes(index) ? '✓' : '○' }}</span>
                  <span class="check-text">{{ item }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { categories as vulnCategories, vulnerabilities, difficultyLabels } from '../data/vulnerabilities'

const router = useRouter()
const showDetailModal = ref(false)
const selectedVuln = ref(null)
const selectedCategory = ref('all')
const viewMode = ref('text')
const currentStep = ref(0)
const checkedItems = ref([])

const categories = ref([...vulnCategories])

onMounted(() => {
  categories.value[0].count = vulnerabilities.length
})

const filteredVulnerabilities = computed(() => {
  if (selectedCategory.value === 'all') {
    return vulnerabilities
  }
  return vulnerabilities.filter(v => v.category === selectedCategory.value)
})

const selectCategory = (id) => {
  selectedCategory.value = id
  currentStep.value = 0
  checkedItems.value = []
}

const getDifficultyClass = (difficulty) => {
  const map = {
    easy: 'easy',
    medium: 'medium',
    hard: 'hard'
  }
  return map[difficulty] || 'easy'
}

const getDifficultyLabel = (difficulty) => {
  return difficultyLabels[difficulty] || difficulty
}

const openVulnDetail = (vuln) => {
  selectedVuln.value = vuln
  showDetailModal.value = true
  viewMode.value = 'text'
  currentStep.value = 0
  checkedItems.value = []
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedVuln.value = null
}

const toggleCheck = (index) => {
  const i = checkedItems.value.indexOf(index)
  if (i > -1) {
    checkedItems.value.splice(i, 1)
  } else {
    checkedItems.value.push(index)
  }
}

const goPractice = () => {
  router.push('/vulnerabilities')
}
</script>

<style scoped>
.learning-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdf4 100%);
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 10px;
}

.page-header p {
  color: #64748b;
  font-size: 1.1rem;
}

.learning-container {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.category-sidebar {
  width: 250px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 20px;
}

.category-sidebar h3 {
  color: #1e293b;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.category-item:hover {
  background: #f1f5f9;
}

.category-item.active {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
}

.category-name {
  flex: 1;
  font-weight: 500;
}

.category-count {
  background: rgba(0,0,0,0.1);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.85rem;
}

.category-item.active .category-count {
  background: rgba(255,255,255,0.3);
}

.content-area {
  flex: 1;
}

.vulnerabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.vuln-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-top: 4px solid transparent;
}

.vuln-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.vuln-card.easy {
  border-top-color: #22c55e;
}

.vuln-card.medium {
  border-top-color: #f59e0b;
}

.vuln-card.hard {
  border-top-color: #ef4444;
}

.vuln-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.vuln-header h4 {
  color: #1e293b;
  font-size: 1.15rem;
  margin: 0;
}

.difficulty-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.difficulty-badge.easy {
  background: #dcfce7;
  color: #166534;
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
  color: #64748b;
  margin-bottom: 15px;
  line-height: 1.6;
  font-size: 0.95rem;
}

.vuln-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #f1f5f9;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.detail-modal-overlay {
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
}

.detail-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 25px;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.modal-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.7rem;
}

.modal-header h2 + .difficulty-badge {
  margin-top: 5px;
  display: inline-block;
}

.modal-close-btn {
  background: #f1f5f9;
  border: none;
  color: #64748b;
  font-size: 1.8rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.modal-close-btn:hover {
  background: #e5e7eb;
  color: #1e293b;
}

.view-toggle {
  display: flex;
  gap: 10px;
  padding: 15px 25px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.toggle-btn {
  padding: 8px 20px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.toggle-btn:hover {
  border-color: #0ea5e9;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  border-color: transparent;
}

.modal-content {
  padding: 25px;
}

.content-section {
  margin-bottom: 30px;
}

.content-section h3 {
  color: #1e293b;
  font-size: 1.25rem;
  margin-bottom: 15px;
}

.content-section p {
  color: #475569;
  line-height: 1.8;
}

.content-section ul {
  color: #475569;
  line-height: 1.8;
  padding-left: 20px;
}

.content-section li {
  margin-bottom: 8px;
}

.content-section pre {
  background: #1e293b;
  color: #e2e8f0;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  line-height: 1.6;
}

.code-example {
  margin-top: 10px;
}

.go-practice-btn {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 10px;
}

.go-practice-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(34, 197, 94, 0.4);
}

.diagram-container {
  margin-bottom: 30px;
}

.diagram-title {
  color: #1e293b;
  font-size: 1.3rem;
  margin-bottom: 20px;
  text-align: center;
}

.flow-diagram {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.flow-step {
  display: flex;
  align-items: center;
  gap: 15px;
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.flow-step:hover {
  background: #f1f5f9;
}

.flow-step.step-active {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
  border-color: #0ea5e9;
}

.step-number {
  width: 36px;
  height: 36px;
  background: #0ea5e9;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 5px;
  color: #1e293b;
}

.step-content p {
  margin: 0;
  color: #64748b;
}

.compare-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.compare-card {
  padding: 20px;
  border-radius: 12px;
}

.compare-card.attack {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.compare-card.secure {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.compare-card h4 {
  margin: 0 0 15px;
}

.compare-card.attack h4 {
  color: #dc2626;
}

.compare-card.secure h4 {
  color: #16a34a;
}

.compare-card pre {
  margin: 0;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-all;
}

.compare-card.attack pre {
  background: rgba(239, 68, 68, 0.1);
}

.compare-card.secure pre {
  background: rgba(34, 197, 94, 0.1);
}

.checklist-section {
  margin-top: 30px;
}

.checklist-section h3 {
  color: #1e293b;
  margin-bottom: 15px;
}

.checklist {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.check-item:hover {
  background: #f1f5f9;
}

.check-item.checked {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%);
}

.check-icon {
  font-size: 1.3rem;
  color: #22c55e;
}

.check-text {
  color: #1e293b;
  flex: 1;
}

@media (max-width: 900px) {
  .learning-container {
    flex-direction: column;
  }

  .category-sidebar {
    width: 100%;
    position: static;
  }

  .vulnerabilities-grid {
    grid-template-columns: 1fr;
  }

  .compare-section {
    grid-template-columns: 1fr;
  }
}
</style>
