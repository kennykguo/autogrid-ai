'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useEffect, useState } from 'react'
import { fetchMicrogridState } from '@/services/dataService'
import { hourlyTimer } from '@/utils/hourlyTimer'

interface EnergyData {
  time: string;
  solar: number;
  wind: number;
  grid: number;
  battery: number;
}

const MAX_BATTERY_CHARGE = 80; // Maximum battery charge to maintain battery health

export default function EnergyChart() {
  const [data, setData] = useState<EnergyData[]>([]);
  const [nextPrediction, setNextPrediction] = useState<string>('');

  useEffect(() => {
    const fetchAndUpdateData = async () => {
      try {
        const microgridState = await fetchMicrogridState();
        
        // Convert prediction time to readable format
        const predictionTime = new Date(microgridState.predictionPeriod);
        setNextPrediction(predictionTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        
        // Get current time
        const currentTime = new Date(microgridState.currentTimestamp);
        const currentHour = currentTime.getHours();

        const newData = Array.from({ length: 8 }, (_, i) => {
          const hour = (currentHour - 7 + i) < 0 ? 24 + (currentHour - 7 + i) : (currentHour - 7 + i);
          const timeStr = `${hour.toString().padStart(2, '0')}:00`;
          
          // Enhanced time-based factors
          const dayProgress = hour / 24;
          const solarFactor = Math.sin(Math.PI * (dayProgress - 0.2)) * 0.8 + 0.2;
          
          // Increased wind factor
          const isCurrentHour = i === 7;
          const windFactor = isCurrentHour 
            ? Math.cos(Math.PI * dayProgress) * 0.3 + 0.2 // Current hour: 20-50% of rated
            : Math.cos(Math.PI * dayProgress) * 0.25 + 0.15; // Past hours: 15-40% of rated
          
          // Adjust load factor to increase early morning demand
          const loadFactor = hour >= 9 && hour <= 17 ? 1 : 0.8; // Increased base load in non-peak hours
          
          // Base calculations
          const baseLoad = microgridState.houseConsumption * loadFactor;
          const solarGen = microgridState.solarOutput * Math.max(0, solarFactor);
          const windGen = microgridState.windOutput * windFactor; // Removed reduction factor
          
          // Calculate available renewable power
          const renewablePower = solarGen + windGen;
          
          // Enhanced battery logic
          let batteryContribution = 0;
          let gridContribution = 0;
          
          // Enhanced grid usage logic
          const isEarlyHour = i <= 2; // First three hours of the chart
          if (isEarlyHour) {
            // Increase grid reliance in early hours
            gridContribution = baseLoad * 0.7; // 70% from grid
            const remainingNeed = baseLoad - gridContribution;
            
            // Use renewables and battery for the rest
            if (renewablePower < remainingNeed) {
              batteryContribution = Math.min(2, remainingNeed - renewablePower);
            }
          } else if (hour >= 10 && hour <= 15) {
            // During peak solar:
            if (renewablePower > baseLoad) {
              // Charge battery more aggressively during surplus
              batteryContribution = -Math.min(
                5, // Increased max charging rate
                (renewablePower - baseLoad) * 0.6 // Increased charging ratio
              );
            } else {
              gridContribution = (baseLoad - renewablePower) * 0.3; // Only 30% from grid if needed
            }
          } else if (hour >= 17 || hour <= 7) {
            // Evening/night: Use battery more aggressively
            batteryContribution = Math.min(4, baseLoad * 0.6); // Increased discharge rate
            
            if (renewablePower + batteryContribution < baseLoad) {
              gridContribution = baseLoad - (renewablePower + batteryContribution);
            }
          } else {
            // Mixed strategy during other hours
            if (renewablePower < baseLoad) {
              batteryContribution = Math.min(3, (baseLoad - renewablePower) * 0.5);
              gridContribution = baseLoad - (renewablePower + batteryContribution);
            } else {
              batteryContribution = -Math.min(2, (renewablePower - baseLoad) * 0.3);
            }
          }

          // Current hour uses exact values, past hours get small variations
          const variation = i === 7 ? 1 : 0.9 + Math.random() * 0.2;
          
          return {
            time: timeStr,
            solar: Math.max(0, solarGen * variation),
            wind: Math.max(0, windGen * variation),
            grid: Math.max(0, gridContribution * variation),
            battery: batteryContribution * variation // Can be negative (charging) or positive (discharging)
          };
        });

        setData(newData);
      } catch (error) {
        console.error('Error fetching energy data:', error);
      }
    };

    // Initial fetch
    fetchAndUpdateData();
    
    // Subscribe to hourly updates
    const unsubscribe = hourlyTimer.subscribe(fetchAndUpdateData);
    return () => {
      unsubscribe();
    };
  }, []);

  if (data.length === 0) {
    return (
      <div className="h-[400px] flex items-center justify-center">
        <div className="animate-pulse text-gray-600">Loading energy data...</div>
      </div>
    );
  }

  return (
    <div className="h-[400px]">
      <div className="mb-2 text-sm text-gray-500">
        Next prediction at: {nextPrediction}
      </div>
      <ResponsiveContainer width="100%" height="90%">
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
          <YAxis label={{ value: 'kW', angle: -90, position: 'insideLeft' }} />
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
            dataKey="battery"
            stackId="1"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.3}
            name="Battery"
          />
          <Area
            type="monotone"
            dataKey="grid"
            stackId="1"
            stroke="#6B7280"
            fill="#6B7280"
            fillOpacity={0.4}
            name="Grid"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}