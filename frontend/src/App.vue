<template>
    <StartScreen v-if="showStart" @start="handleStart" />

  <div v-else class="app">
    <!-- Top bar -->
    <header class="topbar">
      <div class="brand"> <a href="http://localhost:5173/" >PromptWear</a></div>
<div>      <a href="#"><img class="github" src="C:\Users\user\Documents\lidia\lidia\thesis\PromptWear\frontend\public\social.png" alt=""></a>
</div>
      
    </header>
    <div class="divider"></div>
    <!-- Stepper -->
    <div class="stepper">
      <button
        v-for="(t, i) in tabs"
        :key="t"
        class="chip"
        :class="{ active: step === i + 1, locked: !canGoTo(i + 1) }"
        @click="goTo(i + 1)"
      >
        {{ i + 1 }}. {{ t }}
      </button>
    </div>

    <!-- Steps 1–6 (your current layout) -->
    <div v-if="step !== 7" class="grid">
      <!-- Left options -->
      <div class="left">
        <StepButtons
          v-if="step === 1"
          v-model="selection.garment"
          :options="opts(garments)"
        />
        <StepButtons
          v-else-if="step === 2"
          v-model="selection.silhouette"
          :options="opts(silhouettes[selection.garment || 'shirt'] || [])"
        />
        <StepButtons
          v-else-if="step === 3"
          v-model="selection.style"
          :options="opts(styles)"
        />
        <StepButtons
          v-else-if="step === 4"
          v-model="selection.color"
          :options="opts(colors)"
        />
        <StepButtons
          v-else-if="step === 5"
          v-model="selection.pattern"
          :options="opts(patterns)"
        />
        <StepButtons
          v-else-if="step === 6"
          v-model="selection.material"
          :options="opts(materials)"
        />
      </div>

      <!-- Center description -->
      <div class="center">
        <h2>Description</h2>
<p class="desc">{{ currentDescription }}</p>

<div class="refs">
  <img v-for="src in refImages"
       :key="src"
       :src="src"
       class="ref"
       @error="e => e.target.style.opacity = 0.2"
  />
</div>
        <div class="nav">
          <button @click="prev" :disabled="step === 1">Previous step</button>
          <button @click="next" :disabled="!canNext">
            Next: {{ nextLabel }}
          </button>
        </div>
      </div>

      <!-- Right prompt + generate -->
      <div class="right">
        <h2>Design prompt</h2>
        <div class="prompt-box">{{ naturalPrompt }}</div>
      </div>
    </div>

    <!-- Step 7: RESULT LAYOUT -->
    <div v-else class="result-layout">
      <!-- left: prompt + Generate/Regenerate -->
      <div class="result-prompt">
        <h2>Design prompt</h2>
        <p class="prompt-preview">{{ naturalPrompt }}</p>

        <button
          class="btn-act primary"
          @click="generate"
          :disabled="!readyToGenerate"
        >
          {{ image ? "Regenerate" : "Generate" }}
        </button>
      </div>

      <!-- middle: image -->
      <div class="result-image">
        <h2>Result</h2>
        <div class="image-wrap" v-if="image">
          <img :src="'data:image/png;base64,' + image" alt="generated" />
        </div>
        <div v-else class="image-placeholder">No image yet</div>
      </div>

      <!-- right: actions -->
      <div class="result-actions">
        <button class="btn-act" @click="saveImage" :disabled="!image">
          Save
        </button>
        <button class="btn-act" @click="resetAll">From the beginning</button>
      </div>

      <div class="nav"><button @click="prev">Previous step</button></div>
    </div>
  </div>
</template>

<script setup>
import StepButtons from "./components/StepButtons.vue";
import axios from "axios";
import StartScreen from './components/StartSreen.vue'
import { descriptions } from './data/descriptions.js'


import {
  garments,
  silhouettes,
  styles,
  colors,
  patterns,
  materials
} from "./taxonomy.js";
import { reactive, computed, ref, watch } from "vue";

const tabs = [
  "Garment",
  "Silhouette",
  "Style",
  "Color",
  "Pattern",
  "Material",
  "Result",
];
const step = ref(1);
const selection = reactive({
  garment: "",
  silhouette: "",
  style: "",
  color: "",
  pattern: "",
  material: "",
});

const showStart = ref(true)

function handleStart () {
  showStart.value = false     // hide start page, show your wizard
  // optional: step.value = 1  // if you want to force step 1 on start
}


// Reset silhouette when garment changes (avoids mismatched combos)
watch(
  () => selection.garment,
  () => {
    selection.silhouette = "";
  }
);

function opts(list) {
  return list.map((v) => ({ label: cap(v), value: v }));
}
function next() {
  step.value = Math.min(7, step.value + 1);
}
function prev() {
  step.value = Math.max(1, step.value - 1);
}

const canNext = computed(() => {
  const need = {
    1: "garment",
    2: "silhouette",
    3: "style",
    4: "color",
    5: "pattern",
    6: "material",
  };
  const key = need[step.value];
  return key ? !!selection[key] : true;
});
const readyToGenerate = computed(
  () =>
    !!(
      selection.garment &&
      selection.silhouette &&
      selection.style &&
      selection.color &&
      selection.pattern &&
      selection.material
    )
);
const nextLabel = computed(
  () =>
    ["", "Silhouette", "Style", "Color", "Pattern", "Material", "Result"][
      step.value
    ] || "Result"
);

const naturalPrompt = computed(() => {
  // human-readable preview on the right
  const { color, silhouette, material, garment, pattern, style } = selection;
  const parts = [];
  if (color) parts.push(color);
  if (silhouette) parts.push(silhouette);
  if (material) parts.push(material);
  if (garment) parts.push(garment);
  if (pattern && pattern !== "none") parts.push(`with ${pattern} pattern`);
  if (style) parts.push(`in ${style} style`);
  return parts.length ? `A ${parts.join(" ")}` : "—";
});

function buildFullSDPrompt(sel) {
  // This matches your spec: header + weighted attributes + BREAK + lighting + framing
  const header =
    "RAW photo, best quality, photo-realistic, 1 girl, beautiful white shiny skin, short hair";

  const parts = [];
  if (sel.color) parts.push(sel.color);
  if (sel.silhouette) parts.push(sel.silhouette);
  if (sel.material) parts.push(sel.material);
  if (sel.garment) parts.push(sel.garment);
  if (sel.pattern && sel.pattern !== "none")
    parts.push(`with ${sel.pattern} pattern`);
  if (sel.style) parts.push(`in ${sel.style} style`);
  const natural = parts.length ? "A " + parts.join(" ") : "";

  const weighted = [];
  const csg = [sel.color, sel.silhouette, sel.garment]
    .filter(Boolean)
    .join(" ");
  if (csg) weighted.push(`((${csg}:1.5))`);
  if (sel.material) weighted.push(`((${sel.material}:1.4))`);
  if (sel.pattern && sel.pattern !== "none")
    weighted.push(`((${sel.pattern}:1.3))`);
  if (sel.style) weighted.push(`((${sel.style} style:1.2))`);

  const lighting = "black background, studio light, soft light";
  const framing =
    "(full body, standing pose, from head to toe, neutral stance, long shot, entire body visible, centered)";

  return `${header}, ${natural}, ${weighted.join(
    ", "
  )}\nBREAK\n${lighting},\n${framing}`;
}

function describe() {
  if (step.value === 1 && selection.garment)
    return descriptions[selection.garment] || "";
  return "Choose an option on the left to see its description and references.";
}

function cap(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

const image = ref(null);
const apiPrompt = ref("");

async function generate() {
  try {
    const prompt = buildFullSDPrompt(selection); // build the full prompt here
    const res = await axios.post("http://127.0.0.1:8000/generate", {
      prompt, // Route B: POST /generate expects { prompt }
    });
    image.value = res.data.images?.[0] || null;
    apiPrompt.value = res.data.prompt || prompt;
    step.value = 7;
  } catch (e) {
    alert("Generation failed. Is FastAPI / SD running?\n" + e);
  }
}

async function regenerate() {
  // call generate again with the same selection
  await generate();
}

function slug(s=''){
  return s.toLowerCase().replace(/[’']/g,'').replace(/\s+/g,'-')
}

const currentDescription = computed(() => {
  const s = selection
  if (step.value === 1 && s.garment) {
    return descriptions.garment[s.garment] || ''
  }
  if (step.value === 2 && s.garment && s.silhouette) {
    return descriptions.silhouette?.[s.garment]?.[s.silhouette] || ''
  }
  if (step.value === 3 && s.style)   return descriptions.style[s.style]   || ''
  if (step.value === 4 && s.color)   return descriptions.color[s.color]   || ''
  if (step.value === 5 && s.pattern) return descriptions.pattern[s.pattern]|| ''
  if (step.value === 6 && s.material)return descriptions.material[s.material]|| ''
  return 'Choose an option on the left to see its description and references.'
})

// build 5 sample image URLs from /public/samples/...
function range(n){ return Array.from({length:n},(_,i)=>i+1) }
const refImages = computed(() => {
  const base = '/samples'
  if (step.value === 1 && selection.garment) {
    return range(5).map(i => `${base}/garment/${slug(selection.garment)}/${i}.png`)
  }
  if (step.value === 2 && selection.garment && selection.silhouette) {
    return range(5).map(i => `${base}/silhouette/${slug(selection.garment)}/${slug(selection.silhouette)}/${i}.jpg`)
  }
  if (step.value === 3 && selection.style) {
    return range(5).map(i => `${base}/style/${slug(selection.style)}/${i}.jpg`)
  }
  if (step.value === 4 && selection.color) {
    return range(5).map(i => `${base}/color/${slug(selection.color)}/${i}.jpg`)
  }
  if (step.value === 5 && selection.pattern) {
    return range(5).map(i => `${base}/pattern/${slug(selection.pattern)}/${i}.jpg`)
  }
  if (step.value === 6 && selection.material) {
    return range(5).map(i => `${base}/material/${slug(selection.material)}/${i}.jpg`)
  }
  return []
})

function saveImage() {
  if (!image.value) return;
  const a = document.createElement("a");
  a.href = "data:image/png;base64," + image.value;
  a.download = `design_${Date.now()}.png`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function resetAll() {
  selection.garment = "";
  selection.silhouette = "";
  selection.style = "";
  selection.color = "";
  selection.pattern = "";
  selection.material = "";
  image.value = null;
  apiPrompt.value = "";
  step.value = 1;
}

const prereq = {
  1: [],
  2: ["garment"],
  3: ["garment", "silhouette"],
  4: ["garment", "silhouette", "style"],
  5: ["garment", "silhouette", "style", "color"],
  6: ["garment", "silhouette", "style", "color", "pattern"],
  7: ["garment", "silhouette", "style", "color", "pattern", "material"],
};

function hasAll(keys) {
  return keys.every((k) => !!selection[k]);
}

function canGoTo(target) {
  if (target <= step.value) return true; // always allow going back
  return hasAll(prereq[target] || []);
}

function goTo(target) {
  if (target === step.value) return;
  if (target < step.value || canGoTo(target)) {
    step.value = target;
  } else {
    alert("Please complete previous selections first.");
  }
}
</script>

<style>
:root {
  --bg: #000;
  --fg: #fff;
  --mut: #ffffffcc;
  --rose: #f43f5e;
}
* {
  box-sizing: border-box;
}
body,
html,
#app {
  margin: 0;
  height: 100%;
  background: var(--bg);
  color: var(--fg);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto,
    Noto Sans, Arial;
}

.stepper {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.chip {
    padding: 8px 14px;
    border: 2px solid #fff3;
    border-radius: 999px;
    color: #f43f5e;
    background: #ffff;
    cursor: pointer;
    border-color: #f43f5e;
}
.chip.active {
  background: var(--rose);
  color: #ffff;
}
.grid {
  display: grid;
  grid-template-columns: 260px 1fr 340px;
  gap: 20px;
  align-items: start;
}
.center h2,
.right h2 {
  margin: 0 0 10px;
}
.desc {
  color: #fff;
  opacity: 0.9;
  line-height: 1.5;
  min-height: 80px;
  white-space: normal;
  overflow: auto;
  max-height: 180px;
}
.refs {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  margin-top: 10px;
}
.ref {
  background: #ffffff1a;
  border-radius: 0px;
  height: 200px;
}
.nav {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}
.nav button {
  padding: 10px 14px;
  border-radius: 999px;
  background: #ffffff1a;
  color: #fff;
  border: 1px solid #fff3;
}
.nav button:hover {
  background: #ffffff2a;
}
.right .prompt-box {
  background: #ffffff0f;
  padding: 12px;
  border-radius: 12px;
  min-height: 100px;
  white-space: pre-wrap;
}
.generate {
  width: 100%;
  margin-top: 12px;
  padding: 12px;
  border-radius: 12px;
  background: var(--rose);
  color: #000;
  border: none;
  font-weight: 600;
}
.result {
  width: 100%;
  margin-top: 12px;
  border-radius: 12px;
}

.result-layout {
  display: grid;
  grid-template-columns: 1fr 460px 200px;
  gap: 24px;
  align-items: start;
  margin-top: 10px;
}

.result-prompt h2,
.result-image h2 {
  margin: 0 0 12px;
}

.prompt-preview {
  background: #ffffff0f;
  border-radius: 12px;
  padding: 14px;
  min-height: 100px;
  white-space: pre-wrap;
}

.image-wrap {
  background: #111;
  border-radius: 12px;
  overflow: hidden;
  width: 460px;
  /* keep your image around poster-like size */
}
.image-wrap img {
  display: block;
  width: 100%;
  height: auto;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 40px; /* to align roughly with image title */
}
.btn-act {
  background: #f43f5e; /* rose */
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 12px;
  text-align: left;
}
.btn-act:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.github
{
  height: 36px;;
}


.image-placeholder {
  width: 460px;
  height: 460px;
  background: #ffffff12;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #ccc;
}

/* top navigation */
.stepper {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.chip {
  padding: 8px 14px;
  border: 1px solid #fff3;
  border-radius: 999px;
  color: #fff;
  background: #111;
  cursor: pointer;
}
.chip.active {
  background: #f43f5e;
  border-color: #fda4af;
}
.chip.locked {
  opacity: 0.6;
}

.start-wrap { min-height: 100vh; background:#000; color:#fff; }
.topbar { display:flex; align-items:center; justify-content:space-between; padding:16px 24px; }
.brand { font-weight:700; font-size:22px; letter-spacing:0.2px; }
.gh { color:#ff6b6b; opacity:.85; }
.gh:hover { opacity:1; }
.divider { height:2px; background:#ffffff; box-shadow:0 0 0 1px rgba(14,165,233,.15) inset; margin-bottom: 30px; }

.hero { max-width:720px; margin:72px auto 0; text-align:center; padding:0 16px; }
.hero h1 { font-size:20px; line-height:1.5; margin:0; }
.lead { margin:14px 0 8px; color:#f3f3f3; line-height:1.7; }
.muted { color:#cfcfcf; margin:10px 0 26px; }

.start-btn {
  background:#f43f5e; color:#fff; border:none;
  padding:12px 32px; border-radius:10px; font-weight:700; font-size:16px;
  cursor:pointer; box-shadow:0 6px 20px rgba(244,63,94,.25);
}
.start-btn:hover { filter:brightness(1.05); }
</style>
