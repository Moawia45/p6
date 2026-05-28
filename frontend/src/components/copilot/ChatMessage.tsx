/**
 * ConstructMind AI - Copilot ChatMessage
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'motion/react';
import { Brain, User } from 'lucide-react';
import { CopilotMessage } from '@/types/project';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: CopilotMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistant = message.role === 'assistant';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'flex items-start space-x-3 max-w-[85%] mb-4',
        isAssistant ? 'self-start' : 'self-end flex-row-reverse space-x-reverse'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'h-8 w-8 rounded-xl flex items-center justify-center border flex-shrink-0',
          isAssistant 
            ? 'bg-primary/10 border-primary/20 text-primary glow-primary' 
            : 'bg-zinc-800 border-zinc-700 text-zinc-300'
        )}
      >
        {isAssistant ? <Brain className="h-4.5 w-4.5" /> : <User className="h-4.5 w-4.5" />}
      </div>

      {/* Message Balloon */}
      <div
        className={cn(
          'rounded-2xl p-4 text-sm leading-relaxed border',
          isAssistant
            ? 'bg-surface-2/40 border-white/5 text-zinc-100 text-left'
            : 'bg-primary text-white border-primary/20 text-left'
        )}
      >
        {isAssistant ? (
          <div className="prose prose-invert max-w-none text-left">
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                li: ({ children }) => <li className="text-zinc-200">{children}</li>,
                h3: ({ children }) => <h3 className="text-sm font-bold text-white mt-3 mb-1">{children}</h3>,
                h4: ({ children }) => <h4 className="text-xs font-bold text-white mt-2 mb-1">{children}</h4>,
                code: ({ children }) => (
                  <code className="bg-zinc-800/80 px-1 py-0.5 rounded text-xs text-primary font-mono">
                    {children}
                  </code>
                ),
                strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{message.content}</p>
        )}
      </div>
    </motion.div>
  );
}
