'use client'

import { BoltIcon, SunIcon, Battery100Icon, ChartBarIcon, ClockIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'
import { fetchMicrogridState } from '@/services/dataService'
import { hourlyTimer } from '@/utils/hourlyTimer'

interface StatusData {
  title: string;
  value: string;
  icon: any;
  trend: string;
  trendColor: string;
}

export default function StatusCards() {
  const [statusData, setStatusData] = useState<StatusData[]>([]);
  const [nextUpdate, setNextUpdate] = useState<string>('');

  useEffect(() => {
    const fetchAndUpdateData = async () => {
      try {
        const data = await fetchMicrogridState();
        const predictionTime = new Date(data.predictionPeriod);
        setNextUpdate(predictionTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        
        setStatusData([
          {
            title: 'Prediction Period',
            value: `Until ${nextUpdate}`,
            icon: ClockIcon,
            trend: 'Next Hour',
            trendColor: 'text-blue-500'
          },
          {
            title: 'Solar Generation',
            value: `${data.solarOutput.toFixed(1)} kW`,
            icon: SunIcon,
            trend: 'Predicted',
            trendColor: 'text-yellow-500'
          },
          {
            title: 'Battery Level',
            value: `${data.batteryCharge}%`,
            icon: Battery100Icon,
            trend: data.batteryCharge > 50 ? 'Charging' : 'Discharging',
            trendColor: data.batteryCharge > 50 ? 'text-green-500' : 'text-red-500'
          },
          {
            title: 'Grid Exchange',
            value: `${Math.abs(data.gridConnection).toFixed(1)} kW`,
            icon: ChartBarIcon,
            trend: data.gridConnection > 0 ? 'Import' : 'Export',
            trendColor: data.gridConnection > 0 ? 'text-yellow-500' : 'text-green-500'
          }
        ]);
      } catch (error) {
        console.error('Error fetching status data:', error);
      }
    };

    // Initial fetch
    fetchAndUpdateData();
    
    // Subscribe to hourly updates
    const unsubscribe = hourlyTimer.subscribe(fetchAndUpdateData);
    return unsubscribe;
  }, [nextUpdate]);

  if (statusData.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-6 w-24 bg-gray-200 rounded mb-4"></div>
            <div className="h-8 w-16 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statusData.map((item) => (
        <div
          key={item.title}
          className="bg-white rounded-lg shadow p-6"
        >
          <div className="flex items-center">
            <item.icon className="h-8 w-8 text-gray-400 mr-2" />
            <div>
              <p className="text-sm text-gray-500">{item.title}</p>
              <p className="text-2xl font-semibold text-gray-900">
                {item.value}
              </p>
              <p className={`text-sm ${item.trendColor}`}>
                {item.trend}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}