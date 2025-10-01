'use client'

import { Play, Plus, Star, ShoppingBag } from 'lucide-react'
import { useState } from 'react'
import { Video, Product } from '@/lib/types'
import { formatDate } from '@/lib/utils'

interface VideoCardProps {
    video: Video
    onPlay: (video: Video) => void
    onAddToCart: (item: Product) => void
    onAddToWatchlist: (video: Video) => void
}

export function VideoCard({ video, onPlay, onAddToCart, onAddToWatchlist }: VideoCardProps) {
    const [showProductInfo, setShowProductInfo] = useState(false)
    const [imageError, setImageError] = useState(false)

    const getThumbnailUrl = (thumbnail: string): string => {
        if (thumbnail && thumbnail !== '/videos/thumbnails/placeholder.jpg') {
            return thumbnail
        }

        const placeholders = [
            'https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80',
            'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=225&fit=crop&q=80',
            'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=225&fit=crop&q=80',
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=225&fit=crop&q=80',
            'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=225&fit=crop&q=80',
        ]

        const index = Math.abs(video.id.charCodeAt(video.id.length - 1)) % placeholders.length
        return placeholders[index]
    }

    const sampleProduct: Product = {
        id: `product-${video.id}`,
        name: `Featured Item from ${video.title}`,
        price: 29.99,
        image: getThumbnailUrl(video.thumbnail),
        category: 'fashion',
        description: 'Product featured in this video'
    }

    return (
        <div
            className="group relative bg-gray-900 rounded-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:z-10"
            onClick={() => onPlay(video)}
            style={{ width: '280px' }}
        >
            {/* Thumbnail */}
            <div className="relative aspect-video bg-gray-800">
                <img
                    src={getThumbnailUrl(video.thumbnail)}
                    alt={video.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    onError={(e) => {
                        if (!imageError) {
                            setImageError(true)
                            e.currentTarget.src = 'https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80'
                        }
                    }}
                />

                {/* Play overlay */}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                    <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
                        <Play className="w-8 h-8 text-white fill-current" />
                    </div>
                </div>

                {/* Duration badge */}
                <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                    {video.duration}
                </div>

                {/* Rating badge */}
                <div className="absolute top-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
                    <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    <span>{video.rating}</span>
                </div>
            </div>

            {/* Content */}
            <div className="p-4">
                <h4 className="font-semibold text-white mb-1 line-clamp-2 group-hover:text-cyan-400 transition-colors">
                    {video.title}
                </h4>

                <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                    {video.description}
                </p>

                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <span>{video.views} views</span>
                    <span>{formatDate(video.releaseDate)}</span>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-3">
                    {video.tags.slice(0, 3).map((tag) => (
                        <span
                            key={tag}
                            className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded"
                        >
                            #{tag}
                        </span>
                    ))}
                </div>

                {/* Action buttons */}
                <div className="flex items-center justify-between">
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            onAddToWatchlist(video)
                        }}
                        className="flex items-center space-x-1 text-gray-400 hover:text-white transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        <span className="text-xs">Add to List</span>
                    </button>

                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            setShowProductInfo(true)
                        }}
                        className="flex items-center space-x-1 text-gray-400 hover:text-cyan-400 transition-colors"
                    >
                        <ShoppingBag className="w-4 h-4" />
                        <span className="text-xs">Shop</span>
                    </button>
                </div>
            </div>

            {/* Product info popup */}
            {showProductInfo && (
                <div
                    className="absolute inset-0 bg-black/90 backdrop-blur-sm p-4 flex flex-col justify-center items-center z-20 transition-opacity duration-300"
                    onClick={(e) => {
                        e.stopPropagation()
                        setShowProductInfo(false)
                    }}
                >
                    <div className="text-center">
                        <ShoppingBag className="w-12 h-12 text-cyan-400 mx-auto mb-2" />
                        <h5 className="text-white font-semibold mb-2">Shop This Video</h5>
                        <p className="text-gray-300 text-sm mb-4">Discover products featured in this video</p>

                        <div className="space-y-2">
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    onAddToCart(sampleProduct)
                                    setShowProductInfo(false)
                                }}
                                className="w-full bg-cyan-500 hover:bg-cyan-600 text-white py-2 px-4 rounded transition-colors"
                            >
                                Add Sample Product ($29.99)
                            </button>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    setShowProductInfo(false)
                                }}
                                className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

