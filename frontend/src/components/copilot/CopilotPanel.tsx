/**
 * ConstructMind AI - Copilot Panel
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Brain, X, Send, CornerDownLeft, Sparkles, AlertCircle } from 'lucide-react';
import { useCopilotStore } from '@/store/copilot-store';
import { useProjectStore } from '@/store/project-store';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { cn } from '@/lib/utils';

export function CopilotPanel() {
  const { messages, isOpen, setOpen, isStreaming, sendMessage, clearChat } = useCopilotStore();
  const { activeProject } = useProjectStore();
  const [inputValue, setInputValue] = React.useState('');
  
  const scrollRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || isStreaming) return;

    setInputValue('');
    await sendMessage(text, activeProject?.id);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedPrompts = [
    { text: 'Why is the project delayed?', icon: AlertCircle },
    { text: 'Show critical path analysis', icon: Brain },
    { text: 'How many masons needed to finish in 5 days?', icon: Sparkles },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 50 }}
          transition={{ type: 'spring', stiffness: 350, damping: 30 }}
          className="fixed right-6 bottom-24 w-[420px] h-[600px] rounded-2xl bg-surface border border-white/5 shadow-2xl flex flex-col z-50 overflow-hidden glass-strong"
        >
          {/* Header */}
          <div className="h-14 px-4 bg-surface-2/60 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="h-7 w-7 rounded-lg bg-primary/10 border border-primary/20 text-primary flex items-center justify-center glow-primary">
                <Brain className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">
                  ConstructMind AI
                </h3>
                <p className="text-[10px] text-zinc-500 font-medium leading-none">
                  Llama 4 Maverick Scheduling Copilot
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-1.5">
              <button
                onClick={clearChat}
                className="text-[10px] uppercase font-bold tracking-wider text-zinc-500 hover:text-white px-2 py-1 hover:bg-white/5 rounded-md transition-colors"
              >
                Clear
              </button>
              <button
                onClick={() => setOpen(false)}
                className="text-zinc-400 hover:text-white p-1 hover:bg-white/5 rounded-lg transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Conversation Screen */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 flex flex-col space-y-4 scroll-smooth"
          >
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}

            {isStreaming && <TypingIndicator />}
          </div>

          {/* Suggested prompts (when clean or just greeting is present) */}
          {messages.length <= 1 && (
            <div className="px-4 pb-3 space-y-2">
              <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider text-left">
                Suggested Prompts
              </p>
              <div className="flex flex-col space-y-1.5">
                {suggestedPrompts.map((p) => {
                  const Icon = p.icon;
                  return (
                    <button
                      key={p.text}
                      onClick={() => {
                        setInputValue(p.text);
                      }}
                      className="flex items-center space-x-2 p-2 rounded-xl bg-surface-2/40 border border-white/5 hover:bg-white/5 text-xs text-zinc-300 hover:text-white text-left transition-all duration-200"
                    >
                      <Icon className="h-3.5 w-3.5 text-primary flex-shrink-0" />
                      <span className="truncate">{p.text}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Input Panel */}
          <div className="p-3 bg-surface-2/60 border-t border-white/5">
            <div className="relative flex items-center bg-surface border border-border rounded-xl px-3 focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all duration-200">
              <input
                type="text"
                placeholder={isStreaming ? "AI is typing..." : "Ask copilot about construction logs..."}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isStreaming}
                className="w-full h-11 bg-transparent text-sm text-foreground focus:outline-none placeholder:text-zinc-500 disabled:cursor-not-allowed"
              />
              <div className="flex items-center space-x-1.5 pl-2 border-l border-white/5">
                <button
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isStreaming}
                  className="h-8 w-8 rounded-lg bg-primary hover:bg-primary-hover text-white flex items-center justify-center transition-all disabled:opacity-50 disabled:bg-zinc-800 disabled:text-zinc-500 shadow-sm"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="flex justify-between items-center mt-2 px-1 text-[10px] text-zinc-500">
              <span>UET Taxila Civil Copilot</span>
              <span className="flex items-center space-x-1">
                <span>Press Enter</span>
                <CornerDownLeft className="h-2.5 w-2.5" />
              </span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
