// Backend VideoInfo model
export interface VideoInfo {
  id: string;
  filename: string;
  status: "processing" | "completed" | "failed";
  file_path?: string;
  results_dir?: string;
  error_message?: string;
  video_url?: string;
}

// Extended Video interface for frontend display
export interface Video extends VideoInfo {
  title?: string;
  description?: string;
  videoUrl?: string; // Alias for video_url for backwards compatibility
  thumbnail?: string;
  localThumbnail?: string;
  duration?: string;
  views?: string;
  rating?: number;
  category?: string;
  tags?: string[];
  releaseDate?: string;
  source?: string;
  fileSize?: string;
  thumbnailGenerated?: boolean;
  exists?: boolean;
  lastVerified?: string;
}

// Backend ProductResult model
export interface ProductResult {
  object_type: string;
  category?: string; // "clothing" or "jewelry"
  image_url: string;
  title: string;
  stock: string;
  direct_url: string;
  confidence?: number;
}

// Extended Product interface for frontend
export interface Product extends ProductResult {
  id?: string;
  name?: string;
  price?: number;
  image?: string;
  category?: string;
  confidence?: number;
  timestamp?: number;
  original_detection_time?: number;
  detected_category_from_video?: string;
  ai_generated_search_query?: string;
  found_online_images?: OnlineImage[];
  local_images?: LocalImage[];
  description?: string;
  tags?: string[];
  timeStart?: number;
  timeEnd?: number;
}

export interface OnlineImage {
  image_url: string;
  website_url: string;
}

export interface LocalImage {
  local_path: string;
  website_url: string;
  online_url: string;
}

export interface CartItem {
  id: string;
  name: string;
  price: number;
  image: string;
  quantity: number;
  type?: "bundle" | "product";
  bundle_products?: Product[];
}

export interface Bundle {
  id: string;
  name: string;
  description: string;
  total_price: number;
  discount_price: number;
  category: string;
  image_url: string;
  product_ids: string[];
  products?: Product[];
  similarity_score: number;
  time_range?: string;
}

export interface VideosData {
  videos: Video[];
  metadata: {
    total_videos: number;
    last_updated: string;
    video_directory: string;
    thumbnail_directory: string;
    supported_formats: string[];
    auto_refresh: boolean;
    thumbnails_generated: boolean;
  };
}

// API Response Types
export interface VideoUploadResponse {
  video_id: string;
  filename: string;
  status: string;
}

export interface APIError {
  detail: string;
  status?: number;
}

export interface HealthCheckResponse {
  status: string;
}
