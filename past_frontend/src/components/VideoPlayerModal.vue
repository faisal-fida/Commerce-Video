<template>
  <div class="fixed inset-0 z-50 bg-black">
    <!-- Header -->
    <div class="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/80 to-transparent p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="$emit('close')"
            class="flex items-center space-x-2 text-white hover:text-gray-300 transition-colors"
          >
            <ArrowLeft class="w-5 h-5" />
            <span>Back</span>
          </button>

          <!-- Search Button -->
          <button
            @click="toggleSearch"
            class="flex items-center space-x-2 text-white hover:text-gray-300 transition-colors bg-white/10 backdrop-blur-sm px-3 py-2 rounded-lg"
          >
            <Search class="w-4 h-4" />
            <span>Search Products</span>
          </button>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Cart Button -->
          <button
            @click="handleCartClick"
            class="text-white hover:text-gray-300 transition-colors bg-white/10 backdrop-blur-sm p-2 rounded-lg relative group hover:bg-white/20"
            :title="`Cart (${cartItemsCount} items) - Click to view cart`"
          >
            <ShoppingBag class="w-5 h-5 transition-transform group-hover:scale-110" />
            <span
              v-if="cartItemsCount > 0"
              class="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center animate-pulse font-bold shadow-lg"
            >
              {{ cartItemsCount }}
            </span>
          </button>

          <button
            @click="toggleFullscreen"
            class="text-white hover:text-gray-300 transition-colors"
          >
            <Maximize class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Search Overlay -->
    <Transition name="slide-down">
      <div v-if="showSearchOverlay" class="absolute top-16 left-0 right-0 z-20 bg-black/95 backdrop-blur-md border-b border-gray-800 p-4">
        <div class="max-w-4xl mx-auto">
          <div class="relative mb-4">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search for products..."
              class="w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg px-4 py-3 pl-12 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 transition-colors"
              @input="handleSearch"
            />
            <Search class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <button
              @click="showSearchOverlay = false"
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="isLoadingProducts" class="text-center py-8">
            <div class="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-3"></div>
            <p class="text-gray-400">Loading detected products...</p>
          </div>

          <!-- Search Results -->
          <div v-else-if="filteredProducts.length > 0" class="max-h-60 overflow-y-auto custom-scrollbar">
            <div class="mb-3">
              <p class="text-cyan-400 text-sm font-medium">{{ filteredProducts.length }} detected products found</p>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div
                v-for="product in filteredProducts"
                :key="product.id"
                class="bg-gray-900/50 rounded-lg p-3 hover:bg-gray-800/50 transition-colors cursor-pointer group"
                @click="addToCart(product)"
              >
                <div class="relative mb-2">
                  <img
                    :src="product.image || product.image_url"
                    :alt="product.name"
                    class="w-full h-20 object-cover rounded"
                    @error="handleImageError"
                  />
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded flex items-center justify-center">
                    <ShoppingBag class="w-6 h-6 text-white" />
                  </div>
                  <!-- Confidence badge -->
                  <div v-if="product.confidence" class="absolute top-1 right-1 bg-black/70 text-white text-xs px-1 py-0.5 rounded">
                    {{ Math.round(product.confidence * 100) }}%
                  </div>
                </div>
                <h5 class="text-white text-sm font-medium mb-1 line-clamp-2">{{ product.name }}</h5>
                <p class="text-cyan-400 text-sm font-semibold">${{ product.price.toFixed(2) }}</p>
                <p v-if="product.timestamp" class="text-gray-500 text-xs mt-1">{{ product.timestamp }}s in video</p>
              </div>
            </div>
          </div>

          <!-- Show all products when no search query -->
          <div v-else-if="!searchQuery.trim() && allProducts.length > 0" class="max-h-60 overflow-y-auto custom-scrollbar">
            <div class="mb-3">
              <p class="text-cyan-400 text-sm font-medium">{{ allProducts.length }} products detected in this video</p>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div
                v-for="product in allProducts.slice(0, 20)"
                :key="product.id"
                class="bg-gray-900/50 rounded-lg p-3 hover:bg-gray-800/50 transition-colors cursor-pointer group"
                @click="addToCart(product)"
              >
                <div class="relative mb-2">
                  <img
                    :src="product.image || product.image_url"
                    :alt="product.name"
                    class="w-full h-20 object-cover rounded"
                    @error="handleImageError"
                  />
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded flex items-center justify-center">
                    <ShoppingBag class="w-6 h-6 text-white" />
                  </div>
                  <!-- Confidence badge -->
                  <div v-if="product.confidence" class="absolute top-1 right-1 bg-black/70 text-white text-xs px-1 py-0.5 rounded">
                    {{ Math.round(product.confidence * 100) }}%
                  </div>
                </div>
                <h5 class="text-white text-sm font-medium mb-1 line-clamp-2">{{ product.name }}</h5>
                <p class="text-cyan-400 text-sm font-semibold">${{ product.price.toFixed(2) }}</p>
                <p v-if="product.timestamp" class="text-gray-500 text-xs mt-1">{{ product.timestamp }}s in video</p>
              </div>
            </div>
          </div>

          <div v-else-if="searchQuery.trim()" class="text-center py-8">
            <p class="text-gray-400">No products found for "{{ searchQuery }}"</p>
          </div>

          <div v-else-if="!isLoadingProducts" class="text-center py-8">
            <ShoppingBag class="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p class="text-gray-400">No products detected in this video</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Video Player -->
    <div class="relative w-full h-full flex items-center justify-center bg-black">
      <video
        ref="videoPlayer"
        :src="props.video.videoUrl"
        :poster="getThumbnailUrl(video.thumbnail)"
        class="max-w-full max-h-full"
        controls
        autoplay
        @loadedmetadata="onVideoLoaded"
        @timeupdate="onTimeUpdate"
        @pause="onVideoPause"
        @play="onVideoPlay"
      >
        Your browser does not support the video tag.
      </video>

      <!-- Video unavailable placeholder -->
      <div
        v-if="videoError"
        class="absolute inset-0 flex items-center justify-center bg-gray-900"
      >
        <div class="text-center">
          <AlertCircle class="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 class="text-white text-xl mb-2">Video Unavailable</h3>
          <p class="text-gray-400 mb-4">This video is currently not available for playback.</p>
          <button
            @click="$emit('close')"
            class="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-2 rounded transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>

    <!-- Video Info Overlay -->
    <div
      class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent p-6"
      :class="{ 'translate-y-full': !showInfo }"
      style="transition: transform 0.3s ease;"
    >
      <div class="max-w-4xl">
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-white mb-2">{{ video.title }}</h2>
            <p class="text-gray-300 mb-4">{{ video.description }}</p>

            <div class="flex items-center space-x-6 text-sm text-gray-400 mb-4">
              <div class="flex items-center space-x-1">
                <Eye class="w-4 h-4" />
                <span>{{ video.views }} views</span>
              </div>
              <div class="flex items-center space-x-1">
                <Star class="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <span>{{ video.rating }} rating</span>
              </div>
              <div class="flex items-center space-x-1">
                <Clock class="w-4 h-4" />
                <span>{{ video.duration }}</span>
              </div>
              <span>{{ formatDate(video.releaseDate) }}</span>
            </div>

            <!-- Tags -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span
                v-for="tag in video.tags"
                :key="tag"
                class="bg-gray-800 text-gray-300 text-sm px-3 py-1 rounded-full"
              >
                #{{ tag }}
              </span>
            </div>
          </div>

          <button
            @click="showInfo = !showInfo"
            class="text-white hover:text-gray-300 ml-4 transition-colors"
          >
            <ChevronUp v-if="showInfo" class="w-5 h-5" />
            <ChevronDown v-else class="w-5 h-5" />
          </button>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center space-x-4">
          <button
            @click="addToWatchlist"
            class="bg-white/20 backdrop-blur-sm text-white px-6 py-2 rounded-lg font-medium hover:bg-white/30 transition-colors flex items-center space-x-2"
          >
            <Plus class="w-4 h-4" />
            <span>Add to List</span>
          </button>

          <button
            @click="shareVideo"
            class="bg-white/20 backdrop-blur-sm text-white px-6 py-2 rounded-lg font-medium hover:bg-white/30 transition-colors flex items-center space-x-2"
          >
            <Share class="w-4 h-4" />
            <span>Share</span>
          </button>

          <button
            @click="showShoppingPanel = true"
            class="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <ShoppingBag class="w-4 h-4" />
            <span>Shop This Video</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Tab Bar -->
    <div class="absolute bottom-0 left-0 right-0 z-30">
      <TabBar
        v-model:activeTab="activeTab"
        @toggle-content="showBottomContent = !showBottomContent"
        class="mb-0"
      />

      <!-- Bottom Content Panel -->
      <Transition name="slide-up">
        <div
          v-if="showBottomContent"
          class="bg-black/90 backdrop-blur-sm border-t border-gray-800 overflow-hidden relative"
          :style="{ height: `${bottomContentHeight}px` }"
        >
          <!-- Drag Handle for Resizing -->
          <div
            class="absolute top-0 left-0 right-0 h-2 cursor-row-resize bg-gradient-to-b from-white/20 to-transparent hover:from-white/30 z-10 flex items-center justify-center group"
            @mousedown="startResizing"
          >
            <div class="w-12 h-1 bg-white/40 rounded-full group-hover:bg-white/60 transition-colors"></div>
          </div>

          <!-- Content Area with padding for drag handle -->
          <div class="pt-2 h-full overflow-hidden flex">
            <!-- Sidebar for Products Tab -->
            <div
              v-if="activeTab === 'products' && showProductsSidebar"
              class="bg-white/5 border-r border-white/10 flex-shrink-0 relative"
              :style="{ width: `${sidebarWidth}px` }"
            >
              <!-- Sidebar Drag Handle -->
              <div
                class="absolute top-0 right-0 w-2 h-full cursor-col-resize bg-gradient-to-r from-transparent to-white/20 hover:to-white/30 flex items-center justify-center group"
                @mousedown="startSidebarResize"
              >
                <div class="w-1 h-12 bg-white/40 rounded-full group-hover:bg-white/60 transition-colors"></div>
              </div>

              <!-- Sidebar Content -->
              <div class="p-4 h-full overflow-y-auto custom-scrollbar">
                <h3 class="text-white font-semibold mb-3">Product Filters</h3>
                <div class="space-y-3">
                  <div class="text-xs text-gray-400">
                    Total Products: {{ allProducts.length }}
                  </div>
                  <button
                    class="w-full text-left text-xs bg-white/10 hover:bg-white/20 text-white p-2 rounded border border-white/20"
                    @click="showProductsSidebar = false"
                  >
                    ← Hide Sidebar
                  </button>
                </div>
              </div>
            </div>

            <!-- Main Content Area -->
            <div class="flex-1 relative">
              <!-- Show Sidebar Button (when sidebar is hidden) -->
              <button
                v-if="activeTab === 'products' && !showProductsSidebar"
                @click="showProductsSidebar = true"
                class="absolute top-2 left-2 z-10 bg-white/10 hover:bg-white/20 text-white text-xs px-2 py-1 rounded border border-white/20"
              >
                Show Filters →
              </button>

              <ProductsTab
                v-if="activeTab === 'products'"
                :products="currentTimeProducts"
                :current-time="currentTime"
                @add-to-cart="addToCart"
                @add-to-favorites="addToFavorites"
              />
              <BundlesTab
                v-else-if="activeTab === 'bundles'"
                :bundles="allBundles"
                @add-to-cart="addToCart"
              />
              <ProfileTab
                v-else-if="activeTab === 'profile'"
                :user="sampleUser"
              />
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Cart Drawer -->
    <CartDrawer
      v-model:open="showCartDrawer"
      :items="cartItems"
      :total="cartTotal"
      @remove-item="removeFromCart"
      @update-quantity="updateQuantity"
    />

    <!-- Info toggle button -->
    <button
      @click="showInfo = !showInfo"
      class="absolute bottom-4 right-4 bg-black/50 backdrop-blur-sm text-white p-2 rounded-full hover:bg-black/70 transition-colors"
    >
      <Info class="w-5 h-5" />
    </button>

    <!-- Full-screen Products Popup (triggered on video pause) -->
    <Transition name="fullscreen-fade">
      <div
        v-if="showFullscreenProducts"
        class="fixed inset-0 z-[60] bg-black/95 backdrop-blur-xl"
      >
        <!-- Header with Home Button -->
        <div class="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/80 to-transparent p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <button
                @click="closeFullscreenProducts"
                class="flex items-center space-x-3 text-white hover:text-cyan-400 transition-colors bg-cyan-500/20 backdrop-blur-sm px-4 py-2 rounded-lg border border-cyan-500/30 hover:bg-cyan-500/30"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span class="font-medium">Back to Video</span>
              </button>

              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
                <h1 class="text-2xl font-bold text-white">Products at {{ formatTime(currentTime) }}</h1>
              </div>
            </div>

            <div class="flex items-center space-x-2 text-sm text-gray-300">
              <span>{{ currentTimeProducts.length }} items found</span>
            </div>
          </div>
        </div>

        <!-- Full-screen Product Grid -->
        <div class="pt-24 p-6 h-full overflow-y-auto">
          <div class="max-w-7xl mx-auto">
            <!-- Time indicator -->
            <div class="mb-6 text-center">
              <div class="inline-flex items-center gap-3 text-cyan-400 bg-cyan-400/10 px-4 py-2 rounded-lg border border-cyan-400/20">
                <div class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                <span class="text-sm">Showing products detected at {{ formatTime(currentTime) }} (±3s tolerance)</span>
              </div>
            </div>

            <!-- Products Grid -->
            <div v-if="currentTimeProducts.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              <div
                v-for="product in currentTimeProducts"
                :key="product.id"
                class="bg-gray-900/50 rounded-xl p-4 hover:bg-gray-800/50 transition-all duration-300 hover:scale-105 border border-gray-800 hover:border-cyan-500/30 group"
              >
                <!-- Product Image -->
                <div class="relative mb-4">
                  <img
                    :src="product.image || product.found_online_images?.[0]?.image_url"
                    :alt="product.name"
                    class="w-full h-48 object-cover rounded-lg"
                    @error="handleImageError"
                  />
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                    <button
                      @click="addToCart(product)"
                      class="bg-cyan-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-cyan-400 transition-colors flex items-center space-x-2"
                    >
                      <ShoppingBag class="w-4 h-4" />
                      <span>Add to Cart</span>
                    </button>
                  </div>

                  <!-- Detection time badge -->
                  <div class="absolute top-2 left-2 bg-cyan-500/80 backdrop-blur-sm text-white text-xs px-2 py-1 rounded">
                    {{ formatTime(product.original_detection_time || product.timestamp || 0) }}
                  </div>
                </div>

                <!-- Product Info -->
                <div class="space-y-2">
                  <h3 class="text-white font-medium text-sm line-clamp-2" :title="product.name || product.ai_generated_search_query">
                    {{ product.name || product.ai_generated_search_query || 'Detected Item' }}
                  </h3>

                  <p class="text-gray-400 text-xs line-clamp-2">
                    {{ product.description || `${product.detected_category_from_video} detected in video` }}
                  </p>

                  <div class="flex items-center justify-between">
                    <span class="text-cyan-400 font-semibold">
                      ${{ (product.price || 99.99).toFixed(0) }}
                    </span>
                    <span class="text-xs text-purple-300 bg-purple-500/10 px-2 py-1 rounded border border-purple-500/20">
                      {{ product.detected_category_from_video }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-16">
              <div class="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search class="w-12 h-12 text-gray-500" />
              </div>
              <h3 class="text-2xl font-bold text-white mb-4">No Products at This Time</h3>
              <p class="text-gray-400 text-lg mb-6">
                No products were detected at {{ formatTime(currentTime) }}.
              </p>
              <p class="text-gray-500 text-sm">
                Products are detected within ±3 seconds of the current video time.
              </p>
              <button
                @click="closeFullscreenProducts"
                class="mt-6 bg-cyan-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-400 transition-colors"
              >
                Continue Watching Video
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  ArrowLeft, Maximize, AlertCircle, Eye, Star, Clock, ChevronUp, ChevronDown,
  Plus, Share, ShoppingBag, X, Info, Search
} from 'lucide-vue-next'

// Components
import TabBar from './TabBar.vue'
import ProductsTab from './ProductsTab.vue'
import BundlesTab from './BundlesTab.vue'
import ProfileTab from './ProfileTab.vue'
import CartDrawer from './CartDrawer.vue'

const props = defineProps({
  video: {
    type: Object,
    required: true
  },
  cartItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'add-to-cart', 'open-cart'])

const videoPlayer = ref(null)
const videoError = ref(false)
const showInfo = ref(true)
const showSearchOverlay = ref(false)
const searchQuery = ref('')
const currentTime = ref(0)

// Bottom panel state
const activeTab = ref('products')
const showBottomContent = ref(false)
const bottomContentHeight = ref(384)
const isResizing = ref(false)
const showProductsSidebar = ref(false)
const sidebarWidth = ref(320)

// Cart state
const showCartDrawer = ref(false)
const cartItems = ref([])
const favoriteItems = ref([])

// Full-screen product popup state
const showFullscreenProducts = ref(false)

// Detected products from video analysis
const allProducts = ref([])
const isLoadingProducts = ref(false)

// Dynamic bundle generation from detected products
const dynamicBundles = computed(() => {
  if (allProducts.value.length === 0) return []

  const bundles = []

  // 1. Group products by category
  const categoryGroups = {}
  allProducts.value.forEach(product => {
    const category = product.detected_category_from_video || product.category || 'accessories'
    if (!categoryGroups[category]) {
      categoryGroups[category] = []
    }
    categoryGroups[category].push(product)
  })

  // 2. Create category-based bundles (minimum 2 products per bundle)
  Object.entries(categoryGroups).forEach(([category, products], index) => {
    if (products.length >= 2) {
      const totalPrice = products.reduce((sum, p) => sum + (p.price || 99.99), 0)
      const discountedPrice = totalPrice * 0.85 // 15% bundle discount

      bundles.push({
        id: `bundle-category-${category}-${props.video.id}`,
        name: `${category.charAt(0).toUpperCase() + category.slice(1)} Collection`,
        description: `Complete ${category} collection with ${products.length} items`,
        total_price: totalPrice,
        discount_price: discountedPrice,
        category: 'wardrobe',
        image_url: products[0]?.image || products[0]?.image_url || '/placeholder.jpg',
        product_ids: products.map(p => p.id),
        products: products,
        similarity_score: 0.9
      })
    }
  })

  // 3. Create time-based bundles (products detected within 10 seconds of each other)
  const timeClusters = []
  const sortedProducts = [...allProducts.value].sort((a, b) => {
    const timeA = a.timestamp || a.original_detection_time || 0
    const timeB = b.timestamp || b.original_detection_time || 0
    return timeA - timeB
  })

  let currentCluster = []
  let lastTime = 0

  sortedProducts.forEach(product => {
    const currentTime = product.timestamp || product.original_detection_time || 0

    if (currentCluster.length === 0 || Math.abs(currentTime - lastTime) <= 10) {
      currentCluster.push(product)
      lastTime = currentTime
    } else {
      if (currentCluster.length >= 2) {
        timeClusters.push([...currentCluster])
      }
      currentCluster = [product]
      lastTime = currentTime
    }
  })

  // Add the last cluster
  if (currentCluster.length >= 2) {
    timeClusters.push(currentCluster)
  }

  // 4. Create time-based bundles
  timeClusters.forEach((cluster, index) => {
    if (cluster.length >= 2) {
      const totalPrice = cluster.reduce((sum, p) => sum + (p.price || 99.99), 0)
      const discountedPrice = totalPrice * 0.8 // 20% bundle discount for time-based
      const avgTime = Math.round(cluster.reduce((sum, p) => sum + (p.timestamp || p.original_detection_time || 0), 0) / cluster.length)

      bundles.push({
        id: `bundle-time-${index}-${props.video.id}`,
        name: `Scene Bundle @${Math.floor(avgTime / 60)}:${(avgTime % 60).toString().padStart(2, '0')}`,
        description: `Products appearing together at ${Math.floor(avgTime / 60)}:${(avgTime % 60).toString().padStart(2, '0')} - ${cluster.length} items`,
        total_price: totalPrice,
        discount_price: discountedPrice,
        category: 'tech-bundle',
        image_url: cluster[0]?.image || cluster[0]?.image_url || '/placeholder.jpg',
        product_ids: cluster.map(p => p.id),
        products: cluster,
        similarity_score: 0.85,
        time_range: `${Math.floor(avgTime / 60)}:${(avgTime % 60).toString().padStart(2, '0')}`
      })
    }
  })

  // 5. Create "Most Popular" bundle from highest-priced items
  if (allProducts.value.length >= 3) {
    const topProducts = [...allProducts.value]
      .sort((a, b) => (b.price || 99.99) - (a.price || 99.99))
      .slice(0, Math.min(4, allProducts.value.length))

    if (topProducts.length >= 2) {
      const totalPrice = topProducts.reduce((sum, p) => sum + (p.price || 99.99), 0)
      const discountedPrice = totalPrice * 0.75 // 25% premium bundle discount

      bundles.push({
        id: `bundle-premium-${props.video.id}`,
        name: 'Premium Selection',
        description: `Top ${topProducts.length} premium items from this video`,
        total_price: totalPrice,
        discount_price: discountedPrice,
        category: 'skincare-routine',
        image_url: topProducts[0]?.image || topProducts[0]?.image_url || '/placeholder.jpg',
        product_ids: topProducts.map(p => p.id),
        products: topProducts,
        similarity_score: 0.95
      })
    }
  }

  return bundles
})

// Keep sample bundles as fallback if no dynamic bundles are generated
const sampleBundles = ref([
  {
    id: `bundle-sample-${props.video.id}`,
    name: 'Complete Outfit Bundle',
    description: 'Everything you need for a perfect look',
    total_price: 299.97,
    discount_price: 249.99,
    category: 'wardrobe',
    image_url: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&h=200&fit=crop&q=80',
    product_ids: ['product-1', 'product-2', 'product-4'],
    products: [],
    similarity_score: 0.8
  }
])

// Combined bundles - prefer dynamic bundles, fallback to sample
const allBundles = computed(() => {
  const dynamic = dynamicBundles.value
  return dynamic.length > 0 ? dynamic : sampleBundles.value
})

const sampleUser = ref({
  full_name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&q=80'
})

// Computed properties - use props cart items from parent
const cartItemsCount = computed(() => props.cartItems.reduce((sum, item) => sum + item.quantity, 0))
const cartTotal = computed(() => props.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0))

// Time-based product filtering for ProductsTab
const currentTimeProducts = computed(() => {
  const timeToleranceSeconds = 3 // ±3 seconds tolerance
  const current = currentTime.value

  return allProducts.value.filter(product => {
    // Use original_detection_time for filtering
    const detectionTime = product.timestamp || product.original_detection_time || 0
    const timeDiff = Math.abs(current - detectionTime)
    return timeDiff <= timeToleranceSeconds
  })
})

// Search-based filtering for search overlay
const filteredProducts = computed(() => {
  if (!searchQuery.value.trim()) return []

  const query = searchQuery.value.toLowerCase()
  return allProducts.value.filter(product =>
    product.name.toLowerCase().includes(query) ||
    product.description.toLowerCase().includes(query) ||
    product.tags.some(tag => tag.toLowerCase().includes(query))
  )
})

const getVideoUrl = () => {
  // Return the actual video URL from the video props
  return props.video.videoUrl || props.video.src || '/downloaded_videos/8CKF3ziEPCM.mp4'
}

const getThumbnailUrl = (thumbnail) => {
  if (thumbnail && !thumbnail.includes('placeholder')) {
    return thumbnail
  }
  return 'https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const onVideoLoaded = () => {
  videoError.value = false
}

const onTimeUpdate = (event) => {
  currentTime.value = event.target.currentTime
}

// Handle video pause - show full-screen products
const onVideoPause = () => {
  console.log('🎬🎬🎬 VIDEO PAUSED EVENT TRIGGERED! 🎬🎬🎬')
  console.log('Current video state:', {
    paused: videoPlayer.value?.paused,
    currentTime: currentTime.value,
    showFullscreenProducts: showFullscreenProducts.value,
    showBottomContent: showBottomContent.value
  })

  // Show full-screen products popup
  showFullscreenProducts.value = true

  // Also show bottom content (as fallback)
  showBottomContent.value = true

  console.log('✅ Set showFullscreenProducts = true, showBottomContent = true')
}

// Handle video play - hide full-screen products
const onVideoPlay = () => {
  console.log('▶️▶️▶️ VIDEO PLAY EVENT TRIGGERED! ▶️▶️▶️')
  console.log('Current video state:', {
    paused: videoPlayer.value?.paused,
    currentTime: currentTime.value,
    showFullscreenProducts: showFullscreenProducts.value,
    showBottomContent: showBottomContent.value
  })

  // Hide full-screen products popup
  showFullscreenProducts.value = false

  // Hide bottom content when playing
  showBottomContent.value = false

  console.log('✅ Set showFullscreenProducts = false, showBottomContent = false')
}

// Close full-screen products and return to video
const closeFullscreenProducts = () => {
  console.log('🏠 Home button clicked - returning to video')
  showFullscreenProducts.value = false
  showBottomContent.value = false
  if (videoPlayer.value) {
    videoPlayer.value.play() // Resume video playback
  }
  console.log('✅ Resumed video playback')
}

const toggleFullscreen = () => {
  if (videoPlayer.value) {
    if (videoPlayer.value.requestFullscreen) {
      videoPlayer.value.requestFullscreen()
    }
  }
}

const toggleSearch = () => {
  showSearchOverlay.value = !showSearchOverlay.value
  if (!showSearchOverlay.value) {
    searchQuery.value = ''
  }
}

const handleSearch = () => {
  // Search is handled by computed property filteredProducts
}

const handleImageError = (event) => {
  // Fallback to a placeholder image if the detected image fails to load
  event.target.src = 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&h=200&fit=crop&q=80'
}

const addToCart = (item) => {
  console.log('Adding to cart via VideoPlayerModal:', item) // Debug log

  // Check if it's a bundle (has products array) or individual product
  if (item.products && Array.isArray(item.products)) {
    console.log('Adding bundle to cart:', item)

    // For bundles, create a special bundle cart item
    const bundleCartItem = {
      id: item.id,
      name: item.name,
      description: item.description,
      price: item.discount_price || item.total_price,
      image: item.image_url || item.image,
      quantity: 1,
      type: 'bundle',
      bundle_products: item.products,
      category: item.category,
      similarity_score: item.similarity_score
    }

    emit('add-to-cart', bundleCartItem)
  } else {
    // Individual product
    emit('add-to-cart', item)
  }

  console.log('Emitted add-to-cart event to parent')

  // Close search overlay after adding to cart
  if (showSearchOverlay.value) {
    showSearchOverlay.value = false
    searchQuery.value = ''
  }
}

const addToFavorites = (product) => {
  console.log('Adding to favorites:', product) // Debug log

  const existingFavorite = favoriteItems.value.find(item => item.id === product.id)
  if (existingFavorite) {
    console.log('Product already in favorites')
    // Remove from favorites if already exists (toggle)
    favoriteItems.value = favoriteItems.value.filter(item => item.id !== product.id)
    console.log('Removed from favorites')
  } else {
    const favoriteItem = {
      ...product,
      name: product.name || product.class_name || 'Unknown Product',
      price: product.price || 99.99,
      image: product.image || product.image_url || '/placeholder.jpg'
    }
    favoriteItems.value.push(favoriteItem)
    console.log('Added to favorites:', favoriteItem)
  }

  console.log('Current favorite items:', favoriteItems.value) // Debug log
}

const handleCartClick = () => {
  console.log('🛒 Cart button clicked!')
  console.log('Cart items from props:', props.cartItems)
  console.log('Cart items count:', cartItemsCount.value)

  // Emit to parent component to open the main cart
  emit('open-cart')
  console.log('Emitted open-cart event to parent')
}

const removeFromCart = (itemId) => {
  cartItems.value = cartItems.value.filter(item => item.id !== itemId)
}

const updateQuantity = (itemId, quantity) => {
  if (quantity <= 0) {
    removeFromCart(itemId)
  } else {
    const item = cartItems.value.find(item => item.id === itemId)
    if (item) {
      item.quantity = quantity
    }
  }
}

const addToWatchlist = () => {
  console.log(`Added "${props.video.title}" to watchlist`)
}

const shareVideo = () => {
  if (navigator.share) {
    navigator.share({
      title: props.video.title,
      text: props.video.description,
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href)
    console.log('Video URL copied to clipboard')
  }
}

// Resize functionality for bottom content
const startResizing = (event) => {
  event.preventDefault()
  isResizing.value = true

  const startY = event.clientY
  const startHeight = bottomContentHeight.value

  const handleMouseMove = (e) => {
    if (!isResizing.value) return

    const deltaY = startY - e.clientY
    const newHeight = Math.max(200, Math.min(window.innerHeight * 0.8, startHeight + deltaY))
    bottomContentHeight.value = newHeight
  }

  const handleMouseUp = () => {
    isResizing.value = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = 'row-resize'
  document.body.style.userSelect = 'none'
}

// Resize functionality for sidebar
const startSidebarResize = (event) => {
  event.preventDefault()

  const startX = event.clientX
  const startWidth = sidebarWidth.value

  const handleMouseMove = (e) => {
    const deltaX = e.clientX - startX
    const newWidth = Math.max(200, Math.min(600, startWidth + deltaX))
    sidebarWidth.value = newWidth
  }

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

// Load detected products from video analysis
const loadDetectedProducts = async () => {
  isLoadingProducts.value = true
  try {
    // Try to get video name from the video prop and extract the core name
    let videoName = '8CKF3ziEPCM' // Default fallback

    console.log('🎬 VideoPlayerModal received video object:', JSON.stringify(props.video, null, 2))

    if (props.video?.id) {
      console.log('🔍 Extracting video name from ID:', props.video.id)
      // Extract core video name from generated ID (e.g., "video-8CKF3ziEPCM-1" → "8CKF3ziEPCM")
      videoName = props.video.id
        .replace('video-', '')     // Remove "video-" prefix
        .replace(/[-_]\d+$/, '')   // Remove "-1" or "_1" suffix if present
    } else if (props.video?.filename) {
      console.log('🔍 Extracting video name from filename:', props.video.filename)
      // Extract from filename (e.g., "8CKF3ziEPCM_1.mp4" → "8CKF3ziEPCM")
      videoName = props.video.filename
        .replace(/\.[^/.]+$/, '') // Remove extension
        .replace(/_\d+$/, '')     // Remove "_1" suffix if present
    }

    const cacheBuster = new Date().getTime()
    console.log(`🎬 Final video name for analysis lookup: ${videoName}`)
    console.log(`🔍 Will try to load: /analyzed_files/${videoName}/analyzed.json`)

    const url = `/analyzed_files/${videoName}/analyzed.json?t=${cacheBuster}`
    console.log(`🌐 Fetching URL: ${url}`)

    const response = await fetch(url, {
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    })

    console.log(`📡 Response status: ${response.status}`)
    console.log(`📡 Response headers:`, response.headers)

    if (response.ok) {
      const responseText = await response.text()
      console.log(`📄 Response content preview:`, responseText.substring(0, 100))

      try {
        const analyzedData = JSON.parse(responseText)
        if (analyzedData && analyzedData.length > 0) {
        // Transform analyzed products to match our format
        allProducts.value = analyzedData.map((product, index) => ({
          id: `analyzed-${index}`,
          name: product.ai_generated_search_query || product.detected_category_from_video || 'Detected Item',
          description: `${product.detected_category_from_video} detected at ${product.original_detection_time}s`,
          price: 99.99, // Default price
          image: product.found_online_images?.[0]?.image_url || '/placeholder.jpg',
          category: product.detected_category_from_video || 'general',
          tags: [product.detected_category_from_video, product.ai_generated_search_query].filter(Boolean),
          timestamp: product.original_detection_time || 0,
          found_online_images: product.found_online_images || []
        }))
        console.log(`✅ Loaded ${allProducts.value.length} detected products`)
        } else {
          console.log('📦 No detected products found')
          allProducts.value = []
        }
      } catch (jsonError) {
        console.error('❌ JSON parsing error:', jsonError)
        console.error('📄 Raw response was:', responseText.substring(0, 200))
        console.log('📄 Falling back to sample data due to JSON parsing error')
        // Fall back to sample data instead of throwing error
        allProducts.value = [
          {
            id: 'sample-1',
            name: 'Sample Product (JSON Parse Error)',
            description: 'Fallback sample product due to JSON parsing error',
            price: 29.99,
            image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&h=200&fit=crop&q=80',
            category: 'fashion',
            tags: ['sample', 'error-fallback']
          }
        ]
      }
    } else {
      console.log('📄 analyzed.json not found - using sample data')
      // Fallback to sample data
      allProducts.value = [
        {
          id: 'sample-1',
          name: 'Sample Product',
          description: 'Sample product for testing',
          price: 29.99,
          image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=200&h=200&fit=crop&q=80',
          category: 'fashion',
          tags: ['sample', 'test']
        }
      ]
    }
  } catch (error) {
    console.error('❌ Error loading products:', error)
    allProducts.value = []
  } finally {
    isLoadingProducts.value = false
  }
}

onMounted(async () => {
  // Debug: Log the video data being passed
  console.log('🎬 VideoPlayerModal opened with video:', props.video)
  console.log('📹 Video URL:', props.video.videoUrl)
  console.log('🖼️ Thumbnail URL:', props.video.thumbnail)

  // Load detected products
  await loadDetectedProducts()

  // Auto-hide info panel after 3 seconds
  setTimeout(() => {
    showInfo.value = false
  }, 3000)

  // Don't show bottom content by default - only show when paused
  // showBottomContent.value = true
})
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100%);
}

.slide-up-leave-to {
  transform: translateY(100%);
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
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

/* Fullscreen fade transition */
.fullscreen-fade-enter-active,
.fullscreen-fade-leave-active {
  transition: all 0.3s ease;
}

.fullscreen-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fullscreen-fade-leave-to {
  opacity: 0;
  transform: scale(1.05);
}
</style>