"use client"

import React, { useState, useEffect } from 'react'
import { 
  History, 
  CheckCircle2, 
  XCircle, 
  MessageSquare, 
  TrendingUp, 
  TrendingDown,
  ChevronDown
} from 'lucide-react'

export default function HistoryPage() {
  const [signals, setSignals] = useState<any[]>([])

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/signals`)
      .then(res => res.json())
      .then(data => setSignals(data))
  }, [])

  const updateOutcome = async (id: number, outcome: string) => {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/signals/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ outcome })
    })
    setSignals(signals.map(s => s.id === id ? { ...s, outcome } : s))
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8 pl-64">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <History className="w-8 h-8 text-purple-500" />
            Signal History
          </h1>
          <p className="text-slate-400">Review past setups, verify outcomes, and manage your trading journal.</p>
        </div>
      </div>

      <div className="glass-card rounded-2xl overflow-hidden border border-slate-800/50">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-900/80 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Date</th>
                <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Asset</th>
                <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Direction</th>
                <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Entry</th>
                <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Outcome</th>
                <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest text-right">Journal</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {signals.map((signal) => (
                <tr key={signal.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <span className="text-sm text-slate-400">
                      {new Date(signal.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold text-white">{signal.symbol}</td>
                  <td className="px-6 py-4">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      signal.direction === 'LONG' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'
                    }`}>
                      {signal.direction}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-slate-300">
                    ${signal.entry_price?.toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    {signal.outcome ? (
                      <div className={`flex items-center gap-2 font-bold text-xs ${
                        signal.outcome === 'WIN' ? 'text-emerald-500' : 'text-rose-500'
                      }`}>
                        {signal.outcome === 'WIN' ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                        {signal.outcome}
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => updateOutcome(signal.id, 'WIN')}
                          className="px-2 py-1 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded hover:bg-emerald-500 hover:text-white transition-all text-[10px] font-bold"
                        >
                          WIN
                        </button>
                        <button 
                          onClick={() => updateOutcome(signal.id, 'LOSS')}
                          className="px-2 py-1 bg-rose-500/10 text-rose-500 border border-rose-500/20 rounded hover:bg-rose-500 hover:text-white transition-all text-[10px] font-bold"
                        >
                          LOSS
                        </button>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-2 text-slate-500 hover:text-white transition-colors">
                      <MessageSquare className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
