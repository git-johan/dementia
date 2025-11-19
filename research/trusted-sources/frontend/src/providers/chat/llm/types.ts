import { Message } from "../../../components/chat/ChatMessage";

export interface LLMProvider {
  /**
   * Stream chat responses (optional)
   * @param messages - Array of conversation messages
   * @returns AsyncGenerator yielding response chunks
   */
  streamChat?(messages: Message[]): AsyncGenerator<string, void, unknown>;

  /**
   * Send message and get full response (optional)
   * @param messages - Array of conversation messages
   * @returns Promise with complete response
   */
  sendMessage?(messages: Message[]): Promise<string>;
}