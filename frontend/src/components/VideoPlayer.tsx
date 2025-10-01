"use client";

import { useRef, useState, useEffect } from "react";

interface VideoPlayerProps {
    onPause: (time: number) => void;
    src: string | null;
}

export default function VideoPlayer({ onPause, src }: VideoPlayerProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const handlePlayPause = () => {
        if (videoRef.current) {
            if (videoRef.current.paused) {
                videoRef.current.play();
                setIsPlaying(true);
            } else {
                videoRef.current.pause();
                setIsPlaying(false);
            }
        }
    };

    useEffect(() => {
        const videoElement = videoRef.current;
        if (!videoElement) return;

        const handlePauseEvent = () => {
            setIsPlaying(false);
            onPause(videoElement.currentTime);
        };

        const handlePlayEvent = () => {
            setIsPlaying(true);
        };

        videoElement.addEventListener("pause", handlePauseEvent);
        videoElement.addEventListener("play", handlePlayEvent);


        return () => {
            videoElement.removeEventListener("pause", handlePauseEvent);
            videoElement.removeEventListener("play", handlePlayEvent);
        };
    }, [onPause]);

    if (!src) {
        return (
            <div className="w-full h-full bg-gray-800 flex items-center justify-center rounded-lg">
                <p className="text-gray-500">Loading video...</p>
            </div>
        );
    }

    return (
        <div className="relative">
            <video
                ref={videoRef}
                key={src} // Add key to force re-render when src changes
                className="w-full rounded-lg"
                controls
                src={src}
            />
        </div>
    );
}
