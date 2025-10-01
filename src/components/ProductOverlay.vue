<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="products.length" class="fixed inset-0 z-40">
        <!-- Backdrop -->
        <div
          v-motion
          :initial="{ opacity: 0 }"
          :enter="{ opacity: 1 }"
          :leave="{ opacity: 0 }"
          class="fixed inset-0 bg-black/20 backdrop-blur-sm"
          @click="$emit('close')"
        />

        <!-- Sliding Panel -->
        <div
          v-motion
          :initial="{ x: '-100%', opacity: 0 }"
          :enter="{ x: 0, opacity: 1 }"
          :leave="{ x: '-100%', opacity: 0 }"
          :transition="{ type: 'spring', damping: 25, stiffness: 200 }"
          class="fixed left-0 top-0 h-full w-80 bg-black/95 backdrop-blur-xl border-r border-white/10 z-50 overflow-hidden"
        >
          <div class="flex flex-col h-full">
            <!-- Header -->
            <div class="p-6 border-b border-white/10">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-semibold text-white">Products</h2>
                <button
                  class="text-white/60 hover:text-white hover:bg-white/10 p-2 rounded transition-colors"
                  @click="$emit('close')"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>

              <div
                v-if="visibleProducts.length > 0"
                class="text-sm text-cyan-300 bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20"
              >
                {{ visibleProducts.length }} item{{ visibleProducts.length !== 1 ? 's' : '' }} featured now
              </div>
            </div>

            <!-- Products List -->
            <div class="flex-1 overflow-y-auto custom-scrollbar">
              <div class="p-4 space-y-4">
                <div
                  v-for="(product, index) in allProducts"
                  :key="product.id"
                  v-motion
                  :initial="{ opacity: 0, y: 20 }"
                  :enter="{ opacity: 1, y: 0 }"
                  :transition="{ delay: index * 0.1 }"
                  :class="[
                    'group relative bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-4 hover:bg-white/10 transition-all duration-300',
                    visibleProducts.includes(product) ? 'ring-2 ring-purple-500/50 bg-purple-500/10' : ''
                  ]"
                >
                  <div class="flex gap-3">
                    <!-- Product Image -->
                    <div class="relative flex-shrink-0">
                      <img
                        :src="getProductImage(product)"
                        :alt="product.name || product.ai_generated_search_query"
                        class="w-16 h-16 object-cover rounded-xl"
                        @error="handleImageError"
                      />
                      <div
                        v-if="visibleProducts.includes(product)"
                        class="absolute -top-1 -right-1 w-4 h-4 bg-purple-500 rounded-full animate-pulse"
                      />
                    </div>

                    <!-- Product Info -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-start justify-between mb-2">
                        <h3 class="font-medium text-white text-sm leading-tight truncate">
                          {{ product.name || product.ai_generated_search_query }}
                        </h3>
                        <button class="w-6 h-6 text-white/60 hover:text-pink-400 opacity-0 group-hover:opacity-100 transition-all duration-200">
                          <Heart class="w-3 h-3" />
                        </button>
                      </div>

                      <span
                        :class="[
                          'inline-block text-xs mb-2 px-2 py-1 rounded border',
                          getCategoryColor(product.category)
                        ]"
                      >
                        {{ formatCategory(product.category) }}
                      </span>

                      <div class="flex items-center justify-between">
                        <span class="text-white font-semibold">
                          ${{ product.price.toFixed(2) }}
                        </span>

                        <div class="flex gap-1">
                          <button class="h-7 px-2 text-white/70 hover:text-white rounded transition-colors">
                            <ExternalLink class="w-3 h-3" />
                          </button>
                          <button
                            class="h-7 px-3 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white text-xs rounded flex items-center transition-colors"
                            @click="$emit('add-to-cart', product)"
                          >
                            <ShoppingCart class="w-3 h-3 mr-1" />
                            Add
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X, ShoppingCart, Heart, ExternalLink } from 'lucide-vue-next'

const props = defineProps({
  products: {
    type: Array,
    default: () => []
  },
  currentTime: {
    type: Number,
    default: 0
  }
})

defineEmits(['close', 'add-to-cart'])

// Computed properties
const visibleProducts = computed(() => {
  return props.products.filter(product => {
    // Use original_detection_time for analyzed products
    if (product.original_detection_time !== undefined) {
      return Math.abs(product.original_detection_time - props.currentTime) <= 2
    }
    // Fallback to legacy time comparison
    return Math.abs((product.video_timestamp || product.timeStart || 0) - props.currentTime) < 5
  })
})

const allProducts = computed(() => {
  return props.products.slice(0, 8) // Show max 8 products
})

// Methods
const categoryColors = {
  fashion: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
  'home-decor': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  electronics: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  kids: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  beauty: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  fitness: 'bg-green-500/20 text-green-300 border-green-500/30',
  outerwear: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  bottoms: 'bg-teal-500/20 text-teal-300 border-teal-500/30'
}

const getCategoryColor = (category) => {
  return categoryColors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30'
}

const formatCategory = (category) => {
  return category.replace('-', ' ')
}

// Get product image (prioritize local images)
const getProductImage = (product) => {
  // For analyzed products, prioritize local images from searched_images folder
  if (product.local_images && product.local_images.length > 0) {
    return product.local_images[0].local_path
  }

  // Fallback to online images
  if (product.found_online_images && product.found_online_images.length > 0) {
    return product.found_online_images[0].image_url
  }

  // Fallback to legacy image properties
  return product.image_url || product.image || '/placeholder.jpg'
}

// Handle image loading errors
const handleImageError = (event) => {
  console.warn('Image failed to load:', event.target.src)
  // Set a placeholder image instead of hiding
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjMzMzMzMzIi8+Cjx0ZXh0IHg9IjUwIiB5PSI1NSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkZhaWxlZCBMb2FkPC90ZXh0Pgo8L3N2Zz4K'
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

.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.3s ease;
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}
</style>