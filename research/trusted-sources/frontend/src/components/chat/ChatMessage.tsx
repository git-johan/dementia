"use client";

import { MarkdownRenderer } from "../../utils/markdown";

export interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

interface ChatMessageProps {
  /** The message to display */
  message: Message;
  /** Whether to show spacing as if this is a new conversation section */
  showHeader?: boolean;
  /** Custom className for the message container */
  className?: string;
  /** Custom className for user messages */
  userMessageClassName?: string;
  /** Custom className for assistant messages */
  assistantMessageClassName?: string;
}

export function ChatMessage({
  message,
  showHeader = true,
  className = "",
  userMessageClassName = "",
  assistantMessageClassName = "",
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`animate-fade-in ${
        showHeader
          ? "mb-4 mt-4 first:mt-0"
          : "mb-2"
      } ${isUser ? "flex justify-end" : ""} ${className}`.trim()}
    >
      {isUser ? (
        <div
          className={`px-3 sm:px-4 py-3 rounded-2xl whitespace-pre-wrap break-words text-sm leading-[1.1] max-w-[85%] sm:max-w-[650px] bg-chat-primary text-white ${userMessageClassName}`.trim()}
        >
          {message.content}
        </div>
      ) : (
        <div className="flex justify-start">
          <div
            className={`px-3 sm:px-4 py-3 rounded-2xl break-words text-sm max-w-[85%] sm:max-w-[650px] bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 ${assistantMessageClassName}`.trim()}
          >
            <MarkdownRenderer
              content={message.content}
              className="text-inherit"
            />
          </div>
        </div>
      )}
    </div>
  );
}