"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Hook that provides scroll management for chat interface
 * @param messages - Array of messages
 * @returns Scroll utilities and state
 */
export function useScrollToBottom(messages: unknown[]) {
  const endRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const previousMessageCountRef = useRef(0);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const scrollToBottom = (immediate = false) => {
    if (endRef.current) {
      endRef.current.scrollIntoView({
        behavior: immediate ? "instant" : "smooth",
        block: "nearest"
      });
    }
  };

  const checkScrollPosition = () => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    }
  };

  useEffect(() => {
    const currentMessageCount = Array.isArray(messages) ? messages.length : 0;
    const previousMessageCount = previousMessageCountRef.current;

    // Only scroll when a new message is added (user sent message)
    if (currentMessageCount > previousMessageCount) {
      // Check if the last message is from user
      const lastMessage = Array.isArray(messages) && messages[currentMessageCount - 1];
      const isUserMessage = lastMessage && typeof lastMessage === 'object' && 'role' in lastMessage && lastMessage.role === 'user';

      if (isUserMessage) {
        // Immediate scroll to bottom when user sends message
        setTimeout(() => scrollToBottom(true), 10);
      }
    }

    // Check scroll position whenever messages change (including content additions)
    setTimeout(checkScrollPosition, 50);

    previousMessageCountRef.current = currentMessageCount;
  }, [messages]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollPosition);

      // Initial check after a short delay to ensure content is rendered
      setTimeout(checkScrollPosition, 100);

      return () => container.removeEventListener('scroll', checkScrollPosition);
    }
  }, []);

  return {
    endRef,
    containerRef,
    scrollToBottom,
    showScrollButton
  };
}