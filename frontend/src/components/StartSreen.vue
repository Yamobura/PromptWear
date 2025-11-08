<template>
  <header class="topbar">
    <div class="brand"><a href="http://localhost:5173/">PromptWear</a></div>
    <div>
      <a href="#"
        ><img
          class="github"
          src="/social.png"
          alt=""
      /></a>
    </div>
  </header>
  <div class="divider"></div>
  <div class="start-wrap">
    <!-- Center content -->
    <main class="hero">
      <h1>
        <strong>PromptWear</strong> is a step-by-step learning application for
        fashion designers.
      </h1>
      <p class="lead">
        이 인터랙티브 도구는 패션 디자인의 여섯 가지 핵심 요소인
의복 종류, 실루엣, 스타일, 색상, 패턴, 소재를 단계별로 탐색하도록 안내합니다.
<br>
각 단계에서 제공되는 참고 이미지와 설명을 통해 실제 패션 디자인에서 각 요소가 어떻게 시각적 결과에 영향을 미치는지 배울 수 있습니다.
선택한 요소들은 자동으로 구조화된 AI 이미지 생성 프롬프트로 조합되어, 사용자의 디자인을 시각적으로 표현합니다.
<br>
원하는 대로 실험하고, 결과를 비교해보세요.
작은 변화 하나로 전체 이미지가 어떻게 달라지는지 확인할 수 있습니다.
모든 선택을 마치면 결과 페이지(Result) 에서 AI가 생성한 최종 이미지를 확인하세요.
      </p>

      <button class="start-btn" @click="$emit('start')">Start</button>
    </main>
  </div>
</template>

<script setup>
defineProps({
  githubUrl: { type: String, default: "" }, // optional top-right icon link
});
</script>

<style scoped></style>
