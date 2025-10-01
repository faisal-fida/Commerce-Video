/**
 * API Client for CommerceVideo Backend
 * Handles all communication with the FastAPI backend
 */

import {
  VideoInfo,
  VideoUploadResponse,
  ProductResult,
  Bundle,
  HealthCheckResponse,
  APIError,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const MAX_RETRIES = 1;
const RETRY_DELAY = 500; // ms
const REQUEST_TIMEOUT = 5000; // 5 seconds

/**
 * Custom error class for API errors
 */
class APIException extends Error {
  status?: number;
  detail: string;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "APIException";
    this.status = status;
    this.detail = message;
  }
}

/**
 * Delay utility for retry logic
 */
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Make an HTTP request with retry logic and timeout
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = MAX_RETRIES
): Promise<Response> {
  try {
    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    // If response is ok or client error (4xx), return immediately
    if (response.ok || (response.status >= 400 && response.status < 500)) {
      return response;
    }

    // For server errors (5xx), retry
    if (retries > 0 && response.status >= 500) {
      console.warn(
        `Request failed with ${response.status}, retrying... (${retries} left)`
      );
      await delay(RETRY_DELAY);
      return fetchWithRetry(url, options, retries - 1);
    }

    return response;
  } catch (error) {
    // Network errors or timeout - retry
    if (retries > 0 && error instanceof Error) {
      const isTimeout = error.name === "AbortError";
      console.warn(
        `${
          isTimeout ? "Timeout" : "Network error"
        }, retrying... (${retries} left)`
      );
      await delay(RETRY_DELAY);
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
}

/**
 * Handle API response and errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // If response is not JSON, use status text
    }

    throw new APIException(errorMessage, response.status);
  }

  // Handle empty responses
  if (response.status === 204) {
    return {} as T;
  }

  try {
    return await response.json();
  } catch (error) {
    throw new APIException("Failed to parse response JSON");
  }
}

/**
 * API Client Class
 */
class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Upload a video file
   */
  async uploadVideo(file: File): Promise<VideoUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetchWithRetry(`${this.baseURL}/api/upload`, {
      method: "POST",
      body: formData,
    });

    return handleResponse<VideoUploadResponse>(response);
  }

  /**
   * Get all videos
   */
  async getVideos(): Promise<VideoInfo[]> {
    const response = await fetchWithRetry(`${this.baseURL}/api/videos`);
    return handleResponse<VideoInfo[]>(response);
  }

  /**
   * Get a single video by ID
   */
  async getVideoById(videoId: string): Promise<VideoInfo> {
    const response = await fetchWithRetry(
      `${this.baseURL}/api/videos/${videoId}`
    );
    return handleResponse<VideoInfo>(response);
  }

  /**
   * Get detection results for a video at a specific timestamp
   */
  async getResults(
    videoId: string,
    timestamp: number
  ): Promise<ProductResult[]> {
    const url = `${this.baseURL}/api/results/${videoId}?time=${timestamp}`;
    const response = await fetchWithRetry(url);
    return handleResponse<ProductResult[]>(response);
  }

  /**
   * Get product bundles for a video at a specific timestamp
   * Note: This endpoint needs to be implemented in the backend
   */
  async getBundles(videoId: string, timestamp: number): Promise<Bundle[]> {
    try {
      const url = `${this.baseURL}/api/bundles/${videoId}?time=${timestamp}`;
      const response = await fetchWithRetry(url, {}, 0); // No retries for not-yet-implemented endpoint
      return handleResponse<Bundle[]>(response);
    } catch (error) {
      // If endpoint doesn't exist yet, return empty array
      console.warn(
        "Bundles endpoint not yet implemented, returning empty array"
      );
      return [];
    }
  }

  /**
   * Search videos by query
   * Note: This endpoint needs to be implemented in the backend
   */
  async searchVideos(
    query: string,
    status?: string,
    limit?: number,
    offset?: number
  ): Promise<VideoInfo[]> {
    try {
      const params = new URLSearchParams();
      if (query) params.append("q", query);
      if (status) params.append("status", status);
      if (limit) params.append("limit", limit.toString());
      if (offset) params.append("offset", offset.toString());

      const url = `${this.baseURL}/api/videos/search?${params.toString()}`;
      const response = await fetchWithRetry(url, {}, 0);
      return handleResponse<VideoInfo[]>(response);
    } catch (error) {
      // Fallback to getVideos if search endpoint doesn't exist
      console.warn(
        "Search endpoint not yet implemented, falling back to getVideos"
      );
      return this.getVideos();
    }
  }

  /**
   * Reprocess a failed video
   * Note: This endpoint needs to be implemented in the backend
   */
  async reprocessVideo(videoId: string): Promise<void> {
    try {
      const response = await fetchWithRetry(
        `${this.baseURL}/api/videos/${videoId}/reprocess`,
        { method: "POST" },
        0
      );
      return handleResponse<void>(response);
    } catch (error) {
      console.error("Reprocess endpoint not yet implemented");
      throw new APIException("Reprocess feature not available yet");
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await fetchWithRetry(`${this.baseURL}/health`);
    return handleResponse<HealthCheckResponse>(response);
  }

  /**
   * Get full URL for a video
   */
  getVideoUrl(videoInfo: VideoInfo): string {
    if (videoInfo.video_url) {
      // If video_url is already set, use it
      if (videoInfo.video_url.startsWith("http")) {
        return videoInfo.video_url;
      }
      return `${this.baseURL}${videoInfo.video_url}`;
    }
    // Construct URL from video ID and filename
    return `${this.baseURL}/static_videos/${videoInfo.id}/${videoInfo.filename}`;
  }

  /**
   * Get full URL for a product image
   */
  getProductImageUrl(imagePath: string): string {
    // Handle different image path formats
    if (imagePath.startsWith("http")) {
      return imagePath;
    }

    // Extract filename from paths like "data/image_db/ (19).jpg"
    const filename = imagePath.replace(/^data\/image_db\//, "");
    return `${this.baseURL}/static_images/${filename}`;
  }

  /**
   * Get full URL for a video thumbnail
   */
  getThumbnailUrl(videoId: string): string {
    return `${this.baseURL}/static_videos/${videoId}/thumbnail.jpg`;
  }
}

// Export singleton instance
export const api = new APIClient();

// Export class for testing
export { APIClient, APIException };
