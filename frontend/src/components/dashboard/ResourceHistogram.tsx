/**
 * ConstructMind AI - Resource Histogram Recharts Component
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ReferenceLine
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../shared/Card';

interface HistogramDataPoint {
  date: string;
  masons: number;
  carpenters: number;
  laborers: number;
}

interface ResourceHistogramProps {
  data?: HistogramDataPoint[];
  title?: string;
  capacityLimit?: number;
}

export function ResourceHistogram({
  title = 'Labor Resource Allocation Histogram',
  capacityLimit = 12,
  data = [
    { date: '06/01', masons: 2, carpenters: 1, laborers: 4 },
    { date: '06/08', masons: 3, carpenters: 2, laborers: 5 },
    { date: '06/15', masons: 4, carpenters: 4, laborers: 6 },
    { date: '06/22', masons: 5, carpenters: 5, laborers: 7 }, // Peak allocation: exceeds capacity limit
    { date: '06/29', masons: 4, carpenters: 3, laborers: 5 },
    { date: '07/06', masons: 2, carpenters: 2, laborers: 4 },
    { date: '07/13', masons: 3, carpenters: 1, laborers: 3 },
  ],
}: ResourceHistogramProps) {
  // Custom tool-tip with glass styles
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const total = payload.reduce((sum: number, entry: any) => sum + entry.value, 0);
      const limitExceeded = total > capacityLimit;
      
      return (
        <div className="bg-surface/90 border border-white/5 backdrop-blur-md p-3.5 rounded-xl shadow-xl text-xs space-y-2 text-left">
          <p className="font-bold text-white uppercase tracking-wider">{label}</p>
          <div className="flex flex-col space-y-1">
            <span className="text-primary font-medium">Masons: <strong className="text-white">{payload[0].value} heads</strong></span>
            <span className="text-secondary font-medium">Carpenters: <strong className="text-white">{payload[1].value} heads</strong></span>
            <span className="text-accent font-medium">General Laborers: <strong className="text-white">{payload[2].value} heads</strong></span>
            <div className="h-px bg-white/5 my-1" />
            <span className={limitExceeded ? 'text-danger font-bold' : 'text-emerald-400 font-bold'}>
              Total Crew: {total} heads {limitExceeded && '(Over-allocated!)'}
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="w-full border-white/5">
      <CardHeader className="pb-3 text-left">
        <CardTitle className="text-base font-bold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="h-[280px] w-full text-xs font-medium">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="#666" 
                tickLine={false} 
                axisLine={false}
                dy={10}
              />
              <YAxis 
                stroke="#666" 
                tickLine={false} 
                axisLine={false}
                dx={-5}
                label={{ value: 'Headcount (Heads)', angle: -90, position: 'insideLeft', offset: 0, fill: '#666' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="rect" 
                iconSize={8}
                wrapperStyle={{ paddingTop: 20 }}
              />
              <ReferenceLine 
                y={capacityLimit} 
                stroke="var(--danger)" 
                strokeDasharray="4 4" 
                label={{ value: `Max Crew Limit (${capacityLimit} heads)`, position: 'top', fill: 'var(--danger)', fontSize: 10, fontWeight: 'bold' }} 
              />
              <Bar name="Masons" dataKey="masons" stackId="a" fill="var(--primary)" radius={[0, 0, 0, 0]} />
              <Bar name="Carpenters" dataKey="carpenters" stackId="a" fill="var(--secondary)" radius={[0, 0, 0, 0]} />
              <Bar name="Laborers" dataKey="laborers" stackId="a" fill="var(--accent)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
export default ResourceHistogram;
