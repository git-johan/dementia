"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  PlusIcon,
  MicrophoneIcon,
  VoiceConversationIcon,
  SendIcon,
  StopIcon,
  RecordIcon,
} from "./icons/SFSymbols";

/**
 * Configuration for toolbar features
 * Set enabled: true and provide handler to activate features
 */
export interface ToolbarConfig {
  fileUpload: {
    enabled: boolean;
    handler?: () => void;
    photoHandler?: () => void;
  };
  microphone: {
    enabled: boolean;
    handler?: () => void;
  };
  voiceConversation: {
    enabled: boolean;
    handler?: () => void;
  };
  record: {
    enabled: boolean;
    handler?: () => void;
  };
  send: {
    enabled: boolean;
    handler?: () => void;
  };
  stop: {
    enabled: boolean;
    handler?: () => void;
  };
}

interface ChatInputToolbarProps {
  /** Whether the input field has text */
  hasInput: boolean;
  /** Whether AI is currently generating a response */
  isLoading: boolean;
  /** Toolbar configuration - controls which features are enabled */
  config: ToolbarConfig;
  /** Custom className for the toolbar */
  className?: string;
}

interface ToolbarButtonProps {
  onClick?: () => void;
  disabled?: boolean;
  children: React.ReactNode;
  title?: string;
  className?: string;
}

const ToolbarButton = React.forwardRef<HTMLButtonElement, ToolbarButtonProps>(
  ({ onClick, disabled = false, children, title, className = "" }, ref) => {
    return (
      <button
        ref={ref}
        type="button"
        onClick={onClick}
        disabled={disabled}
        title={title}
        className={`
        w-8 h-8 rounded-lg flex items-center justify-center
        transition-colors duration-200
        text-icon-light/80 dark:text-white/80
        hover:bg-icon-light/5 dark:hover:bg-white/5
        disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent
        ${className}
      `.trim()}
      >
        {children}
      </button>
    );
  },
);

ToolbarButton.displayName = "ToolbarButton";

export function ChatInputToolbar({
  hasInput,
  isLoading,
  config,
  className = "",
}: ChatInputToolbarProps) {
  const [showUploadDropdown, setShowUploadDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState<"top" | "bottom">(
    "top",
  );
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Smart positioning and close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowUploadDropdown(false);
      }
    };

    const calculatePosition = () => {
      if (buttonRef.current) {
        const buttonRect = buttonRef.current.getBoundingClientRect();
        const spaceAbove = buttonRect.top;
        const spaceBelow = window.innerHeight - buttonRect.bottom;

        // If there's more space above than below, show dropdown above
        setDropdownPosition(spaceAbove > spaceBelow ? "top" : "bottom");
      }
    };

    if (showUploadDropdown) {
      calculatePosition();
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showUploadDropdown]);

  // Get left side buttons (record and microphone - always visible when enabled)
  const getLeftButtons = () => {
    const buttons = [];

    // Record button
    if (config.record.enabled) {
      buttons.push(
        <ToolbarButton
          key="record"
          onClick={config.record.handler}
          title="Record a conversation (Coming soon)"
          disabled={true}
        >
          <RecordIcon size={24} />
        </ToolbarButton>,
      );
    }

    // Microphone button
    if (config.microphone.enabled) {
      buttons.push(
        <ToolbarButton
          key="microphone"
          onClick={config.microphone.handler}
          title="Dictate instead of write (Coming soon)"
          disabled={true}
        >
          <MicrophoneIcon size={24} />
        </ToolbarButton>,
      );
    }

    return buttons;
  };

  // Get right side buttons based on state
  const getRightButtons = () => {
    const buttons = [];

    if (isLoading && config.stop.enabled) {
      // When sending: show stop button
      buttons.push(
        <ToolbarButton
          key="stop"
          onClick={config.stop.handler}
          title="Stop generating"
        >
          <StopIcon size={24} />
        </ToolbarButton>,
      );
    } else if (hasInput && config.send.enabled) {
      // When text in input: show send button (with blue background)
      buttons.push(
        <button
          key="send"
          type="submit"
          title="Send message"
          className="w-8 h-8 rounded-full flex items-center justify-center transition-colors duration-200 bg-chat-primary text-icon-light/90 dark:text-white/90 hover:bg-chat-primary/90 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <SendIcon size={24} />
        </button>,
      );
    } else if (!hasInput && config.voiceConversation.enabled) {
      // When empty input: show voice button (with blue background)
      buttons.push(
        <ToolbarButton
          key="voice"
          onClick={config.voiceConversation.handler}
          title="Have voice conversation with AI (Coming soon)"
          disabled={true}
        >
          <VoiceConversationIcon size={24} />
        </ToolbarButton>,
      );
    }

    return buttons;
  };

  return (
    <div
      className={`flex items-center justify-between pt-0 ${className}`.trim()}
    >
      {/* Left section - Plus button only */}
      <div className="flex items-center gap-1 relative">
        {config.fileUpload.enabled && (
          <div ref={dropdownRef} className="relative">
            <ToolbarButton
              ref={buttonRef}
              onClick={() => setShowUploadDropdown(!showUploadDropdown)}
              title="Upload file or photo (Coming soon)"
              disabled={true}
            >
              <PlusIcon size={24} />
            </ToolbarButton>

            {/* Upload Dropdown */}
            {showUploadDropdown && (
              <div
                className={`absolute left-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1 min-w-[140px] z-50 ${
                  dropdownPosition === "top" ? "bottom-full" : "top-full"
                }`}
              >
                <button
                  onClick={() => {
                    config.fileUpload.handler?.();
                    setShowUploadDropdown(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Upload file
                </button>
                <button
                  onClick={() => {
                    config.fileUpload.photoHandler?.();
                    setShowUploadDropdown(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Upload photo
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right section - Record/Microphone + State-based buttons */}
      <div className="flex items-center gap-1">
        {/* Record and Microphone buttons - left of send button */}
        {getLeftButtons()}
        {/* State-based button (voice/send/stop) */}
        {getRightButtons()}
      </div>
    </div>
  );
}

/**
 * Development toolbar configuration - shows ALL buttons for testing
 * Switch to `defaultToolbarConfig` for production
 */
export const developmentToolbarConfig: ToolbarConfig = {
  fileUpload: { enabled: true, handler: undefined },
  microphone: { enabled: true, handler: undefined },
  voiceConversation: { enabled: true, handler: undefined },
  record: { enabled: true, handler: undefined },
  send: { enabled: true, handler: undefined },
  stop: { enabled: true, handler: undefined },
};

/**
 * Default toolbar configuration
 * Matches ChatGPT layout: Plus icon (left) + Voice/Send (right)
 *
 * To provide handlers for the enabled features:
 *
 * const customConfig: Partial<ToolbarConfig> = {
 *   fileUpload: { enabled: true, handler: handleFileUpload },
 *   voiceConversation: { enabled: true, handler: handleVoiceConversation },
 * };
 */
export const defaultToolbarConfig: ToolbarConfig = developmentToolbarConfig; // Using dev config for now

// Production config (commented out during development)
// export const defaultToolbarConfig: ToolbarConfig = {
//   fileUpload: { enabled: true, handler: undefined }, // Enabled by default - needs handler
//   microphone: { enabled: false, handler: undefined }, // TODO: Implement microphone input
//   voiceConversation: { enabled: true, handler: undefined }, // Enabled by default - needs handler
//   record: { enabled: false, handler: undefined }, // TODO: Implement recording
//   send: { enabled: true, handler: undefined }, // Will be provided by ChatInput
//   stop: { enabled: true, handler: undefined }, // Enabled by default - will be provided by ChatInput
// };
