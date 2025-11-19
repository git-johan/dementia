"use client";

interface FloatingActionButtonProps {
  isLoading: boolean;
  showScrollButton: boolean;
  onScrollToBottom: () => void;
  className?: string;
}

function ChevronDownIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 14 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M11 5L7 9L3 5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function TypingDots() {
  return (
    <div className="flex gap-0.5">
      <div className="w-1.5 h-1.5 bg-gray-600 dark:bg-gray-400 rounded-full animate-pulse"></div>
      <div className="w-1.5 h-1.5 bg-gray-600 dark:bg-gray-400 rounded-full animate-pulse [animation-delay:0.2s]"></div>
      <div className="w-1.5 h-1.5 bg-gray-600 dark:bg-gray-400 rounded-full animate-pulse [animation-delay:0.4s]"></div>
    </div>
  );
}

export function FloatingActionButton({
  isLoading,
  showScrollButton,
  onScrollToBottom,
  className = ""
}: FloatingActionButtonProps) {
  // Show if AI is typing OR if user scrolled up
  const shouldShow = isLoading || showScrollButton;

  if (!shouldShow) return null;

  if (isLoading) {
    // When typing: wider button with dots + arrow
    return (
      <button
        onClick={onScrollToBottom}
        className={`h-7 px-2 rounded-full flex items-center justify-between gap-1 transition-opacity hover:opacity-80 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 shadow-sm ${className}`.trim()}
        title="AI is typing... Click to follow"
      >
        <TypingDots />
        <ChevronDownIcon />
      </button>
    );
  }

  // When not typing: compact button with just arrow
  return (
    <button
      onClick={onScrollToBottom}
      className={`w-7 h-7 rounded-full flex items-center justify-center transition-opacity hover:opacity-80 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 shadow-sm ${className}`.trim()}
      title="Scroll to bottom"
    >
      <ChevronDownIcon />
    </button>
  );
}