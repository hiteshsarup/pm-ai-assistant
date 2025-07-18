import React from 'react';
import { cn } from '@/lib/utils';
import MarkdownRenderer from './markdown-renderer';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
}

const Message: React.FC<MessageProps> = ({ role, content }) => {
  const isUser = role === 'user';
  return (
    <div
      className={cn(
        "flex",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-md p-3 rounded-lg",
          isUser ? "bg-blue-700 text-white" : "bg-gray-700 text-gray-100"
        )}
      >
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
};

export default Message;