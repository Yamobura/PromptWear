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
  border-radius: 10px;
  border: 1px solid #fff3;
  color: #fff;
  background: #ffffff0f;
  text-align: left;
}
.btn-active {
  background: #f43f5e;
  border-color: #fda4af;
}
.btn:hover {
  background: #ffffff1f;
}
</style>
