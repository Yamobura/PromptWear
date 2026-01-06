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
This interactive tool guides users through the six key elements of fashion design: garment type, silhouette, style, color, pattern, and material. At each step, reference images and explanations help learners understand how each element influences the visual outcome in actual fashion design. The selected elements are automatically combined into a structured AI image-generation prompt, allowing the user’s design choices to be visualized.

Users can freely experiment and compare results, observing how even small changes can alter the overall image. After completing all selections, the final AI-generated image can be viewed on the Result page.
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
