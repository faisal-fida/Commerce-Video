"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { api, APIException } from "@/lib/api";
import { VideoUploadResponse } from "@/lib/types";

interface VideoUploadProps {
    onUploadComplete?: (videoId: string) => void;
    onClose?: () => void;
}

const ALLOWED_TYPES = ["video/mp4", "video/avi", "video/mov", "video/x-matroska", "video/webm", "video/x-m4v"];
const MAX_SIZE_MB = parseInt(process.env.NEXT_PUBLIC_MAX_UPLOAD_SIZE || "100");
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export function VideoUpload({ onUploadComplete, onClose }: VideoUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<VideoUploadResponse | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const validateFile = (file: File): string | null => {
        // Check file type
        if (!ALLOWED_TYPES.includes(file.type)) {
            return "Invalid file type. Please upload MP4, AVI, MOV, MKV, WEBM, or M4V files.";
        }

        // Check file size
        if (file.size > MAX_SIZE_BYTES) {
            return `File too large. Maximum size is ${MAX_SIZE_MB}MB.`;
        }

        return null;
    };

    const handleFileSelect = (selectedFile: File) => {
        const validationError = validateFile(selectedFile);
        if (validationError) {
            setError(validationError);
            return;
        }

        setFile(selectedFile);
        setError(null);
        setSuccess(null);
    };

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            handleFileSelect(droppedFile);
        }
    }, []);

    const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            handleFileSelect(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);
        setUploadProgress(0);

        try {
            // Simulate progress (FastAPI doesn't provide upload progress by default)
            const progressInterval = setInterval(() => {
                setUploadProgress((prev) => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return 90;
                    }
                    return prev + 10;
                });
            }, 200);

            const response = await api.uploadVideo(file);

            clearInterval(progressInterval);
            setUploadProgress(100);
            setSuccess(response);

            // Notify parent component
            if (onUploadComplete) {
                onUploadComplete(response.video_id);
            }

            // Auto-close after 2 seconds if onClose is provided
            if (onClose) {
                setTimeout(() => {
                    onClose();
                }, 2000);
            }
        } catch (err) {
            const errorMessage =
                err instanceof APIException
                    ? err.detail
                    : "Upload failed. Please try again.";
            setError(errorMessage);
            setUploadProgress(0);
        } finally {
            setUploading(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setError(null);
        setSuccess(null);
        setUploadProgress(0);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className="bg-gray-900 rounded-lg p-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Upload Video</h2>
                {onClose && (
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                )}
            </div>

            {/* Drop Zone */}
            {!file && !success && (
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging
                            ? "border-cyan-500 bg-cyan-500/10"
                            : "border-gray-700 hover:border-gray-600"
                        }`}
                >
                    <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-white text-lg mb-2">
                        Drag & drop your video here
                    </p>
                    <p className="text-gray-400 text-sm mb-4">or</p>
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-2 rounded-lg transition-colors"
                    >
                        Browse Files
                    </button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept={ALLOWED_TYPES.join(",")}
                        onChange={handleFileInputChange}
                        className="hidden"
                    />
                    <p className="text-gray-500 text-xs mt-4">
                        Supported formats: MP4, AVI, MOV, MKV, WEBM, M4V (Max {MAX_SIZE_MB}
                        MB)
                    </p>
                </div>
            )}

            {/* File Selected */}
            {file && !success && (
                <div className="space-y-4">
                    <div className="bg-gray-800 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <p className="text-white font-medium mb-1">{file.name}</p>
                                <p className="text-gray-400 text-sm">
                                    {formatFileSize(file.size)}
                                </p>
                            </div>
                            {!uploading && (
                                <button
                                    onClick={handleReset}
                                    className="text-gray-400 hover:text-white transition-colors ml-4"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            )}
                        </div>

                        {/* Progress Bar */}
                        {uploading && (
                            <div className="mt-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-gray-400">Uploading...</span>
                                    <span className="text-sm text-cyan-400">
                                        {uploadProgress}%
                                    </span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div
                                        className="bg-cyan-500 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Upload Button */}
                    {!uploading && (
                        <button
                            onClick={handleUpload}
                            disabled={uploading}
                            className="w-full bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white py-3 rounded-lg transition-colors font-medium"
                        >
                            {uploading ? (
                                <span className="flex items-center justify-center">
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    Uploading...
                                </span>
                            ) : (
                                "Upload Video"
                            )}
                        </button>
                    )}
                </div>
            )}

            {/* Success Message */}
            {success && (
                <div className="bg-green-900/20 border border-green-500 rounded-lg p-6 text-center">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">
                        Upload Successful!
                    </h3>
                    <p className="text-gray-300 mb-4">
                        Your video is being processed. This may take a few minutes.
                    </p>
                    <p className="text-sm text-gray-400">
                        Video ID: <span className="text-cyan-400">{success.video_id}</span>
                    </p>
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="mt-4 bg-gray-700 hover:bg-gray-600 text-white px-6 py-2 rounded-lg transition-colors"
                        >
                            Close
                        </button>
                    )}
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-red-400 font-medium">Upload Failed</p>
                        <p className="text-red-300 text-sm mt-1">{error}</p>
                    </div>
                    <button
                        onClick={() => setError(null)}
                        className="text-red-400 hover:text-red-300 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>
            )}
        </div>
    );
}

