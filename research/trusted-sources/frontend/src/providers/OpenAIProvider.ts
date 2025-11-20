import { loadMessages, saveMessages, generateMessageId, type ChatMessage } from '../utils/messageStorage';

// Configuration
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const CHAT_ENDPOINT = `${BACKEND_URL}/api/v1/chat`;

export class OpenAIProvider {
  private messages: ChatMessage[] = [];

  constructor() {
    // Load existing messages from localStorage
    this.messages = loadMessages();
    console.log(`OpenAI Provider initialized with ${this.messages.length} existing messages`);
  }

  async* streamChat(messages: ChatMessage[]): AsyncGenerator<string, void, unknown> {
    try {
      // Get the latest user message
      const latestMessage = messages[messages.length - 1];
      if (!latestMessage || latestMessage.role !== 'user') {
        throw new Error('No valid user message found');
      }

      console.log('Sending message to FastAPI backend:', latestMessage.content);

      // Call FastAPI backend
      const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: latestMessage.content,
          user_id: 'frontend-user' // Simple user ID for now
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Backend error:', errorData);
        throw new Error(`Backend error: ${errorData.detail || response.statusText}`);
      }

      const data = await response.json();
      const responseText = data.response;

      console.log('Received response from FastAPI:', responseText);

      // Update local messages with the new conversation
      this.messages = [
        ...messages,
        {
          id: generateMessageId(),
          role: 'assistant',
          content: responseText,
          timestamp: Date.now()
        }
      ];

      // Save updated messages to localStorage
      saveMessages(this.messages);

      // Yield the response text as a single chunk (non-streaming)
      yield responseText;

    } catch (error) {
      console.error('OpenAI Provider Error:', error);

      // Yield error message
      const errorMessage = error instanceof Error
        ? `Beklager, jeg kunne ikke få svar fra systemet. Feil: ${error.message}`
        : 'Beklager, det oppstod en ukjent feil.';

      yield errorMessage;
    }
  }

  // Method to get current messages (useful for debugging)
  getMessages(): ChatMessage[] {
    return this.messages;
  }

  // Method to clear conversation
  clearMessages(): void {
    this.messages = [];
    saveMessages(this.messages);
    console.log('Conversation cleared');
  }
}