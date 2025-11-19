"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-gray dark:prose-invert max-w-none ${className}`.trim()}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre: ({ children, ...props }) => (
            <pre
              className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg p-4 overflow-x-auto border border-gray-200 dark:border-gray-600 my-4"
              {...props}
            >
              {children}
            </pre>
          ),
          code: ({ children, className, ...props }: any) => {
            const isInline = !className?.includes('language-');
            if (isInline) {
              return (
                <code
                  className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-1.5 py-0.5 rounded font-mono"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}