<template>
  <div class="right-page">
    <div class="centered-content">
      <div class="icon-area">
        <span class="icon">🎧</span>
      </div>

      <!-- AI 상태 메시지 -->
      <div class="status-box" v-if="!summary">
        <span>AI가 자동 응답 중 입니다..</span>
      </div>

      <!-- 요약 정보 표시 -->
      <div v-else class="summary-container">
        <h3>상담 요약</h3>
        <div class="summary-content">
          <p><strong>요약:</strong><br/><span v-html="summary"></span></p>
          <p><strong>필터링된 질문:</strong><br/><span v-html="filteredQuestion"></span></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

// props 정의
const props = defineProps({
  summary: {
    type: String,
    default: ''
  },
  filteredQuestion: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.right-page {
  width: 100%;
  height: 100%;
  flex: 1;    
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 16px;
  box-sizing: border-box;
  overflow-y: auto;
  min-height: 0;      /* ← flex 자식에 꼭 필요 */
}

.centered-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 80%;
  text-align: center;
}

.icon-area {
  font-size: 40px;
  margin-bottom: 16px;
  color: #ea002c;
}

.status-box {
  border: none;
  color: #ea002c;
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  background-color: #fff;
  margin-bottom: 16px;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.summary-container {
  width: 100%;
}

h3 {
  margin-bottom: 16px;
  font-size: 20px;
  color: #333;
  text-align: center;
}

ul {
  list-style: none;
  padding: 0;
  text-align: left;
}

li {
  margin-bottom: 12px;
  font-size: 16px;
}

.summary-content {
  background-color: #f8f8f8;
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
  text-align: left;
}

.summary-content p {
  margin: 8px 0;
  line-height: 1.5;
}
</style>
