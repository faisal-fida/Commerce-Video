<template>
  <div id="app" class="min-h-screen bg-black">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('Scene to Screen Vue.js App initialized')
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  background-color: #000000;
}
</style>