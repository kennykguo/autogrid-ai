'use client'

import { CloudIcon, SunIcon, BoltIcon } from '@heroicons/react/24/outline'

const forecastData = [
  {
    day: 'Today',
    icon: SunIcon,
    temp: '24°C',
    condition: 'Sunny',
    wind: '12 km/h'
  },
  {
    day: 'Tomorrow',
    icon: CloudIcon,
    temp: '22°C',
    condition: 'Partly Cloudy',
    wind: '15 km/h'
  },
  {
    day: 'Day 3',
    icon: BoltIcon,
    temp: '20°C',
    condition: 'Thunderstorms',
    wind: '20 km/h'
  }
]

export default function WeatherForecast() {
  return (
    <div className="space-y-4">
      {forecastData.map((day) => (
        <div key={day.day} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <day.icon className="h-8 w-8 text-gray-600 mr-4" />
            <div>
              <p className="font-medium text-gray-900">{day.day}</p>
              <p className="text-sm text-gray-500">{day.condition}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="font-medium text-gray-900">{day.temp}</p>
            <p className="text-sm text-gray-500">Wind: {day.wind}</p>
          </div>
        </div>
      ))}
    </div>
  )
} 