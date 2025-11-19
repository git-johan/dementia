/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["ai-chat-ui"],
  // Disable all development overlays and indicators
  devIndicators: {
    buildActivity: false,
    appIsrStatus: false,
    buildActivityPosition: 'top-right',
  },
  // Disable development overlay entirely
  experimental: {
    turbo: false, // Disable turbopack overlay if using it
  },
};

module.exports = nextConfig;