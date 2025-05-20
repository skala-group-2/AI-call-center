<template>
  <div class="container">
    <div class="half left">
      <LeftPage
        :chat-log="chatLog"
        @send-message="handleSendMessage"
        @summary="handleSummary"
        @human-mode-triggered="handleHumanModeTriggered"
      />
    </div>
    <div class="half right">
      <RightPage
        :chat-log="chatLog"
        :summary="summary"
        :filtered-question="filteredQuestion"
        :is-human-mode="isHumanMode"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LeftPage from './components/LeftPage.vue'
import RightPage from './components/RightPage.vue'

const chatLog = ref([])
const summary = ref('')
const filteredQuestion = ref('')
const isHumanMode = ref(false)

const handleSendMessage = (newMsg) => {
  chatLog.value.push(newMsg)
}

const handleSummary = (data) => {
  summary.value = data.summary
  filteredQuestion.value = data.filtered_question
}

const handleHumanModeTriggered = (value) => {
  isHumanMode.value = value
}
</script>

<style>
/* 전역 스타일로 변경 (scoped 제거) */
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  /* overflow: hidden; */
}
</style>

<style scoped>
.container {
  display: flex;
  width: 100vw;
  height: 100vh;
  /* overflow: hidden; */
}

.half {
  flex: 1;
  height: 100%;
  box-sizing: border-box;
  min-width: 0;
  min-height: 0;     /* ← 꼭 추가: y축 오버플로우 허용 */
  max-width: 50%; /* 최대 너비를 50%로 제한 */
  overflow-y: auto; /* 내용이 넘치지 않도록 함 */
}

.left {
  border-right: 1px solid #eee;
}
.right {
  background-color: white;
}
</style>