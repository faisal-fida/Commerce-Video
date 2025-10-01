import { Video, VideoInfo } from "./types";
import { api } from "./api";

export class VideoDiscoveryService {
  private videoExtensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"];
  private videosCache: Video[] | null = null;
  private lastFetchTime: number | null = null;
  private cacheExpiry = 30000; // 30 seconds cache

  async discoverVideos(): Promise<Video[]> {
    try {
      console.log("🔍 Loading videos from API...");

      // Check cache first
      const now = Date.now();
      if (
        this.videosCache &&
        this.lastFetchTime &&
        now - this.lastFetchTime < this.cacheExpiry
      ) {
        console.log("📦 Using cached video data");
        return this.videosCache;
      }

      // Fetch videos from API
      const videosData: VideoInfo[] = await api.getVideos();
      console.log("📄 Loaded videos from API:", videosData);

      // Enhance videos with display properties
      const enhancedVideos = await this.enhanceVideos(videosData);

      // Update cache
      this.videosCache = enhancedVideos;
      this.lastFetchTime = now;

      console.log(`🎬 Total videos: ${enhancedVideos.length}`);
      return enhancedVideos;
    } catch (error) {
      console.error("Error loading videos from API:", error);
      // Fallback to empty array on error
      return [];
    }
  }

  private async enhanceVideos(videos: VideoInfo[]): Promise<Video[]> {
    const enhancedVideos: Video[] = [];

    for (const videoInfo of videos) {
      try {
        // Convert VideoInfo to Video with display properties
        const videoUrl = api.getVideoUrl(videoInfo);
        const thumbnailUrl = api.getThumbnailUrl(videoInfo.id);

        const enhancedVideo: Video = {
          ...videoInfo,
          // Backend properties
          video_url: videoUrl,

          // Frontend display properties
          title: videoInfo.filename.replace(/\.[^/.]+$/, ""), // Remove extension
          description: `Video ${videoInfo.status}`,
          videoUrl: videoUrl,
          thumbnail: thumbnailUrl,
          localThumbnail: thumbnailUrl,
          duration: "N/A",
          views: "0",
          rating: 0,
          category: "Uploaded Videos",
          tags: [videoInfo.status],
          releaseDate: new Date().toISOString().split("T")[0],
          source: "api",
          fileSize: "N/A",
          thumbnailGenerated: videoInfo.status === "completed",
          exists: true,
          lastVerified: new Date().toISOString(),
        };

        enhancedVideos.push(enhancedVideo);
        console.log(
          `✅ Enhanced video: ${videoInfo.filename} (${videoInfo.status})`
        );
      } catch (err) {
        console.log(`⚠️ Error enhancing video ${videoInfo.filename}:`, err);
      }
    }

    return enhancedVideos;
  }

  refreshVideoList(): void {
    console.log("🔄 Refreshing video list...");
    this.videosCache = null;
    this.lastFetchTime = null;
  }

  /**
   * Filter videos by status
   */
  async getVideosByStatus(
    status?: "processing" | "completed" | "failed"
  ): Promise<Video[]> {
    const allVideos = await this.discoverVideos();

    if (!status) {
      return allVideos;
    }

    return allVideos.filter((video) => video.status === status);
  }

  /**
   * Get a single video by ID
   */
  async getVideoById(videoId: string): Promise<Video | null> {
    try {
      const videoInfo = await api.getVideoById(videoId);
      const enhancedVideos = await this.enhanceVideos([videoInfo]);
      return enhancedVideos[0] || null;
    } catch (error) {
      console.error(`Error fetching video ${videoId}:`, error);
      return null;
    }
  }
}

export const videoDiscovery = new VideoDiscoveryService();
