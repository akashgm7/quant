"use client"

import React, { useState } from 'react'
import { 
  Play, 
  Settings, 
  History, 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Activity,
  ArrowRight
} from 'lucide-react'
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts'

export default function BacktestPage() {
  const [params, setParams] = useState({ symbol: 'BTC/USDT', timeframe: '15m', days: 30 })
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const runBacktest = async () => {
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/v1/backtest/run?symbol=${params.symbol}&timeframe=${params.timeframe}&days=${params.days}`)
      const json = await res.json()
      setResults(json)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8 pl-64">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <History className="w-8 h-8 text-blue-500" />
            Strategy Backtester
          </h1>
          <p className="text-slate-400">Validate confluence logic against historical market data.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Controls */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800/50 space-y-6">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <Settings className="w-4 h-4" /> Simulation Parameters
          </h3>
          
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400">Asset Pair</label>
              <select 
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white text-sm outline-none"
                value={params.symbol}
                onChange={(e) => setParams({...params, symbol: e.target.value})}
              >
                <option>BTC/USDT</option>
                <option>ETH/USDT</option>
                <option>SOL/USDT</option>
                <option>BNB/USDT</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400">Timeframe</label>
              <select 
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white text-sm outline-none"
                value={params.timeframe}
                onChange={(e) => setParams({...params, timeframe: e.target.value})}
              >
                <option value="15m">15 Minutes</option>
                <option value="1h">1 Hour</option>
                <option value="4h">4 Hours</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-400">Duration (Days)</label>
              <input 
                type="number" 
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white text-sm outline-none"
                value={params.days}
                onChange={(e) => setParams({...params, days: parseInt(e.target.value)})}
              />
            </div>

            <button 
              onClick={runBacktest}
              disabled={loading}
              className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-8">
          {results ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <div className="glass-card p-6 rounded-2xl border border-slate-800/50">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-2">Net Profit</p>
                    <h3 className={`text-2xl font-bold ${results.net_profit >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                      ${results.net_profit.toLocaleString()}
                    </h3>
                 </div>
                 <div className="glass-card p-6 rounded-2xl border border-slate-800/50">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-2">Win Rate</p>
                    <h3 className="text-2xl font-bold text-white">{results.win_rate}%</h3>
                 </div>
                 <div className="glass-card p-6 rounded-2xl border border-slate-800/50">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-2">Total Trades</p>
                    <h3 className="text-2xl font-bold text-white">{results.total_trades}</h3>
                 </div>
              </div>

              <div className="glass-card p-8 rounded-3xl border border-slate-800/50 h-[400px]">
                <h3 className="text-xl font-bold text-white mb-8">Simulation Equity Curve</h3>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={results.equity_curve}>
                    <defs>
                      <linearGradient id="colorBacktest" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis dataKey="timestamp" hide />
                    <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                      itemStyle={{ color: '#f8fafc' }}
                    />
                    <Area type="monotone" dataKey="balance" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorBacktest)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="glass-card p-6 rounded-2xl border border-slate-800/50 overflow-hidden">
                 <h3 className="text-lg font-bold text-white mb-6">Trade Log</h3>
                 <div className="space-y-4">
                    {results.trades.map((trade: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl border border-slate-800/50">
                        <div className="flex items-center gap-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${trade.outcome === 'WIN' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                            {trade.outcome}
                          </span>
                          <span className="text-sm font-bold text-slate-200">{trade.direction}</span>
                        </div>
                        <div className="flex items-center gap-8">
                           <span className="text-sm font-mono text-slate-400">${trade.entry.toLocaleString()}</span>
                           <span className={`text-sm font-bold ${trade.pnl >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                             {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toLocaleString()}
                           </span>
                        </div>
                      </div>
                    ))}
                 </div>
              </div>
            </>
          ) : (
            <div className="h-[600px] flex flex-col items-center justify-center text-center space-y-4 border-2 border-dashed border-slate-800 rounded-3xl">
               <History className="w-16 h-16 text-slate-700" />
               <div>
                 <h3 className="text-xl font-bold text-white">No Simulation Data</h3>
                 <p className="text-slate-500 max-w-xs mx-auto">Configure your parameters and run the backtester to see historical strategy performance.</p>
               </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
