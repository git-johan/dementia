"use client";

import { ChatContainer } from "../components/chat/ChatContainer";
import { ChatProvider } from "../providers/chat/ChatProvider";
import { OpenAIProvider } from "../providers/OpenAIProvider";

export default function HomePage() {
  return (
    <ChatProvider llmProvider={new OpenAIProvider() as any}>
      <ChatContainer
        className="h-screen"
        showHeader={true}
        title="Demens-assistenten"
      />
    </ChatProvider>
  );
}