<template>
  <div class="h-full bg-black/90 backdrop-blur-xl border-t border-white/10">
    <div class="p-4 space-y-4 h-full overflow-hidden">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Package class="w-5 h-5 text-purple-400" />
          <h2 class="text-white font-semibold">Smart Bundles</h2>
        </div>
        <div class="text-xs text-gray-400">
          {{ bundles.length }} {{ bundles.length === 1 ? 'bundle' : 'bundles' }} available
        </div>
      </div>

      <div class="flex-1 overflow-y-auto custom-scrollbar pb-20">
        <div class="space-y-4">
          <div
            v-for="(bundle, index) in bundles"
            :key="bundle.id"
            v-motion
            :initial="{ opacity: 0, x: -20 }"
            :enter="{ opacity: 1, x: 0 }"
            :transition="{ delay: index * 0.15 }"
            class="group bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden hover:bg-white/10 transition-all duration-300"
          >
            <div class="flex">
              <!-- Bundle Image -->
              <div class="w-24 h-24 flex-shrink-0">
                <img
                  :src="bundle.image_url || bundle.image"
                  :alt="bundle.name"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
              </div>

              <!-- Bundle Info -->
              <div class="flex-1 p-4">
                <div class="flex items-start justify-between mb-2">
                  <div class="flex-1">
                    <span
                      :class="[
                        'inline-block text-xs mb-2 px-2 py-1 rounded border',
                        getCategoryColor(bundle.category)
                      ]"
                    >
                      {{ formatCategory(bundle.category) }}
                    </span>
                    <h3 class="text-white font-medium text-sm leading-tight mb-1">
                      {{ bundle.name }}
                    </h3>
                    <p class="text-white/60 text-xs line-clamp-2">
                      {{ bundle.description }}
                    </p>
                  </div>
                </div>

                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span
                      v-if="bundle.discount_price && bundle.discount_price < bundle.total_price"
                      class="text-white/60 text-sm line-through"
                    >
                      ${{ bundle.total_price.toFixed(2) }}
                    </span>
                    <span class="text-white font-semibold">
                      ${{ (bundle.discount_price || bundle.total_price).toFixed(2) }}
                    </span>
                    <span
                      v-if="bundle.discount_price && bundle.discount_price < bundle.total_price"
                      class="text-xs bg-green-500/20 text-green-300 border border-green-500/30 px-2 py-1 rounded flex items-center"
                    >
                      <Tag class="w-2 h-2 mr-1" />
                      Save ${{ (bundle.total_price - bundle.discount_price).toFixed(2) }}
                    </span>
                  </div>

                  <button
                    class="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white text-xs px-3 py-1 rounded flex items-center transition-colors"
                    @click="$emit('add-to-cart', bundle)"
                  >
                    <ShoppingCart class="w-3 h-3 mr-1" />
                    Add Bundle
                  </button>
                </div>

                <!-- Items Count, Time Range, and Similarity -->
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-center gap-3">
                    <div class="flex items-center gap-1">
                      <Star class="w-3 h-3 text-yellow-400" />
                      <span class="text-white/60 text-xs">
                        {{ bundle.product_ids?.length || bundle.products?.length || 0 }} items
                      </span>
                    </div>
                    <!-- Show time range for time-based bundles -->
                    <div v-if="bundle.time_range" class="text-xs text-blue-300 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20 flex items-center gap-1">
                      <Clock class="w-3 h-3" />
                      {{ bundle.time_range }}
                    </div>
                  </div>
                  <div v-if="bundle.similarity_score" class="text-xs text-cyan-300 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/20">
                    {{ Math.round(bundle.similarity_score * 100) }}% match
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Package, ShoppingCart, Star, Tag, Clock } from 'lucide-vue-next'

const props = defineProps({
  bundles: {
    type: Array,
    default: () => []
  }
})

defineEmits(['add-to-cart'])

// Methods
const categoryColors = {
  wardrobe: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
  'home-setup': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  'tech-bundle': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  'skincare-routine': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  'workout-gear': 'bg-green-500/20 text-green-300 border-green-500/30'
}

const getCategoryColor = (category) => {
  return categoryColors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30'
}

const formatCategory = (category) => {
  return category ? category.replace('-', ' ') : 'Bundle'
}
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>