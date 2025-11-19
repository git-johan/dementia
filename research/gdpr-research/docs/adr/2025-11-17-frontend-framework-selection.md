# ADR: Frontend Framework Selection

**Date**: 2025-11-17
**Status**: Accepted
**Deciders**: Johan Josok

## Context

We need to create a React-based frontend for our Norwegian dementia care AI assistant that integrates with the ai-chat-ui package for conversational interface. The frontend must support both speech-to-text (NB-Whisper) and chat (NB-Llama) functionality. We need to choose between different React frameworks that can provide optimal development experience, performance, and future scalability.

## Decision Drivers

- **ai-chat-ui Integration**: Seamless integration with existing ai-chat-ui package
- **Norwegian Language Support**: Proper internationalization and character encoding
- **Performance**: Fast loading and responsive interface for elderly users
- **Development Experience**: TypeScript support, hot reloading, good debugging
- **Production Deployment**: Easy deployment to Hetzner servers
- **Routing Capability**: Support for multiple pages/views as the app grows
- **SSR/SSG Support**: Better SEO and initial load performance
- **Ecosystem Maturity**: Strong community, documentation, and tooling

## Options Considered

### Option 1: Create React App (REJECTED)

**Approach**: Traditional CRA with React Scripts

**Pros**:
- Simple setup and configuration
- Well-established and stable
- Good TypeScript support
- Large community and documentation

**Cons**:
- **Deprecated by React team**: No longer actively maintained
- **Slow build times**: Webpack-based bundling is slower than modern alternatives
- **No SSR support**: Client-side only rendering
- **Limited routing**: Need to add React Router manually
- **Bundle size**: Larger bundles compared to modern alternatives
- **Development server**: Slower hot reloading compared to Vite/Next.js

### Option 2: Vite + React (INITIALLY CONSIDERED)

**Approach**: Modern build tool with React template

**Pros**:
- **Fast development server**: Near-instant hot module replacement (HMR)
- **Quick build times**: ES modules and esbuild-based bundling
- **Modern by default**: ES6+, TypeScript, CSS modules out of the box
- **Lightweight**: Smaller bundle sizes
- **Plugin ecosystem**: Rich plugin system for customization

**Cons**:
- **No SSR out of the box**: Requires additional setup for server-side rendering
- **Manual routing setup**: Need to configure React Router manually
- **Limited opinionation**: More configuration decisions required
- **Production complexity**: Need to set up deployment pipeline manually
- **No built-in API routes**: Can't handle backend integration within the same project

### Option 3: Next.js (CHOSEN)

**Approach**: Full-stack React framework with built-in optimizations

**Pros**:
- **Server-Side Rendering (SSR)**: Better performance for initial page loads
- **Static Site Generation (SSG)**: Pre-built pages for optimal loading
- **Built-in routing**: File-system based routing with dynamic routes
- **API routes**: Can handle backend utilities within the same project
- **Image optimization**: Automatic image optimization and lazy loading
- **Automatic code splitting**: Optimized bundle loading
- **TypeScript first-class support**: Excellent TypeScript integration
- **Vercel deployment**: Seamless deployment options (though we'll use Hetzner)
- **Mature ecosystem**: Extensive community and documentation
- **i18n support**: Built-in internationalization for Norwegian language
- **Performance optimizations**: Font optimization, script loading, etc.

**Cons**:
- **More complex**: Steeper learning curve than simple React setup
- **Heavier framework**: Larger framework overhead compared to Vite
- **Opinionated**: Less flexibility in build configuration
- **Potential overkill**: For simple single-page apps, might be excessive

## Decision

**We choose Option 3: Next.js with React**

### Primary Rationale

**Performance for Target Users**:
- **SSR capabilities**: Faster initial page loads for elderly users who may have slower devices
- **Automatic optimizations**: Font loading, image optimization, code splitting benefit users with limited bandwidth
- **Better SEO**: While not critical now, future discoverability and accessibility improvements

**Development Efficiency**:
- **Built-in routing**: File-system routing will be beneficial as we add more pages (settings, help, history)
- **TypeScript integration**: First-class TypeScript support for better code quality
- **API routes**: Can handle frontend utilities or proxy requests to FastAPI backend
- **Hot reloading**: Excellent development experience with fast refresh

**ai-chat-ui Integration**:
- **SSR compatibility**: ai-chat-ui works well with Next.js SSR
- **Client-side interactivity**: Chat interface requires client-side state management which Next.js handles well
- **Custom components**: Easy to extend ai-chat-ui with custom Norwegian language components

**Norwegian Language Support**:
- **Built-in i18n**: Next.js internationalization for Norwegian text, date formatting, etc.
- **Character encoding**: Proper UTF-8 handling for Norwegian characters (æ, ø, å)
- **Font optimization**: Automatic font loading optimization for Norwegian-specific fonts if needed

**Future Scalability**:
- **Multiple pages**: Easy to add settings, help, conversation history pages
- **Authentication**: Built-in support for authentication providers when needed
- **Progressive Web App**: Can easily convert to PWA for mobile installation
- **Production deployment**: Mature deployment patterns for Docker/server deployment

### Architecture Decision

```typescript
// Next.js project structure
/frontend
  /pages
    index.tsx          // Main chat interface
    /api
      proxy.ts         // Optional proxy to FastAPI backend
  /components
    ChatInterface.tsx  // ai-chat-ui integration
    Layout.tsx         // Norwegian language layout
  /styles
    globals.css        // Norwegian-specific styling
  next.config.js       // Norwegian locale configuration
  package.json
```

**Key Configuration**:
```javascript
// next.config.js
module.exports = {
  i18n: {
    locales: ['no'],
    defaultLocale: 'no'
  },
  async rewrites() {
    return [
      {
        source: '/api/chat/:path*',
        destination: 'http://localhost:8000/api/chat/:path*'
      }
    ]
  }
}
```

## Implementation Strategy

### Phase 1: Basic Setup
```bash
# Create Next.js app with TypeScript
npx create-next-app@latest frontend --typescript --tailwind --app-router
cd frontend
npm install ai-chat-ui
```

### Phase 2: ai-chat-ui Integration
```typescript
// pages/index.tsx
import { ChatProvider, ChatContainer, CustomProvider } from 'ai-chat-ui'

const nbLlamaProvider = new CustomProvider({
  endpoint: '/api/chat',  // Proxied through Next.js
  headers: { 'Content-Type': 'application/json' },
  temperature: 0.7,
  maxTokens: 2000
})

export default function Home() {
  return (
    <ChatProvider llmProvider={nbLlamaProvider}>
      <ChatContainer
        title="AI-assistent for demensomsorg"
        placeholder="Skriv din melding her..."
      />
    </ChatProvider>
  )
}
```

### Phase 3: Norwegian Localization
```typescript
// Norwegian language configuration
const norwegianConfig = {
  title: "AI-assistent for demensomsorg",
  placeholder: "Skriv din melding her...",
  sendButton: "Send",
  errorMessage: "Beklager, det oppstod en feil. Vennligst prøv igjen.",
  loadingMessage: "Tenker..."
}
```

## Consequences

### Positive

- **Optimal Performance**: SSR and automatic optimizations benefit elderly users
- **Future-Proof Architecture**: Can easily scale to multi-page application
- **Norwegian Language Support**: Built-in i18n capabilities for proper localization
- **Development Experience**: Excellent TypeScript, hot reloading, and debugging
- **Production Ready**: Mature deployment patterns and optimization features
- **ai-chat-ui Compatibility**: Proven integration patterns with SSR

### Negative

- **Framework Overhead**: Slightly heavier than simple Vite setup
- **Learning Curve**: More concepts to learn compared to basic React
- **Build Complexity**: More complex build process than Vite

### Neutral

- **API Route Usage**: May or may not use built-in API routes (depends on backend integration needs)
- **Deployment Options**: Multiple deployment strategies available (Vercel, Docker, static export)

## Future Considerations

**Progressive Enhancement**:
- **PWA Support**: Convert to installable mobile app
- **Offline Capability**: Cache conversations for offline access
- **Push Notifications**: Reminders for medication, appointments

**Multi-Page Evolution**:
- **Settings Page**: Model selection, language preferences
- **History Page**: Conversation history and search
- **Help Page**: User guide and tutorials for elderly users

**Performance Optimization**:
- **Bundle Analysis**: Monitor and optimize bundle size
- **Image Optimization**: Leverage Next.js image optimization for any medical diagrams
- **Caching Strategy**: Implement proper caching for better performance

**Accessibility**:
- **Screen Reader Support**: Excellent accessibility for visually impaired users
- **Keyboard Navigation**: Full keyboard support for mobility-impaired users
- **High Contrast**: Support for high contrast mode

## References

- Development Principles: `/docs/development-principles.md`
- ai-chat-ui Documentation: Package analysis conducted 2025-11-17
- Next.js Documentation: https://nextjs.org/docs
- Norwegian Web Accessibility Guidelines: WCAG 2.1 compliance