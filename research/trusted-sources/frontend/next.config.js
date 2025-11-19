/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove deprecated appDir setting - it's now stable in Next.js 14
  transpilePackages: ['ai-chat-ui'],

  // Add headers for CSP to allow font loading
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "font-src 'self' https://fonts.gstatic.com data:",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "connect-src 'self' http://localhost:8000 ws://localhost:3001 https://api.openai.com",
              "img-src 'self' data: blob:",
            ].join('; '),
          },
        ],
      },
    ];
  },
}

module.exports = nextConfig