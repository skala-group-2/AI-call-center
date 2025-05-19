<template>
  <div class="right-page">
    <div class="centered-content">
      <div class="icon-area">
        <span class="icon">🎧</span>
      </div>

      <!-- AI 상태 메시지 -->
      <div class="status-box" v-if="aiStatus === 'responding'">
        <span>AI가 자동 응답 중 입니다..</span>
      </div>

      <!-- 추후 요약 리스트 -->
      <div v-else-if="aiStatus === 'escalated'" class="summary-container">
        <h3>상담 요약</h3>
        <ul>
          <li v-for="(item, idx) in escalatedQuestions" :key="idx">
            {{ item.text }} - <strong>{{ item.filter }}</strong>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

// 상태 플래그
const aiStatus = ref("responding"); // 'responding' 또는 'escalated'

// 상담사용 요약 예시 (추후 실제 이관 시 노출)
const escalatedQuestions = ref([
  {
    text: "This is really frustrating. I want to speak to a real person!",
    filter: "정상",
  },
  { text: "You guys are useless!", filter: "욕설" },
]);
</script>

<style scoped>
.right-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
  overflow: hidden;
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
</style>
