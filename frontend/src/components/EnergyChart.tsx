'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { time: '00:00', production: 1.2, consumption: 1.8 },
  { time: '03:00', production: 0.8, consumption: 1.5 },
  { time: '06:00', production: 1.5, consumption: 1.6 },
  { time: '09:00', production: 2.8, consumption: 2.0 },
  { time: '12:00', production: 3.5, consumption: 2.2 },
  { time: '15:00', production: 3.2, consumption: 2.4 },
  { time: '18:00', production: 1.8, consumption: 2.6 },
  { time: '21:00', production: 1.0, consumption: 2.0 },
]

export default function EnergyChart() {
  return (
    <div className="h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis label={{ value: 'MW', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="production"
            stackId="1"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.3}
            name="Production"
          />
          <Area
            type="monotone"
            dataKey="consumption"
            stackId="2"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.3}
            name="Consumption"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
} 