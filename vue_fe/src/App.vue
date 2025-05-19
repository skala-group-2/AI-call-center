<template>
  <div class="container">
    <div class="half left">
      <LeftPage />
    </div>
    <div class="half right">
      <RightPage />
    </div>
  </div>
</template>

<script setup>
import LeftPage from "./components/LeftPage.vue";
import RightPage from "./components/RightPage.vue";
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
  overflow: hidden;
}
</style>

<style scoped>
.container {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.half {
  flex: 1;
  height: 100%;
  box-sizing: border-box;
  min-width: 0;
  max-width: 50%; /* 최대 너비를 50%로 제한 */
  overflow: hidden; /* 내용이 넘치지 않도록 함 */
}

.left {
  border-right: 1px solid #eee;
}
.right {
  background-color: white;
}
</style>
