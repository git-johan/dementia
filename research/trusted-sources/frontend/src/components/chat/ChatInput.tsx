"use client";

import { useState, FormEvent, KeyboardEvent, useRef, useEffect } from "react";
import { useChat } from "../../hooks/useChat";
import {
  ChatInputToolbar,
  defaultToolbarConfig,
  type ToolbarConfig,
} from "./ChatInputToolbar";

interface ChatInputProps {
  /** Custom className for the input container */
  className?: string;
  /** Custom placeholder text */
  placeholder?: string;
  /** Custom className for the textarea */
  textareaClassName?: string;
  /** Custom className for the toolbar */
  toolbarClassName?: string;
  /** Disable the input */
  disabled?: boolean;
  /** Toolbar configuration - controls which features are enabled */
  toolbarConfig?: Partial<ToolbarConfig>;
}

export function ChatInput({
  className = "",
  placeholder = "Type a message...",
  textareaClassName = "",
  toolbarClassName = "",
  disabled = false,
  toolbarConfig = {},
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const { sendMessage, isLoading } = useChat();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "44px";
      const scrollHeight = textarea.scrollHeight;
      textarea.style.height = Math.min(scrollHeight, 200) + "px";
    }
  }, [input]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || disabled) return;

    const message = input.trim();
    setInput("");
    await sendMessage(message);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Placeholder handlers for toolbar features
  const handleFileUpload = () => {
    console.log("📄 UPLOAD FILE - implement your file upload logic here");
  };

  const handlePhotoUpload = () => {
    console.log("📸 UPLOAD PHOTO - implement your photo upload logic here");
  };

  const handleVoiceConversation = () => {
    console.log(
      "💬 VOICE CONVERSATION - have a voice conversation with the AI",
    );
  };

  const handleMicrophone = () => {
    console.log("🎙️ DICTATE - dictate instead of write (voice-to-text)");
  };

  const handleRecord = () => {
    console.log("🔴 RECORD CONVERSATION - record a conversation");
  };

  // Merge provided config with defaults
  const config: ToolbarConfig = {
    ...defaultToolbarConfig,
    ...toolbarConfig,
    // Provide default handlers if not specified
    fileUpload: {
      enabled:
        toolbarConfig.fileUpload?.enabled ??
        defaultToolbarConfig.fileUpload.enabled,
      handler: toolbarConfig.fileUpload?.handler ?? handleFileUpload,
      photoHandler: toolbarConfig.fileUpload?.photoHandler ?? handlePhotoUpload,
    },
    microphone: {
      enabled:
        toolbarConfig.microphone?.enabled ??
        defaultToolbarConfig.microphone.enabled,
      handler: toolbarConfig.microphone?.handler ?? handleMicrophone,
    },
    voiceConversation: {
      enabled:
        toolbarConfig.voiceConversation?.enabled ??
        defaultToolbarConfig.voiceConversation.enabled,
      handler:
        toolbarConfig.voiceConversation?.handler ?? handleVoiceConversation,
    },
    record: {
      enabled:
        toolbarConfig.record?.enabled ?? defaultToolbarConfig.record.enabled,
      handler: toolbarConfig.record?.handler ?? handleRecord,
    },
    // Always override send and stop with actual handlers
    send: {
      enabled: toolbarConfig.send?.enabled ?? true,
      handler: () => handleSubmit(new Event("submit") as any),
    },
    stop: {
      enabled: toolbarConfig.stop?.enabled ?? true, // Enable stop by default
      handler:
        toolbarConfig.stop?.handler ??
        (() => {
          console.log("⏹️ STOP GENERATION - stop AI from generating");
        }),
    },
  };

  return (
    <form onSubmit={handleSubmit} className={`w-full ${className}`.trim()}>
      {/* Visual container that encompasses both input and toolbar */}
      <div
        className={`rounded-[14px] bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 transition-opacity ${
          input.trim() ? "opacity-100" : "opacity-75"
        }`}
      >
        {/* Textarea */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`w-full min-h-[44px] max-h-[200px] px-3 sm:px-4 pt-3 pb-1 resize-none overflow-y-auto bg-transparent border-none text-base text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none disabled:opacity-50 chat-input leading-[1.1] ${textareaClassName}`.trim()}
            disabled={isLoading || disabled}
            autoFocus
            rows={1}
          />
        </div>

        {/* Toolbar */}
        <div className="px-2 pb-2">
          <ChatInputToolbar
            hasInput={input.trim().length > 0}
            isLoading={isLoading}
            config={config}
            className={toolbarClassName}
          />
        </div>
      </div>
    </form>
  );
}
