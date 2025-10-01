'use client'

import { X, Minus, Plus, Trash2, ShoppingBag, CreditCard } from 'lucide-react'
import { CartItem } from '@/lib/types'

interface CartDrawerProps {
    open: boolean
    items: CartItem[]
    onClose: () => void
    onRemoveItem: (itemId: string) => void
    onUpdateQuantity: (itemId: string, quantity: number) => void
}

export function CartDrawer({ open, items, onClose, onRemoveItem, onUpdateQuantity }: CartDrawerProps) {
    const subtotal = items.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0)
    const tax = subtotal * 0.08 // 8% tax
    const total = subtotal + tax

    const handleCheckout = () => {
        console.log('Checkout clicked')
    }

    if (!open) return null

    return (
        <div className="fixed inset-0 z-[100]">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/20 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Sliding Cart Panel */}
            <div
                className={`fixed right-0 top-0 h-full w-96 bg-black/95 backdrop-blur-xl border-l border-white/10 z-[101] overflow-hidden transform transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'
                    }`}
            >
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="p-6 border-b border-white/10">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full flex items-center justify-center">
                                    <ShoppingBag className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-semibold text-white">Your Cart</h2>
                                    <p className="text-sm text-white/60">
                                        {items.length} item{items.length !== 1 ? 's' : ''}
                                    </p>
                                </div>
                            </div>
                            <button
                                className="text-white/60 hover:text-white hover:bg-white/10 p-2 rounded transition-colors"
                                onClick={onClose}
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Cart Items */}
                    <div className="flex-1 overflow-y-auto custom-scrollbar">
                        {items.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center p-6">
                                <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                                    <ShoppingBag className="w-8 h-8 text-white/40" />
                                </div>
                                <h3 className="text-white/60 font-medium mb-2">Your cart is empty</h3>
                                <p className="text-white/40 text-sm">Add some products to get started!</p>
                            </div>
                        ) : (
                            <div className="p-4 space-y-4">
                                {items.map((item, index) => (
                                    <div
                                        key={`${item.id}-${index}`}
                                        className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-4"
                                    >
                                        <div className="flex gap-3">
                                            {/* Product Image */}
                                            <img
                                                src={item.image || '/placeholder.jpg'}
                                                alt={item.name || 'Product'}
                                                className="w-16 h-16 object-cover rounded-xl flex-shrink-0"
                                            />

                                            {/* Product Details */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex justify-between items-start mb-2">
                                                    <h3 className="font-medium text-white text-sm leading-tight">
                                                        {item.name || 'Product'}
                                                    </h3>
                                                    <button
                                                        className="w-6 h-6 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors"
                                                        onClick={() => onRemoveItem(item.id)}
                                                    >
                                                        <Trash2 className="w-3 h-3" />
                                                    </button>
                                                </div>

                                                <div className="mb-3">
                                                    <p className="text-white/60 text-xs">
                                                        ${(item.price || 0).toFixed(2)} each
                                                    </p>
                                                    {item.type === 'bundle' && item.bundle_products && (
                                                        <div className="mt-1">
                                                            <p className="text-blue-300 text-xs">
                                                                Bundle: {item.bundle_products.length} items included
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Quantity Controls */}
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2 bg-white/5 rounded-lg p-1">
                                                        <button
                                                            className="w-6 h-6 text-white/60 hover:text-white rounded transition-colors"
                                                            onClick={() => onUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                                                        >
                                                            <Minus className="w-3 h-3" />
                                                        </button>
                                                        <span className="text-white text-sm font-medium w-8 text-center">
                                                            {item.quantity}
                                                        </span>
                                                        <button
                                                            className="w-6 h-6 text-white/60 hover:text-white rounded transition-colors"
                                                            onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                                                        >
                                                            <Plus className="w-3 h-3" />
                                                        </button>
                                                    </div>

                                                    <span className="text-white font-semibold">
                                                        ${((item.price || 0) * item.quantity).toFixed(2)}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Checkout Section */}
                    {items.length > 0 && (
                        <div className="border-t border-white/10 p-6 space-y-4">
                            {/* Price Breakdown */}
                            <div className="space-y-2">
                                <div className="flex justify-between text-white/60 text-sm">
                                    <span>Subtotal</span>
                                    <span>${subtotal.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-white/60 text-sm">
                                    <span>Tax</span>
                                    <span>${tax.toFixed(2)}</span>
                                </div>
                                <div className="h-px bg-white/10" />
                                <div className="flex justify-between text-white font-semibold">
                                    <span>Total</span>
                                    <span>${total.toFixed(2)}</span>
                                </div>
                            </div>

                            {/* Checkout Button */}
                            <button
                                className="w-full h-12 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-purple-500/20 flex items-center justify-center"
                                onClick={handleCheckout}
                            >
                                <CreditCard className="w-5 h-5 mr-2" />
                                Checkout
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

