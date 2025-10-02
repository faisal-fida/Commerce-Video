'use client'

import { ShoppingCart, Heart, Search } from 'lucide-react'
import { useState } from 'react'
import { Product } from '@/lib/types'
import { formatTime } from '@/lib/utils'

interface ProductsTabProps {
    products: Product[]
    currentTime: number
    onAddToCart: (product: Product) => void
    isLoading?: boolean
    error?: string | null
}

export function ProductsTab({ products, currentTime, onAddToCart, isLoading = false, error = null }: ProductsTabProps) {
    const [activeCategory, setActiveCategory] = useState('all')

    const availableCategories = ['all', ...new Set(products.map(p => p.category).filter(Boolean))]

    const filteredProducts = activeCategory === 'all'
        ? products
        : products.filter(product => product.category === activeCategory)

    const categoryColors: Record<string, string> = {
        all: 'bg-white/10 text-white border-white/20',
        clothing: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        jewelry: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
        fashion: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
        'home-decor': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
        electronics: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
        beauty: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    }

    const getCategoryColor = (category: string) => {
        return categoryColors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }

    const formatCategory = (category: string) => {
        if (!category) return 'Item'
        return category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'clothing':
                return '👕'
            case 'jewelry':
                return '💎'
            default:
                return ''
        }
    }

    return (
        <div className="h-full bg-black/90 backdrop-blur-xl border-t border-white/10">
            <div className="p-4 space-y-4 h-full overflow-y-auto custom-scrollbar pb-20">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Search className="w-5 h-5 text-purple-400" />
                        <h2 className="text-white font-semibold">Products at {formatTime(currentTime)}</h2>
                    </div>
                    <div className="text-xs text-gray-400">
                        {filteredProducts.length} {filteredProducts.length === 1 ? 'item' : 'items'} found
                    </div>
                </div>

                {/* Time indicator */}
                <div className="flex items-center gap-2 text-xs text-cyan-400 bg-cyan-400/10 px-2 py-1 rounded border border-cyan-400/20">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                    <span>Showing products detected at {formatTime(currentTime)} (±3s)</span>
                </div>

                {/* Category Filter */}
                {products.length > 0 && (
                    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                        {availableCategories.map((category) => (
                            <button
                                key={category}
                                className={`whitespace-nowrap px-3 py-1.5 text-sm rounded-lg border transition-all duration-300 ${activeCategory === category
                                    ? getCategoryColor(category)
                                    : 'bg-white/5 text-white/60 border-white/10 hover:bg-white/10'
                                    }`}
                                onClick={() => setActiveCategory(category || '')}
                            >
                                <span className="flex items-center gap-1.5">
                                    {getCategoryIcon(category || '')}
                                    {formatCategory(category || '')}
                                </span>
                            </button>
                        ))}
                    </div>
                )}

                {/* Products Grid */}
                <div className="pb-4">
                    {/* Loading State */}
                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="relative w-16 h-16 mb-4">
                                <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20"></div>
                                <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-cyan-500 animate-spin"></div>
                            </div>
                            <h3 className="text-white/80 font-medium mb-2 animate-pulse">
                                Loading products...
                            </h3>
                            <p className="text-white/50 text-sm">
                                Fetching products at {formatTime(currentTime)}
                            </p>
                        </div>
                    ) : error ? (
                        /* Error State */
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-4">
                                <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <h3 className="text-red-400 font-medium mb-2">
                                {error}
                            </h3>
                            <p className="text-white/40 text-sm">
                                Try pausing at a different timestamp
                            </p>
                        </div>
                    ) : filteredProducts.length === 0 ? (
                        /* Empty State */
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                                <Search className="w-8 h-8 text-white/40" />
                            </div>
                            <h3 className="text-white/60 font-medium mb-2">
                                {products.length === 0 ? 'No products detected' : 'No matching products'}
                            </h3>
                            <p className="text-white/40 text-sm">
                                {products.length === 0
                                    ? 'Upload and analyze a video to discover items'
                                    : `No ${formatCategory(activeCategory)} items found. Try "All" category.`
                                }
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                            {filteredProducts.map((product) => (
                                <div
                                    key={product.id}
                                    className="group bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 p-2 hover:bg-white/10 transition-all duration-300"
                                >
                                    <div className="relative">
                                        {/* Product Image */}
                                        <div className="w-full aspect-square relative rounded-md mb-2 overflow-hidden">
                                            <img
                                                src={product.image || product.image_url || '/placeholder.jpg'}
                                                alt={product.name}
                                                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                                            />

                                            {/* Hover Overlay */}
                                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
                                                <div className="flex flex-col gap-1">
                                                    <button
                                                        className="bg-gradient-to-r from-purple-600 to-cyan-600 text-white text-xs px-2 py-1 rounded flex items-center justify-center min-w-[60px]"
                                                        onClick={() => onAddToCart(product)}
                                                        title="Add to Cart"
                                                    >
                                                        <ShoppingCart className="w-3 h-3 mr-1" />
                                                        Add
                                                    </button>
                                                    <button
                                                        className="bg-gradient-to-r from-pink-600 to-red-600 text-white text-xs px-2 py-1 rounded flex items-center justify-center min-w-[60px]"
                                                        title="Add to Favorites"
                                                    >
                                                        <Heart className="w-3 h-3 mr-1" />
                                                        Fave
                                                    </button>
                                                </div>
                                            </div>

                                            {/* Confidence Badge */}
                                            <div className="absolute top-1 left-1 bg-black/70 backdrop-blur-sm text-white text-xs px-1 py-0.5 rounded">
                                                {Math.round((product.confidence || 0.8) * 100)}%
                                            </div>
                                        </div>

                                        {/* Product Info */}
                                        <div className="space-y-1">
                                            <div className="flex items-center justify-between">
                                                <span
                                                    className={`inline-flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded border ${getCategoryColor(product.category)}`}
                                                >
                                                    {getCategoryIcon(product.category || '')}
                                                    <span className="font-medium">
                                                        {product.category === 'clothing' || product.category === 'jewelry'
                                                            ? formatCategory(product.category)
                                                            : formatCategory(product.object_type || product.category || '')}
                                                    </span>
                                                </span>
                                                {product.stock === 'In Stock' && (
                                                    <span className="text-green-400 text-xs">●</span>
                                                )}
                                            </div>

                                            <h3 className="text-white font-medium text-xs leading-tight line-clamp-1">
                                                {product.name}
                                            </h3>

                                            {product.timestamp !== undefined && (
                                                <p className="text-xs text-cyan-400 leading-none">
                                                    {formatTime(product.timestamp)}
                                                </p>
                                            )}

                                            <div className="flex items-center justify-between">
                                                <span className="text-white font-semibold text-xs">
                                                    ${(product.price || 99.99).toFixed(0)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

