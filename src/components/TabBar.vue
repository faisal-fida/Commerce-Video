<template>
  <div class="bg-black/90 backdrop-blur-xl border-t border-white/10 px-4 py-2">
    <div class="flex justify-center gap-1 max-w-md mx-auto">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="[
          'relative flex-1 h-12 rounded-xl transition-all duration-300 flex flex-col items-center justify-center gap-1',
          activeTab === tab.id
            ? 'text-white bg-gradient-to-r from-purple-600/20 to-cyan-600/20 border border-purple-500/30'
            : 'text-white/60 hover:text-white hover:bg-white/5'
        ]"
        @click="handleTabChange(tab.id)"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        <span class="text-xs font-medium">{{ tab.label }}</span>

        <div
          v-if="activeTab === tab.id"
          v-motion
          :initial="{ opacity: 0, scale: 0.8 }"
          :enter="{ opacity: 1, scale: 1 }"
          :transition="{ type: 'spring', damping: 25, stiffness: 200 }"
          class="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-cyan-600/10 rounded-xl border border-purple-500/20 -z-10"
        />
      </button>
    </div>
  </div>
</template>

<script setup>
import { Grid, Package, User } from 'lucide-vue-next'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'products'
  }
})

const emit = defineEmits(['update:activeTab', 'toggle-content'])

const tabs = [
  { id: 'products', label: 'Products', icon: Grid },
  { id: 'bundles', label: 'Bundles', icon: Package },
  { id: 'profile', label: 'Profile', icon: User }
]

const handleTabChange = (tabId) => {
  emit('update:activeTab', tabId)
  emit('toggle-content')
}
</script>