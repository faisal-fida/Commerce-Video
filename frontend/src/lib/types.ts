export interface Product {
  object_type: string;
  image_url: string;
  title: string;
  stock: string;
  direct_url: string;
}

export interface DetectionResults {
  [timestamp: string]: Product[];
}

export interface VideoInfo {
  id: string;
  filename: string;
  status: "processing" | "completed" | "failed";
  file_path?: string;
  results_dir?: string;
  error_message?: string;
}
