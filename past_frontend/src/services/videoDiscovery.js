// Video discovery service to load videos from videos.json file

export class VideoDiscoveryService {
  constructor() {
    this.videoExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'];
    this.videosCache = null;
    this.lastFetchTime = null;
    this.cacheExpiry = 30000; // 30 seconds cache
  }

  // Discover videos from the videos.json file
  async discoverVideos() {
    try {
      console.log('🔍 Loading videos from videos.json...');

      // Check cache first
      const now = Date.now();
      if (this.videosCache && this.lastFetchTime && (now - this.lastFetchTime < this.cacheExpiry)) {
        console.log('📦 Using cached video data');
        return this.videosCache;
      }

      // Fetch videos.json with cache busting to ensure fresh data
      const response = await fetch(`/videos.json?t=${now}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch videos.json: ${response.status}`);
      }

      const videosData = await response.json();
      console.log('📄 Loaded videos.json:', videosData);

      // Verify video files exist and update info
      const verifiedVideos = await this.verifyAndEnhanceVideos(videosData.videos || []);

      // Update cache
      this.videosCache = verifiedVideos;
      this.lastFetchTime = now;

      console.log(`🎬 Total verified videos: ${verifiedVideos.length}`);
      return verifiedVideos;
    } catch (error) {
      console.error('Error loading videos from videos.json:', error);

      // Fallback to empty array with error message
      return [];
    }
  }

  // Verify videos exist and enhance with real-time data
  async verifyAndEnhanceVideos(videos) {
    const verifiedVideos = [];

    for (const video of videos) {
      try {
        // Check if video file actually exists
        const exists = await this.checkVideoExists(video.videoUrl);

        if (exists) {
          // Check for local thumbnail first, then fallback to remote thumbnail
          const thumbnailUrl = await this.getBestThumbnail(video);

          // Enhance video with real-time thumbnail
          const enhancedVideo = {
            ...video,
            exists: true,
            thumbnail: thumbnailUrl,
            lastVerified: new Date().toISOString()
          };

          verifiedVideos.push(enhancedVideo);
          console.log(`✅ Verified video: ${video.filename} with thumbnail: ${thumbnailUrl}`);
        } else {
          console.log(`❌ Video file not found: ${video.filename}`);
        }
      } catch (error) {
        console.log(`⚠️ Error verifying video ${video.filename}:`, error.message);
      }
    }

    return verifiedVideos;
  }

  // Force refresh video list (clears cache)
  refreshVideoList() {
    console.log('🔄 Refreshing video list...');
    this.videosCache = null;
    this.lastFetchTime = null;
  }

  // Get the best available thumbnail (local first, then remote, then placeholder)
  async getBestThumbnail(video) {
    // Try local thumbnail first
    if (video.localThumbnail) {
      try {
        const response = await fetch(video.localThumbnail, { method: 'HEAD' });
        if (response.ok) {
          console.log(`📸 Using local thumbnail: ${video.localThumbnail}`);
          return video.localThumbnail;
        }
      } catch (error) {
        console.log(`⚠️ Local thumbnail not accessible: ${video.localThumbnail}`);
      }
    }

    // Try the thumbnail from videos.json
    if (video.thumbnail && video.thumbnail.startsWith('http')) {
      console.log(`🌐 Using remote thumbnail: ${video.thumbnail}`);
      return video.thumbnail;
    }

    // Generate thumbnail path dynamically
    const dynamicThumbnail = await this.generateThumbnailPath(video.filename);
    console.log(`🎯 Using dynamic thumbnail: ${dynamicThumbnail}`);
    return dynamicThumbnail;
  }

  // Generate thumbnail path with improved logic
  async generateThumbnailPath(filename) {
    const thumbnailName = filename.replace(/\.[^/.]+$/, ".jpg");
    const possibleThumbnailPaths = [
      `/videos/thumbnails/${thumbnailName}`,
      `/thumbnails/${thumbnailName}`,
      `/downloaded_videos/thumbnails/${thumbnailName}`
    ];

    // Try to find existing thumbnail
    for (const thumbnailPath of possibleThumbnailPaths) {
      try {
        const response = await fetch(thumbnailPath, { method: 'HEAD' });
        if (response.ok) {
          return thumbnailPath;
        }
      } catch (error) {
        // Continue to next path
      }
    }

    // Return placeholder if no thumbnail found
    return this.getPlaceholderThumbnail();
  }

  // Get placeholder thumbnail
  getPlaceholderThumbnail() {
    const placeholders = [
      'https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80',
      'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=225&fit=crop&q=80',
      'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop&q=80',
    ];

    return placeholders[Math.floor(Math.random() * placeholders.length)];
  }

  // Check if a video file exists
  async checkVideoExists(videoPath) {
    try {
      const response = await fetch(videoPath, { method: 'HEAD' });
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

export const videoDiscovery = new VideoDiscoveryService();