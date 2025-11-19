"use client";

import React from "react";
import { useChat } from "../../hooks/useChat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { ChatHeader } from "./ChatHeader";
import { FloatingActionButton } from "./FloatingActionButton";
import { useScrollToBottom } from "../../hooks/useScrollToBottom";
import { ExampleQuestions } from "./ExampleQuestions";

interface ChatContainerProps {
  /** Custom className for the main container */
  className?: string;
  /** Custom className for the messages container */
  messagesClassName?: string;
  /** Custom className for the input container */
  inputClassName?: string;
  /** Show header with title and clear button */
  showHeader?: boolean;
  /** Custom header title */
  title?: string;
  /** Custom placeholder message when chat is empty */
  placeholder?: string;
}

export function ChatContainer({
  className = "",
  messagesClassName = "",
  inputClassName = "",
  showHeader = true,
  title = "AI Chat",
  placeholder = "Start a conversation...",
}: ChatContainerProps) {
  const { messages, isLoading, clearMessages, sendMessage } = useChat();

  // Debug logging
  console.log("ChatContainer render:", {
    isLoading,
    messagesCount: messages.length,
    lastMessage: messages[messages.length - 1],
  });

  // Smart scroll management
  const { endRef, containerRef, scrollToBottom, showScrollButton } =
    useScrollToBottom(messages);

  return (
    <div
      className={`flex flex-col h-full chat-container bg-white dark:bg-gray-900 relative ${className}`.trim()}
    >
      {/* Header */}
      {showHeader && (
        <ChatHeader
          title={title}
          hasMessages={messages.length > 0}
          onClear={clearMessages}
        />
      )}

      {/* Messages Container */}
      <div
        ref={containerRef}
        className={`flex-1 overflow-y-auto chat-messages chat-scrollable bg-white dark:bg-gray-900 ${messagesClassName}`.trim()}
      >
        <div className="px-2 py-2 max-w-[900px] mx-auto">
          {/* Show example questions when empty, otherwise show messages */}
          {messages.length === 0 ? (
            <ExampleQuestions onSelect={sendMessage} />
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={message.id || index}
                message={message}
                showHeader={
                  index === 0 || messages[index - 1]?.role !== message.role
                }
              />
            ))
          )}

          <div ref={endRef} />
        </div>
      </div>

      {/* Input - Fixed at bottom */}
      <div className={`px-2 py-2 relative ${inputClassName}`.trim()}>
        <div className="max-w-[900px] mx-auto relative">
          {/* Floating Action Button - combines typing indicator and scroll-to-bottom */}
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-4 z-10">
            <FloatingActionButton
              isLoading={isLoading}
              showScrollButton={showScrollButton}
              onScrollToBottom={() => scrollToBottom(false)}
            />
          </div>
          <ChatInput />
        </div>
      </div>
    </div>
  );
}
