'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useEffect, useState } from 'react'
import { fetchEnergySources } from '@/services/dataService'

interface EnergyData {
  time: string;
  solar: number;
  wind: number;
  grid: number;
  battery: number;
}

export default function EnergyChart() {
  const [data, setData] = useState<EnergyData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const energyData = await fetchEnergySources();
        const formattedData = energyData.times.map((time, index) => ({
          time,
          solar: energyData.solar[index],
          wind: energyData.wind[index],
          grid: energyData.grid[index],
          battery: energyData.battery[index]
        }));
        setData(formattedData);
      } catch (error) {
        console.error('Error fetching energy data:', error);
      }
    };

    fetchData();
    // Set up polling every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (data.length === 0) {
    return <div className="h-[400px] flex items-center justify-center">Loading energy data...</div>;
  }

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
          <Legend />
          <Area
            type="monotone"
            dataKey="solar"
            stackId="1"
            stroke="#F59E0B"
            fill="#F59E0B"
            fillOpacity={0.3}
            name="Solar"
          />
          <Area
            type="monotone"
            dataKey="wind"
            stackId="1"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.3}
            name="Wind"
          />
          <Area
            type="monotone"
            dataKey="grid"
            stackId="1"
            stroke="#6B7280"
            fill="#6B7280"
            fillOpacity={0.3}
            name="Grid"
          />
          <Area
            type="monotone"
            dataKey="battery"
            stackId="1"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.3}
            name="Battery"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
} 