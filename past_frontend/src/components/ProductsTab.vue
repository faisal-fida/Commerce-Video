<template>
  <div class="h-full bg-black/90 backdrop-blur-xl border-t border-white/10">
    <div class="p-4 space-y-4 h-full overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Search class="w-5 h-5 text-purple-400" />
          <h2 class="text-white font-semibold">Products at {{ formatTime(currentTime) }}</h2>
        </div>
        <div class="text-xs text-gray-400">
          {{ filteredProducts.length }} {{ filteredProducts.length === 1 ? 'item' : 'items' }} found
        </div>
      </div>

      <!-- Time indicator -->
      <div class="flex items-center gap-2 text-xs text-cyan-400 bg-cyan-400/10 px-2 py-1 rounded border border-cyan-400/20">
        <div class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
        <span>Showing products detected at {{ formatTime(currentTime) }} (±3s)</span>
      </div>

      <!-- Category Filter (only show if products exist) -->
      <div v-if="products.length > 0" class="flex gap-2 overflow-x-auto pb-2 overflow-y-auto">
        
        <button
          v-for="category in availableCategories"
          :key="category"
          :class="[
            'whitespace-nowrap px-3 py-1 text-sm rounded border transition-all duration-300',
            activeCategory === category
              ? getCategoryColor(category)
              : 'bg-white/5 text-white/60 border-white/10 hover:bg-white/10'
          ]"
          @click="activeCategory = category"
        >
          {{ formatCategory(category) }}
        </button>
      </div>

      <!-- Products Grid -->
      <div class="flex-1 overflow-y-auto custom-scrollbar pb-20">
        <!-- Empty State -->
        <div v-if="filteredProducts.length === 0" class="flex flex-col items-center justify-center h-64 text-center">
          <div class="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
            <Search class="w-16 h-16 text-white/40" />
          </div>
          <h3 class="text-white/60 font-medium mb-2">
            {{ products.length === 0 ? 'No products detected' : 'No matching products' }}
          </h3>
          <p class="text-white/40 text-sm">
            {{ products.length === 0
              ? 'Upload and analyze a video to discover fashion items'
              : `No ${formatCategory(activeCategory)} items found. Try "All" category.`
            }}
          </p>
        </div>

        <!-- Products Grid -->
        <div v-else class="grid grid-cols-8 gap-4 overflow-auto  ">
          <div
            v-for="(product, index) in filteredProducts"
            :key="product.id"
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :enter="{ opacity: 1, y: 0 }"
            :transition="{ delay: index * 0.1 }"
            class="group bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 p-1 hover:bg-white/10 transition-all duration-300"
          >
            <div class="relative">
              <!-- Product Image(s) -->
              <div class="w-1500 h-1500 relative rounded-md mb-1">
                <!-- Main product image -->
                <img
                  :src="getMainImageUrl(product)"
                  :alt="product.name || product.ai_generated_search_query || 'Product image'"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  @error="handleImageError"
                  @load="handleImageLoad"
                />

                <!-- Image counter if multiple images available -->
                <div v-if="getImageCount(product) > 1"
                     class="absolute bottom-0 right-0 bg-black/70 backdrop-blur-sm text-white text-xs px-1 py-0.5 rounded text-xs leading-none">
                  1/{{ getImageCount(product) }}
                </div>

                <!-- Confidence Badge -->
                <div class="absolute top-0 left-0 bg-black/70 backdrop-blur-sm text-white text-xs px-1 py-0.5 rounded text-xs leading-none">
                  {{ Math.round((product.confidence || 0.8) * 100) }}%
                </div>

                <!-- Hover Overlay with 3 Options -->
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
                  <div class="flex flex-col gap-1">
                    <!-- 1. Add to Cart Button -->
                    <button
                      class="bg-gradient-to-r from-purple-600 to-cyan-600 text-white text-xs px-2 py-1 rounded transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300 flex items-center justify-center min-w-[60px]"
                      @click="$emit('add-to-cart', product)"
                      title="Add to Cart"
                    >
                      <ShoppingCart class="w-3 h-3 mr-1" />
                      Add
                    </button>

                    <!-- 2. View Details Button -->
                    <button
                      class="bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-xs px-2 py-1 rounded transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300 flex items-center justify-center min-w-[60px] delay-75"
                      @click="showProductImages(product)"
                      title="View Product Details"
                    >
                      <Search class="w-3 h-3 mr-1" />
                      View
                    </button>

                    <!-- 3. Add to Favorites Button -->
                    <button
                      class="bg-gradient-to-r from-pink-600 to-red-600 text-white text-xs px-2 py-1 rounded transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300 flex items-center justify-center min-w-[60px] delay-150"
                      @click="$emit('add-to-favorites', product)"
                      title="Add to Favorites"
                    >
                      <Heart class="w-3 h-3 mr-1" />
                      Fave
                    </button>
                  </div>
                </div>
              </div>

              <!-- Product Info -->
              <div class="space-y-0.5">
                <span
                  :class="[
                    'inline-block text-xs px-1 py-0.5 rounded border text-xs leading-none',
                    getCategoryColor(product.category)
                  ]"
                >
                  {{ formatCategory(product.category).substring(0, 3) }}
                </span>

                <h3 class="text-white font-medium text-xs leading-tight line-clamp-1" :title="product.name || product.ai_generated_search_query || product.label">
                  {{ product.name || product.ai_generated_search_query || product.label }}
                </h3>

                <!-- AI Generated Search Query for analyzed products -->
                <div v-if="product.ai_generated_search_query && product.detected_category_from_video" class="text-xs text-purple-300 bg-purple-500/10 px-1 py-0.5 rounded border border-purple-500/20 leading-none">
                  {{ product.detected_category_from_video.substring(0, 8) }}
                </div>

                <!-- YOLO11 Detection Details (legacy) -->
                <div v-else-if="product.class_name" class="text-xs text-purple-300 bg-purple-500/10 px-1 py-0.5 rounded border border-purple-500/20 leading-none">
                  {{ product.class_name.substring(0, 8) }}
                </div>

                <!-- Timestamp info for video products -->
                <p v-if="product.timestamp !== undefined || product.original_detection_time !== undefined" class="text-xs text-cyan-400 leading-none">
                  {{ formatTime(product.original_detection_time !== undefined ? product.original_detection_time : product.timestamp) }}
                </p>

                <div class="flex items-center justify-between">
                  <span class="text-white font-semibold text-xs">
                    ${{ (product.price || 99.99).toFixed(0) }}
                  </span>

                  <button
                    v-if="product.affiliate_url"
                    class="w-4 h-4 text-white/60 hover:text-white transition-colors rounded flex items-center justify-center"
                    @click="openProductLink(product.affiliate_url)"
                  >
                    <ExternalLink class="w-2 h-2" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Product Images Modal -->
    <Transition name="modal">
      <div v-if="showImagesModal" class="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
           @click="closeImagesModal">
        <div class="max-w-4xl w-full bg-gray-900 rounded-lg border border-white/10 overflow-hidden"
             @click.stop>
          <!-- Modal Header -->
          <div class="flex items-center justify-between p-4 border-b border-white/10">
            <div class="flex-1">
              <h3 class="text-white font-semibold">{{ selectedProduct?.ai_generated_search_query || selectedProduct?.name }}</h3>
              <p class="text-gray-400 text-sm">{{ selectedProduct?.detected_category_from_video }}</p>
              <p class="text-cyan-400 text-sm font-semibold mt-1">${{ (selectedProduct?.price || 99.99).toFixed(2) }}</p>
            </div>
            <div class="flex items-center space-x-3">
              <!-- Add to Cart Button -->
              <button
                @click="addToCartAndClose"
                class="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 transform hover:scale-105"
              >
                <ShoppingCart class="w-4 h-4" />
                <span>Add to Cart</span>
              </button>
              <!-- Close Button -->
              <button @click="closeImagesModal"
                      class="text-white/60 hover:text-white p-2 rounded transition-colors">
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Images Grid -->
          <div class="p-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                v-for="(imageInfo, index) in getProductImages(selectedProduct)"
                :key="index"
                class="group bg-white/5 rounded-lg border border-white/10 overflow-hidden hover:border-cyan-400/50 transition-colors"
              >
                <div class="relative aspect-square">
                  <img
                    :src="imageInfo.image_url"
                    :alt="`Product image ${index + 1}`"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    @error="handleImageError"
                  />
                  <!-- Enhanced Overlay with Add to Cart button -->
                  <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col items-center justify-center space-y-2">
                    <!-- Add to Cart Button -->
                    <button
                      @click.stop="emit('add-to-cart', selectedProduct)"
                      class="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 transform hover:scale-105 shadow-lg"
                    >
                      <ShoppingCart class="w-4 h-4" />
                      <span>Add to Cart</span>
                    </button>

                    <!-- Visit Store Button -->
                    <button
                      @click="openProductWebsite(imageInfo.website_url)"
                      class="bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white px-3 py-2 rounded-lg transition-all duration-300 flex items-center space-x-2"
                    >
                      <ExternalLink class="w-4 h-4" />
                      <span class="text-sm">Visit Store</span>
                    </button>
                  </div>
                </div>

                <!-- Image info -->
                <div class="p-3">
                  <p class="text-white text-xs line-clamp-2 mb-2">
                    Shop this item online
                  </p>
                  <p class="text-cyan-400 text-xs hover:text-cyan-300 transition-colors">
                    Click to visit store →
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ShoppingCart, Heart, ExternalLink, Search, X } from 'lucide-vue-next'

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

// Reactive data
const activeCategory = ref('all')
const showImagesModal = ref(false)
const selectedProduct = ref(null)

// Computed properties
const availableCategories = computed(() => {
  const categories = ['all', ...new Set(props.products.map(p => p.category).filter(Boolean))]
  return categories
})

const filteredProducts = computed(() => {
  return activeCategory.value === 'all'
    ? props.products
    : props.products.filter(product => product.category === activeCategory.value)
})

// Methods
const categoryColors = {
  all: 'bg-white/10 text-white border-white/20',
  fashion: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
  'home-decor': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  electronics: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  kids: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  beauty: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  fitness: 'bg-green-500/20 text-green-300 border-green-500/30',
  outerwear: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  bottoms: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
  clothing: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  details: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  other: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  eyewear: 'bg-amber-500/20 text-amber-300 border-amber-500/30'
}

const getCategoryColor = (category) => {
  return categoryColors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30'
}

const formatCategory = (category) => {
  if (!category) return 'Item'
  return category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const openProductLink = (url) => {
  if (url) {
    window.open(url, '_blank', 'noopener,noreferrer')
  }
}

// Image handling methods
const getImageUrl = (product) => {
  // Handle different image path formats
  let imagePath = product.image || product.image_url || product.image_path

  if (!imagePath) {
    // Return a simple gray placeholder SVG
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjMzMzMzMzIi8+Cjx0ZXh0IHg9IjUwIiB5PSI1NSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiPk5vIEltYWdlPC90ZXh0Pgo8L3N2Zz4K'
  }

  // Debug logging (can be removed after testing)
  console.log('Processing image path:', imagePath, 'for product:', product.label || product.name)

  // If it's already a full URL, return as-is
  if (imagePath.startsWith('http') || imagePath.startsWith('data:')) {
    return imagePath
  }

  // If it starts with '/', it's already a public path
  if (imagePath.startsWith('/')) {
    return imagePath
  }

  // For relative paths from backend, ensure they're served from detected_object folder
  // If path doesn't start with 'detected_object', prepend it
  if (!imagePath.includes('detected_object') && !imagePath.includes('detected_objects')) {
    return `/detected_object/${imagePath}`
  }

  // For paths that already include detected_objects/detected_object, prepend with '/'
  return `/${imagePath}`
}

const handleImageError = (event) => {
  console.warn('Image failed to load:', event.target.src)
  // Set a placeholder image instead of hiding
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjMzMzMzMzIi8+Cjx0ZXh0IHg9IjUwIiB5PSI1NSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkZhaWxlZCBMb2FkPC90ZXh0Pgo8L3N2Zz4K'
}

const handleImageLoad = (event) => {
  console.log('Image loaded successfully:', event.target.src)
}

// Modal and image handling methods
const showProductImages = (product) => {
  selectedProduct.value = product
  showImagesModal.value = true
}

const closeImagesModal = () => {
  showImagesModal.value = false
  selectedProduct.value = null
}

const addToCartAndClose = () => {
  if (selectedProduct.value) {
    // Emit add-to-cart event
    emit('add-to-cart', selectedProduct.value)
    // Close the modal with a slight delay for better UX
    setTimeout(() => {
      closeImagesModal()
    }, 300)
  }
}

const emit = defineEmits(['add-to-cart', 'add-to-favorites'])

const openProductWebsite = (websiteUrl) => {
  if (websiteUrl) {
    window.open(websiteUrl, '_blank', 'noopener,noreferrer')
  }
}

// Enhanced image URL method to handle analyzed products
const getMainImageUrl = (product) => {
  // For analyzed products, prioritize local images from searched_images folder
  if (product.local_images && product.local_images.length > 0) {
    return product.local_images[0].local_path
  }

  // Fallback to online images
  if (product.found_online_images && product.found_online_images.length > 0) {
    return product.found_online_images[0].image_url
  }

  // Fallback to original method for legacy products
  return getImageUrl(product)
}

// Get image count for a product
const getImageCount = (product) => {
  // Return actual count of local images or fallback to online count
  return product.local_images?.length || product.found_online_images?.length || 0
}

// Get all images for modal display (prioritize local images)
const getProductImages = (product) => {
  if (!product) return []

  // Use local images if available
  if (product.local_images && product.local_images.length > 0) {
    return product.local_images.map(localImg => ({
      image_url: localImg.local_path,
      website_url: localImg.website_url,
      isLocal: true
    }))
  }

  // Fallback to online images
  return product.found_online_images?.map(img => ({
    image_url: img.image_url,
    website_url: img.website_url,
    isLocal: false
  })) || []
}
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.4) rgba(255, 255, 255, 0.1);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  margin: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg,
    rgba(168, 85, 247, 0.6) 0%,
    rgba(59, 130, 246, 0.6) 50%,
    rgba(6, 182, 212, 0.6) 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg,
    rgba(168, 85, 247, 0.8) 0%,
    rgba(59, 130, 246, 0.8) 50%,
    rgba(6, 182, 212, 0.8) 100%);
  transform: scaleX(1.2);
  border-color: rgba(255, 255, 255, 0.2);
}

.custom-scrollbar::-webkit-scrollbar-thumb:active {
  background: linear-gradient(180deg,
    rgba(168, 85, 247, 0.9) 0%,
    rgba(59, 130, 246, 0.9) 50%,
    rgba(6, 182, 212, 0.9) 100%);
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>