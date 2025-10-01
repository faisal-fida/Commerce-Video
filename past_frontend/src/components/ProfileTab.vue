<template>
  <div class="h-full bg-black/90 backdrop-blur-xl border-t border-white/10">
    <div class="p-4 space-y-6 h-full overflow-y-auto custom-scrollbar pb-20">
      <!-- Profile Header -->
      <div class="text-center space-y-4">
        <div
          v-motion
          :initial="{ scale: 0.8, opacity: 0 }"
          :enter="{ scale: 1, opacity: 1 }"
          class="relative inline-block"
        >
          <div class="w-20 h-20 rounded-full ring-2 ring-purple-500/30 bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center text-white text-xl font-semibold">
            <img
              v-if="user?.avatar"
              :src="user.avatar"
              :alt="user.full_name || 'User'"
              class="w-full h-full rounded-full object-cover"
            />
            <span v-else>{{ (user?.full_name?.charAt(0) || 'U').toUpperCase() }}</span>
          </div>
          <div class="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-black" />
        </div>

        <div>
          <h2 class="text-xl font-semibold text-white">
            {{ user?.full_name || 'User' }}
          </h2>
          <p class="text-white/60 text-sm">{{ user?.email }}</p>
          <span class="inline-block mt-2 bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-1 rounded text-xs">
            Premium Member
          </span>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-3">
        <div
          v-for="(stat, index) in stats"
          :key="stat.label"
          v-motion
          :initial="{ y: 20, opacity: 0 }"
          :enter="{ y: 0, opacity: 1 }"
          :transition="{ delay: index * 0.1 }"
          class="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-3 text-center"
        >
          <p class="text-white font-semibold text-lg">{{ stat.value }}</p>
          <p class="text-white/60 text-xs">{{ stat.label }}</p>
        </div>
      </div>

      <!-- Connected Accounts -->
      <div class="space-y-2">
        <h3 class="text-sm font-semibold text-white/60 px-2">Connected Accounts</h3>
        <div
          v-for="(item, index) in ecomConnections"
          :key="item.name"
          v-motion
          :initial="{ x: -20, opacity: 0 }"
          :enter="{ x: 0, opacity: 1 }"
          :transition="{ delay: (index * 0.1) + 0.3 }"
          class="flex items-center w-full p-2 bg-white/5 rounded-xl border border-transparent hover:border-white/10 hover:bg-white/10 transition-colors"
        >
          <div class="w-8 h-8 bg-white/5 rounded-full flex items-center justify-center mr-3">
            <component :is="item.icon" class="w-4 h-4 text-cyan-400" />
          </div>
          <span class="flex-1 text-left text-sm font-medium text-white">{{ item.name }}</span>
          <button
            :class="[
              'h-7 text-xs px-3 rounded transition-colors',
              item.connected
                ? 'bg-transparent border border-green-500/50 text-green-400 hover:bg-green-500/10 hover:text-green-300'
                : 'bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white'
            ]"
          >
            {{ item.connected ? 'Manage' : 'Connect' }}
          </button>
        </div>
      </div>

      <!-- Menu Items -->
      <div class="space-y-2">
        <h3 class="text-sm font-semibold text-white/60 px-2 pt-2">Menu</h3>
        <div
          v-for="(item, index) in menuItems"
          :key="item.label"
          v-motion
          :initial="{ x: -20, opacity: 0 }"
          :enter="{ x: 0, opacity: 1 }"
          :transition="{ delay: (index * 0.1) + 0.6 }"
        >
          <button class="w-full flex items-center h-12 text-white hover:bg-white/10 rounded-xl px-3 transition-colors">
            <div class="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center mr-3">
              <component :is="item.icon" class="w-4 h-4 text-white/60" />
            </div>
            <span class="flex-1 text-left">{{ item.label }}</span>
            <span
              v-if="item.count !== undefined"
              class="bg-white/10 text-white/80 px-2 py-1 rounded text-xs"
            >
              {{ item.count }}
            </span>
          </button>
        </div>
      </div>

      <!-- Logout -->
      <div class="pt-4 border-t border-white/10">
        <button class="w-full flex items-center h-12 text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-xl px-3 transition-colors">
          <div class="w-10 h-10 bg-red-500/10 rounded-full flex items-center justify-center mr-3">
            <LogOut class="w-4 h-4" />
          </div>
          Sign Out
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { User, Heart, ShoppingBag, Settings, Bell, CreditCard, LogOut, Store } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({
      full_name: 'Guest User',
      email: 'guest@example.com',
      avatar: null
    })
  }
})

// Computed properties
const stats = computed(() => [
  { label: 'Items Bought', value: '12' },
  { label: 'Money Saved', value: '$245' },
  { label: 'Wishlist', value: '8' }
])

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
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}
</style>