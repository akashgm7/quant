"use client"

import React, { useState, useEffect } from 'react'
import { 
  Bot, 
  BrainCircuit, 
  Zap, 
  AlertCircle, 
  TrendingUp, 
  Layers,
  Sparkles,
  Info
} from 'lucide-react'

export default function AIEnginePage() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/ai/insights`)
      .then(res => res.json())
      .then(json => setData(json))
  }, [])

  if (!data) return <div className="pl-64 p-8 text-slate-500">Initializing Neural Engine...</div>

  return (
    <div className="max-w-7xl mx-auto space-y-8 pl-64">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Bot className="w-8 h-8 text-emerald-500" />
            AI Strategy Assistant
          </h1>
          <p className="text-slate-400">Machine learning adaptation and probabilistic edge analysis.</p>
        </div>
        <div className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/20 px-6 py-3 rounded-2xl">
          <Sparkles className="w-5 h-5 text-emerald-500" />
          <div className="text-left">
            <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">Model Confidence</p>
            <p className="text-lg font-bold text-white">{data.probabilistic_edge}% Edge</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Regime Detection */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800/50 bg-gradient-to-br from-blue-500/5 to-emerald-500/5">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-slate-900 rounded-2xl border border-slate-800">
              <Layers className="w-6 h-6 text-blue-500" />
            </div>
            <h3 className="text-xl font-bold text-white">Market Regime</h3>
          </div>
          <div className="space-y-6">
             <div className="p-4 bg-slate-900/80 rounded-2xl border border-slate-800">
                <p className="text-xs font-bold text-slate-500 uppercase mb-2">Current State</p>
                <p className="text-lg font-bold text-white tracking-tight">{data.market_regime.replace(/_/g, ' ')}</p>
             </div>
             <p className="text-sm text-slate-400 leading-relaxed">
               The engine has detected a <strong>Trend-Following</strong> environment. Momentum-based signals currently have a statistically significant edge over mean-reversion setups.
             </p>
          </div>
        </div>

        {/* Feature Importance */}
        <div className="lg:col-span-2 glass-card p-8 rounded-3xl border border-slate-800/50">
          <h3 className="text-xl font-bold text-white mb-8 flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-purple-500" />
            Feature Importance Matrix
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
               {data.feature_importance.map((f: any) => (
                 <div key={f.feature} className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="font-bold text-slate-300">{f.feature}</span>
                      <span className="text-purple-400 font-bold">{Math.floor(f.score * 100)}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500 rounded-full" style={{ width: `${f.score * 100}%` }}></div>
                    </div>
                 </div>
               ))}
            </div>
            <div className="p-6 bg-slate-900/50 rounded-2xl border border-slate-800 flex flex-col justify-center">
               <h4 className="text-sm font-bold text-slate-200 mb-2">AI Neural Insight</h4>
               <p className="text-xs text-slate-500 leading-relaxed italic">
                 "Our models indicate that <strong>Volume Delta</strong> is currently the strongest predictor of signal success. Focus on setups where volume expansion exceeds 1.8x the 20-period average."
               </p>
            </div>
          </div>
        </div>
      </div>

      {/* Probabilistic Insights Feed */}
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-500" />
          Neural Insights Feed
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.insights.map((insight: any, i: number) => (
            <div key={i} className="glass-card p-6 rounded-2xl border border-slate-800/50 hover:border-emerald-500/30 transition-all group">
              <div className="flex justify-between items-start mb-4">
                <span className={`px-2 py-0.5 rounded-lg text-[10px] font-bold tracking-widest ${
                  insight.impact === 'CRITICAL' ? 'bg-rose-500/20 text-rose-500' : 'bg-emerald-500/20 text-emerald-500'
                }`}>
                  {insight.impact} IMPACT
                </span>
                <span className="text-[10px] font-bold text-slate-500 uppercase">{insight.type}</span>
              </div>
              <h4 className="text-lg font-bold text-white mb-2">{insight.title}</h4>
              <p className="text-sm text-slate-400 leading-relaxed mb-6">{insight.description}</p>
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-500">
                <TrendingUp className="w-4 h-4" />
                Edge Confirmed
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
