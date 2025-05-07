'use client';

import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const resSolar = await fetch('/api/forecast?model=solar&features=...');
        const solar = await resSolar.json();
        const resWind = await fetch('/api/forecast?model=wind&features=...');
        const wind = await resWind.json();
        setData({ solar, wind });
      } catch (err) {
        setError('Failed to fetch forecast data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-xl text-gray-600">Loading...</div>
    </div>
  );

  if (error) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-xl text-red-600">{error}</div>
    </div>
  );

  const chartData = {
    labels: ['Now'],
    datasets: [
      {
        label: 'Solar',
        data: [data.solar.prediction],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Wind',
        data: [data.wind.prediction],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Energy Production Forecast',
      },
    },
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Microgrid Dashboard</h1>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}