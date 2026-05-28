/**
 * ConstructMind AI - Dashboard AIInsightCard
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { Brain, Sparkles, CheckCircle2 } from 'lucide-react';
import { Card, CardContent } from '../shared/Card';
import { cn } from '@/lib/utils';

interface AIInsightCardProps {
  title: string;
  insights: string[];
  className?: string;
}

export function AIInsightCard({ title, insights, className }: AIInsightCardProps) {
  const [currentInsightIndex, setCurrentInsightIndex] = React.useState(0);
  const [displayText, setDisplayText] = React.useState('');
  const [isTyping, setIsTyping] = React.useState(true);

  const fullText = insights[currentInsightIndex] || '';

  // Typewriter effect
  React.useEffect(() => {
    setDisplayText('');
    setIsTyping(true);
    let i = 0;
    
    const interval = setInterval(() => {
      if (i < fullText.length) {
        setDisplayText((prev) => prev + fullText.charAt(i));
        i++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 25); // 25ms per character typing rate

    return () => clearInterval(interval);
  }, [currentInsightIndex, fullText]);

  return (
    <Card className={cn('relative border-transparent overflow-hidden border p-0.5 bg-gradient-to-r from-primary/20 via-secondary/15 to-accent/20', className)}>
      {/* Inner card panel */}
      <div className="bg-surface rounded-[15px] p-5 h-full flex flex-col justify-between text-left space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="h-8 w-8 rounded-lg bg-primary/10 border border-primary/20 text-primary flex items-center justify-center glow-primary animate-pulse">
              <Brain className="h-4.5 w-4.5" />
            </div>
            <h4 className="text-sm font-bold text-white tracking-tight">
              {title}
            </h4>
          </div>
          <div className="flex items-center space-x-1 text-[10px] font-bold text-primary bg-primary/5 border border-primary/15 px-2 py-0.5 rounded-full uppercase tracking-wider">
            <Sparkles className="h-3 w-3 animate-spin" style={{ animationDuration: '4s' }} />
            <span>AI Copilot Insight</span>
          </div>
        </div>

        {/* Content Typing Area */}
        <div className="min-h-[90px] flex items-start space-x-3 text-zinc-300 text-sm leading-relaxed">
          <CheckCircle2 className="h-5 w-5 text-accent mt-0.5 flex-shrink-0" />
          <div className="space-y-2">
            <p className="whitespace-pre-line text-left">
              {displayText}
              {isTyping && (
                <motion.span
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ repeat: Infinity, duration: 0.8 }}
                  className="inline-block w-1.5 h-3.5 bg-primary ml-1 align-middle"
                />
              )}
            </p>
          </div>
        </div>

        {/* Selector pagination tabs */}
        {insights.length > 1 && (
          <div className="flex items-center justify-between pt-3 border-t border-white/5 mt-4">
            <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">
              Recommendation {currentInsightIndex + 1} of {insights.length}
            </span>
            <div className="flex space-x-1.5">
              {insights.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentInsightIndex(idx)}
                  className={cn(
                    'h-1.5 rounded-full transition-all duration-300',
                    idx === currentInsightIndex ? 'w-4 bg-primary' : 'w-1.5 bg-zinc-700'
                  )}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
export default AIInsightCard;
