'use client'

import { Grid, Package, User } from 'lucide-react'

interface TabBarProps {
    activeTab: 'products' | 'bundles' | 'profile'
    onTabChange: (tab: 'products' | 'bundles' | 'profile') => void
    onToggleContent: () => void
}

export function TabBar({ activeTab, onTabChange, onToggleContent }: TabBarProps) {
    const tabs = [
        { id: 'products' as const, label: 'Products', icon: Grid },
        { id: 'bundles' as const, label: 'Bundles', icon: Package },
        { id: 'profile' as const, label: 'Profile', icon: User }
    ]

    const handleTabChange = (tabId: 'products' | 'bundles' | 'profile') => {
        // Only toggle content if clicking on a different tab
        // This keeps the panel open when switching between tabs
        const isDifferentTab = activeTab !== tabId
        onTabChange(tabId)

        // Only open the panel, never close it
        if (isDifferentTab) {
            onToggleContent()
        }
    }

    return (
        <div className="bg-black/90 backdrop-blur-xl border-t border-white/10 px-4 py-2">
            <div className="flex justify-center gap-1 max-w-md mx-auto">
                {tabs.map((tab) => {
                    const Icon = tab.icon
                    return (
                        <button
                            key={tab.id}
                            className={`relative flex-1 h-12 rounded-xl transition-all duration-300 flex flex-col items-center justify-center gap-1 ${activeTab === tab.id
                                ? 'text-white bg-gradient-to-r from-purple-600/20 to-cyan-600/20 border border-purple-500/30'
                                : 'text-white/60 hover:text-white hover:bg-white/5'
                                }`}
                            onClick={() => handleTabChange(tab.id)}
                        >
                            <Icon className="w-4 h-4" />
                            <span className="text-xs font-medium">{tab.label}</span>
                        </button>
                    )
                })}
            </div>
        </div>
    )
}

