<template>
  <div
    class="group relative bg-gray-900 rounded-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:z-10"
    @click="$emit('play', video)"
    style="width: 280px;"
  >
    <!-- Thumbnail -->
    <div class="relative aspect-video bg-gray-800">
      <img
        :src="getThumbnailUrl(video.thumbnail)"
        :alt="video.title"
        class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
        @error="handleImageError"
      />

      <!-- Play overlay -->
      <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
        <div class="bg-white/20 backdrop-blur-sm rounded-full p-3">
          <Play class="w-8 h-8 text-white fill-current" />
        </div>
      </div>

      <!-- Duration badge -->
      <div class="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
        {{ video.duration }}
      </div>

      <!-- Rating badge -->
      <div class="absolute top-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
        <Star class="w-3 h-3 fill-yellow-400 text-yellow-400" />
        <span>{{ video.rating }}</span>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4">
      <h4 class="font-semibold text-white mb-1 line-clamp-2 group-hover:text-cyan-400 transition-colors">
        {{ video.title }}
      </h4>

      <p class="text-sm text-gray-400 mb-3 line-clamp-2">
        {{ video.description }}
      </p>

      <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
        <span>{{ video.views }} views</span>
        <span>{{ formatDate(video.releaseDate) }}</span>
      </div>

      <!-- Tags -->
      <div class="flex flex-wrap gap-1 mb-3">
        <span
          v-for="tag in video.tags.slice(0, 3)"
          :key="tag"
          class="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded"
        >
          #{{ tag }}
        </span>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center justify-between">
        <button
          @click.stop="$emit('add-to-watchlist', video)"
          class="flex items-center space-x-1 text-gray-400 hover:text-white transition-colors"
        >
          <Plus class="w-4 h-4" />
          <span class="text-xs">Add to List</span>
        </button>

        <button
          @click.stop="showProductInfo = true"
          class="flex items-center space-x-1 text-gray-400 hover:text-cyan-400 transition-colors"
        >
          <ShoppingBag class="w-4 h-4" />
          <span class="text-xs">Shop</span>
        </button>
      </div>
    </div>

    <!-- Product info popup -->
    <Transition name="fade">
      <div
        v-if="showProductInfo"
        class="absolute inset-0 bg-black/90 backdrop-blur-sm p-4 flex flex-col justify-center items-center z-20"
        @click.stop="showProductInfo = false"
      >
        <div class="text-center">
          <ShoppingBag class="w-12 h-12 text-cyan-400 mx-auto mb-2" />
          <h5 class="text-white font-semibold mb-2">Shop This Video</h5>
          <p class="text-gray-300 text-sm mb-4">Discover products featured in this video</p>

          <div class="space-y-2">
            <button
              @click.stop="$emit('add-to-cart', sampleProduct)"
              class="w-full bg-cyan-500 hover:bg-cyan-600 text-white py-2 px-4 rounded transition-colors"
            >
              Add Sample Product ($29.99)
            </button>
            <button
              @click.stop="showProductInfo = false"
              class="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Play, Plus, Star, ShoppingBag } from 'lucide-vue-next'

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['play', 'add-to-cart', 'add-to-watchlist'])

const showProductInfo = ref(false)

// Sample product for demonstration
const sampleProduct = computed(() => ({
  id: `product-${props.video.id}`,
  name: `Featured Item from ${props.video.title}`,
  price: 29.99,
  image: getThumbnailUrl(props.video.thumbnail),
  description: 'Product featured in this video'
}))

const getThumbnailUrl = (thumbnail) => {
  // Return placeholder if thumbnail doesn't exist
  if (thumbnail && thumbnail !== '/videos/thumbnails/placeholder.jpg') {
    return thumbnail
  }

  // Generate a random placeholder image based on video category
  const placeholders = [
    'https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80',
    'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=225&fit=crop&q=80',
    'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=225&fit=crop&q=80',
    'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=225&fit=crop&q=80',
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=225&fit=crop&q=80',
  ]

  const index = Math.abs(props.video.id.charCodeAt(props.video.id.length - 1)) % placeholders.length
  return placeholders[index]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 1) return '1 day ago'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
  return `${Math.floor(diffDays / 365)} years ago`
}

const handleImageError = (event) => {
  // Fallback to a different placeholder if image fails to load
  event.target.src = 'https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80'
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>