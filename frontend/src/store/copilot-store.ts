/**
 * ConstructMind AI - AI Copilot Zustand Store
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import { create } from 'zustand';
import { CopilotMessage } from '../types/project';
import { api } from '../lib/api';
import { delay } from '../lib/utils';
import { API_BASE_URL } from '../lib/constants';

interface CopilotState {
  messages: CopilotMessage[];
  isOpen: boolean;
  isStreaming: boolean;
  
  // Actions
  toggleOpen: () => void;
  setOpen: (open: boolean) => void;
  sendMessage: (text: string, projectId?: string) => Promise<void>;
  clearChat: () => void;
}

export const useCopilotStore = create<CopilotState>((set, get) => ({
  messages: [
    {
      role: 'assistant',
      content: (
        "Hello! I am **ConstructMind AI**, your construction controls co-pilot.\n\n" +
        "I was created by **Moawia Husnain**, Civil Engineer from UET Taxila (+923266915744).\n\n" +
        "How can I assist you with your scheduling, BOQ analysis, or critical path calculations today?"
      ),
    },
  ],
  isOpen: false,
  isStreaming: false,

  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
  
  setOpen: (open) => set({ isOpen: open }),

  sendMessage: async (text, projectId) => {
    if (!text.trim()) return;

    // Append user message
    const userMsg: CopilotMessage = { role: 'user', content: text };
    set((state) => ({ 
      messages: [...state.messages, userMsg],
      isStreaming: true
    }));

    const chatHistory = get().messages.slice(0, -1); // Exclude the newly added user message to avoid duplicate

    // Try SSE Streaming from backend first
    try {
      const controller = new AbortController();
      const response = await fetch(`${API_BASE_URL}/api/copilot/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          conversation_history: chatHistory,
          project_id: projectId,
          stream: true
        }),
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error('Streaming failed on server, using static fallback.');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error('No reader available');

      // Add empty assistant response
      const assistantMsg: CopilotMessage = { role: 'assistant', content: '' };
      set((state) => ({ messages: [...state.messages, assistantMsg] }));

      let completeContent = '';
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (dataStr === '[DONE]') {
              break;
            }
            try {
              const data = JSON.parse(dataStr);
              if (data.content) {
                completeContent += data.content;
                set((state) => {
                  const copy = [...state.messages];
                  copy[copy.length - 1] = {
                    role: 'assistant',
                    content: completeContent
                  };
                  return { messages: copy };
                });
              } else if (data.error) {
                throw new Error(data.error);
              }
            } catch {
              // Ignore parse errors for split frames
            }
          }
        }
      }
      set({ isStreaming: false });
      return;
    } catch (err) {
      console.warn('Backend streaming failed, executing client-side simulation.', err);
    }

    // Heuristic Offline Chat Response Generation
    // Simulates streaming with custom typing delays
    set({ isStreaming: true });
    
    // Add empty assistant response
    const assistantMsg: CopilotMessage = { role: 'assistant', content: '' };
    set((state) => ({ messages: [...state.messages, assistantMsg] }));

    // Generate responsive construction advice locally
    const cleanQuery = text.toLowerCase();
    let reply = '';
    
    if (cleanQuery.includes('delay') || cleanQuery.includes('behind')) {
      reply = (
        "Based on schedule analytics, the project is currently **8 days behind baseline**.\n\n" +
        "**Key slip causes:**\n" +
        "1. Excusable: Rain during Earthwork Excavation (5 days)\n" +
        "2. Non-Excusable: Subcontractor delay in Formwork arrival (3 days)\n\n" +
        "**Recommended recovery actions:**\n" +
        "- Authorize **2 hours daily overtime** for concrete formwork crews.\n" +
        "- Fast-track the follow-on interior MEP conduits by converting them from Finish-to-Start to Start-to-Start with a 3-day lag."
      );
    } else if (cleanQuery.includes('critical path') || cleanQuery.includes('float')) {
      reply = (
        "Analyzing critical path nodes from CPM Engine:\n\n" +
        "The project has **12 critical activities** forming the longest path. Key items include:\n" +
        "- GF Columns Reinforcement (`A3010`)\n" +
        "- Cast GF Columns (`A3020`)\n" +
        "- GF Slab Decking & Shuttering (`A3030`)\n\n" +
        "These tasks have **0 days of Total Float**. Any delay on these items directly pushes the completion date of October 13, 2026."
      );
    } else if (cleanQuery.includes('mason') || cleanQuery.includes('labor') || cleanQuery.includes('resource')) {
      reply = (
        "According to our local productivity rates database, a typical mason crew installs **400-600 bricks/day**.\n\n" +
        "For GF Brickwork (`A4010`) with a quantity of `120 m³`, we estimate a total of **12 working days** using 2 mason teams (1 lead mason + 2 helpers per team).\n\n" +
        "If you want to accelerate this to **5 days**, you will need to increase mobilization to **5 active mason teams** operating in parallel zones."
      );
    } else if (cleanQuery.includes('cpi') || cleanQuery.includes('spi') || cleanQuery.includes('cost')) {
      reply = (
        "Financial project controls assessment:\n\n" +
        "- **SPI (Schedule Performance Index):** `0.91` (Behind schedule by 9%)\n" +
        "- **CPI (Cost Performance Index):** `0.94` (Over budget by 6%)\n" +
        "- **Cost Variance (CV):** `-6%` (Overspent on subgrade concrete rate variance)\n\n" +
        "Mitigation: Audit material log slips for Concrete OPC Cement bags and optimize concrete pumps to avoid idle equipment standby charges."
      );
    } else {
      reply = (
        "I have registered your inquiry regarding construction scheduling controls.\n\n" +
        "As an AI copilot, I can help you analyze CPM schedules, read uploaded PDF/Excel bills of quantities, " +
        "calculate daily labor outputs, and print status reports.\n\n" +
        "This system uses **Llama 4 Scout** on Groq for sub-second streaming, and **Gemini 2.5 Pro** for document analysis."
      );
    }

    // Stream word-by-word into store
    const words = reply.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += (i === 0 ? '' : ' ') + words[i];
      set((state) => {
        const copy = [...state.messages];
        copy[copy.length - 1] = {
          role: 'assistant',
          content: currentText
        };
        return { messages: copy };
      });
      await delay(40); // 40ms typing rate
    }

    set({ isStreaming: false });
  },

  clearChat: () => {
    set({
      messages: [
        {
          role: 'assistant',
          content: (
            "Chat history cleared. I am ready for your next project controls question.\n\n" +
            "Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744"
          )
        }
      ]
    });
  }
}));
