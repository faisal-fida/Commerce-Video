<template>
  <div class="min-h-screen bg-black text-white">
    <!-- Header -->
    <header class="relative z-10 p-4 bg-gradient-to-b from-black/80 to-transparent">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full flex items-center justify-center">
            <span class="text-white font-bold text-sm">Z</span>
          </div>
          <h1 class="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Zora Video
          </h1>
        </div>

        <div class="flex items-center space-x-4">
          <button
            class="p-2 hover:bg-white/10 rounded-full transition-colors"
            @click="toggleSearch"
          >
            <Search class="w-5 h-5" />
          </button>
          <button
            class="p-2 hover:bg-white/10 rounded-full transition-colors"
            @click="refreshVideos"
            :disabled="isLoadingVideos"
          >
            <svg
              class="w-5 h-5"
              :class="{ 'animate-spin': isLoadingVideos }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            class="p-2 hover:bg-white/10 rounded-full transition-colors relative"
            @click="showCart = true"
          >
            <ShoppingBag class="w-5 h-5" />
            <span v-if="cartCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-xs rounded-full w-4 h-4 flex items-center justify-center">
              {{ cartCount }}
            </span>
          </button>
          <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
        </div>
      </div>
    </header>

    <!-- Search Bar -->
    <Transition name="slide-down">
      <div v-if="showSearchBar" class="relative z-10 px-4 pb-4">
        <div class="max-w-7xl mx-auto">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search videos..."
              class="w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg px-4 py-3 pl-12 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 transition-colors"
              @input="handleSearch"
            />
            <Search class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          </div>
        </div>
      </div>
    </Transition>

    <!-- Featured Video -->
    <section v-if="featuredVideo" class="relative mb-8">
      <div
        class="relative h-96 bg-cover bg-center"
        :style="`background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=1920&h=600&fit=crop&q=80')`"
      >
        <div class="absolute inset-0 flex items-center">
          <div class="max-w-7xl mx-auto px-4 w-full">
            <div class="max-w-2xl">
              <span class="inline-block bg-red-600 text-white px-2 py-1 text-xs font-bold rounded mb-2 uppercase">
                Featured
              </span>
              <h2 class="text-4xl font-bold mb-4">{{ featuredVideo.title }}</h2>
              <p class="text-lg text-gray-200 mb-6 line-clamp-2">{{ featuredVideo.description }}</p>
              <div class="flex items-center space-x-4 mb-6">
                <span class="text-sm text-gray-300">{{ featuredVideo.views }} views</span>
                <span class="text-sm text-gray-300">•</span>
                <div class="flex items-center space-x-1">
                  <Star class="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span class="text-sm text-gray-300">{{ featuredVideo.rating }}</span>
                </div>
                <span class="text-sm text-gray-300">•</span>
                <span class="text-sm text-gray-300">{{ featuredVideo.duration }}</span>
              </div>
              <div class="flex items-center space-x-4">
                <button
                  @click="playVideo(featuredVideo)"
                  class="bg-white text-black px-8 py-3 rounded-lg font-semibold flex items-center space-x-2 hover:bg-gray-200 transition-colors"
                >
                  <Play class="w-5 h-5 fill-current" />
                  <span>Play</span>
                </button>
                <button
                  @click="addToWatchlist(featuredVideo)"
                  class="bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 hover:bg-white/30 transition-colors"
                >
                  <Plus class="w-5 h-5" />
                  <span>My List</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="isLoadingVideos && discoveredVideos.length === 0" class="max-w-7xl mx-auto px-4 py-16">
      <div class="text-center">
        <div class="animate-spin w-12 h-12 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-white text-lg">Loading videos...</p>
        <p class="text-gray-400 text-sm mt-2">Reading videos.json and verifying files</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!isLoadingVideos && discoveredVideos.length === 0" class="max-w-7xl mx-auto px-4 py-16">
      <div class="text-center">
        <div class="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-12 h-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2C7 1.45 7.45 1 8 1h8c.55 0 1 .45 1 1v2m0 0v16c0 .55-.45 1-1 1H8c-.55 0-1-.45-1-1V4m0 0H5c-.55 0-1 .45-1 1v14c0 .55.45 1 1 1h2m10-16h2c.55 0 1 .45 1 1v14c0 .55-.45 1-1 1h-2"></path>
          </svg>
        </div>
        <h3 class="text-2xl font-bold text-white mb-4">No Videos Found</h3>
        <p class="text-gray-400 text-lg mb-6">
          No videos found in the <code class="bg-gray-800 px-2 py-1 rounded text-cyan-400">downloaded_videos</code> folder.
        </p>
        <p class="text-gray-500 text-sm">
          Add video files to <code class="text-cyan-400">Frontend_UI/public/downloaded_videos/</code> to see them here.
        </p>
      </div>
    </div>

    <!-- Video Categories -->
    <main v-else-if="filteredCategories.length > 0" class="max-w-7xl mx-auto px-4 space-y-8 pb-8">
      <div v-for="category in filteredCategories" :key="category.id" class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-semibold">{{ category.name }}</h3>
          <button class="text-cyan-400 hover:text-cyan-300 text-sm font-medium">
            View All
          </button>
        </div>

        <div class="relative">
          <div
            ref="scrollContainer"
            class="flex space-x-4 overflow-x-auto scrollbar-hide pb-2"
            :class="`scroll-container-${category.id}`"
          >
            <VideoCard
              v-for="video in category.videos"
              :key="video.id"
              :video="video"
              @play="playVideo"
              @add-to-cart="addToCart"
              @add-to-watchlist="addToWatchlist"
              class="flex-shrink-0"
            />
          </div>

          <!-- Scroll buttons -->
          <button
            @click="scrollLeft(category.id)"
            class="absolute left-0 top-1/2 transform -translate-y-1/2 bg-black/60 hover:bg-black/80 rounded-full p-2 transition-colors z-10"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          <button
            @click="scrollRight(category.id)"
            class="absolute right-0 top-1/2 transform -translate-y-1/2 bg-black/60 hover:bg-black/80 rounded-full p-2 transition-colors z-10"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>
      </div>
    </main>

    <!-- Video Player Modal -->
    <VideoPlayerModal
      v-if="selectedVideo"
      :video="selectedVideo"
      :cart-items="cartItems"
      @close="closeVideoPlayer"
      @add-to-cart="addToCart"
      @open-cart="openCart"
    />

    <!-- Cart Drawer -->
    <CartDrawer
      v-model:open="showCart"
      :items="cartItems"
      :total="cartTotal"
      @remove-item="removeFromCart"
      @update-quantity="updateQuantity"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, ShoppingBag, Play, Plus, Star, ChevronLeft, ChevronRight } from 'lucide-vue-next'

// Components
import VideoCard from '../components/VideoCard.vue'
import VideoPlayerModal from '../components/VideoPlayerModal.vue'
import CartDrawer from '../components/CartDrawer.vue'

// Services
import { videoDiscovery } from '../services/videoDiscovery.js'

// Data
const discoveredVideos = ref([])
const selectedVideo = ref(null)
const showSearchBar = ref(false)
const searchQuery = ref('')
const showCart = ref(false)
const cartItems = ref([])
const watchlist = ref([])
const isLoadingVideos = ref(false)

// Computed - only use discovered videos as featured
const featuredVideo = computed(() => {
  // Use the first discovered video as featured if available
  if (discoveredVideos.value.length > 0) {
    return discoveredVideos.value[0]
  }
  // No featured video if no discovered videos
  return null
})

const filteredCategories = computed(() => {
  const categories = []

  // ONLY show discovered videos from downloaded_videos folder
  if (discoveredVideos.value.length > 0) {
    categories.push({
      id: 'discovered',
      name: 'Available Videos',
      videos: discoveredVideos.value
    })
  }

  // Do not add catalog categories - only show real videos from folder
  // if (videoCatalog.value?.categories) {
  //   categories.push(...videoCatalog.value.categories)
  // }

  if (categories.length === 0) return []

  if (!searchQuery.value.trim()) {
    return categories
  }

  const query = searchQuery.value.toLowerCase()
  return categories.map(category => ({
    ...category,
    videos: category.videos.filter(video =>
      video.title.toLowerCase().includes(query) ||
      video.description.toLowerCase().includes(query) ||
      video.tags.some(tag => tag.toLowerCase().includes(query))
    )
  })).filter(category => category.videos.length > 0)
})

const cartCount = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity, 0))
const cartTotal = computed(() => cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0))

// Methods - removed loadVideoCatalog since we only use downloaded_videos folder

const toggleSearch = () => {
  showSearchBar.value = !showSearchBar.value
  if (!showSearchBar.value) {
    searchQuery.value = ''
  }
}

const handleSearch = () => {
  // Search is handled by computed property filteredCategories
}

const playVideo = (video) => {
  selectedVideo.value = video
}

const closeVideoPlayer = () => {
  selectedVideo.value = null
}

const addToWatchlist = (video) => {
  const exists = watchlist.value.find(item => item.id === video.id)
  if (!exists) {
    watchlist.value.push(video)
    // Show toast notification
    console.log(`Added "${video.title}" to watchlist`)
  }
}

const addToCart = (item) => {
  console.log('🛒 VideoShowcase - Adding item to cart:', item)
  const existingItem = cartItems.value.find(cartItem => cartItem.id === item.id)
  if (existingItem) {
    existingItem.quantity += 1
    console.log('🛒 VideoShowcase - Updated quantity:', existingItem.quantity)
  } else {
    const cartItem = {
      ...item,
      quantity: 1,
      // Ensure we have required properties
      name: item.name || item.class_name || 'Unknown Product',
      price: item.price || 99.99,
      image: item.image || item.image_url || '/placeholder.jpg'
    }
    cartItems.value.push(cartItem)
    console.log('🛒 VideoShowcase - Added new item:', cartItem)
  }
  console.log('🛒 VideoShowcase - Total cart items:', cartItems.value.length)
  console.log('🛒 VideoShowcase - Cart items:', cartItems.value)
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

const scrollLeft = (categoryId) => {
  const container = document.querySelector(`.scroll-container-${categoryId}`)
  if (container) {
    container.scrollBy({ left: -320, behavior: 'smooth' })
  }
}

const scrollRight = (categoryId) => {
  const container = document.querySelector(`.scroll-container-${categoryId}`)
  if (container) {
    container.scrollBy({ left: 320, behavior: 'smooth' })
  }
}

// Load discovered videos from videos.json
const loadDiscoveredVideos = async () => {
  isLoadingVideos.value = true
  try {
    console.log('🔍 Loading videos from videos.json...')
    const videos = await videoDiscovery.discoverVideos()
    discoveredVideos.value = videos
    console.log(`✅ Loaded ${videos.length} videos:`, videos)
  } catch (error) {
    console.error('❌ Error loading videos:', error)
    discoveredVideos.value = []
  } finally {
    isLoadingVideos.value = false
  }
}

// Refresh videos (force reload from videos.json)
const refreshVideos = async () => {
  console.log('🔄 Refreshing video list...')
  videoDiscovery.refreshVideoList() // Clear cache
  await loadDiscoveredVideos()
}

const openCart = () => {
  console.log('🛒 Opening cart from VideoPlayerModal')
  console.log('Current showCart value:', showCart.value)
  showCart.value = true
  console.log('Set showCart to:', showCart.value)
  console.log('Cart items:', cartItems.value)
}

// Lifecycle
onMounted(async () => {
  // Load videos from videos.json file
  await loadDiscoveredVideos()
})
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
</style>