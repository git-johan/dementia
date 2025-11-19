"use client";

import { useState, useEffect } from "react";

/**
 * Hook to detect and monitor system theme preference
 * @returns Current theme ("light" | "dark")
 */
export function useTheme(): "light" | "dark" {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Check initial theme
    const checkTheme = () => {
      if (typeof window !== "undefined") {
        const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        setTheme(isDark ? "dark" : "light");
      }
    };

    // Set initial theme
    checkTheme();

    // Listen for theme changes
    if (typeof window !== "undefined") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const handleChange = (e: MediaQueryListEvent) => {
        setTheme(e.matches ? "dark" : "light");
      };

      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    }
  }, []);

  return theme;
}