/**
 * ConstructMind AI - AI BOQ Analyzer Workspace
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'motion/react';
import { 
  FileSpreadsheet, 
  Upload, 
  Brain, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle,
  Play,
  RotateCw,
  FolderOpen
} from 'lucide-react';
import { useScheduleStore } from '@/store/schedule-store';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { Badge } from '@/components/shared/Badge';
import { ProgressBar } from '@/components/shared/ProgressBar';
import { formatCurrency, formatNumber } from '@/lib/utils';

export default function BOQPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const { 
    boqItems, 
    fetchBOQItems, 
    uploadBOQFile, 
    analyzeBOQ, 
    convertBOQ,
    loading 
  } = useScheduleStore();

  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [isUploading, setIsUploading] = React.useState(false);
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);
  const [isConverting, setIsConverting] = React.useState(false);

  React.useEffect(() => {
    if (projectId) {
      fetchBOQItems(projectId);
    }
  }, [projectId, fetchBOQItems]);

  // Dropzone Setup
  const onDrop = React.useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(15);
    
    // Simulate upload progress animation
    const progressTimer = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressTimer);
          return 90;
        }
        return prev + 15;
      });
    }, 100);

    try {
      await uploadBOQFile(projectId, file);
      setUploadProgress(100);
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 500);
    } catch {
      clearInterval(progressTimer);
      setIsUploading(false);
    }
  }, [projectId, uploadBOQFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const handleAIAnalyze = async () => {
    setIsAnalyzing(true);
    await analyzeBOQ(projectId);
    setIsAnalyzing(false);
  };

  const handleConvert = async () => {
    setIsConverting(true);
    await convertBOQ(projectId);
    setIsConverting(false);
    // Route directly to schedule page to show Gantt bars
    router.push(`/projects/${projectId}/schedule`);
  };

  const totalCost = boqItems.reduce((sum, item) => sum + (item.total_amount || 0), 0);
  const analyzedCount = boqItems.filter(i => i.ai_parsed).length;
  const isAllAnalyzed = boqItems.length > 0 && analyzedCount === boqItems.length;

  return (
    <div className="space-y-8 text-left">
      {/* Top Banner Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight flex items-center space-x-2.5">
            <span>Bill of Quantities Workspace</span>
          </h1>
          <p className="text-xs text-zinc-400 font-medium">
            Upload contract estimates, run CSI classification, and compile schedule activity lines.
          </p>
        </div>

        {boqItems.length > 0 && (
          <div className="flex items-center space-x-3">
            {!isAllAnalyzed ? (
              <Button
                variant="outline"
                onClick={handleAIAnalyze}
                isLoading={isAnalyzing}
                className="border-primary/30 text-primary hover:bg-primary/5 rounded-xl glow-primary"
              >
                <Brain className="h-4.5 w-4.5 mr-2" />
                <span>Analyze with AI</span>
              </Button>
            ) : (
              <Button
                variant="primary"
                onClick={handleConvert}
                isLoading={isConverting}
                className="rounded-xl flex items-center space-x-2 shadow-lg shadow-primary/20 glow-primary"
              >
                <Play className="h-4.5 w-4.5" />
                <span>Build CPM Schedule</span>
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Grid: Upload pane or items table */}
      {boqItems.length === 0 ? (
        <Card className="border-white/5 border-dashed bg-surface/20 hover:bg-surface/35 transition-all duration-300">
          <CardContent className="p-12">
            <div 
              {...getRootProps()} 
              className="flex flex-col items-center justify-center text-center space-y-6 cursor-pointer py-16"
            >
              <input {...getInputProps()} />
              <div className="h-16 w-16 rounded-2xl bg-primary/10 border border-primary/20 text-primary flex items-center justify-center glow-primary animate-pulse">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  {isDragActive ? 'Drop your file here...' : 'Upload Bill of Quantities File'}
                </h3>
                <p className="text-xs text-zinc-500 max-w-sm mx-auto leading-relaxed">
                  Drag and drop your engineering estimate spreadsheet (.xlsx/.xls) or catalog PDF. We will automatically parse columns.
                </p>
              </div>
              
              {isUploading && (
                <div className="w-full max-w-xs space-y-2">
                  <ProgressBar value={uploadProgress} color="primary" size="sm" />
                  <p className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider">Parsing columns & rows...</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
          {/* Left panel: BOQ table */}
          <div className="lg:col-span-3 space-y-6">
            <Card className="border-white/5 p-0">
              <div className="p-4 border-b border-white/5 bg-white/2 flex justify-between items-center text-xs">
                <div className="flex items-center space-x-2 text-zinc-400 font-semibold">
                  <FileSpreadsheet className="h-4.5 w-4.5 text-zinc-500" />
                  <span>Parsed BOQ Items</span>
                </div>
                
                {/* Reset button */}
                <button
                  onClick={async () => {
                    // Simulating file deletion by uploading empty or reloading
                    await uploadBOQFile(projectId, new File([], 'delete'));
                  }}
                  className="text-zinc-500 hover:text-white transition-colors flex items-center space-x-1 uppercase font-bold tracking-wider text-[10px]"
                >
                  <RotateCw className="h-3 w-3" />
                  <span>Reset Sheet</span>
                </button>
              </div>
              
              <div className="w-full overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 text-[10px] font-bold text-zinc-500 uppercase tracking-widest bg-white/2">
                      <th className="py-3.5 px-6">Item</th>
                      <th className="py-3.5 px-4">Description</th>
                      <th className="py-3.5 px-4 text-right">Quantity</th>
                      <th className="py-3.5 px-4 text-center">Unit</th>
                      <th className="py-3.5 px-4 text-right">Rate</th>
                      <th className="py-3.5 px-4 text-right">Amount</th>
                      <th className="py-3.5 px-6 text-center">CSI Category</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/2">
                    {boqItems.map((item) => (
                      <tr key={item.id} className="hover:bg-white/1 transition-colors">
                        <td className="py-3 px-6 font-mono font-bold text-zinc-400">
                          {item.item_no}
                        </td>
                        <td className="py-3 px-4 text-white font-medium max-w-[280px] truncate" title={item.description}>
                          {item.description}
                        </td>
                        <td className="py-3 px-4 text-right text-zinc-300">
                          {formatNumber(item.quantity)}
                        </td>
                        <td className="py-3 px-4 text-center text-zinc-400 font-bold uppercase">
                          {item.unit}
                        </td>
                        <td className="py-3 px-4 text-right text-zinc-300 font-medium">
                          {formatCurrency(item.unit_rate)}
                        </td>
                        <td className="py-3 px-4 text-right text-white font-bold">
                          {formatCurrency(item.total_amount)}
                        </td>
                        <td className="py-3 px-6 text-center">
                          {item.ai_parsed ? (
                            <Badge variant="success" dot className="font-bold rounded-full py-0.5 px-2.5">
                              {item.ai_category || 'General'}
                            </Badge>
                          ) : (
                            <Badge variant="zinc" className="rounded-full">Unclassified</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Right panel: Analysis Summary */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="border-white/5">
              <CardHeader className="pb-3 text-left">
                <CardTitle className="text-sm font-bold">Analysis Summary</CardTitle>
                <CardDescription>CSI Division classification statistics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-xs text-left">
                <div className="flex justify-between items-center">
                  <span className="text-zinc-500">Total Items:</span>
                  <span className="text-white font-bold">{boqItems.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-500">Project Value:</span>
                  <span className="text-white font-black text-sm">{formatCurrency(totalCost)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-500">Classified:</span>
                  <span className="text-white font-bold">{analyzedCount} / {boqItems.length}</span>
                </div>
                
                <div className="h-px bg-white/5 my-2" />

                {/* Progress Circle Heuristic or Alert */}
                {isAllAnalyzed ? (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-4 rounded-xl flex items-start space-x-3">
                    <CheckCircle2 className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="space-y-1">
                      <h5 className="font-bold text-white">Analysis Complete</h5>
                      <p className="text-[10px] text-zinc-400 leading-normal">
                        All items have been mapped to standard CSI Division codes. Ready to generate CPM Gantt schedule bars.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-amber-500/10 border border-amber-500/20 text-amber-400 p-4 rounded-xl flex items-start space-x-3">
                    <AlertTriangle className="h-5 w-5 mt-0.5 flex-shrink-0 animate-pulse" />
                    <div className="space-y-1">
                      <h5 className="font-bold text-white">Pending AI Analysis</h5>
                      <p className="text-[10px] text-zinc-400 leading-normal">
                        Classification division codes have not been run. Trigger AI Analysis to catalog items.
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
