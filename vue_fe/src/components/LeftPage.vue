<template>
  <div class="left-page">
    <!-- 왼쪽 상단에 고정된 로고/아이콘 -->
    <div class="header-logo">
      <img src="../assets/logo.svg" alt="Group Logo" class="logo-svg" />
    </div>

    <div class="chat-area">
      <!-- 메시지 구조 변경 - AI 메시지일 때 순서 조정 -->
      <div v-for="(msg, i) in chatLog" :key="i" :class="['message', msg.role]">
        <!-- 사용자 메시지는 Q-버블 순서, AI 메시지는 버블-A 순서 -->
        <template v-if="msg.role === 'user'">
          <div class="label">Q</div>
          <div class="bubble">{{ msg.message }}</div>
        </template>
        <template v-else>
          <div class="bubble">{{ msg.message }}</div>
          <div class="label">A</div>
        </template>
      </div>
    </div>

    <!-- 상태 텍스트 -->
    <div class="recording-status" v-if="isRecording">
      고객님이 대화 중입니다...
    </div>

    <!-- 녹음 버튼 -->
    <div
      class="call-button"
      :class="{ recording: isRecording }"
      @click="handleCall"
    >
      <span class="icon">{{ isRecording ? "■" : "📞" }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const isRecording = ref(false);
const chatLog = ref([]);

// const props = useProps({ chatLog: Array });
const emit = defineEmits(['summary']);

// const userInput = ref('');

let mediaRecorder;
let audioChunks = [];

const handleCall = async () => {
  if (!isRecording.value) {
    // 녹음 시작
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/webm" });

      const formData = new FormData();
      formData.append("audio", blob, "recording.webm"); //수정

      try {
        const res = await fetch("/call-center/", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          // 서버가 500을 던지면 res.ok가 false가 됩니다
          const contentType = res.headers.get('content-type');
          let errDetail;
          if (contentType && contentType.includes('application/json')) {
            const errJson = await res.json();
            errDetail = errJson.detail || JSON.stringify(errJson);
          } else {
            errDetail = await res.text();
          }
          console.error(`Call Center API 실패 [${res.status}]:`, errDetail);
          return;
        }

        const data = await res.json();

        // Q: 사용자의 인식된 질문
        chatLog.value.push({
          role: "user",
          message: data.stt_text || "(음성 인식 실패)",
        });

        if (data.gpt_response) {
          // A: GPT 응답
          chatLog.value.push({
            role: "ai",
            message: data.gpt_response || "(응답 없음)",
          });
          
          if (data.tts_file_path) {
            const audioUrl = `http://localhost:8005${data.tts_file_path}`  
            new Audio(audioUrl).play().catch(err => console.error("오디오 재생 실패:", err));
          }
        } else if (data.message?.includes("HUMAN MODE")) {
          // AI 불가 → 상담사 이관
          chatLog.value.push({
            role: "ai",
            message: "상담사 연결이 필요합니다. 상담사와의 통화로 변환하겠습니다."
          });

          // 요약/필터링 결과 표시 (선택)
          if (data.summary) {
            chatLog.value.push({
              role: "ai",
              message: `요약: ${data.summary}\n필터링 결과: ${data.filtered_question}`,
            });

            emit('summary', {
              summary: data.summary,
              filtered_question: data.filtered_question
            });
          }
        }
      } catch (err) {
        console.error("API 요청 오류:", err);
      }

      isRecording.value = false;
    };

    mediaRecorder.start();
    isRecording.value = true;
  } else {
    mediaRecorder.stop();
  }
};
</script>

<style scoped>
.left-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-sizing: border-box;
  position: relative;
  overflow: hidden; /* 추가: 페이지 전체 오버플로우 제어 */
}

/* 헤더 로고 스타일 */
.header-logo {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
}

.logo-svg {
  height: 32px;
  width: auto;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden; /* 추가: 가로 스크롤 방지 */
  padding-right: 8px;
  margin-bottom: 16px;
  margin-top: 60px; /* 로고 아래에 공간 확보 */
  width: 100%; /* 추가: 너비 명시 */
  box-sizing: border-box; /* 추가: 패딩 포함 */
}

/* 메시지 컨테이너 */
.message {
  font-weight: bold;
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  width: 100%;
  box-sizing: border-box;
}

/* 사용자 메시지(질문) 스타일 */
.message.user {
  justify-content: flex-start; /* 왼쪽 정렬 */
}

/* AI 메시지(답변) 스타일 */
.message.ai {
  justify-content: flex-end; /* 오른쪽 정렬 */
}

/* 라벨 스타일 */
.label {
  font-weight: bold;
  min-width: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.message.user .label {
  color: #ea002c;
  margin-right: 8px;
}

.message.ai .label {
  color: #f74a19;
  margin-left: 8px;
}

/* 버블 스타일 */
.bubble {
  background-color: #f2f2f2;
  padding: 10px 14px;
  border-radius: 8px;
  max-width: 70%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  box-sizing: border-box;
}

/* 사용자와 AI의 버블 색상 구분 */
.message.user .bubble {
  background-color: #f0f0f0;
  border-radius: 8px 8px 8px 0; /* 왼쪽 아래 모서리 뾰족하게 */
}

.message.ai .bubble {
  background-color: #ea002c10; /* 연한 빨간색 배경 */
  border-radius: 8px 8px 0 8px; /* 오른쪽 아래 모서리 뾰족하게 */
}

.divider {
  text-align: center;
  margin: 16px 0;
  font-size: 14px;
  color: #ea002c;
  border-top: 1px dashed #ea002c;
  padding-top: 8px;
}

.call-button {
  width: 60px;
  height: 60px;
  background-color: #ea002c;
  color: white;
  font-size: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: center;
  margin-top: 16px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.1s ease;
  line-height: 1;
  text-align: center;
  padding: 0;
}

.call-button:hover {
  transform: scale(1.05);
}

.recording-status {
  margin: 12px 0;
  font-weight: bold;
  color: green;
  text-align: center;
}

.call-button.recording {
  background-color: red;
  color: white;
}

.icon {
  display: inline-block;
  transform: translateY(-1px);
}
</style>
