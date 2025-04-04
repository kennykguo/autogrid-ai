'use client'

import { BoltIcon, SunIcon, Battery100Icon, ChartBarIcon } from '@heroicons/react/24/outline'

const statusCards = [
  {
    title: 'Current Power',
    value: '2.4 MW',
    icon: BoltIcon,
    trend: '+12%',
    trendColor: 'text-green-500'
  },
  {
    title: 'Solar Generation',
    value: '1.2 MW',
    icon: SunIcon,
    trend: '+8%',
    trendColor: 'text-green-500'
  },
  {
    title: 'Battery Level',
    value: '78%',
    icon: Battery100Icon,
    trend: '-5%',
    trendColor: 'text-red-500'
  },
  {
    title: 'Grid Import',
    value: '0.8 MW',
    icon: ChartBarIcon,
    trend: '-15%',
    trendColor: 'text-green-500'
  }
]

export default function StatusCards() {
  return (
    <>
      {statusCards.map((card) => (
        <div key={card.title} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{card.title}</p>
              <p className="text-2xl font-semibold text-gray-900">{card.value}</p>
            </div>
            <div className="flex items-center">
              <card.icon className="h-8 w-8 text-gray-400 mr-2" />
              <span className={`text-sm font-medium ${card.trendColor}`}>
                {card.trend}
              </span>
            </div>
          </div>
        </div>
      ))}
    </>
  )
} 