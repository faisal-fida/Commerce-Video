"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { VideoInfo } from "@/lib/types"; // I'll create this type

export default function VideoList() {
    const [videos, setVideos] = useState<VideoInfo[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchVideos() {
            try {
                const response = await fetch("/api/videos");
                if (!response.ok) {
                    throw new Error("Failed to fetch videos");
                }
                const data = await response.json();
                setVideos(data);
            } catch (err: any) {
                setError(err.message);
            }
        }

        fetchVideos();
        // Simple polling to refresh the list every 5 seconds
        const interval = setInterval(fetchVideos, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full max-w-md mx-auto">
            <h2 className="text-2xl font-bold mb-4 text-center text-white">
                Processed Videos
            </h2>
            {error && <p className="text-red-500 text-center">{error}</p>}
            {videos.length === 0 && !error && (
                <p className="text-gray-500 text-center">
                    No videos found. Upload one to get started.
                </p>
            )}
            <ul className="space-y-3">
                {videos.map((video) => (
                    <li
                        key={video.id}
                        className="bg-gray-800 p-4 rounded-lg flex justify-between items-center"
                    >
                        <div>
                            <span className="text-gray-300">{video.filename}</span>
                            <span
                                className={`ml-3 text-xs font-medium px-2.5 py-0.5 rounded-full ${video.status === "completed"
                                        ? "bg-green-900 text-green-300"
                                        : video.status === "processing"
                                            ? "bg-yellow-900 text-yellow-300"
                                            : "bg-red-900 text-red-300"
                                    }`}
                            >
                                {video.status}
                            </span>
                        </div>
                        {video.status === "completed" ? (
                            <Link
                                href={`/videos/${video.id}`}
                                className="text-white bg-green-600 hover:bg-green-700 focus:ring-4 focus:ring-green-800 font-medium rounded-lg text-sm px-5 py-2.5"
                            >
                                View Results
                            </Link>
                        ) : (
                            <span className="text-gray-500 text-sm px-5 py-2.5">
                                Processing...
                            </span>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
}
