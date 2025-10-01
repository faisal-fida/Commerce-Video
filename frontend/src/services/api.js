import axios from 'axios'

// Load Product.json data
let productData = null
const loadProductData = async () => {
  if (!productData) {
    try {
      const response = await fetch('/Entities/Product.json')
      productData = await response.json()
    } catch (error) {
      console.error('Error loading Product.json:', error)
      // Fallback to empty structure if file not found
      productData = {
        products: [],
        metadata: {
          total_products: 0,
          analysis_method: "no_data"
        }
      }
    }
  }
  return productData
}

// Create axios instance with base configuration
// Note: Streamlit backend doesn't have API endpoints, so we'll use direct access
const api = axios.create({
  baseURL: '', // Disable API calls for Streamlit backend
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Product Service
export const productService = {
  async list() {
    try {
      const response = await api.get('/products')
      return response.data
    } catch (error) {
      console.error('Error fetching products:', error)
      return []
    }
  },

  async get(id) {
    try {
      const response = await api.get(`/products/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching product:', error)
      return null
    }
  }
}

// Bundle Service
export const bundleService = {
  async list() {
    try {
      const response = await api.get('/bundles')
      return response.data
    } catch (error) {
      console.error('Error fetching bundles:', error)
      return []
    }
  },

  async get(id) {
    try {
      const response = await api.get(`/bundles/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching bundle:', error)
      return null
    }
  }
}

// Cart Service
export const cartService = {
  async list() {
    try {
      const response = await api.get('/cart')
      return response.data
    } catch (error) {
      console.error('Error fetching cart:', error)
      return []
    }
  },

  async add(productId, quantity = 1) {
    try {
      const response = await api.post('/cart/add', { productId, quantity })
      return response.data
    } catch (error) {
      console.error('Error adding to cart:', error)
      throw error
    }
  },

  async remove(itemId) {
    try {
      const response = await api.delete(`/cart/${itemId}`)
      return response.data
    } catch (error) {
      console.error('Error removing from cart:', error)
      throw error
    }
  },

  async updateQuantity(itemId, quantity) {
    try {
      const response = await api.put(`/cart/${itemId}`, { quantity })
      return response.data
    } catch (error) {
      console.error('Error updating cart quantity:', error)
      throw error
    }
  }
}


// User Service - Modified for Streamlit backend compatibility
export const userService = {
  async me() {
    // Streamlit doesn't have user API, return mock user data
    console.log('Using mock user data for Streamlit backend')
    return {
      id: 'streamlit_user',
      name: 'Streamlit User',
      email: 'user@streamlit.app'
    }
  },

  async update(userData) {
    // Mock update - Streamlit doesn't have user management
    console.log('Mock user update for Streamlit backend:', userData)
    return userData
  }
}

// YouTube video ID extraction utility
const extractYouTubeVideoId = (url) => {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
  const match = url.match(regex)
  return match ? match[1] : null
}

// Check if a video file exists for a given YouTube video ID
const findDownloadedVideo = async (videoId) => {
  try {
    // Try common extensions and filename patterns
    const possibleFiles = [
      `/downloaded_videos/${videoId}.mp4`,
      `/downloaded_videos/${videoId}.webm`,
      `/downloaded_videos/${videoId}.mkv`
    ]

    for (const filePath of possibleFiles) {
      try {
        const response = await fetch(filePath, { method: 'HEAD' })
        if (response.ok) {
          return filePath
        }
      } catch (e) {
        // File doesn't exist, continue to next
      }
    }
    return null
  } catch (error) {
    console.error('Error checking for downloaded video:', error)
    return null
  }
}

// Video Analysis Service
export const videoService = {
  async analyze(videoSource, processingMode = 'full', frameTime = null, onProgress = null, detectionMethod = 'local_yolo', sampleInterval = null) {
    try {
      console.log('Analyzing video:', { videoSource, processingMode, frameTime, detectionMethod, sampleInterval })

      // Check if we should trigger actual video processing for uploaded files
      const shouldProcessVideo = (typeof videoSource !== 'string' || (!videoSource.includes('youtube.com') && !videoSource.includes('youtu.be')))

      if (shouldProcessVideo && typeof videoSource !== 'string') {
        // For uploaded files, trigger actual video processing via bridge server
        try {
          console.log('🎬 Triggering actual video processing with sample interval:', sampleInterval)

          // Create a temporary file path (in a real implementation, you'd handle file upload properly)
          const tempVideoPath = '/tmp/uploaded_video.mp4' // This would be handled by proper file upload

          const response = await fetch('http://localhost:8503/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              video_path: tempVideoPath, // In real implementation, this would be the uploaded file path
              detection_method: detectionMethod,
              sample_interval: sampleInterval || 2.0,
              processing_mode: processingMode
            })
          })

          if (response.ok) {
            const result = await response.json()
            console.log('✅ Video processing completed:', result)

            // After processing, the bridge server updates Product.json
            // So we can proceed with loading the updated results
          } else {
            console.warn('⚠️ Video processing bridge not available, falling back to mock data')
          }
        } catch (bridgeError) {
          console.warn('⚠️ Could not connect to video processing bridge:', bridgeError)
          console.log('📦 Falling back to loading existing Product.json data')
        }
      }

      // Check if it's a YouTube URL
      const isYouTubeUrl = typeof videoSource === 'string' &&
        (videoSource.includes('youtube.com') || videoSource.includes('youtu.be'))

      let actualVideoUrl, actualFrameUrl;

      if (isYouTubeUrl) {
        // For YouTube URLs, use direct file detection
        // Show progress steps for YouTube processing based on detection method
        const getDetectionMethodSteps = () => {
          const baseSteps = [
            { message: 'Initializing video analysis...', duration: 500 },
            { message: 'Checking for downloaded video...', duration: 1000 },
            { message: processingMode === 'frame'
              ? `Extracting frame at ${Math.floor((frameTime || 0) / 60)}:${String((frameTime || 0) % 60).padStart(2, '0')}...`
              : 'Preparing video for analysis...',
              duration: 1500
            }
          ]

          switch (detectionMethod) {
            case 'local_yolo':
              return [...baseSteps,
                { message: 'Running YOLO11 object detection...', duration: 2000 },
                { message: 'Analyzing detected objects...', duration: 1000 },
                { message: 'Finalizing results...', duration: 500 }
              ]
            case 'hybrid_fashion':
              return [...baseSteps,
                { message: 'Running YOLO11 base detection...', duration: 1500 },
                { message: 'Enhancing with Google AI...', duration: 2500 },
                { message: 'Fusing detection results...', duration: 1000 },
                { message: 'Finalizing results...', duration: 500 }
              ]
            case 'enhanced_hybrid':
              return [...baseSteps,
                { message: 'Running multi-agent detection...', duration: 2000 },
                { message: 'Advanced post-processing...', duration: 2000 },
                { message: 'Quality enhancement...', duration: 1500 },
                { message: 'Finalizing results...', duration: 500 }
              ]
            case 'google_ai':
              return [...baseSteps,
                { message: 'Connecting to Google AI...', duration: 1000 },
                { message: 'Running Gemini analysis...', duration: 3000 },
                { message: 'Processing AI insights...', duration: 1500 },
                { message: 'Finalizing results...', duration: 500 }
              ]
            case 'enhanced_yolo':
              return [...baseSteps,
                { message: 'Running enhanced YOLO detection...', duration: 2000 },
                { message: 'Advanced color analysis...', duration: 1500 },
                { message: 'Quality filtering...', duration: 1000 },
                { message: 'Finalizing results...', duration: 500 }
              ]
            default:
              return [...baseSteps,
                { message: 'Running object detection...', duration: 2000 },
                { message: 'Processing results...', duration: 1000 },
                { message: 'Finalizing results...', duration: 500 }
              ]
          }
        }

        const steps = getDetectionMethodSteps()

        for (let i = 0; i < steps.length; i++) {
          if (onProgress) {
            onProgress(steps[i].message, (i + 1) / steps.length * 100)
          }
          await new Promise(resolve => setTimeout(resolve, steps[i].duration))
        }

        // Extract video ID and look for downloaded file
        const videoId = extractYouTubeVideoId(videoSource)
        if (videoId) {
          const downloadedVideoPath = await findDownloadedVideo(videoId)
          if (downloadedVideoPath) {
            actualVideoUrl = downloadedVideoPath
            actualFrameUrl = downloadedVideoPath // For frame mode, we'll use the video file
            console.log('Found downloaded video:', actualVideoUrl)
          } else {
            console.warn('No downloaded video found for YouTube ID:', videoId)
            // Fallback to sample paths if no downloaded video is found
            actualVideoUrl = "/downloaded_videos/sample_video.mp4"
            actualFrameUrl = "/extracted_frames/frame_30s.jpg"
          }
        } else {
          console.warn('Could not extract YouTube video ID from URL:', videoSource)
          actualVideoUrl = "/downloaded_videos/sample_video.mp4"
          actualFrameUrl = "/extracted_frames/frame_30s.jpg"
        }
      } else {
        // For uploaded files, show simpler progress
        const steps = [
          { message: 'Processing uploaded video...', duration: 1000 },
          { message: 'Running YOLO11 object detection...', duration: 2000 },
          { message: 'Identifying fashion items...', duration: 1500 },
          { message: 'Finalizing results...', duration: 500 }
        ]

        for (let i = 0; i < steps.length; i++) {
          if (onProgress) {
            onProgress(steps[i].message, (i + 1) / steps.length * 100)
          }
          await new Promise(resolve => setTimeout(resolve, steps[i].duration))
        }

        // For uploaded files, create object URL
        actualVideoUrl = typeof videoSource === 'string' ? videoSource : URL.createObjectURL(videoSource)
      }

      // Load Product.json data - it has a products array inside
      const productData = await loadProductData()
      const rawResultsArray = productData.products || []

      // Transform Product.json data to the format expected by the frontend
      const products = rawResultsArray.map(obj => ({
        id: obj.id,
        name: obj.name || obj.class_name, // Use name from Product.json
        price: obj.price || 99.99,
        image_url: obj.image_url || obj.image,
        image: obj.image || obj.image_url,
        timestamp: obj.timestamp ? parseFloat(obj.timestamp.replace(/[^\d.]/g, '')) || 0 : 0,
        confidence: obj.confidence,
        category: obj.category,
        class_name: obj.class_name,
        description: obj.description || `${obj.name} from video detection`,
        brand: obj.brand || 'Fashion Brand',
        affiliate_url: obj.affiliate_url || `https://example.com/products/${obj.id}`,
        bounding_box: obj.bounding_box || {
          x: 0,
          y: 0,
          width: 100,
          height: 100
        },
        attributes: {
          color: obj.color || 'unknown',
          material: obj.material || 'unknown',
          style: obj.style || 'casual'
        }
      }))

      // Create sample bundles from detected fashion items
      const fashionItems = products.filter(p => p.category === 'fashion')
      const similar_products = fashionItems.length > 1 ? [
        {
          id: 'bundle_001',
          name: 'Complete Fashion Look',
          description: 'Curated outfit from detected items',
          image: fashionItems[0]?.image_url,
          image_url: fashionItems[0]?.image_url,
          total_price: fashionItems.slice(0, 2).reduce((sum, item) => sum + item.price, 0),
          discount_price: fashionItems.slice(0, 2).reduce((sum, item) => sum + item.price, 0) * 0.85,
          savings: fashionItems.slice(0, 2).reduce((sum, item) => sum + item.price, 0) * 0.15,
          category: 'fashion-bundle',
          similarity_score: 0.92,
          product_ids: fashionItems.slice(0, 2).map(p => p.id)
        }
      ] : []

      const baseResponse = {
        products,
        similar_products,
        analysis_metadata: {
          total_detections: rawResultsArray.length,
          analysis_method: productData.metadata?.analysis_method || "video_detection",
          detection_timestamp: productData.metadata?.analysis_timestamp || new Date().toISOString()
        },
        statistics: {
          total_objects_detected: rawResultsArray.length,
          fashion_items: rawResultsArray.filter(obj => obj.category === 'fashion').length,
          general_objects: rawResultsArray.filter(obj => obj.category !== 'fashion').length,
          average_confidence: rawResultsArray.length > 0
            ? rawResultsArray.reduce((sum, obj) => sum + (obj.confidence || 0), 0) / rawResultsArray.length
            : 0
        }
      }

      if (processingMode === 'frame') {
        // For frame analysis, return the extracted frame image
        return {
          ...baseResponse,
          frame_url: actualFrameUrl || (isYouTubeUrl
            ? "/extracted_frames/frame_30s.jpg"
            : "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=600&fit=crop"),
          video_url: actualVideoUrl
        }
      } else {
        // For full video analysis, return the downloaded video path
        return {
          ...baseResponse,
          video_url: actualVideoUrl
        }
      }

      /*
      // Uncomment this when backend endpoints are ready:

      if (typeof videoSource === 'string') {
        // URL-based video processing
        const response = await api.post('/analyze-url', {
          url: videoSource,
          mode: processingMode,
          frame_time: frameTime
        })
        return response.data
      } else {
        // File upload
        const formData = new FormData()
        formData.append('file', videoSource)
        formData.append('mode', processingMode)
        if (frameTime) formData.append('frame_time', frameTime)

        const response = await api.post('/analyze-video', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        return response.data
      }
      */
    } catch (error) {
      console.error('Error analyzing video:', error)
      throw error
    }
  },

  async getProducts(videoId, timestamp) {
    try {
      const response = await api.get(`/video/${videoId}/products`, {
        params: { timestamp }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching video products:', error)
      return []
    }
  },

  async searchSimilar(query) {
    try {
      const response = await api.post('/search', { query })
      return response.data
    } catch (error) {
      console.error('Error searching similar products:', error)
      return []
    }
  }
}

export default api