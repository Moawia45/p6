/**
 * ConstructMind AI - Settings Page
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { Settings, Key, Brain, Save, Check, Eye, EyeOff, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

// Simple localStorage-based settings
function useSettings() {
  const [groqApiKey, setGroqApiKey] = React.useState('');
  const [groqModel, setGroqModel] = React.useState('meta-llama/llama-4-scout-17b-16e-instruct');
  const [saved, setSaved] = React.useState(false);

  React.useEffect(() => {
    const key = localStorage.getItem('constructmind_groq_api_key') || '';
    const model = localStorage.getItem('constructmind_groq_model') || 'meta-llama/llama-4-scout-17b-16e-instruct';
    setGroqApiKey(key);
    setGroqModel(model);
  }, []);

  const save = () => {
    localStorage.setItem('constructmind_groq_api_key', groqApiKey);
    localStorage.setItem('constructmind_groq_model', groqModel);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return { groqApiKey, setGroqApiKey, groqModel, setGroqModel, save, saved };
}

const AVAILABLE_MODELS = [
  { value: 'meta-llama/llama-4-scout-17b-16e-instruct', label: 'Llama 4 Scout 17B (Recommended)' },
  { value: 'meta-llama/llama-4-maverick-17b-128e-instruct', label: 'Llama 4 Maverick 17B' },
  { value: 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B', label: 'DeepSeek R1 70B' },
  { value: 'google/gemma-2-9b-it', label: 'Gemma 2 9B' },
  { value: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B' },
  { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B Versatile' },
];

export default function SettingsPage() {
  const { groqApiKey, setGroqApiKey, groqModel, setGroqModel, save, saved } = useSettings();
  const [showKey, setShowKey] = React.useState(false);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100 } }
  };

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-8 max-w-3xl">
      {/* Header */}
      <motion.div variants={itemVariants} className="space-y-1">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center">
            <Settings className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">Settings</h1>
        </div>
        <p className="text-xs text-zinc-400 font-medium">Configure API keys, AI models, and application preferences.</p>
      </motion.div>

      {/* API Keys Section */}
      <motion.div variants={itemVariants} className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6 space-y-6">
        <div className="flex items-center space-x-3 pb-4 border-b border-white/5">
          <Key className="h-5 w-5 text-primary" />
          <h2 className="text-base font-bold text-white">API Keys</h2>
        </div>

        {/* Groq API Key */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider flex items-center space-x-2">
            <Shield className="h-3.5 w-3.5" />
            <span>Groq API Key</span>
          </label>
          <p className="text-[10px] text-zinc-500">
            Required for AI Copilot chat. Get your key from{' '}
            <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              console.groq.com
            </a>
          </p>
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={groqApiKey}
              onChange={(e) => setGroqApiKey(e.target.value)}
              placeholder="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              className="w-full h-11 bg-[var(--background)] border border-white/10 rounded-xl px-4 pr-12 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white transition-colors"
            >
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </motion.div>

      {/* AI Model Section */}
      <motion.div variants={itemVariants} className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6 space-y-6">
        <div className="flex items-center space-x-3 pb-4 border-b border-white/5">
          <Brain className="h-5 w-5 text-secondary" />
          <h2 className="text-base font-bold text-white">AI Model Configuration</h2>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Groq Model</label>
          <p className="text-[10px] text-zinc-500">Select the AI model used for copilot analysis and report generation.</p>
          <select
            value={groqModel}
            onChange={(e) => setGroqModel(e.target.value)}
            className="w-full h-11 bg-[var(--background)] border border-white/10 rounded-xl px-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary cursor-pointer transition-all"
          >
            {AVAILABLE_MODELS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div variants={itemVariants}>
        <button
          onClick={save}
          className={cn(
            'h-12 px-8 rounded-xl font-bold text-sm flex items-center space-x-2 transition-all duration-300 shadow-lg',
            saved
              ? 'bg-emerald-500 text-white'
              : 'bg-primary text-white hover:bg-primary/90'
          )}
        >
          {saved ? (
            <><Check className="h-4 w-4" /><span>Settings Saved!</span></>
          ) : (
            <><Save className="h-4 w-4" /><span>Save Settings</span></>
          )}
        </button>
      </motion.div>
    </motion.div>
  );
}
