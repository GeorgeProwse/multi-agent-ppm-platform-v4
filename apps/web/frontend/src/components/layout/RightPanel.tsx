import { useState } from 'react';
import { useAppStore } from '@/store';
import styles from './RightPanel.module.css';

export function RightPanel() {
  const {
    rightPanelCollapsed,
    toggleRightPanel,
    chatMessages,
    addChatMessage,
  } = useAppStore();
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    addChatMessage({
      role: 'user',
      content: inputValue.trim(),
    });

    // Simulate assistant response (placeholder)
    setTimeout(() => {
      addChatMessage({
        role: 'assistant',
        content:
          'This is a placeholder response. The assistant functionality will be implemented in a future iteration.',
      });
    }, 500);

    setInputValue('');
  };

  if (rightPanelCollapsed) {
    return (
      <aside className={`${styles.panel} ${styles.collapsed}`}>
        <button
          className={styles.expandButton}
          onClick={toggleRightPanel}
          title="Open Assistant"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </aside>
    );
  }

  return (
    <aside className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>Assistant</h2>
        <button
          className={styles.collapseButton}
          onClick={toggleRightPanel}
          title="Close Assistant"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      <div className={styles.messages}>
        {chatMessages.length === 0 ? (
          <div className={styles.empty}>
            <svg
              width="48"
              height="48"
              viewBox="0 0 20 20"
              fill="currentColor"
              className={styles.emptyIcon}
            >
              <path
                fillRule="evenodd"
                d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
                clipRule="evenodd"
              />
            </svg>
            <p className={styles.emptyText}>
              Ask the assistant for help with your project, program, or
              portfolio management tasks.
            </p>
          </div>
        ) : (
          chatMessages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${styles[message.role]}`}
            >
              <div className={styles.messageContent}>{message.content}</div>
              <time className={styles.messageTime}>
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </time>
            </div>
          ))
        )}
      </div>

      <form className={styles.inputArea} onSubmit={handleSubmit}>
        <input
          type="text"
          className={styles.input}
          placeholder="Ask the assistant..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button
          type="submit"
          className={styles.sendButton}
          disabled={!inputValue.trim()}
          title="Send message"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        </button>
      </form>
    </aside>
  );
}
