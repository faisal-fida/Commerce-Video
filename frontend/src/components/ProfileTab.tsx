'use client'

import { Heart, ShoppingBag, Settings, Bell, CreditCard, LogOut, Store } from 'lucide-react'

interface ProfileTabProps {
    user: {
        full_name?: string
        email?: string
        avatar?: string
    }
}

export function ProfileTab({ user }: ProfileTabProps) {
    const stats = [
        { label: 'Items Bought', value: '12' },
        { label: 'Money Saved', value: '$245' },
        { label: 'Wishlist', value: '8' }
    ]

    const menuItems = [
        { icon: Heart, label: 'Saved Items', count: 5 },
        { icon: ShoppingBag, label: 'Purchase History', count: 12 },
        { icon: Bell, label: 'Notifications', count: 3 },
        { icon: CreditCard, label: 'Payment Methods' },
        { icon: Settings, label: 'Settings' }
    ]

    const ecomConnections = [
        { name: 'Shopify', icon: Store, connected: true },
        { name: 'Amazon Store', icon: Store, connected: false },
        { name: 'Etsy Shop', icon: Store, connected: false }
    ]

    return (
        <div className="h-full bg-black/90 backdrop-blur-xl border-t border-white/10">
            <div className="p-4 space-y-6 h-full overflow-y-auto custom-scrollbar pb-20">
                {/* Profile Header */}
                <div className="text-center space-y-4">
                    <div className="relative inline-block">
                        <div className="w-20 h-20 rounded-full ring-2 ring-purple-500/30 bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center text-white text-xl font-semibold">
                            {user?.avatar ? (
                                <img
                                    src={user.avatar}
                                    alt={user.full_name || 'User'}
                                    className="w-full h-full rounded-full object-cover"
                                />
                            ) : (
                                <span>{(user?.full_name?.charAt(0) || 'U').toUpperCase()}</span>
                            )}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-black" />
                    </div>

                    <div>
                        <h2 className="text-xl font-semibold text-white">
                            {user?.full_name || 'Guest User'}
                        </h2>
                        <p className="text-white/60 text-sm">{user?.email || 'guest@example.com'}</p>
                        <span className="inline-block mt-2 bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-1 rounded text-xs">
                            Premium Member
                        </span>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3">
                    {stats.map((stat) => (
                        <div
                            key={stat.label}
                            className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-3 text-center"
                        >
                            <p className="text-white font-semibold text-lg">{stat.value}</p>
                            <p className="text-white/60 text-xs">{stat.label}</p>
                        </div>
                    ))}
                </div>

                {/* Connected Accounts */}
                <div className="space-y-2">
                    <h3 className="text-sm font-semibold text-white/60 px-2">Connected Accounts</h3>
                    {ecomConnections.map((item) => {
                        const Icon = item.icon
                        return (
                            <div
                                key={item.name}
                                className="flex items-center w-full p-2 bg-white/5 rounded-xl border border-transparent hover:border-white/10 hover:bg-white/10 transition-colors"
                            >
                                <div className="w-8 h-8 bg-white/5 rounded-full flex items-center justify-center mr-3">
                                    <Icon className="w-4 h-4 text-cyan-400" />
                                </div>
                                <span className="flex-1 text-left text-sm font-medium text-white">{item.name}</span>
                                <button
                                    className={`h-7 text-xs px-3 rounded transition-colors ${item.connected
                                            ? 'bg-transparent border border-green-500/50 text-green-400 hover:bg-green-500/10 hover:text-green-300'
                                            : 'bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white'
                                        }`}
                                >
                                    {item.connected ? 'Manage' : 'Connect'}
                                </button>
                            </div>
                        )
                    })}
                </div>

                {/* Menu Items */}
                <div className="space-y-2">
                    <h3 className="text-sm font-semibold text-white/60 px-2 pt-2">Menu</h3>
                    {menuItems.map((item) => {
                        const Icon = item.icon
                        return (
                            <button
                                key={item.label}
                                className="w-full flex items-center h-12 text-white hover:bg-white/10 rounded-xl px-3 transition-colors"
                            >
                                <div className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center mr-3">
                                    <Icon className="w-4 h-4 text-white/60" />
                                </div>
                                <span className="flex-1 text-left">{item.label}</span>
                                {item.count !== undefined && (
                                    <span className="bg-white/10 text-white/80 px-2 py-1 rounded text-xs">
                                        {item.count}
                                    </span>
                                )}
                            </button>
                        )
                    })}
                </div>

                {/* Logout */}
                <div className="pt-4 border-t border-white/10">
                    <button className="w-full flex items-center h-12 text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-xl px-3 transition-colors">
                        <div className="w-10 h-10 bg-red-500/10 rounded-full flex items-center justify-center mr-3">
                            <LogOut className="w-4 h-4" />
                        </div>
                        Sign Out
                    </button>
                </div>
            </div>
        </div>
    )
}

