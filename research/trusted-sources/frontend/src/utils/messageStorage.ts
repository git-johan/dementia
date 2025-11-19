export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface UserConversation {
  userId: string;
  messages: ChatMessage[];
  lastUpdated: number;
}

// Generate a consistent browser-based user ID
export const getUserId = (): string => {
  if (typeof window === 'undefined') {
    return 'server-side-fallback'; // For SSR compatibility
  }

  let userId = localStorage.getItem('dementia-care-user-id');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('dementia-care-user-id', userId);
    console.log('Generated new user ID:', userId);
  }
  return userId;
};

// Save messages to localStorage
export const saveMessages = (messages: ChatMessage[]): void => {
  if (typeof window === 'undefined') {
    console.warn('Cannot save messages: localStorage not available (SSR)');
    return;
  }

  try {
    const userId = getUserId();
    const conversation: UserConversation = {
      userId,
      messages,
      lastUpdated: Date.now()
    };

    const storageKey = `conversation_${userId}`;
    localStorage.setItem(storageKey, JSON.stringify(conversation));
    console.log(`Saved ${messages.length} messages for user ${userId}`);
  } catch (error) {
    console.error('Error saving messages to localStorage:', error);
  }
};

// Load messages from localStorage
export const loadMessages = (): ChatMessage[] => {
  if (typeof window === 'undefined') {
    console.warn('Cannot load messages: localStorage not available (SSR)');
    return [];
  }

  try {
    const userId = getUserId();
    const storageKey = `conversation_${userId}`;
    const saved = localStorage.getItem(storageKey);

    if (saved) {
      const conversation: UserConversation = JSON.parse(saved);
      console.log(`Loaded ${conversation.messages.length} messages for user ${userId}`);
      return conversation.messages;
    } else {
      console.log('No saved conversation found for user', userId);
      return [];
    }
  } catch (error) {
    console.error('Error loading messages from localStorage:', error);
    return [];
  }
};

// Clear all messages for the current user
export const clearMessages = (): void => {
  if (typeof window === 'undefined') {
    console.warn('Cannot clear messages: localStorage not available (SSR)');
    return;
  }

  try {
    const userId = getUserId();
    const storageKey = `conversation_${userId}`;
    localStorage.removeItem(storageKey);
    console.log('Cleared all messages for user', userId);
  } catch (error) {
    console.error('Error clearing messages from localStorage:', error);
  }
};

// Generate a unique message ID
export const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};