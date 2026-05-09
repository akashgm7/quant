"use client"

import React from 'react'
import { Bell, User, Search, Terminal } from 'lucide-react'

const TopNav = () => {
  return (
    <div className="h-16 border-b border-[#1e293b] bg-[#0a0e14]/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-40 ml-64">
      <div className="flex items-center gap-4 bg-slate-900/50 px-4 py-2 rounded-full border border-slate-800 w-96">
        <Search className="w-4 h-4 text-slate-500" />
        <input 
          type="text" 
          placeholder="Search market, signals, or strategy..." 
          className="bg-transparent border-none outline-none text-sm text-slate-300 w-full placeholder:text-slate-600"
        />
        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded border border-slate-700 text-[10px] text-slate-500 font-mono">
          <Terminal className="w-3 h-3" />
          <span>/</span>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 rounded-full">
          <span className="w-2 h-2 rounded-full bg-amber-500"></span>
          <span className="text-xs font-bold text-amber-500 uppercase tracking-tight">System Monitor: Stable</span>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 text-slate-400 hover:text-slate-200 transition-colors relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-emerald-500 rounded-full border-2 border-[#0a0e14]"></span>
          </button>
          <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
            <div className="text-right">
              <p className="text-sm font-bold text-slate-200">Institutional Pro</p>
              <p className="text-[10px] text-slate-500 uppercase font-semibold">Tier 1 Access</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-900 border border-slate-600 flex items-center justify-center">
              <User className="w-6 h-6 text-slate-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopNav
