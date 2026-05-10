"use client"

import React, { useEffect, useRef } from 'react'
import { createChart, ColorType } from 'lightweight-charts'

interface SignalChartProps {
  symbol: string
  entry?: number
  sl?: number
  tp?: number
}

const SignalChart: React.FC<SignalChartProps> = ({ symbol, entry, sl, tp }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    const container = chartContainerRef.current;

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      width: container.clientWidth,
      height: 200,
      timeScale: {
        borderColor: '#1e293b',
      },
    })

    // Create the series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    })

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://quant-2.onrender.com/api/v1';

    // Fetch Data
    fetch(`${API_URL}/history/ohlcv?symbol=${symbol}`)
      .then(res => res.json())
      .then(data => {
        if (data && Array.isArray(data)) {
            candlestickSeries.setData(data)
            
            // Add Price Lines
            if (entry) {
              candlestickSeries.createPriceLine({
                price: entry,
                color: '#3b82f6',
                lineWidth: 2,
                lineStyle: 2,
                axisLabelVisible: true,
                title: 'ENTRY',
              })
            }
            if (sl) {
              candlestickSeries.createPriceLine({
                price: sl,
                color: '#ef4444',
                lineWidth: 2,
                lineStyle: 2,
                axisLabelVisible: true,
                title: 'SL',
              })
            }
            if (tp) {
              candlestickSeries.createPriceLine({
                price: tp,
                color: '#10b981',
                lineWidth: 2,
                lineStyle: 2,
                axisLabelVisible: true,
                title: 'TP',
              })
            }

            chart.timeScale().fitContent()
        }
      })
      .catch(err => console.error("Chart Data Error:", err))

    const handleResize = () => {
      chart.applyOptions({ width: container.clientWidth })
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [symbol, entry, sl, tp])

  return <div ref={chartContainerRef} className="w-full" />
}

export default SignalChart
