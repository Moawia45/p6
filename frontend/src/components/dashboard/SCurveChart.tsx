/**
 * ConstructMind AI - S-Curve Recharts Component
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../shared/Card';

interface DataPoint {
  date: string;
  planned: number;
  actual?: number;
}

interface SCurveChartProps {
  data?: DataPoint[];
  title?: string;
}

export function SCurveChart({
  title = 'Planned vs Actual S-Curve',
  data = [
    { date: 'Jun 01', planned: 0, actual: 0 },
    { date: 'Jun 15', planned: 8, actual: 9 },
    { date: 'Jul 01', planned: 18, actual: 16 },
    { date: 'Jul 15', planned: 28, actual: 27 },
    { date: 'Aug 01', planned: 42, actual: 36 },
    { date: 'Aug 15', planned: 58, actual: 52 },
    { date: 'Sep 01', planned: 72 },
    { date: 'Sep 15', planned: 85 },
    { date: 'Oct 01', planned: 96 },
    { date: 'Oct 13', planned: 100 },
  ],
}: SCurveChartProps) {
  // Custom tool-tip with glass styles
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface/90 border border-white/5 backdrop-blur-md p-3.5 rounded-xl shadow-xl text-xs space-y-1.5 text-left">
          <p className="font-bold text-white uppercase tracking-wider">{label}</p>
          <div className="flex flex-col space-y-1">
            <span className="text-primary font-medium">
              Planned Progress: <strong className="text-white">{payload[0].value}%</strong>
            </span>
            {payload[1] && (
              <span className="text-accent font-medium">
                Actual Progress: <strong className="text-white">{payload[1].value}%</strong>
              </span>
            )}
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
            <AreaChart
              data={data}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorPlanned" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="var(--accent)" stopOpacity={0}/>
                </linearGradient>
              </defs>
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
                tickFormatter={(value) => `${value}%`}
                dx={-5}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="circle" 
                iconSize={8}
                wrapperStyle={{ paddingTop: 20 }}
              />
              <Area
                name="Planned Progress (Cumulative %)"
                type="monotone"
                dataKey="planned"
                stroke="var(--primary)"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#colorPlanned)"
                activeDot={{ r: 6 }}
              />
              <Area
                name="Actual Progress (Cumulative %)"
                type="monotone"
                dataKey="actual"
                stroke="var(--accent)"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#colorActual)"
                activeDot={{ r: 6 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
export default SCurveChart;
