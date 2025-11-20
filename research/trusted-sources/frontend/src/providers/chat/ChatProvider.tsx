"use client";

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { Message } from "../../components/chat/ChatMessage";
import { LLMProvider } from "./llm/types";
import { loadMessages, saveMessages, getUserId, clearMessages as clearStoredMessages } from "../../utils/messageStorage";

export interface ChatContextType {
  messages: Message[];
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  addMessage: (role: "user" | "assistant", content: string) => void;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
  llmProvider: LLMProvider;
  /** Custom className to be used by components */
  className?: string;
}

export function ChatProvider({ children, llmProvider, className }: ChatProviderProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load messages from localStorage on mount (client-side only)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedMessages = loadMessages();
      if (savedMessages && savedMessages.length > 0) {
        // Convert ChatMessage[] to Message[] (timestamp: number -> string)
        const convertedMessages: Message[] = savedMessages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp).toISOString()
        }));
        setMessages(convertedMessages);
      }
    }
  }, []);

  const addMessage = useCallback((role: "user" | "assistant", content: string) => {
    const message: Message = {
      id: `${Date.now()}-${Math.random()}`,
      role,
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, message]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    clearStoredMessages();
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message immediately
    addMessage("user", content.trim());
    setIsLoading(true);

    try {
      const updatedMessages: Message[] = [
        ...messages,
        {
          id: `${Date.now()}-user`,
          role: "user",
          content: content.trim(),
          timestamp: new Date().toISOString(),
        },
      ];

      // Check if provider supports streaming
      if (llmProvider.streamChat) {
        let assistantContent = "";
        const assistantMessageId = `${Date.now()}-assistant`;

        // Start with empty assistant message
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessageId,
            role: "assistant",
            content: "",
            timestamp: new Date().toISOString(),
          },
        ]);

        // Stream the response
        for await (const chunk of llmProvider.streamChat(updatedMessages)) {
          assistantContent += chunk;

          // Update the assistant message with accumulated content
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: assistantContent }
                : msg
            )
          );
        }
      } else if (llmProvider.sendMessage) {
        // Fallback to non-streaming
        const response = await llmProvider.sendMessage(updatedMessages);
        addMessage("assistant", response);
      } else {
        throw new Error("LLM provider must implement either streamChat or sendMessage");
      }
    } catch (error) {
      console.error("Error sending message:", error);
      addMessage("assistant", "Sorry, I encountered an error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading, llmProvider, addMessage]);

  const value: ChatContextType = {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    addMessage,
  };

  return (
    <ChatContext.Provider value={value}>
      <div className={`chat-container ${className || ""}`.trim()}>
        {children}
      </div>
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}