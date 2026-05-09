"use client"

import React, { useState, useEffect } from 'react'
import { 
  ShieldCheck, 
  Wallet, 
  Percent, 
  AlertTriangle, 
  Save,
  Info
} from 'lucide-react'

export default function RiskPage() {
  const [settings, setSettings] = useState({
    account_balance: 10000.0,
    risk_per_trade_percent: 1.0,
    max_open_trades: 3,
    max_daily_drawdown_percent: 5.0,
    trailing_stop_activation_percent: 2.0
  })

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/risk')
      .then(res => res.json())
      .then(json => setSettings(json))
  }, [])

  const handleSave = async () => {
    const res = await fetch('http://localhost:8000/api/v1/risk/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    })
    if (res.ok) {
      alert("Settings saved successfully!")
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pl-64">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-amber-500" />
            Risk Management
          </h1>
          <p className="text-slate-400">Configure institutional-grade capital protection rules.</p>
        </div>
        <button 
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/20"
        >
          <Save className="w-4 h-4" />
          Save Settings
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Capital Settings */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800/50 space-y-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
            <Wallet className="w-5 h-5 text-blue-500" />
            Capital Allocation
          </h3>
          
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-400">Trading Account Balance ($)</label>
            <input 
              type="number" 
              value={settings.account_balance}
              onChange={(e) => setSettings({...settings, account_balance: parseFloat(e.target.value)})}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-400">Risk Per Trade (%)</label>
            <div className="relative">
              <input 
                type="number" 
                value={settings.risk_per_trade_percent}
                onChange={(e) => setSettings({...settings, risk_per_trade_percent: parseFloat(e.target.value)})}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500 transition-colors"
              />
              <Percent className="absolute right-4 top-3.5 w-4 h-4 text-slate-600" />
            </div>
            <p className="text-[10px] text-slate-500 italic">Recommended: 0.5% - 2.0% for institutional safety.</p>
          </div>
        </div>

        {/* Protection Rules */}
        <div className="glass-card p-8 rounded-3xl border border-slate-800/50 space-y-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
            <AlertTriangle className="w-5 h-5 text-rose-500" />
            Drawdown Protection
          </h3>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-400">Max Daily Drawdown (%)</label>
            <input 
              type="number" 
              value={settings.max_daily_drawdown_percent}
              onChange={(e) => setSettings({...settings, max_daily_drawdown_percent: parseFloat(e.target.value)})}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-rose-500 transition-colors"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-400">Max Concurrent Trades</label>
            <input 
              type="number" 
              value={settings.max_open_trades}
              onChange={(e) => setSettings({...settings, max_open_trades: parseInt(e.target.value)})}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-rose-500 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Advanced Info */}
      <div className="p-6 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex gap-4">
        <div className="p-2 bg-blue-500/20 rounded-lg h-fit">
          <Info className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <h4 className="text-sm font-bold text-blue-400 mb-1">Dynamic Risk Engine Active</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            These settings directly influence the Signal Engine's confidence scoring and position sizing logic. 
            If a setup exceeds your Max Daily Drawdown or Max Concurrent Trades, the engine will automatically 
            suppress lower-confidence signals to protect your capital.
          </p>
        </div>
      </div>
    </div>
  )
}
