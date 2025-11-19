"use client";

import { ChatContainer, ChatProvider } from "ai-chat-ui";

// Mock provider for testing (simulates streaming)
class MockProvider {
  async* streamChat(messages: any[]) {
    const responses = [
      "Hello! ",
      "This is a comprehensive markdown test. ",
      "\n\n## Headers Work Great\n",
      "### Subheaders Too\n",
      "#### And Even Smaller Ones\n\n",
      "**Bold text** and *italic text* and ***bold italic*** work perfectly. ",
      "You can also use __bold__ and _italic_ syntax.\n\n",
      "Here's some `inline code` and a [link to Google](https://google.com).\n\n",
      "## Lists\n",
      "**Unordered lists:**\n",
      "- First item\n",
      "- Second item\n",
      "  - Nested item\n",
      "  - Another nested item\n",
      "- Third item\n\n",
      "**Ordered lists:**\n",
      "1. First numbered item\n",
      "2. Second numbered item\n",
      "   1. Nested numbered item\n",
      "   2. Another nested item\n",
      "3. Third numbered item\n\n",
      "## Code Blocks\n",
      "```javascript\n",
      "function greet(name) {\n",
      "  console.log(`Hello, ${name}!`);\n",
      "  return `Welcome to the chat!`;\n",
      "}\n",
      "\n",
      "greet('World');\n",
      "```\n\n",
      "```python\n",
      "def fibonacci(n):\n",
      "    if n <= 1:\n",
      "        return n\n",
      "    return fibonacci(n-1) + fibonacci(n-2)\n",
      "\n",
      "print(fibonacci(10))\n",
      "```\n\n",
      "## Blockquotes\n",
      "> This is a blockquote.\n",
      "> It can span multiple lines\n",
      "> and looks great!\n\n",
      "> Nested blockquotes work too:\n",
      "> > This is nested\n",
      "> > Pretty cool, right?\n\n",
      "## Tables\n",
      "| Feature | Status | Notes |\n",
      "|---------|--------|-------|\n",
      "| Headers | ✅ | Working |\n",
      "| Lists | ✅ | Both types |\n",
      "| Code | ✅ | Inline and blocks |\n",
      "| Links | ✅ | External links |\n",
      "| Tables | ✅ | This one! |\n\n",
      "## Special Characters\n",
      "Here are some special characters: ~strikethrough~ (if supported)\n\n",
      "Math expressions: `x = y + z` and equations like `a² + b² = c²`\n\n",
      "Emojis work too: 🚀 💻 ✨ 🎉\n\n",
      "## Horizontal Rule\n",
      "---\n\n",
      "## Task Lists (if supported)\n",
      "- [x] Completed task\n",
      "- [ ] Pending task\n",
      "- [x] Another completed task\n",
      "- [ ] Future enhancement\n\n",
      "That covers most markdown features! How does everything look? 🎨"
    ];

    for (const chunk of responses) {
      yield chunk;
      await new Promise(resolve => setTimeout(resolve, 80));
    }
  }
}

export default function TestPage() {
  return (
    <ChatProvider llmProvider={new MockProvider() as any}>
      <ChatContainer className="h-screen" />
    </ChatProvider>
  );
}