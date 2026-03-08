"""Token-aware conversation context manager."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Message:
    """Conversation message."""

    role: str
    content: str


@dataclass
class ConversationContext:
    """Manages conversation context with token awareness.

    For edge models like Qwen 0.8B, we need to carefully manage context window.
    This class maintains recent conversation history within token limits.
    """

    messages: List[Message] = field(default_factory=list)
    state: dict = field(default_factory=dict)
    max_history_tokens: int = 512  # ~25% of context for history

    def add_message(self, role: str, content: str):
        """Add a message to conversation history.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.messages.append(Message(role=role, content=content))

    def compact(self, tokenizer) -> List[Message]:
        """Get compacted message history that fits within token limit.

        Keeps most recent messages that fit in max_history_tokens.

        Args:
            tokenizer: Tokenizer to count tokens (must have encode method)

        Returns:
            List of messages within token budget
        """
        if not hasattr(tokenizer, "encode"):
            # Fallback: just return last N messages
            return self.messages[-5:] if len(self.messages) > 5 else self.messages

        total = 0
        kept = []
        for msg in reversed(self.messages):
            tokens = len(tokenizer.encode(msg.content))
            if total + tokens > self.max_history_tokens:
                break
            kept.insert(0, msg)
            total += tokens
        return kept

    def to_dict(self) -> dict:
        """Serialize context to dict.

        Returns:
            Dict representation for client storage
        """
        return {
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in self.messages
            ],
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationContext":
        """Deserialize context from dict.

        Args:
            data: Dict representation

        Returns:
            ConversationContext instance
        """
        messages = [Message(**msg) for msg in data.get("messages", [])]
        state = data.get("state", {})
        return cls(messages=messages, state=state)

    def clear(self):
        """Clear all messages and state."""
        self.messages.clear()
        self.state.clear()
