<template>
  <div class="step-buttons">
    <button
      v-for="opt in options"
      :key="opt.value"
      :class="['btn', opt.value === modelValue ? 'btn-active' : '']"
      @click="$emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({ options: Array, modelValue: String });
defineEmits(["update:modelValue"]);
</script>

<style scoped>
.step-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.btn {
  padding: 10px 14px;
  border: 2px solid #f8657e;
  color: #f8657e;
  background: #ffffff;
  text-align: center;
  max-width: 175px;
}
.btn-active {
  background: #f43f5e;
  color: #ffffff;
}
</style>
