"use client";

interface ScrollToBottomButtonProps {
  onClick: () => void;
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

export function ScrollToBottomButton({ onClick, className = "" }: ScrollToBottomButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-7 h-7 rounded-full flex items-center justify-center transition-opacity hover:opacity-80 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 shadow-sm ${className}`.trim()}
      title="Scroll to bottom"
    >
      <ChevronDownIcon />
    </button>
  );
}