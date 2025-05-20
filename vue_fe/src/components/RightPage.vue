<template>
  <div class="right-page">
    <div class="centered-content">
      <div class="icon-area">
        <span class="icon">🎧</span>
      </div>

      <!-- AI 상태 메시지 -->
      <div class="status-box" v-if="!props.isHumanMode">
        <span>AI가 자동 응답 중 입니다..</span>
      </div>

      <!-- 요약 정보 표시 -->
      <div v-else-if="props.summary">
        <h3>상담 요약</h3>
        <div class="summary-content">
          <p><span v-html="props.summary"></span></p>
        </div>
      </div>
      <div v-else>
        <h3>상담 요약</h3>
        <div class="summary-content">
          <p> (요약 내용 없음) </p>
        </div>
      </div>

      <!-- 채팅 영역 추가 -->
      <div class="chat-area">
        <div
          v-for="(msg, i) in props.chatLog"
          :key="i"
          :class="['message', msg.role]"
        >
          <template v-if="msg.role === 'filter'">
            <div class="label">Q</div>
            <div class="bubble" v-html="msg.message"></div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

// props 정의
const props = defineProps({
  chatLog: {
    type: Array,
    required: true
  },
  summary: {
    type: String,
    default: ''
  },
  filteredQuestion: {
    type: String,
    default: ''
  },
  isHumanMode: {
    type: Boolean,
    default: false
  }
});

// props 변경 감지 및 로깅
watch(() => props.summary, (newSummary) => {
  console.log('RightPage - summary 변경됨:', newSummary);
});

watch(() => props.filteredQuestion, (newQuestion) => {
  console.log('RightPage - filteredQuestion 변경됨:', newQuestion);
});

watch(() => props.isHumanMode, (newValue) => {
  console.log('RightPage - HUMAN MODE 상태 변경:', newValue);
});

// 초기 props 로깅
console.log('RightPage - 초기 props:', {
  chatLog: props.chatLog,
  summary: props.summary,
  filteredQuestion: props.filteredQuestion,
  isHumanMode: props.isHumanMode
});

// chatLog 변경 감지 및 로깅
watch(() => props.chatLog, (newChatLog) => {
  console.log('RightPage - chatLog 변경됨:', newChatLog);
}, { deep: true });

// 초기 chatLog 로깅
console.log('RightPage - 초기 chatLog:', props.chatLog);
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

/* 채팅 영역 스타일 추가 */
.chat-area {
  /* background-color: #f8f8f8; */
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
  overflow-y: auto;
  text-align: left;
}

.message {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
  justify-content: flex-start;
}

.message.user {
  flex-direction: row;
}

.message.assistant {
  flex-direction: row;
}

.label {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin: 0 8px;
  flex-shrink: 0;
}

.message.user .label {
  background-color: #ea002c;
  color: white;
}

.message.assistant .label {
  background-color: #4CAF50;
  color: white;
}

.bubble {
  background-color: #f8f8f8;
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 70%;
  word-wrap: break-word;
  margin-left: 8px;
}

.message.user .bubble {
  background-color: #f0f0f0;
  color: #333;
}

.message.assistant .bubble {
  background-color: #e3f2fd;
  color: #333;
}
</style>
