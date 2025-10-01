"use client";

import { useState } from "react";

export default function VideoUpload() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadMessage, setUploadMessage] = useState("");

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            setSelectedFile(event.target.files[0]);
            setUploadMessage("");
        }
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setUploadMessage("");
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setUploadMessage("Please select a file first.");
            return;
        }

        setIsUploading(true);
        setUploadMessage("Uploading...");

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }

            const result = await response.json();
            setUploadMessage(`Upload successful! Video ID: ${result.video_id}. It is now being processed.`);
            // TODO: Add logic to refresh the video list
        } catch (error: any) {
            setUploadMessage(`Error: ${error.message}`);
        } finally {
            setIsUploading(false);
            setSelectedFile(null);
        }
    };

    return (
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg w-full max-w-md mx-auto my-8">
            <h2 className="text-2xl font-bold mb-4 text-center text-white">
                Upload a Video
            </h2>

            {selectedFile ? (
                <div className="text-center">
                    <p className="text-gray-300 mb-4">
                        Selected file: {selectedFile.name}
                    </p>
                    <button
                        onClick={handleRemoveFile}
                        className="text-white bg-red-600 hover:bg-red-700 font-medium rounded-lg text-sm px-5 py-2.5"
                    >
                        Remove
                    </button>
                </div>
            ) : (
                <div className="flex items-center justify-center w-full">
                    <label
                        htmlFor="dropzone-file"
                        className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-700 hover:bg-gray-600"
                    >
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg
                                className="w-8 h-8 mb-4 text-gray-400"
                                aria-hidden="true"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 20 16"
                            >
                                <path
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 4.25a5.592 5.592 0 0 0-4.025 2.227 5.253 5.253 0 0 0-1.254 3.7A5.226 5.226 0 0 0 5 13h3m0 0v-5m0 5l-2-2m2 2 2-2"
                                />
                            </svg>
                            <p className="mb-2 text-sm text-gray-400">
                                <span className="font-semibold">Click to upload</span> or drag
                                and drop
                            </p>
                            <p className="text-xs text-gray-400">
                                MP4, AVI, MOV, or WMV (MAX. 500MB)
                            </p>
                        </div>
                        <input
                            id="dropzone-file"
                            type="file"
                            className="hidden"
                            onChange={handleFileChange}
                            accept="video/mp4,video/avi,video/quicktime,video/x-ms-wmv"
                        />
                    </label>
                </div>
            )}

            <button
                type="button"
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                className="w-full mt-6 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center disabled:bg-gray-500 disabled:cursor-not-allowed"
            >
                {isUploading ? "Uploading..." : "Upload"}
            </button>

            {uploadMessage && (
                <p className="mt-4 text-center text-sm text-gray-400">
                    {uploadMessage}
                </p>
            )}
        </div>
    );
}
