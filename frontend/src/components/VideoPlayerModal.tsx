'use client'

import { X, ArrowLeft, ShoppingBag } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Video, CartItem, Product, Bundle, ProductResult } from '@/lib/types'
import { api } from '@/lib/api'
import { TabBar } from './TabBar'
import { ProductsTab } from './ProductsTab'
import { BundlesTab } from './BundlesTab'
import { ProfileTab } from './ProfileTab'

interface VideoPlayerModalProps {
    video: Video
    cartItems: CartItem[]
    onClose: () => void
    onAddToCart: (item: Product | Bundle) => void
    onOpenCart: () => void
}

export function VideoPlayerModal({
    video,
    cartItems,
    onClose,
    onAddToCart,
    onOpenCart
}: VideoPlayerModalProps) {
    const videoRef = useRef<HTMLVideoElement>(null)
    const [showInfo, setShowInfo] = useState(true)
    const [activeTab, setActiveTab] = useState<'products' | 'bundles' | 'profile'>('products')
    const [showBottomContent, setShowBottomContent] = useState(false) // Start hidden
    const [bottomContentHeight, setBottomContentHeight] = useState(384) // Default 384px
    const [isResizing, setIsResizing] = useState(false)
    const [currentTime, setCurrentTime] = useState(0)
    const [products, setProducts] = useState<Product[]>([])
    const [bundles, setBundles] = useState<Bundle[]>([])
    const [loadingProducts, setLoadingProducts] = useState(false)
    const [productsError, setProductsError] = useState<string | null>(null)
    const lastLoadedTimeRef = useRef<number>(-1)
    const isVideoPlayingRef = useRef<boolean>(true) // Assume playing initially (autoplay)

    const cartItemsCount = cartItems.reduce((sum, item) => sum + item.quantity, 0)

    const sampleUser = {
        full_name: 'John Doe',
        email: 'john@example.com'
    }

    const handleTimeUpdate = (e: React.SyntheticEvent<HTMLVideoElement>) => {
        const time = e.currentTarget.currentTime
        setCurrentTime(time)

        // Track if video is playing
        isVideoPlayingRef.current = !e.currentTarget.paused
    }

    const handlePause = () => {
        isVideoPlayingRef.current = false

        // Automatically show bottom content panel when paused
        setShowBottomContent(true)

        // Load products immediately when paused
        if (video.status === 'completed') {
            const roundedTime = Math.round(currentTime / 6) * 6

            // Clear products immediately if pausing at a different time
            if (lastLoadedTimeRef.current !== roundedTime) {
                setProducts([])
                setBundles([])
            }

            loadProductsForTime(currentTime)
        }
    }

    const handlePlay = () => {
        isVideoPlayingRef.current = true

        // Automatically hide bottom content panel when playing
        setShowBottomContent(false)
    }

    /**
     * Convert ProductResult from API to Product for frontend
     */
    const mapProductResults = (results: ProductResult[]): Product[] => {
        return results.map((result, index) => ({
            ...result,
            id: `${result.object_type}-${index}`,
            name: result.title,
            price: 29.99 + Math.random() * 50, // Mock price
            image: api.getProductImageUrl(result.image_url),
            category: result.object_type,
            confidence: 0.8 + Math.random() * 0.2,
            timestamp: currentTime,
        }))
    }

    /**
     * Load products for the current timestamp
     */
    const loadProductsForTime = async (time: number) => {
        // Only load products for completed videos
        if (video.status !== 'completed') {
            setProducts([])
            setBundles([])
            return
        }

        // Round time to nearest 6-second interval (matches backend processing interval)
        const roundedTime = Math.round(time / 6) * 6

        // Skip if we already loaded products for this time
        if (lastLoadedTimeRef.current === roundedTime) {
            console.log(`Products already loaded for time ${roundedTime}s, skipping`)
            return
        }

        lastLoadedTimeRef.current = roundedTime
        setLoadingProducts(true)
        setProductsError(null)

        try {
            // Fetch products and bundles in parallel
            const [productsData, bundlesData] = await Promise.all([
                api.getResults(video.id, roundedTime),
                api.getBundles(video.id, roundedTime)
            ])

            setProducts(mapProductResults(productsData))
            setBundles(bundlesData)

            console.log(`Loaded ${productsData.length} products for time ${roundedTime}s`)
        } catch (error) {
            console.error('Error loading products:', error)
            setProductsError('Failed to load products. Please try again.')
            setProducts([])
            setBundles([])
        } finally {
            setLoadingProducts(false)
        }
    }

    /**
     * Load products when video is paused or when time changes significantly
     * Only trigger when video is NOT playing to avoid excessive requests
     */
    useEffect(() => {
        // Skip if video is still processing or failed
        if (video.status !== 'completed') {
            return
        }

        // Only load when video is paused (not during playback)
        // Reduced debounce time for better responsiveness
        const timeoutId = setTimeout(() => {
            if (!isVideoPlayingRef.current) {
                const roundedTime = Math.round(currentTime / 6) * 6

                // Clear products immediately if time changed
                if (lastLoadedTimeRef.current !== roundedTime) {
                    setProducts([])
                    setBundles([])
                }

                loadProductsForTime(currentTime)
            }
        }, 300) // Reduced debounce time from 1000ms to 300ms

        return () => clearTimeout(timeoutId)
    }, [currentTime, video.id, video.status])

    /**
     * Load products initially when modal opens
     */
    useEffect(() => {
        if (video.status === 'completed') {
            loadProductsForTime(0)
        }
    }, [video.id])

    const startResizing = (event: React.MouseEvent) => {
        event.preventDefault()
        setIsResizing(true)

        const startY = event.clientY
        const startHeight = bottomContentHeight

        const handleMouseMove = (e: MouseEvent) => {
            if (!isResizing) return

            const deltaY = startY - e.clientY
            const newHeight = Math.max(200, Math.min(window.innerHeight * 0.8, startHeight + deltaY))
            setBottomContentHeight(newHeight)
        }

        const handleMouseUp = () => {
            setIsResizing(false)
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

    const handleAddToCart = (item: Product | Bundle) => {
        if ('products' in item) {
            // It's a bundle - convert to CartItem format
            const bundleCartItem: CartItem = {
                id: item.id,
                name: item.name,
                price: item.discount_price || item.total_price,
                image: item.image_url,
                quantity: 1,
                type: 'bundle',
                bundle_products: item.products
            }
            onAddToCart(bundleCartItem as unknown as Product)
        } else {
            // It's a product
            onAddToCart(item)
        }
    }

    useEffect(() => {
        // Auto-hide info panel after 3 seconds
        const timer = setTimeout(() => {
            setShowInfo(false)
        }, 3000)

        return () => clearTimeout(timer)
    }, [])

    useEffect(() => {
        // Set initial playing state based on video element
        if (videoRef.current) {
            isVideoPlayingRef.current = !videoRef.current.paused
        }
    }, [])

    return (
        <div className="fixed inset-0 z-50 bg-black">
            {/* Header */}
            <div className="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/80 to-transparent p-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={onClose}
                            className="flex items-center space-x-2 text-white hover:text-gray-300 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            <span>Back</span>
                        </button>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Cart Button */}
                        <button
                            onClick={onOpenCart}
                            className="text-white hover:text-gray-300 transition-colors bg-white/10 backdrop-blur-sm p-2 rounded-lg relative group hover:bg-white/20"
                            title={`Cart (${cartItemsCount} items) - Click to view cart`}
                        >
                            <ShoppingBag className="w-5 h-5 transition-transform group-hover:scale-110" />
                            {cartItemsCount > 0 && (
                                <span className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center animate-pulse font-bold shadow-lg">
                                    {cartItemsCount}
                                </span>
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Video Player */}
            <div className="relative w-full h-full flex items-center justify-center bg-black">
                <video
                    ref={videoRef}
                    src={video.videoUrl || video.video_url}
                    poster={video.thumbnail}
                    className="max-w-full max-h-full"
                    controls
                    autoPlay
                    onTimeUpdate={handleTimeUpdate}
                    onPause={handlePause}
                    onPlay={handlePlay}
                >
                    Your browser does not support the video tag.
                </video>
            </div>

            {/* Video Info Overlay */}
            <div
                className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent p-6 transition-transform duration-300 ${showInfo ? 'translate-y-0' : 'translate-y-full'
                    }`}
            >
                <div className="max-w-4xl">
                    <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                            <h2 className="text-2xl font-bold text-white mb-2">{video.title}</h2>
                            <p className="text-gray-300 mb-4">{video.description}</p>

                            <div className="flex items-center space-x-6 text-sm text-gray-400 mb-4">
                                <span>{video.views} views</span>
                                <span>⭐ {video.rating} rating</span>
                                <span>{video.duration}</span>
                            </div>

                            {/* Tags */}
                            <div className="flex flex-wrap gap-2 mb-4">
                                {video.tags?.map((tag) => (
                                    <span
                                        key={tag}
                                        className="bg-gray-800 text-gray-300 text-sm px-3 py-1 rounded-full"
                                    >
                                        #{tag}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <button
                            onClick={() => setShowInfo(!showInfo)}
                            className="text-white hover:text-gray-300 ml-4 transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Info toggle button */}
            <button
                onClick={() => setShowInfo(!showInfo)}
                className="absolute bottom-4 right-4 bg-black/50 backdrop-blur-sm text-white p-2 rounded-full hover:bg-black/70 transition-colors z-20"
            >
                <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
            </button>

            {/* Bottom Tab Bar */}
            <div className="absolute bottom-0 left-0 right-0 z-30">
                <TabBar
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                    onToggleContent={() => setShowBottomContent(true)}
                />

                {/* Bottom Content Panel with smooth slide animation */}
                <div
                    className={`bg-black/90 backdrop-blur-sm border-t border-gray-800 overflow-hidden relative transition-all duration-500 ease-in-out ${showBottomContent ? 'opacity-100' : 'opacity-0 pointer-events-none'
                        }`}
                    style={{
                        height: showBottomContent ? `${bottomContentHeight}px` : '0px',
                        transform: showBottomContent ? 'translateY(0)' : 'translateY(20px)'
                    }}
                >
                    {/* Drag Handle for Resizing */}
                    <div
                        className="absolute top-0 left-0 right-0 h-2 cursor-row-resize bg-gradient-to-b from-white/20 to-transparent hover:from-white/30 z-10 flex items-center justify-center group"
                        onMouseDown={startResizing}
                    >
                        <div className="w-12 h-1 bg-white/40 rounded-full group-hover:bg-white/60 transition-colors"></div>
                    </div>

                    {/* Content Area with padding for drag handle */}
                    <div className="pt-2 h-full overflow-hidden">
                        {activeTab === 'products' && (
                            <ProductsTab
                                products={products}
                                currentTime={currentTime}
                                onAddToCart={handleAddToCart}
                                isLoading={loadingProducts}
                                error={productsError}
                            />
                        )}
                        {activeTab === 'bundles' && (
                            <BundlesTab
                                bundles={bundles}
                                onAddToCart={handleAddToCart}
                                isLoading={loadingProducts}
                                error={productsError}
                            />
                        )}
                        {activeTab === 'profile' && (
                            <ProfileTab user={sampleUser} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

