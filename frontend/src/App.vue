<template>
  <StartScreen v-if="showStart" @start="handleStart" />

  <div v-else class="app">
    <!-- Top bar -->
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
        <div class="description">
          <h2>Description</h2>
          <p class="desc">{{ currentDescription }}</p>

          <div class="refs">
            <img
              v-for="src in refImages"
              :key="src"
              :src="src"
              class="ref"
              @error="(e) => (e.target.style.opacity = 0.2)"
            />
          </div>
        </div>

        <div class="nav">
          <button @click="prev" :disabled="step === 1">Previous step</button>
          <button @click="next" :disabled="!canNext">
            Next step
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
          class="btn-act"
          @click="generate"
          :disabled="!readyToGenerate"
        >
          {{ image ? "Regenerate" : "Generate" }}
        </button>
      </div>

      
      <!-- middle: image -->
<!-- middle: image -->
<div class="result-image">
  <h2>Result</h2>

  <div class="image-wrap">
    <!-- Render only if there is a preview or final image -->
    <img
      v-if="isLoading ? previewImage : image"
      :src="'data:image/png;base64,' + (isLoading ? previewImage : image)"
      alt="generated"
      class="result-img"
      :class="{ loading: isLoading }"
    />

    <!-- Overlay progress while generating -->
    <div v-if="isLoading" class="overlay">
      <div class="overlay-card">
        <p class="overlay-title">Generating: {{ progress.toFixed(1) }}%</p>
        <progress class="progress-bar" :value="progress" max="100"></progress>
      </div>
    </div>

    <!-- Placeholder text if no image has been generated yet -->
    <div v-if="!isLoading && !image" class="placeholder">
      <p>No image generated yet</p>
    </div>
  </div>
</div>




      <!-- right: actions -->
      <div class="result-actions">
        <button class="btn-act" @click="saveImage" :disabled="!image">
          Save
        </button>
        <button class="btn-act" @click="resetAll">From the beginning</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import StepButtons from "./components/StepButtons.vue";
import axios from "axios";
import StartScreen from "./components/StartSreen.vue";
import { descriptions } from "./data/descriptions.js";

import {
  garments,
  silhouettes,
  styles,
  colors,
  patterns,
  materials,
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

const showStart = ref(true);

function handleStart() {
  showStart.value = false; // hide start page, show your wizard
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

// src/data/styleDescriptions.js
const styleDescriptions = {
  grunge: `in grunge fashion style — inspired by 1990s Seattle subculture, emphasizing a raw, layered, and worn-in look. Key elements include distressed or ripped fabrics, and combat boots. The palette leans toward muted and earthy tones, creating a casual and rebellious atmosphere.`,

  minimalist: `in minimalist fashion style — focused on simplicity, clean lines, and a "less is more" philosophy. Outfits feature smooth silhouettes, and refined tailoring with high-quality materials. Accessories are minimal, emphasizing proportion, structure, and timeless elegance.`,

  lolita: `in Lolita fashion style — inspired by Victorian and Rococo aesthetics, emphasizing modesty, femininity, and elegance. Characterized by lace trims, puffed sleeves, ribbon bows, and delicate accessories like Mary Jane shoes, bonnets, and parasols, creating a soft doll-like impression.`,

  goth: `in Gothic fashion style — rooted in Victorian and post-punk aesthetics, combining dark romanticism, elegance, and mystery. Features include black or deep-toned garments, lace, velvet, corset details, puffed sleeves, and silver accessories with cross or rose motifs. The mood is moody, introspective, and poetic.`,

  punk: `in punk fashion style — expressing rebellion, DIY creativity, and anti-establishment attitude. Key elements include leather, ripped shirts, metal studs, band tees, safety pins, and unconventional layering. The look is aggressive, raw, and intentionally imperfect.`,

  "hip-hop": `in hip-hop fashion style — originating from 1980s–1990s street culture in the U.S., blending comfort, bold branding, and attitude. Outfits feature baggy oversized clothes, tracksuits, sneakers, and gold accessories. The look communicates confidence, rhythm, and individuality.` 
};

function buildFullSDPrompt(sel) {
  // === Header ===
  const header =
    "RAW photo, best quality, photo-realistic, 1 beautiful adult female model, short hair,";

  // === Garment core ===
  const garmentParts = [];

  // e.g. "red blazer jacket in camouflage pattern"
  if (sel.color) garmentParts.push(sel.color);
  if (sel.silhouette) garmentParts.push(sel.silhouette);
  if (sel.garment) garmentParts.push(sel.garment);

  let garmentDesc = garmentParts.join(" ");

  // Add pattern
  if (sel.pattern && sel.pattern.toLowerCase() !== "none") {
    garmentDesc += ` in ${sel.pattern} pattern`;
  }

  // === Material ===
  let materialPart = "";
  if (sel.material) {
    if (sel.material.toLowerCase() === "silk") {
      materialPart = `shiny ${sel.material} material`;
    } else {
      materialPart = `${sel.material} material`;
    }
  }
  // === Restrict pattern placement ===
  const plainClothing =
    sel.garment && sel.pattern && sel.pattern.toLowerCase() !== "none"
      ? `clothing other than the ${sel.garment} is plain color`
      : "";

  // === Style description ===
  const stylePart = sel.style
    ? `in ${sel.style} fashion style — ${
        styleDescriptions[sel.style] || `${sel.style} style`
      }`
    : "";

  // === Lighting & composition ===
  const lighting = "light background, soft light,";
  const framing =
    "full body shot, standing pose, model from head to toe, neutral stance, long shot, entire body visible, centered";

  // === Combine ===
  const prompt = [
    header,
    `${garmentDesc}${materialPart ? `, ${materialPart}` : ""},`,
    plainClothing,
    stylePart,
    lighting,
    framing,
  ]
    .filter(Boolean)
    .join("\n");

  // For debugging in browser console
  console.log("🧠 Final SD Prompt:\n", prompt);

  return prompt;
}




function cap(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

const isLoading = ref(false);
const image = ref(null);
const apiPrompt = ref("");

const progress = ref(0);
const previewImage = ref(null);

async function generate() {
  if (isLoading.value) return; // prevent double-clicks
  isLoading.value = true;
  progress.value = 0;
  previewImage.value = null;

  let poller = null;

  try {
    const prompt = buildFullSDPrompt(selection);

    // 2️⃣ Log it to the browser console
    console.log("🧠 Sending prompt to Stable Diffusion:\n", prompt);

    // --- start polling progress ---
    poller = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/progress");
        const data = await res.json();
        progress.value = data.progress || 0;
        previewImage.value = data.current_image || null;
      } catch (err) {
        console.error("Progress polling failed:", err);
      }
    }, 1000);

    // --- send generation request ---
    const res = await axios.post("http://127.0.0.1:8000/generate", { prompt });
    image.value = res.data.images?.[0] || null;
    apiPrompt.value = res.data.prompt || prompt;
    step.value = 7;

  } catch (e) {
    alert("Generation failed. Is FastAPI / SD running?\n" + e);
  } finally {
    if (poller) clearInterval(poller);
    progress.value = 100;
    isLoading.value = false;
  }
}


function slug(s = "") {
  return s.toLowerCase().replace(/[’']/g, "").replace(/\s+/g, "-");
}

const currentDescription = computed(() => {
  const s = selection;
  if (step.value === 1 && s.garment) {
    return descriptions.garment[s.garment] || "";
  }
  if (step.value === 2 && s.garment && s.silhouette) {
    return descriptions.silhouette?.[s.garment]?.[s.silhouette] || "";
  }
  if (step.value === 3 && s.style) return descriptions.style[s.style] || "";
  if (step.value === 4 && s.color) return descriptions.color[s.color] || "";
  if (step.value === 5 && s.pattern)
    return descriptions.pattern[s.pattern] || "";
  if (step.value === 6 && s.material)
    return descriptions.material[s.material] || "";
  return "Choose an option on the left to see its description and references.";
});

// build 5 sample image URLs from /public/samples/...
function range(n) {
  return Array.from({ length: n }, (_, i) => i + 1);
}
const refImages = computed(() => {
  const base = "/samples";
  if (step.value === 1 && selection.garment) {
    return range(5).map(
      (i) => `${base}/garment/${slug(selection.garment)}/${i}.png`
    );
  }
  if (step.value === 2 && selection.garment && selection.silhouette) {
    return range(5).map(
      (i) =>
        `${base}/silhouette/${slug(selection.garment)}/${slug(
          selection.silhouette
        )}/${i}.jpg`
    );
  }
  if (step.value === 3 && selection.style) {
    return range(5).map(
      (i) => `${base}/style/${slug(selection.style)}/${i}.jpg`
    );
  }
  if (step.value === 4 && selection.color) {
    return range(5).map(
      (i) => `${base}/color/${slug(selection.color)}/${i}.jpg`
    );
  }
  if (step.value === 5 && selection.pattern) {
    return range(5).map(
      (i) => `${base}/pattern/${slug(selection.pattern)}/${i}.jpg`
    );
  }
  if (step.value === 6 && selection.material) {
    return range(5).map(
      (i) => `${base}/material/${slug(selection.material)}/${i}.jpg`
    );
  }
  return [];
});

async function saveImage() {
  if (!image.value) return;

  try {
    // If your image is already the raw base64 (no data URL prefix), send directly.
    // If you ever pass a full data URL, strip it:
    // const raw = image.value.replace(/^data:image\/\w+;base64,/, "");

    const payload = {
      image_base64: image.value,                 // raw base64 from SD
      filename: `design_${Date.now()}.png`,      // optional; backend can auto-name
    };

    const res = await axios.post("http://127.0.0.1:8000/save_image", payload);
    const { ok, saved_path } = res.data || {};

    if (ok) {
      console.log("✅ Saved at:", saved_path);
      alert("Saved to:\n" + saved_path);
    } else {
      alert("Save failed. Please check the backend logs.");
    }
  } catch (err) {
    console.error(err);
    alert("Save failed: " + (err?.response?.data?.detail || err.message));
  }
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
.app{
  min-width: 1280px;
}

.left {
  margin-top: 50px;
}

.stepper {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  justify-content: center;
}
.chip {
  padding: 8px 14px;
  border: 2px solid #f43f5e;
  border-radius: 999px;
  color: #f43f5e;
  background: #ffffff;
  cursor: pointer;
  font-size: 11pt;
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
  min-height: 200px;
}

.center
{
  min-width: 650px;
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
  width: 130px;
  object-fit: fill;
}

.nav {
    margin-top: 28px;
    display: flex;
    gap: 64px;
    justify-content: center;
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
  margin-top: 24px;
  max-width: 285px;
  margin-left: 30px;
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
    grid-template-columns: 304px 496px 216px;
    gap: 83px;
    align-items: start;
    margin-top: 10px;
}

.result-image{
    display: flex;
    flex-direction: column;
    align-items: center;
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

.description {
  min-height: 350px;
}
.github {
  height: 36px;
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

.placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #111;
  color: #777;
  font-size: 14px;
  border-radius: 12px;
  opacity: 0.8;
}


/* top navigation */
.stepper {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.start-wrap {
  background: #000;
  color: #fff;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
}
.brand {
  font-weight: 700;
  font-size: 22px;
  letter-spacing: 0.2px;
}
.gh {
  color: #ff6b6b;
  opacity: 0.85;
}
.gh:hover {
  opacity: 1;
}
.divider {
  height: 2px;
  background: #ffffff;
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.15) inset;
  margin-bottom: 30px;
}

.hero {
  max-width: 720px;
  margin: 72px auto 0;
  text-align: center;
  padding: 0 16px;
}
.hero h1 {
  font-size: 20px;
  line-height: 1.5;
  margin: 0;
}
.lead {
  margin: 14px 0 8px;
  color: #f3f3f3;
  line-height: 1.7;
}
.muted {
  color: #cfcfcf;
  margin: 10px 0 26px;
}

.start-btn {
  background: #f43f5e;
  color: #fff;
  border: none;
  padding: 12px 32px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(244, 63, 94, 0.25);
}
.start-btn:hover {
  filter: brightness(1.05);
}

.image-wrap {
  position: relative;
  width: 460px;                /* set the display size you want */
  aspect-ratio: 7 / 10;        /* keeps height stable (no jump) */
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  background: #151515;         /* fallback while preview not ready */
  box-shadow: 0 6px 24px rgba(0,0,0,0.35);
}

.image-wrap img {
  display: block;
  width: 100%;
}


/* The image always fills the frame */
.result-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 200ms ease, opacity 200ms ease;
}

/* Slight blur/dim while generating (optional) */
.result-img.loading {
  filter: blur(2px) brightness(0.8);
}

/* Progress overlay */
.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;       /* put bar near bottom; use center if preferred */
  justify-content: center;
  background: linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(0,0,0,0.55) 100%);
  padding: 16px;
}

.overlay-card {
  width: 88%;
  max-width: 320px;
  backdrop-filter: blur(6px);
}

.overlay-title {
  margin: 0 0 6px;
  font-weight: 600;
  font-size: 14px;
  color: #fff;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  overflow: hidden;
}



</style>
