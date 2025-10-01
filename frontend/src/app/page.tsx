import VideoUpload from "@/components/VideoUpload";
import VideoList from "@/components/VideoList";

export default function HomePage() {
  return (
    <div className="space-y-12">
      <header className="text-center">
        <h1 className="text-4xl font-bold text-white">
          Visual Ecommerce
        </h1>
        <p className="text-lg text-gray-400 mt-2">
          Discover products from your videos.
        </p>
      </header>
      <VideoUpload />
      <div className="border-t border-gray-700 w-full max-w-md mx-auto"></div>
      <VideoList />
    </div>
  );
}
