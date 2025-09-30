<template>
        <header class="topbar">
      <div class="brand"> <a href="http://localhost:5173/" >PromptWear</a></div>
<div>      <a href="#"><img class="github" src="C:\Users\user\Documents\lidia\lidia\thesis\PromptWear\frontend\public\social.png" alt=""></a>
</div>
      
    </header>
    <div class="divider"></div>
  <div class="start-wrap">
    

    <!-- Center content -->
    <main class="hero">
      <h1><strong>PromptWear</strong> is a step-by-step learning application for fashion designers.</h1>
      <p class="lead">
        This tool guides you through six core elements—<b>garment</b>, <b>silhouette</b>, <b>style</b>, <b>color</b>,
        <b>pattern</b>, and <b>material</b>—and assembles a structured prompt for AI image generation.
        Use the reference images and descriptions to learn, refine choices freely, and produce a final look on the <b>Result</b> page.
      </p>
      <p class="muted">Begin exploring how input decisions affect the output image.</p>

      <button class="start-btn" @click="$emit('start')">Start</button>
    </main>
  </div>
</template>

<script setup>
defineProps({
  githubUrl: { type: String, default: '' } // optional top-right icon link
})
</script>

<style scoped>

</style>
