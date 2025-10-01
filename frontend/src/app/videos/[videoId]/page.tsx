"use client";

import React, { useState, useEffect } from "react";
import VideoPlayer from "@/components/VideoPlayer";
import ProductDisplay from "@/components/ProductDisplay";
import Spinner from "@/components/Spinner";
import { Product, VideoInfo } from "@/lib/types";
import Link from "next/link";

export default function VideoResultsPage({
    params,
}: {
    params: { videoId: string };
}) {
    const { videoId } = React.use(params);
    const [products, setProducts] = useState<Product[]>([]);
    const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isFetchingProducts, setIsFetchingProducts] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);

    useEffect(() => {
        async function fetchVideoInfo() {
            try {
                const response = await fetch(`/api/videos/${videoId}`);
                if (!response.ok) {
                    throw new Error("Failed to fetch video information");
                }
                const data: VideoInfo = await response.json();
                setVideoInfo(data);
            } catch (err: any) {
                setError(err.message);
            }
        }

        fetchVideoInfo();
    }, [videoId]);

    const handlePause = async (time: number) => {
        setError(null);
        setIsFetchingProducts(true);
        setHasSearched(true);
        try {
            // Round to nearest 5-second interval as per requirements
            const roundedTime = Math.round(time / 5) * 5;

            const response = await fetch(
                `/api/results/${videoId}?time=${roundedTime}`
            );
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch results");
            }
            const data: Product[] = await response.json();
            setProducts(data);
        } catch (err: any) {
            setError(err.message);
            setProducts([]); // Clear products on error
        } finally {
            setIsFetchingProducts(false);
        }
    };

    return (
        <div>
            <Link href="/" className="text-blue-400 hover:underline mb-4 block">
                &larr; Back to Videos
            </Link>
            <h1 className="text-3xl font-bold mb-6 text-white">
                Video Results for{" "}
                <span className="text-gray-400 text-2xl break-all">
                    {videoId}
                </span>
            </h1>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                    <VideoPlayer onPause={handlePause} src={videoInfo?.video_url || null} />
                </div>
                <div className="lg:col-span-1 bg-gray-800 p-4 rounded-lg">
                    {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                    {isFetchingProducts ? (
                        <Spinner />
                    ) : (
                        <ProductDisplay products={products} hasSearched={hasSearched} />
                    )}
                </div>
            </div>
        </div>
    );
}
