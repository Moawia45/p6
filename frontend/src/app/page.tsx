/**
 * ConstructMind AI - Cinematic Landing Page
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'motion/react';
import { 
  Brain, 
  ArrowRight, 
  Sparkles, 
  Play, 
  CheckCircle,
  FileSpreadsheet, 
  Calendar, 
  Users, 
  ShieldAlert, 
  FileText, 
  Activity, 
  Cpu, 
  Clock,
  Compass,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/shared/Button';
import { Card, CardContent } from '@/components/shared/Card';
import { Badge } from '@/components/shared/Badge';
import { APP_NAME, CREATOR_INFO } from '@/lib/constants';

export default function LandingPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { type: 'spring' as const, stiffness: 100 } },
  };

  const features = [
    { name: 'AI BOQ Analyzer', desc: 'Upload PDF/Excel bills of quantities. AI extracts, categorizes, and validates items.', icon: FileSpreadsheet, color: 'text-primary' },
    { name: 'Smart Scheduling', desc: 'Auto-sequence tasks, estimate durations, and build WBS branches instantly.', icon: Calendar, color: 'text-accent' },
    { name: 'Resource Allocation', desc: 'Analyze crew histograms, detect over-allocation, and level resources.', icon: Users, color: 'text-secondary' },
    { name: 'CPM Calculations', desc: 'Engine calculates early/late start and finish dates, floats, and isolates the Critical Path.', icon: Activity, color: 'text-rose-400' },
    { name: 'Forensic Delay Analysis', desc: 'Automatically attribute slips to weather, site conflicts, or contractor mobilization.', icon: ShieldAlert, color: 'text-amber-400' },
    { name: 'Interactive Gantt Chart', desc: 'Primavera P6 level timelines with drag bars, custom milestones, and links.', icon: Compass, color: 'text-sky-400' },
    { name: 'AI Copilot Panels', desc: 'Stream construction logs, crew math, and FIDIC contract audits in under 500ms.', icon: Brain, color: 'text-primary' },
    { name: 'Executive Reports', desc: 'Print progress, EVM cost variance, and schedule claim summaries to PDF/Excel.', icon: FileText, color: 'text-emerald-400' },
  ];

  return (
    <div className="relative min-h-screen bg-background overflow-hidden flex flex-col">
      {/* Cinematic CSS background stars & nebulae */}
      <div className="absolute inset-0 z-0 pointer-events-none select-none overflow-hidden">
        {/* Glow gradients */}
        <div className="absolute top-[-20%] left-[-10%] h-[80%] w-[60%] rounded-full bg-primary/5 filter blur-[150px] animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-[-10%] right-[-10%] h-[70%] w-[50%] rounded-full bg-secondary/5 filter blur-[150px] animate-pulse" style={{ animationDuration: '10s' }} />
        
        {/* Pure CSS background grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
      </div>

      {/* Navigation Header */}
      <header className="relative w-full h-20 border-b border-white/5 flex items-center justify-between px-6 md:px-12 z-10 glass">
        <Link href="/" className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center glow-primary">
            <Brain className="h-5.5 w-5.5 text-white" />
          </div>
          <span className="text-lg font-black tracking-tight text-white">{APP_NAME}</span>
        </Link>

        {/* Action Button */}
        <div className="flex items-center space-x-4">
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="border-white/10 text-white hover:bg-white/5 rounded-xl h-10 px-4">
              Enter Workspace
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button variant="primary" size="sm" className="rounded-xl h-10 px-5 shadow-lg">
              Get Started
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative flex-1 flex flex-col items-center justify-center text-center px-6 py-20 z-10">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-4xl space-y-6 flex flex-col items-center"
        >
          {/* Badge: Creator Credits */}
          <motion.div variants={itemVariants}>
            <Badge variant="default" className="py-1.5 px-4 bg-primary/10 border-primary/20 text-primary font-bold shadow-lg hover:shadow-primary/5 select-none rounded-full flex items-center space-x-1.5 uppercase tracking-widest text-[10px]">
              <Sparkles className="h-3.5 w-3.5 animate-spin" style={{ animationDuration: '3s' }} />
              <span>Created by {CREATOR_INFO.name} • Civil Engineer UET Taxila</span>
            </Badge>
          </motion.div>

          {/* Headline */}
          <motion.h1 
            variants={itemVariants} 
            className="text-4xl md:text-6xl font-black tracking-tight leading-tight text-white"
          >
            Construction Intelligence, <br className="hidden md:inline"/>
            <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
              Reimagined
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p 
            variants={itemVariants}
            className="text-base md:text-lg text-zinc-400 max-w-2xl leading-relaxed font-medium"
          >
            AI-powered Primavera-style schedule controls, BOQ analysis, 
            and labor optimization tools that thinks like a senior planning engineer.
          </motion.p>

          {/* CTAs */}
          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-4 pt-4">
            <Link href="/dashboard">
              <Button variant="primary" size="lg" className="rounded-xl font-bold shadow-2xl h-13 px-8 flex items-center space-x-2">
                <span>Start Planning Free</span>
                <ArrowRight className="h-5 w-5 transition-transform duration-200 hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary" size="lg" className="rounded-xl font-semibold border-white/5 h-13 px-6 text-zinc-300 hover:text-white">
                <Play className="h-4.5 w-4.5 mr-2 text-primary" />
                <span>Quick Tour</span>
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Grid Section */}
      <section className="relative px-6 md:px-12 py-24 border-t border-white/5 bg-surface-2/20 z-10">
        <div className="max-w-7xl mx-auto space-y-16">
          <div className="max-w-2xl text-left space-y-3">
            <Badge variant="info" className="uppercase tracking-widest text-[9px] font-bold rounded-full py-1 px-3">
              Power Modules
            </Badge>
            <h2 className="text-2xl md:text-4xl font-black text-white tracking-tight leading-tight">
              Everything You Need to Control Your Project
            </h2>
            <p className="text-sm text-zinc-400 font-medium">
              We automate 80% of planning engineer tasks using latest Gemini & Groq neural models.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feat, index) => {
              const Icon = feat.icon;
              return (
                <motion.div
                  key={feat.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-50px' }}
                  transition={{ duration: 0.4, delay: index * 0.05 }}
                >
                  <Card hoverGlow className="h-full border-white/5 hover:border-primary/20">
                    <CardContent className="p-6 text-left flex flex-col space-y-4 justify-between h-full">
                      <div className="space-y-4">
                        <div className="h-10 w-10 rounded-xl bg-white/3 border border-white/5 flex items-center justify-center">
                          <Icon className={`h-5 w-5 ${feat.color}`} />
                        </div>
                        <h4 className="text-sm font-bold text-white tracking-tight">
                          {feat.name}
                        </h4>
                        <p className="text-xs text-zinc-400 leading-relaxed">
                          {feat.desc}
                        </p>
                      </div>
                      <Link href="/dashboard" className="inline-flex items-center space-x-1 text-[10px] font-bold uppercase tracking-wider text-primary pt-4 select-none hover:text-primary-hover">
                        <span>Launch Module</span>
                        <ChevronRight className="h-3 w-3" />
                      </Link>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Model Tech Specs */}
      <section className="relative px-6 md:px-12 py-20 border-t border-white/5 z-10 select-none">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-12 text-left">
          <div className="max-w-lg space-y-4">
            <Badge variant="zinc" className="uppercase tracking-widest text-[9px] font-bold rounded-full py-1 px-3">
              Neural Network Specs
            </Badge>
            <h3 className="text-2xl md:text-3xl font-black text-white tracking-tight">
              Exclusive LLM Scheduling Stack
            </h3>
            <p className="text-xs md:text-sm text-zinc-400 leading-relaxed">
              We leverage Google Gemini for deep engineering documentation parsing, 
              and Groq Llama 4 for sub-second conversational scheduling calculations. No OpenAI. No Claude.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <div className="p-6 rounded-2xl bg-surface-2/60 border border-white/5 flex items-center space-x-4 w-72">
              <div className="h-11 w-11 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <Cpu className="h-6 w-6" />
              </div>
              <div className="text-left">
                <h4 className="text-xs font-bold text-white leading-none">Gemini 2.5 Pro</h4>
                <p className="text-[10px] text-zinc-500 font-medium mt-1">Deep reasoning, claim reviews, BOQ parsing</p>
              </div>
            </div>
            <div className="p-6 rounded-2xl bg-surface-2/60 border border-white/5 flex items-center space-x-4 w-72">
              <div className="h-11 w-11 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Cpu className="h-6 w-6" />
              </div>
              <div className="text-left">
                <h4 className="text-xs font-bold text-white leading-none">Llama 4 Scout</h4>
                <p className="text-[10px] text-zinc-500 font-medium mt-1">Streaming AI chat, real-time crew counts</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Block */}
      <section className="relative px-6 md:px-12 py-16 border-t border-white/5 bg-surface-2/30 z-10">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: '90%', label: 'Workflows Automated', icon: CheckCircle },
            { value: '10x', label: 'Faster Schedules', icon: Clock },
            { value: '42+', label: 'Scheduling Modules', icon: Sparkles },
            { value: '24/7', label: 'AI Cost Controls', icon: Brain },
          ].map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div key={idx} className="flex flex-col items-center justify-center text-center space-y-2 select-none">
                <Icon className="h-5 w-5 text-primary opacity-60" />
                <h2 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                  {stat.value}
                </h2>
                <p className="text-[10px] uppercase font-bold text-zinc-500 tracking-wider">
                  {stat.label}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="relative w-full border-t border-white/5 py-12 px-6 md:px-12 z-10 glass mt-auto text-left">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center">
                <Brain className="h-4.5 w-4.5 text-white" />
              </div>
              <span className="text-sm font-bold text-white tracking-tight">{APP_NAME}</span>
            </div>
            <p className="text-xs text-zinc-500 max-w-sm">
              ConstructMind AI is a futuristic platform for automated CPM engineering and quantitative project controls.
            </p>
          </div>
          
          <div className="text-zinc-500 text-xs space-y-1.5 md:text-right">
            <p className="font-bold text-zinc-400">Created by Moawia Husnain</p>
            <p>Civil Engineer • UET Taxila</p>
            <p>Contact: {CREATOR_INFO.phone} | {CREATOR_INFO.email}</p>
            <p className="text-[10px] text-zinc-600 pt-2">© {new Date().getFullYear()} ConstructMind AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
