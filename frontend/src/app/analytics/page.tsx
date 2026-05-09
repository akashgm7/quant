"use client"

import React, { useState, useEffect } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownRight, 
  Target,
  BarChart,
  PieChart as PieChartIcon,
  Calendar
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/analytics`)
      .then(res => res.json())
      .then(json => setData(json))
  }, [])

  if (!data) return <div className="pl-64 p-8 text-slate-500">Loading Intelligence...</div>

  return (
    <div className="max-w-7xl mx-auto space-y-8 pl-64">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-500" />
            Performance Analytics
          </h1>
          <p className="text-slate-400">Statistical analysis of the AI signal generation engine.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 text-slate-300 rounded-xl text-sm font-semibold hover:bg-slate-800 transition-colors">
          <Calendar className="w-4 h-4" />
          Last 30 Days
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Win Rate', value: `${data.summary.win_rate}%`, icon: Target, color: 'text-emerald-500' },
          { label: 'Profit Factor', value: data.summary.profit_factor, icon: TrendingUp, color: 'text-blue-500' },
          { label: 'Avg. RR', value: `1:${data.summary.avg_rr}`, icon: ArrowUpRight, color: 'text-amber-500' },
          { label: 'Net Profit', value: `$${data.summary.net_profit.toLocaleString()}`, icon: TrendingUp, color: 'text-emerald-400' },
        ].map((stat, i) => (
          <div key={i} className="glass-card p-6 rounded-2xl border border-slate-800/50">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <span className="text-sm font-medium text-slate-400">{stat.label}</span>
            </div>
            <h3 className="text-2xl font-bold text-white">{stat.value}</h3>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Equity Curve */}
        <div className="lg:col-span-2 glass-card p-8 rounded-3xl border border-slate-800/50 h-[400px]">
          <h3 className="text-xl font-bold text-white mb-8">Equity Growth Curve</h3>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.equity_curve}>
              <defs>
                <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="date" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Area 
                type="monotone" 
                dataKey="balance" 
                stroke="#3b82f6" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorBalance)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Pair Performance */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800/50">
          <h3 className="text-xl font-bold text-white mb-8">Performance by Asset</h3>
          <div className="space-y-6">
            {data.pair_performance.map((pair: any) => (
              <div key={pair.symbol} className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                  <span className="font-bold text-slate-200">{pair.symbol}</span>
                  <span className="text-emerald-500 font-bold">{pair.win_rate}% Win Rate</span>
                </div>
                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pair.win_rate}%` }}></div>
                </div>
                <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                  <span>{pair.trades} Trades</span>
                  <span>+${pair.profit.toLocaleString()} Profit</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
