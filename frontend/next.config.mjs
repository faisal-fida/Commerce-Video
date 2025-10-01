/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
      {
        source: "/static_videos/:path*",
        destination: "http://localhost:8000/static_videos/:path*",
      },
      {
        source: "/static_images/:path*",
        destination: "http://localhost:8000/static_images/:path*",
      },
    ];
  },
};

export default nextConfig;
