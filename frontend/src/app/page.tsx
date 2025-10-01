'use client'

import { useState, useEffect } from 'react'
import { Search, ShoppingBag, Play, Plus, Star, ChevronLeft, ChevronRight, Upload } from 'lucide-react'
import { Video, Product, CartItem, Bundle } from '@/lib/types'
import { videoDiscovery } from '@/lib/videoDiscovery'
import { VideoCard } from '@/components/VideoCard'
import { CartDrawer } from '@/components/CartDrawer'
import { VideoPlayerModal } from '@/components/VideoPlayerModal'
import { VideoUpload } from '@/components/VideoUpload'

export default function VideoShowcase() {
  const [discoveredVideos, setDiscoveredVideos] = useState<Video[]>([])
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [showSearchBar, setShowSearchBar] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCart, setShowCart] = useState(false)
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [watchlist, setWatchlist] = useState<Video[]>([])
  const [isLoadingVideos, setIsLoadingVideos] = useState(true)
  const [showUpload, setShowUpload] = useState(false)

  const featuredVideo = discoveredVideos.length > 0 ? discoveredVideos[0] : null

  const filteredCategories = () => {
    const categories = []

    if (discoveredVideos.length > 0) {
      categories.push({
        id: 'discovered',
        name: 'Available Videos',
        videos: discoveredVideos
      })
    }

    if (categories.length === 0) return []

    if (!searchQuery.trim()) {
      return categories
    }

    const query = searchQuery.toLowerCase()
    return categories.map(category => ({
      ...category,
      videos: category.videos.filter(video =>
        (video.title?.toLowerCase().includes(query) || false) ||
        (video.description?.toLowerCase().includes(query) || false) ||
        (video.tags?.some(tag => tag.toLowerCase().includes(query)) || false)
      )
    })).filter(category => category.videos.length > 0)
  }

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0)

  const toggleSearch = () => {
    setShowSearchBar(!showSearchBar)
    if (!showSearchBar) {
      setSearchQuery('')
    }
  }

  const playVideo = (video: Video) => {
    setSelectedVideo(video)
    console.log('Play video:', video)
  }

  const closeVideoPlayer = () => {
    setSelectedVideo(null)
  }

  const addToWatchlist = (video: Video) => {
    const exists = watchlist.find(item => item.id === video.id)
    if (!exists) {
      setWatchlist([...watchlist, video])
      console.log(`Added "${video.title}" to watchlist`)
    }
  }

  const addToCart = (item: Product | Bundle | CartItem) => {
    console.log('🛒 VideoShowcase - Adding item to cart:', item)
    const existingItem = cartItems.find(cartItem => cartItem.id === item.id)
    if (existingItem) {
      existingItem.quantity += 1
      setCartItems([...cartItems])
      console.log('🛒 VideoShowcase - Updated quantity:', existingItem.quantity)
    } else {
      let cartItem: CartItem

      // Check if it's already a CartItem (from bundles)
      if ('quantity' in item) {
        cartItem = item as CartItem
      } else if ('product_ids' in item || 'products' in item) {
        // It's a Bundle
        const bundle = item as Bundle
        cartItem = {
          id: bundle.id,
          name: bundle.name,
          price: bundle.discount_price || bundle.total_price,
          image: bundle.image_url,
          quantity: 1,
          type: 'bundle',
          bundle_products: bundle.products
        }
      } else {
        // It's a Product
        const product = item as Product
        cartItem = {
          id: product.id || '',
          name: product.name || 'Unknown Product',
          price: product.price || 99.99,
          image: product.image || product.image_url || '/placeholder.jpg',
          quantity: 1
        }
      }

      setCartItems([...cartItems, cartItem])
      console.log('🛒 VideoShowcase - Added new item:', cartItem)
    }
    console.log('🛒 VideoShowcase - Total cart items:', cartItems.length + 1)
  }

  const removeFromCart = (itemId: string) => {
    setCartItems(cartItems.filter(item => item.id !== itemId))
  }

  const updateQuantity = (itemId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(itemId)
    } else {
      const item = cartItems.find(item => item.id === itemId)
      if (item) {
        item.quantity = quantity
        setCartItems([...cartItems])
      }
    }
  }

  const scrollLeft = (categoryId: string) => {
    const container = document.querySelector(`.scroll-container-${categoryId}`)
    if (container) {
      container.scrollBy({ left: -320, behavior: 'smooth' })
    }
  }

  const scrollRight = (categoryId: string) => {
    const container = document.querySelector(`.scroll-container-${categoryId}`)
    if (container) {
      container.scrollBy({ left: 320, behavior: 'smooth' })
    }
  }

  const loadDiscoveredVideos = async () => {
    setIsLoadingVideos(true)
    try {
      console.log('🔍 Loading videos from videos.json...')
      const videos = await videoDiscovery.discoverVideos()
      setDiscoveredVideos(videos)
      console.log(`✅ Loaded ${videos.length} videos:`, videos)
    } catch (error) {
      console.error('❌ Error loading videos:', error)
      setDiscoveredVideos([])
    } finally {
      setIsLoadingVideos(false)
    }
  }

  const refreshVideos = async () => {
    console.log('🔄 Refreshing video list...')
    videoDiscovery.refreshVideoList()
    await loadDiscoveredVideos()
  }

  const handleUploadComplete = async (videoId: string) => {
    console.log(`✅ Video uploaded: ${videoId}`)
    // Refresh video list to show the newly uploaded video
    videoDiscovery.refreshVideoList()
    await loadDiscoveredVideos()
    setShowUpload(false)
  }

  useEffect(() => {
    loadDiscoveredVideos()
  }, [])

  const categories = filteredCategories()

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="relative z-10 p-4 bg-gradient-to-b from-black/80 to-transparent">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">Z</span>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Zora Video
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <button
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
              onClick={toggleSearch}
            >
              <Search className="w-5 h-5" />
            </button>
            <button
              className="bg-cyan-500 hover:bg-cyan-600 px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
              onClick={() => setShowUpload(true)}
            >
              <Upload className="w-4 h-4" />
              <span>Upload</span>
            </button>
            <button
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
              onClick={refreshVideos}
              disabled={isLoadingVideos}
            >
              <svg
                className={`w-5 h-5 ${isLoadingVideos ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button
              className="p-2 hover:bg-white/10 rounded-full transition-colors relative"
              onClick={() => setShowCart(true)}
            >
              <ShoppingBag className="w-5 h-5" />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      {showSearchBar && (
        <div className="relative z-10 px-4 pb-4 transition-all duration-300 ease-in-out">
          <div className="max-w-7xl mx-auto">
            <div className="relative">
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                type="text"
                placeholder="Search videos..."
                className="w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-lg px-4 py-3 pl-12 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 transition-colors"
              />
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>
        </div>
      )}

      {/* Featured Video */}
      {featuredVideo && (
        <section className="relative mb-8">
          <div
            className="relative h-96 bg-cover bg-center"
            style={{
              backgroundImage: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=1920&h=600&fit=crop&q=80')`
            }}
          >
            <div className="absolute inset-0 flex items-center">
              <div className="max-w-7xl mx-auto px-4 w-full">
                <div className="max-w-2xl">
                  <span className="inline-block bg-red-600 text-white px-2 py-1 text-xs font-bold rounded mb-2 uppercase">
                    Featured
                  </span>
                  <h2 className="text-4xl font-bold mb-4">{featuredVideo.title}</h2>
                  <p className="text-lg text-gray-200 mb-6 line-clamp-2">{featuredVideo.description}</p>
                  <div className="flex items-center space-x-4 mb-6">
                    <span className="text-sm text-gray-300">{featuredVideo.views} views</span>
                    <span className="text-sm text-gray-300">•</span>
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm text-gray-300">{featuredVideo.rating}</span>
                    </div>
                    <span className="text-sm text-gray-300">•</span>
                    <span className="text-sm text-gray-300">{featuredVideo.duration}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => playVideo(featuredVideo)}
                      className="bg-white text-black px-8 py-3 rounded-lg font-semibold flex items-center space-x-2 hover:bg-gray-200 transition-colors"
                    >
                      <Play className="w-5 h-5 fill-current" />
                      <span>Play</span>
                    </button>
                    <button
                      onClick={() => addToWatchlist(featuredVideo)}
                      className="bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 hover:bg-white/30 transition-colors"
                    >
                      <Plus className="w-5 h-5" />
                      <span>My List</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Loading State */}
      {isLoadingVideos && discoveredVideos.length === 0 && (
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="text-center">
            <div className="animate-spin w-12 h-12 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-white text-lg">Loading videos...</p>
            <p className="text-gray-400 text-sm mt-2">Reading videos.json and verifying files</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoadingVideos && discoveredVideos.length === 0 && (
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="text-center">
            <div className="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-12 h-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 4V2C7 1.45 7.45 1 8 1h8c.55 0 1 .45 1 1v2m0 0v16c0 .55-.45 1-1 1H8c-.55 0-1-.45-1-1V4m0 0H5c-.55 0-1 .45-1 1v14c0 .55.45 1 1 1h2m10-16h2c.55 0 1 .45 1 1v14c0 .55-.45 1-1 1h-2"></path>
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">No Videos Found</h3>
            <p className="text-gray-500 text-sm">
              Add video files to see them here.
            </p>
          </div>
        </div>
      )}

      {/* Video Categories */}
      {!isLoadingVideos && categories.length > 0 && (
        <main className="max-w-7xl mx-auto px-4 space-y-8 pb-8">
          {categories.map((category) => (
            <div key={category.id} className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold">{category.name}</h3>
                <button className="text-cyan-400 hover:text-cyan-300 text-sm font-medium">
                  View All
                </button>
              </div>

              <div className="relative">
                <div
                  className={`flex space-x-4 overflow-x-auto scrollbar-hide pb-2 scroll-container-${category.id}`}
                >
                  {category.videos.map((video) => (
                    <VideoCard
                      key={video.id}
                      video={video}
                      onPlay={playVideo}
                      onAddToCart={addToCart}
                      onAddToWatchlist={addToWatchlist}
                    />
                  ))}
                </div>

                {/* Scroll buttons */}
                <button
                  onClick={() => scrollLeft(category.id)}
                  className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-black/60 hover:bg-black/80 rounded-full p-2 transition-colors z-10"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => scrollRight(category.id)}
                  className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-black/60 hover:bg-black/80 rounded-full p-2 transition-colors z-10"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </main>
      )}

      {/* Video Player Modal */}
      {selectedVideo && (
        <VideoPlayerModal
          video={selectedVideo}
          cartItems={cartItems}
          onClose={closeVideoPlayer}
          onAddToCart={addToCart}
          onOpenCart={() => setShowCart(true)}
        />
      )}

      {/* Cart Drawer */}
      <CartDrawer
        open={showCart}
        items={cartItems}
        onClose={() => setShowCart(false)}
        onRemoveItem={removeFromCart}
        onUpdateQuantity={updateQuantity}
      />

      {/* Video Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4">
          <VideoUpload
            onUploadComplete={handleUploadComplete}
            onClose={() => setShowUpload(false)}
          />
        </div>
      )}
    </div>
  )
}
