"use client";

interface TypingIndicatorProps {
  /** Custom className for the container */
  className?: string;
  /** Custom text to show (default: "AI is typing...") */
  text?: string;
  /** Show only the dots without text */
  dotsOnly?: boolean;
}

export function TypingIndicator({
  className = "",
  text = "AI is typing...",
  dotsOnly = false,
}: TypingIndicatorProps) {
  return (
    <div className={`animate-fade-in mb-4 mt-6 first:mt-0 ${className}`.trim()}>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          {!dotsOnly && (
            <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
              {text}
            </span>
          )}
          <div className="flex gap-1">
            <div className="w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full typing-dot"></div>
            <div className="w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full typing-dot"></div>
            <div className="w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full typing-dot"></div>
          </div>
        </div>
      </div>
    </div>
  );
}