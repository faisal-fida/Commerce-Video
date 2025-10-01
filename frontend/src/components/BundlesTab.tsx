'use client'

import { Package, ShoppingCart, Star, Tag } from 'lucide-react'
import { Bundle } from '@/lib/types'
import { api } from '@/lib/api'

interface BundlesTabProps {
    bundles: Bundle[]
    onAddToCart: (bundle: Bundle) => void
    isLoading?: boolean
    error?: string | null
}

export function BundlesTab({ bundles, onAddToCart, isLoading = false, error = null }: BundlesTabProps) {
    const categoryColors: Record<string, string> = {
        wardrobe: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
        'home-setup': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
        'tech-bundle': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        'skincare-routine': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
        'workout-gear': 'bg-green-500/20 text-green-300 border-green-500/30'
    }

    const getCategoryColor = (category: string) => {
        return categoryColors[category] || 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }

    const formatCategory = (category: string) => {
        return category ? category.replace('-', ' ') : 'Bundle'
    }

    return (
        <div className="h-full bg-black/90 backdrop-blur-xl border-t border-white/10">
            <div className="p-4 space-y-4 h-full overflow-y-auto custom-scrollbar pb-20">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Package className="w-5 h-5 text-purple-400" />
                        <h2 className="text-white font-semibold">Smart Bundles</h2>
                    </div>
                    <div className="text-xs text-gray-400">
                        {bundles.length} {bundles.length === 1 ? 'bundle' : 'bundles'} available
                    </div>
                </div>

                <div className="pb-4">
                    {isLoading ? (
                        /* Loading State */
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="relative w-16 h-16 mb-4">
                                <div className="absolute inset-0 rounded-full border-4 border-purple-500/20"></div>
                                <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-500 animate-spin"></div>
                            </div>
                            <h3 className="text-white/80 font-medium mb-2 animate-pulse">
                                Loading bundles...
                            </h3>
                            <p className="text-white/50 text-sm">
                                Fetching smart bundles for this scene
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
                    ) : bundles.length === 0 ? (
                        /* Empty State */
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                                <Package className="w-8 h-8 text-white/40" />
                            </div>
                            <h3 className="text-white/60 font-medium mb-2">No bundles available</h3>
                            <p className="text-white/40 text-sm">
                                Bundles will appear here when products are detected
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {bundles.map((bundle) => (
                                <div
                                    key={bundle.id}
                                    className="group bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden hover:bg-white/10 transition-all duration-300"
                                >
                                    <div className="flex">
                                        {/* Bundle Image */}
                                        <div className="w-24 h-24 flex-shrink-0 bg-gradient-to-br from-purple-500/20 to-cyan-500/20">
                                            <img
                                                src={api.getProductImageUrl(bundle.image_url)}
                                                alt={bundle.name}
                                                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                                                onError={(e) => {
                                                    // Fallback to first product image if bundle image fails
                                                    const firstProduct = bundle.products?.[0]
                                                    if (firstProduct?.image_url) {
                                                        e.currentTarget.src = api.getProductImageUrl(firstProduct.image_url)
                                                    } else {
                                                        e.currentTarget.src = '/placeholder.jpg'
                                                    }
                                                }}
                                            />
                                        </div>

                                        {/* Bundle Info */}
                                        <div className="flex-1 p-4">
                                            <div className="flex items-start justify-between mb-2">
                                                <div className="flex-1">
                                                    <span
                                                        className={`inline-block text-xs mb-2 px-2 py-1 rounded border ${getCategoryColor(bundle.category)}`}
                                                    >
                                                        {formatCategory(bundle.category)}
                                                    </span>
                                                    <h3 className="text-white font-medium text-sm leading-tight mb-1">
                                                        {bundle.name}
                                                    </h3>
                                                    <p className="text-white/60 text-xs line-clamp-2">
                                                        {bundle.description}
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    {bundle.discount_price && bundle.discount_price < bundle.total_price && (
                                                        <span className="text-white/60 text-sm line-through">
                                                            ${bundle.total_price.toFixed(2)}
                                                        </span>
                                                    )}
                                                    <span className="text-white font-semibold">
                                                        ${(bundle.discount_price || bundle.total_price).toFixed(2)}
                                                    </span>
                                                    {bundle.discount_price && bundle.discount_price < bundle.total_price && (
                                                        <span className="text-xs bg-green-500/20 text-green-300 border border-green-500/30 px-2 py-1 rounded flex items-center">
                                                            <Tag className="w-2 h-2 mr-1" />
                                                            Save ${(bundle.total_price - bundle.discount_price).toFixed(2)}
                                                        </span>
                                                    )}
                                                </div>

                                                <button
                                                    className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white text-xs px-3 py-1 rounded flex items-center transition-colors"
                                                    onClick={() => onAddToCart(bundle)}
                                                >
                                                    <ShoppingCart className="w-3 h-3 mr-1" />
                                                    Add Bundle
                                                </button>
                                            </div>

                                            {/* Items Count and Similarity */}
                                            <div className="flex items-center justify-between mt-2">
                                                <div className="flex items-center gap-1">
                                                    <Star className="w-3 h-3 text-yellow-400" />
                                                    <span className="text-white/60 text-xs">
                                                        {bundle.product_ids?.length || bundle.products?.length || 0} items
                                                    </span>
                                                </div>
                                                {bundle.similarity_score && (
                                                    <div className="text-xs text-cyan-300 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/20">
                                                        {Math.round(bundle.similarity_score * 100)}% match
                                                    </div>
                                                )}
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

