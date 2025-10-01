<template>
  <Teleport to="body">
    <Transition name="cart-overlay">
      <div v-if="open" class="fixed inset-0 z-[100]">
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-black/20 backdrop-blur-sm"
          @click="$emit('update:open', false)"
        />

        <!-- Sliding Cart Panel -->
        <div
          class="fixed right-0 top-0 h-full w-96 bg-black/95 backdrop-blur-xl border-l border-white/10 z-[101] overflow-hidden transform transition-transform duration-300"
          :class="{ 'translate-x-0': open, 'translate-x-full': !open }"
        >
          <div class="flex flex-col h-full">
            <!-- Header -->
            <div class="p-6 border-b border-white/10">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full flex items-center justify-center">
                    <ShoppingBag class="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 class="text-xl font-semibold text-white">Your Cart</h2>
                    <p class="text-sm text-white/60">
                      {{ items.length }} item{{ items.length !== 1 ? 's' : '' }}
                    </p>
                  </div>
                </div>
                <button
                  class="text-white/60 hover:text-white hover:bg-white/10 p-2 rounded transition-colors"
                  @click="$emit('update:open', false)"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- Cart Items -->
            <div class="flex-1 overflow-y-auto custom-scrollbar">
              <div v-if="items.length === 0" class="flex flex-col items-center justify-center h-full text-center p-6">
                <div class="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                  <ShoppingBag class="w-8 h-8 text-white/40" />
                </div>
                <h3 class="text-white/60 font-medium mb-2">Your cart is empty</h3>
                <p class="text-white/40 text-sm">Add some products to get started!</p>
              </div>

              <div v-else class="p-4 space-y-4">
                <div
                  v-for="(item, index) in items"
                  :key="`${item.id}-${index}`"
                  class="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-4"
                >
                  <div class="flex gap-3">
                    <!-- Product Image -->
                    <img
                      :src="item.image || item.image_url || '/placeholder.jpg'"
                      :alt="item.name || 'Product'"
                      class="w-16 h-16 object-cover rounded-xl flex-shrink-0"
                    />

                    <!-- Product Details -->
                    <div class="flex-1 min-w-0">
                      <div class="flex justify-between items-start mb-2">
                        <h3 class="font-medium text-white text-sm leading-tight">
                          {{ item.name || 'Product' }}
                        </h3>
                        <button
                          class="w-6 h-6 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors"
                          @click="$emit('remove-item', item.id)"
                        >
                          <Trash2 class="w-3 h-3" />
                        </button>
                      </div>

                      <div class="mb-3">
                        <p class="text-white/60 text-xs">
                          ${{ (item.price || 0).toFixed(2) }} each
                        </p>
                        <!-- Show bundle info if it's a bundle -->
                        <div v-if="item.type === 'bundle' && item.bundle_products" class="mt-1">
                          <p class="text-blue-300 text-xs">
                            Bundle: {{ item.bundle_products.length }} items included
                          </p>
                        </div>
                      </div>

                      <!-- Quantity Controls -->
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2 bg-white/5 rounded-lg p-1">
                          <button
                            class="w-6 h-6 text-white/60 hover:text-white rounded transition-colors"
                            @click="$emit('update-quantity', item.id, Math.max(1, item.quantity - 1))"
                          >
                            <Minus class="w-3 h-3" />
                          </button>
                          <span class="text-white text-sm font-medium w-8 text-center">
                            {{ item.quantity }}
                          </span>
                          <button
                            class="w-6 h-6 text-white/60 hover:text-white rounded transition-colors"
                            @click="$emit('update-quantity', item.id, item.quantity + 1)"
                          >
                            <Plus class="w-3 h-3" />
                          </button>
                        </div>

                        <span class="text-white font-semibold">
                          ${{ ((item.price || 0) * item.quantity).toFixed(2) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Checkout Section -->
            <div v-if="items.length > 0" class="border-t border-white/10 p-6 space-y-4">
              <!-- Price Breakdown -->
              <div class="space-y-2">
                <div class="flex justify-between text-white/60 text-sm">
                  <span>Subtotal</span>
                  <span>${{ subtotal.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-white/60 text-sm">
                  <span>Tax</span>
                  <span>${{ tax.toFixed(2) }}</span>
                </div>
                <div class="h-px bg-white/10" />
                <div class="flex justify-between text-white font-semibold">
                  <span>Total</span>
                  <span>${{ total.toFixed(2) }}</span>
                </div>
              </div>

              <!-- Checkout Button -->
              <button
                class="w-full h-12 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-purple-500/20 flex items-center justify-center"
                @click="handleCheckout"
              >
                <CreditCard class="w-5 h-5 mr-2" />
                Checkout
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X, Minus, Plus, Trash2, ShoppingBag, CreditCard } from 'lucide-vue-next'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  items: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:open', 'remove-item', 'update-quantity', 'checkout'])

// Computed properties
const subtotal = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0)
})

const tax = computed(() => {
  return subtotal.value * 0.08 // 8% tax
})

const total = computed(() => {
  return subtotal.value + tax.value
})

// Methods
const handleCheckout = () => {
  emit('checkout')
}
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

.cart-overlay-enter-active,
.cart-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.cart-overlay-enter-from,
.cart-overlay-leave-to {
  opacity: 0;
}
</style>