"use client"

import React, { useState, useEffect } from 'react'
import { 
  Search, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Activity,
  ArrowUpRight,
  Filter
} from 'lucide-react'

export default function ScannerPage() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scanner`)
        const json = await res.json()
        setData(json)
      } catch (err) {
        console.error("Error fetching scanner data:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Update every 30s
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="max-w-7xl mx-auto space-y-8 pl-64">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Search className="w-8 h-8 text-emerald-500" />
            Market Scanner
          </h1>
          <p className="text-slate-400">Real-time technical bias across all monitored pairs.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 text-slate-300 rounded-xl text-sm font-semibold hover:bg-slate-800 transition-colors">
            <Filter className="w-4 h-4" />
            Filter
          </button>
          <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-xl">
             <span className="text-xs font-bold text-emerald-500 uppercase">Live Updating</span>
          </div>
        </div>
      </div>

      <div className="glass-card rounded-2xl overflow-hidden border border-slate-800/50">
        <table className="w-full text-left">
          <thead className="bg-slate-900/80 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Asset</th>
              <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Current Price</th>
              <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Market Bias</th>
              <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">Volatility</th>
              <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest">RSI (14)</th>
              <th className="px-6 py-4 text-[10px] uppercase font-bold text-slate-500 tracking-widest text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {loading ? (
              [1, 2, 3, 4, 5].map(i => (
                <tr key={i} className="animate-pulse">
                  <td colSpan={6} className="px-6 py-4 bg-slate-900/20 h-16"></td>
                </tr>
              ))
            ) : (
              data.map((item) => (
                <tr key={item.symbol} className="hover:bg-slate-800/30 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center font-bold text-xs">
                        {item.symbol.split('/')[0][0]}
                      </div>
                      <span className="font-bold text-white">{item.symbol}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-slate-300">${item.price.toLocaleString()}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border uppercase tracking-wider ${
                      item.bias === 'BULLISH' 
                        ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' 
                        : item.bias === 'BEARISH'
                        ? 'bg-rose-500/10 text-rose-500 border-rose-500/20'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}>
                      {item.bias}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Activity className={`w-4 h-4 ${item.volatility === 'High' ? 'text-amber-500' : 'text-slate-500'}`} />
                      <span className="text-sm text-slate-300">{item.volatility}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${item.rsi > 70 ? 'bg-rose-500' : item.rsi < 30 ? 'bg-emerald-500' : 'bg-blue-500'}`} 
                          style={{ width: `${item.rsi}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-mono text-slate-400">{item.rsi}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-2 text-slate-500 hover:text-emerald-500 transition-colors">
                      <ArrowUpRight className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Heatmap Section Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="glass-card p-6 rounded-2xl border border-slate-800/50">
          <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Top Momentum Gainers
          </h3>
          <div className="space-y-4">
            {data.filter(i => i.rsi > 60).map(item => (
              <div key={item.symbol} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl border border-slate-800/50">
                 <span className="font-bold text-slate-200">{item.symbol}</span>
                 <span className="text-emerald-500 font-bold">+{Math.floor(Math.random() * 5)}%</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="glass-card p-6 rounded-2xl border border-slate-800/50 bg-gradient-to-br from-blue-500/5 to-purple-500/5">
          <h3 className="text-lg font-bold text-white mb-2">Institutional Volume Hub</h3>
          <p className="text-sm text-slate-400 mb-6">Total monitored volume: <span className="text-white font-bold">$1.2B</span></p>
          <div className="flex items-end gap-2 h-32">
             {[40, 70, 45, 90, 65, 80, 30].map((h, i) => (
               <div key={i} className="flex-1 bg-blue-500/20 rounded-t-lg relative group cursor-pointer hover:bg-blue-500/40 transition-colors">
                  <div className="absolute bottom-0 w-full bg-blue-500 rounded-t-lg transition-all" style={{ height: `${h}%` }}></div>
               </div>
             ))}
          </div>
        </div>
      </div>
    </div>
  )
}
