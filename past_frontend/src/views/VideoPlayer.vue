<template>
  <div class="relative w-full h-screen bg-black overflow-hidden">
    <!-- Backend Navigation Button -->
    <div class="absolute top-4 left-4 z-50">
      <button
        @click="openBackend"
        class="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors shadow-lg backdrop-blur-sm"
      >
        <ArrowLeft class="w-4 h-4" />
        Backend UI
      </button>
    </div>
    <!-- Video Upload Section (when no video is loaded) -->
    <div v-if="!currentVideoUrl && !isProcessing" class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
      <div class="max-w-md w-full mx-4 text-center">
        <div class="mb-8">
          <h1 class="text-4xl font-bold text-white mb-4">Scene to Screen</h1>
          <p class="text-gray-300 mb-8">Upload a video or paste a YouTube link to discover shoppable items</p>
        </div>

        <!-- Upload Options -->
        <div class="space-y-4">
          <!-- File Upload -->
          <div class="space-y-2">
            <input
              ref="fileInput"
              type="file"
              accept="video/*"
              class="hidden"
              @change="handleFileSelection"
            />
            <button
              @click="$refs.fileInput.click()"
              class="w-full p-4 border-2 border-dashed border-purple-500 rounded-lg hover:border-purple-400 hover:bg-purple-500/10 transition-colors"
            >
              <Upload class="w-8 h-8 mx-auto mb-2 text-purple-400" />
              <p class="text-white font-medium">Choose Video File</p>
              <p class="text-gray-400 text-sm">MP4, AVI, MOV up to 100MB</p>
            </button>
            <div v-if="selectedFile" class="text-center space-y-2">
              <p class="text-green-400 text-sm">✓ {{ selectedFile.name }}</p>
              <button
                @click="handleFileUpload"
                class="w-full p-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
              >
                <Upload class="w-5 h-5" />
                Analyze Video File
              </button>
            </div>
          </div>

          <!-- URL Input -->
          <div class="space-y-2">
            <input
              v-model="videoUrl"
              type="url"
              placeholder="Paste YouTube URL or video link..."
              class="w-full p-4 bg-white border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:border-purple-500 focus:outline-none"
            />
            <button
              @click="handleUrlSubmit"
              :disabled="!videoUrl.trim()"
              class="w-full p-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-gray-600 disabled:to-gray-600 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
            >
              <Link class="w-5 h-5" />
              Analyze Video URL
            </button>
          </div>

          <!-- Processing Options -->
          <div class="space-y-3">
            <div class="flex gap-2">
              <label class="flex-1 p-3 border border-gray-700 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors">
                <input
                  v-model="processingMode"
                  type="radio"
                  value="full"
                  class="sr-only"
                />
                <div class="text-center">
                  <Film class="w-6 h-6 mx-auto mb-1" :class="processingMode === 'full' ? 'text-purple-400' : 'text-gray-400'" />
                  <p class="text-sm font-medium" :class="processingMode === 'full' ? 'text-white' : 'text-gray-400'">Full Video</p>
                </div>
              </label>
              <label class="flex-1 p-3 border border-gray-700 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors">
                <input
                  v-model="processingMode"
                  type="radio"
                  value="frame"
                  class="sr-only"
                />
                <div class="text-center">
                  <Camera class="w-6 h-6 mx-auto mb-1" :class="processingMode === 'frame' ? 'text-purple-400' : 'text-gray-400'" />
                  <p class="text-sm font-medium" :class="processingMode === 'frame' ? 'text-white' : 'text-gray-400'">Single Frame</p>
                </div>
              </label>
            </div>

            <!-- Detection Method Selection -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-300">
                Choose Detection Method
              </label>
              <select
                v-model="detectionMethod"
                class="w-full p-3 bg-white border border-gray-300 rounded-lg text-black focus:border-purple-500 focus:outline-none"
              >
                <option value="local_yolo">🚀 Local YOLO (Fast, Offline)</option>
                <option value="hybrid_fashion">⚡ Hybrid Fashion (Balanced)</option>
                <option value="enhanced_hybrid">🎯 Enhanced Hybrid (Most Accurate)</option>
                <option value="google_ai">🧠 Google AI (Premium, Online)</option>
                <option value="enhanced_yolo">🔧 Enhanced YOLO (Advanced)</option>
              </select>
              <p class="text-xs text-gray-400">
                {{ getDetectionMethodDescription(detectionMethod) }}
              </p>
            </div>

            <!-- Frame Time Selection (only show when Single Frame is selected) -->
            <div v-if="processingMode === 'frame'" class="space-y-2">
              <label class="block text-sm font-medium text-gray-300">
                Select Frame Time
              </label>
              <div class="flex gap-2">
                <div class="flex-1">
                  <input
                    v-model.number="frameMinutes"
                    type="number"
                    min="0"
                    max="59"
                    placeholder="Min"
                    class="w-full p-2 bg-white border border-gray-300 rounded text-black text-center focus:border-purple-500 focus:outline-none"
                  />
                  <p class="text-xs text-gray-400 text-center mt-1">Minutes</p>
                </div>
                <div class="flex items-center text-white text-lg">:</div>
                <div class="flex-1">
                  <input
                    v-model.number="frameSeconds"
                    type="number"
                    min="0"
                    max="59"
                    placeholder="Sec"
                    class="w-full p-2 bg-white border border-gray-300 rounded text-black text-center focus:border-purple-500 focus:outline-none"
                  />
                  <p class="text-xs text-gray-400 text-center mt-1">Seconds</p>
                </div>
              </div>
              <p class="text-xs text-gray-400 text-center">
                Frame at {{ frameMinutes || 0 }}:{{ String(frameSeconds || 0).padStart(2, '0') }} will be analyzed
              </p>
            </div>

            <!-- Sample Interval Selection (only show when Full Video is selected) -->
            <div v-if="processingMode === 'full'" class="space-y-2">
              <label class="block text-sm font-medium text-gray-300">
                Sample Interval (seconds)
              </label>
              <div class="flex gap-2">
                <div class="flex-1">
                  <input
                    v-model.number="sampleMinutes"
                    type="number"
                    min="0"
                    max="59"
                    placeholder="Min"
                    class="w-full p-2 bg-white border border-gray-300 rounded text-black text-center focus:border-purple-500 focus:outline-none"
                  />
                  <p class="text-xs text-gray-400 text-center mt-1">Minutes</p>
                </div>
                <div class="flex items-center text-white text-lg">:</div>
                <div class="flex-1">
                  <input
                    v-model.number="sampleSeconds"
                    type="number"
                    min="1"
                    max="59"
                    placeholder="Sec"
                    class="w-full p-2 bg-white border border-gray-300 rounded text-black text-center focus:border-purple-500 focus:outline-none"
                  />
                  <p class="text-xs text-gray-400 text-center mt-1">Seconds</p>
                </div>
              </div>
              <p class="text-xs text-gray-400 text-center">
                Analyze every {{ sampleMinutes || 0 }}:{{ String(sampleSeconds || 10).padStart(2, '0') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Processing State -->
    <div v-if="isProcessing" class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
      <div class="text-center max-w-md w-full mx-4">
        <!-- Animated icon -->
        <div class="mb-6">
          <div class="animate-spin w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        </div>

        <!-- Status text -->
        <h3 class="text-xl font-semibold text-white mb-2">{{ processingStatus }}</h3>

        <!-- Progress bar -->
        <div class="w-full bg-gray-700 rounded-full h-2 mb-4">
          <div
            class="bg-gradient-to-r from-purple-600 to-cyan-600 h-2 rounded-full transition-all duration-300"
            :style="`width: ${processingProgress}%`"
          ></div>
        </div>

        <!-- Progress percentage -->
        <p class="text-gray-400 text-sm mb-2">{{ processingProgress }}% Complete</p>

        <!-- Additional info -->
        <p class="text-gray-500 text-xs">
          {{ processingMode === 'frame' ? 'Analyzing single frame' : 'Processing full video' }}
        </p>
      </div>
    </div>

    <!-- Video Player Component (when video is loaded) -->
    <VideoPlayer
      v-if="currentVideoUrl && !isProcessing"
      :video-url="currentVideoUrl"
      :products="products"
      :is-frame-analysis="isFrameAnalysis"
      @time-update="handleTimeUpdate"
      class="absolute inset-0"
    />

    <!-- Product Overlay -->
    <ProductOverlay
      v-if="showProductOverlay && currentVideoUrl"
      :products="timeBasedProducts"
      :current-time="currentTime"
      @close="showProductOverlay = false"
      @add-to-cart="handleAddToCart"
    />

    <!-- Cart Drawer -->
    <CartDrawer
      v-model:open="showCartDrawer"
      :items="cartItems"
      :total="cartTotal"
      @remove-item="handleRemoveFromCart"
      @update-quantity="handleUpdateQuantity"
    />

    <!-- Top Navigation (when video is loaded) -->
    <div v-if="currentVideoUrl && !isProcessing" class="absolute top-0 left-0 right-0 z-30 p-4">
      <div class="flex justify-between items-center">
        <!-- Logo/Brand -->
        <div class="flex items-center space-x-2">
          <button
            @click="resetApp"
            class="flex items-center space-x-2 p-2 bg-white/10 backdrop-blur-sm rounded-full hover:bg-white/20 transition-colors"
          >
            <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center">
              <span class="text-black font-bold">S</span>
            </div>
            <span class="text-white font-semibold">Scene to Screen</span>
          </button>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <button
            @click="showProductOverlay = !showProductOverlay"
            class="p-2 bg-white/20 backdrop-blur-sm rounded-full hover:bg-white/30 transition-colors"
          >
            <Search class="w-5 h-5 text-white" />
          </button>

          <button
            @click="showCartDrawer = true"
            class="p-2 bg-white/20 backdrop-blur-sm rounded-full hover:bg-white/30 transition-colors relative"
          >
            <ShoppingBag class="w-5 h-5 text-white" />
            <span
              v-if="cartItemsCount > 0"
              class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
            >
              {{ cartItemsCount }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Tab Bar (when video is loaded) -->
    <div v-if="currentVideoUrl && !isProcessing" class="absolute bottom-0 left-0 right-0 z-30">
      <TabBar
        v-model:activeTab="activeTab"
        @toggle-content="showBottomContent = !showBottomContent"
        class="mb-4"
      />

      <!-- Bottom Content -->
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
              <div class="p-4 h-full overflow-y-auto">
                <h3 class="text-white font-semibold mb-3">Product Filters</h3>
                <div class="space-y-3">
                  <div class="text-xs text-gray-400">
                    Total Products: {{ products.length }}
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
                :products="products"
                @add-to-cart="handleAddToCart"
              />
              <BundlesTab
                v-else-if="activeTab === 'bundles'"
                :bundles="searchResults"
                @add-to-cart="handleAddToCart"
              />
              <ProfileTab
                v-else-if="activeTab === 'profile'"
                :user="user"
              />
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, ShoppingBag, Upload, Link, Film, Camera, ArrowLeft } from 'lucide-vue-next'

// Components
import ProductOverlay from '../components/ProductOverlay.vue'
import CartDrawer from '../components/CartDrawer.vue'
import TabBar from '../components/TabBar.vue'
import ProductsTab from '../components/ProductsTab.vue'
import BundlesTab from '../components/BundlesTab.vue'
import ProfileTab from '../components/ProfileTab.vue'

// API Services
import { productService, bundleService, cartService, userService, videoService } from '../services/api'

// Reactive data
const products = ref([])
const searchResults = ref([])
const cartItems = ref([])
const user = ref(null)
const currentTime = ref(0)

// Video upload state
const currentVideoUrl = ref("")
const videoUrl = ref("")
const selectedFile = ref(null)
const processingMode = ref('full')
const detectionMethod = ref('local_yolo')
const frameMinutes = ref(0)
const frameSeconds = ref(0)
const sampleMinutes = ref(0)
const sampleSeconds = ref(10)
const isProcessing = ref(false)
const processingStatus = ref('')
const processingProgress = ref(0)
const isFrameAnalysis = ref(false)

// UI State
const showProductOverlay = ref(false)
const showCartDrawer = ref(false)
const activeTab = ref('products')
const showBottomContent = ref(false)
const bottomContentHeight = ref(384) // Default 96 * 4px = 384px (equivalent to max-h-96)
const isResizing = ref(false)
const showProductsSidebar = ref(false)
const sidebarWidth = ref(320) // Default 80 * 4px = 320px (equivalent to w-80)

// Computed properties
const cartItemsCount = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity, 0))
const cartTotal = computed(() => cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0))

const timeBasedProducts = computed(() => {
  return products.value.filter(product => {
    // Use original_detection_time if available (from analyzed files)
    if (product.original_detection_time !== undefined) {
      // Show products detected within 2 seconds of current time
      return Math.abs(product.original_detection_time - currentTime.value) <= 2
    }
    // Fallback to existing timeStart/timeEnd logic for legacy products
    return product.timeStart <= currentTime.value && product.timeEnd >= currentTime.value
  })
})

// Function to load products from analyzed JSON files based on video file name
const loadProductsFromAnalyzedFile = async (videoFileName) => {
  try {
    // Extract video name without extension for folder name
    const videoName = videoFileName ? videoFileName.replace(/\.[^/.]+$/, "") : null

    if (!videoName) {
      console.log('📄 No video file name provided for loading analyzed products')
      return false
    }

    // Load the analyzed.json file directly
    let analyzedData = null
    const jsonFileName = 'analyzed.json'

    try {
      // Add timestamp to bust cache
      const cacheBuster = new Date().getTime()
      const response = await fetch(`/analyzed_files/${videoName}/${jsonFileName}?t=${cacheBuster}`, {
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      })
      if (response.ok) {
        analyzedData = await response.json()
        console.log(`✅ Found analyzed JSON file: ${jsonFileName} (cache-busted)`)
      } else {
        console.log(`⚠️ Could not load ${jsonFileName}: Status ${response.status}`)
      }
    } catch (fileError) {
      console.log(`⚠️ Could not load ${jsonFileName}:`, fileError.message)
    }

    if (analyzedData && analyzedData.length > 0) {
      products.value = analyzedData.map((product, index) => {
        // Generate local image paths based on the actual file naming pattern
        const localImages = []
        const searchQuery = product.ai_generated_search_query || ''
        const cleanQuery = searchQuery.split(' ').slice(0, 3).join('_').replace(/[^a-zA-Z0-9_]/g, '')

        // Map each found_online_images to corresponding local file
        product.found_online_images?.forEach((onlineImg, imgIndex) => {
          // Create local image path for downloaded image (index matches the result number)
          const resultNum = imgIndex + 1
          const localPath = `/analyzed_files/${videoName}/searched_images/item_${index}_result_${resultNum}_${cleanQuery}.jpg?t=${cacheBuster}`
          localImages.push({
            local_path: localPath,
            website_url: onlineImg.website_url,
            online_url: onlineImg.image_url
          })
        })

        return {
          id: `analyzed-${index}`,
          original_detection_time: product.original_detection_time,
          detected_category_from_video: product.detected_category_from_video,
          ai_generated_search_query: product.ai_generated_search_query,
          found_online_images: product.found_online_images || [],
          local_images: localImages, // Add local image mappings
          // Map to existing format for compatibility
          timeStart: Math.max(0, product.original_detection_time - 2),
          timeEnd: product.original_detection_time + 2,
          name: product.ai_generated_search_query || product.detected_category_from_video || 'Detected Item',
          category: product.detected_category_from_video || 'fashion',
          price: 99.99,
          confidence: 0.8,
          // Use first local image as main product image
          image: localImages[0]?.local_path || product.found_online_images?.[0]?.image_url || '/placeholder.jpg',
          timestamp: product.original_detection_time
        }
      })

      console.log(`✅ Loaded ${products.value.length} analyzed products from ${jsonFileName}`)
      return true
    } else {
      console.log('📦 No analyzed file found or contains no products')
      // Fallback to old Product.json method
      return await loadProductsFromProductJson()
    }
  } catch (error) {
    console.error('❌ Error loading analyzed products:', error)
    // Fallback to old method on error
    return await loadProductsFromProductJson()
  }
}

// Fallback function to load products from Product.json (legacy support)
const loadProductsFromProductJson = async () => {
  try {
    const response = await fetch('/Entities/Product.json')
    if (response.ok) {
      const data = await response.json()

      if (data.products && data.products.length > 0) {
        products.value = data.products.map(product => ({
          ...product,
          timeStart: product.timestamp ? parseFloat(product.timestamp.toString().replace('s', '')) - 2 : 0,
          timeEnd: product.timestamp ? parseFloat(product.timestamp.toString().replace('s', '')) + 2 : 10,
          image: product.image || product.image_url || '/detected_objects/crops/placeholder.jpg',
          price: product.price || 99.99,
          name: product.name || product.class_name || 'Detected Item',
          category: product.category || 'fashion',
          confidence: product.confidence || 0.8
        }))

        console.log(`✅ Loaded ${products.value.length} products from Product.json (legacy)`)
        return true
      } else {
        console.log('📦 Product.json exists but contains no products')
        products.value = []
        return false
      }
    } else {
      console.log('📄 Product.json not found')
      products.value = []
      return false
    }
  } catch (error) {
    console.error('❌ Error loading Product.json:', error)
    products.value = []
    return false
  }
}

// Methods
const handleFileSelection = (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 100 * 1024 * 1024) { // 100MB limit
    alert('File size too large. Please select a file under 100MB.')
    return
  }

  selectedFile.value = file
}

const handleFileUpload = async () => {
  if (!selectedFile.value) return
  await processVideo(selectedFile.value)
}

const handleUrlSubmit = async () => {
  if (!videoUrl.value.trim()) return
  await processVideo(videoUrl.value.trim())
}

const processVideo = async (videoSource) => {
  isProcessing.value = true
  processingStatus.value = 'Initializing...'
  processingProgress.value = 0

  try {
    // Calculate frame time in seconds
    const frameTimeInSeconds = processingMode.value === 'frame'
      ? (frameMinutes.value * 60) + frameSeconds.value
      : null

    // Set frame analysis flag
    isFrameAnalysis.value = processingMode.value === 'frame'

    // Progress callback to update status
    const onProgress = (message, progress) => {
      processingStatus.value = message
      processingProgress.value = Math.round(progress)
    }

    // Calculate sample interval in seconds from user input
    const sampleIntervalSeconds = (sampleMinutes.value * 60) + sampleSeconds.value || null

    const response = await videoService.analyze(videoSource, processingMode.value, frameTimeInSeconds, onProgress, detectionMethod.value, sampleIntervalSeconds)

    // Update UI state - for frame analysis, use frame_url; for video analysis, use video_url
    if (isFrameAnalysis.value) {
      currentVideoUrl.value = response.frame_url || response.video_url || (typeof videoSource === 'string' ? videoSource : URL.createObjectURL(videoSource))
    } else {
      currentVideoUrl.value = response.video_url || (typeof videoSource === 'string' ? videoSource : URL.createObjectURL(videoSource))
    }

    // Try to load products from analyzed files first (new backend integration)
    // Extract video file name from different sources
    let videoFileName = null
    if (typeof videoSource === 'string' && videoSource.includes('/')) {
      // Extract filename from URL path
      videoFileName = videoSource.split('/').pop()
    } else if (videoSource && videoSource.name) {
      // Extract filename from File object
      videoFileName = videoSource.name
    }

    const loadedFromFile = await loadProductsFromAnalyzedFile(videoFileName)

    // If no products loaded from file, try loading from API response (legacy)
    if (!loadedFromFile && response.products && response.products.length > 0) {
      products.value = response.products.map(product => ({
        ...product,
        timeStart: product.timestamp ? product.timestamp - 2 : 0,
        timeEnd: product.timestamp ? product.timestamp + 2 : 10,
        image: product.image_url || product.image || 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=300&fit=crop',
        price: product.price || 99.99, // Default price if not provided
        name: product.name || product.class_name || 'Detected Item',
        category: product.category || 'fashion',
        confidence: product.confidence || 0.8
      }))
      console.log(`✅ Loaded ${products.value.length} products from API response (legacy)`)
    } else if (!loadedFromFile) {
      // If no products from either source, show empty state
      products.value = []
      console.log('📦 No products detected from any source')
    }

    // Update search results for bundles tab
    searchResults.value = response.similar_products || []

    // Log results for debugging
    console.log('Analysis complete:', {
      products: products.value,
      searchResults: searchResults.value,
      videoUrl: currentVideoUrl.value
    })

    processingStatus.value = 'Complete!'

  } catch (error) {
    console.error('Error processing video:', error)
    alert('Error processing video. Please try again.')
    // Don't load sample data - show empty state instead
    products.value = []
    searchResults.value = []
  } finally {
    isProcessing.value = false
    processingStatus.value = ''
  }
}

const resetApp = () => {
  currentVideoUrl.value = ""
  videoUrl.value = ""
  selectedFile.value = null
  detectionMethod.value = 'local_yolo'
  frameMinutes.value = 0
  frameSeconds.value = 0
  isFrameAnalysis.value = false
  processingProgress.value = 0
  products.value = []
  searchResults.value = []
  showBottomContent.value = false
  showProductOverlay.value = false
}

const openBackend = () => {
  // Open backend UI in new tab
  window.open('http://localhost:8502', '_blank')
}

// Get description for selected detection method
const getDetectionMethodDescription = (method) => {
  const descriptions = {
    local_yolo: 'Fast YOLO11-based detection. Works offline, good for real-time processing.',
    hybrid_fashion: 'Combines YOLO with Google AI for better fashion item recognition.',
    enhanced_hybrid: 'Multi-agent system with advanced post-processing. Most accurate results.',
    google_ai: 'Uses Google Gemini AI for premium accuracy. Requires internet connection.',
    enhanced_yolo: 'Advanced YOLO with enhanced color detection and quality filtering.'
  }
  return descriptions[method] || 'Select a detection method to see description.'
}

// Resize functionality for bottom content
const startResizing = (event) => {
  event.preventDefault()
  isResizing.value = true

  const startY = event.clientY
  const startHeight = bottomContentHeight.value

  const handleMouseMove = (e) => {
    if (!isResizing.value) return

    // Calculate new height (dragging up decreases height, down increases)
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
    // Calculate new width (dragging right increases width, left decreases)
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

const handleTimeUpdate = (time) => {
  currentTime.value = time
}

const handleAddToCart = (item) => {
  const existingItem = cartItems.value.find(cartItem => cartItem.id === item.id)
  if (existingItem) {
    existingItem.quantity += 1
  } else {
    cartItems.value.push({
      ...item,
      quantity: 1
    })
  }
}

const handleRemoveFromCart = (itemId) => {
  cartItems.value = cartItems.value.filter(item => item.id !== itemId)
}

const handleUpdateQuantity = (itemId, quantity) => {
  if (quantity <= 0) {
    handleRemoveFromCart(itemId)
  } else {
    const item = cartItems.value.find(item => item.id === itemId)
    if (item) {
      item.quantity = quantity
    }
  }
}

// Lifecycle
onMounted(async () => {
  try {
    // Load user data
    user.value = await userService.me()
  } catch (error) {
    console.error('Error loading user data:', error)
    user.value = {
      full_name: 'Guest User',
      email: 'guest@example.com'
    }
  }

  // Load existing products from analyzed files on component mount
  console.log('🔍 Checking for existing detection results...')
  // Try to get video name from current URL if available
  let videoFileName = null
  if (currentVideoUrl.value) {
    videoFileName = currentVideoUrl.value.split('/').pop()
  }

  const hasExistingProducts = await loadProductsFromAnalyzedFile(videoFileName)
  if (hasExistingProducts) {
    showBottomContent.value = true // Show products tab if products are found
  }
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
</style>