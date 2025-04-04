'use client'

import { ArrowPathIcon, BoltIcon, SunIcon, Battery100Icon } from '@heroicons/react/24/outline'

export default function PowerFlow() {
  return (
    <div className="relative h-[300px]">
      {/* Grid Connection */}
      <div className="absolute top-0 left-1/2 transform -translate-x-1/2">
        <div className="bg-gray-200 p-4 rounded-lg flex items-center">
          <BoltIcon className="h-6 w-6 text-gray-600 mr-2" />
          <span className="font-medium">Grid</span>
        </div>
      </div>

      {/* Solar Panels */}
      <div className="absolute top-1/4 left-1/4">
        <div className="bg-yellow-100 p-4 rounded-lg flex items-center">
          <SunIcon className="h-6 w-6 text-yellow-600 mr-2" />
          <span className="font-medium">Solar</span>
        </div>
      </div>

      {/* Battery Storage */}
      <div className="absolute top-1/4 right-1/4">
        <div className="bg-blue-100 p-4 rounded-lg flex items-center">
          <Battery100Icon className="h-6 w-6 text-blue-600 mr-2" />
          <span className="font-medium">Battery</span>
        </div>
      </div>

      {/* Load Center */}
      <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
        <div className="bg-gray-200 p-4 rounded-lg flex items-center">
          <ArrowPathIcon className="h-6 w-6 text-gray-600 mr-2" />
          <span className="font-medium">Load</span>
        </div>
      </div>

      {/* Power Flow Lines */}
      <svg className="absolute inset-0 w-full h-full" style={{ pointerEvents: 'none' }}>
        {/* Grid to Load */}
        <line
          x1="50%"
          y1="60"
          x2="50%"
          y2="240"
          stroke="#6B7280"
          strokeWidth="2"
          strokeDasharray="5,5"
        />
        
        {/* Solar to Load */}
        <line
          x1="25%"
          y1="120"
          x2="50%"
          y2="240"
          stroke="#F59E0B"
          strokeWidth="2"
        />
        
        {/* Battery to Load */}
        <line
          x1="75%"
          y1="120"
          x2="50%"
          y2="240"
          stroke="#3B82F6"
          strokeWidth="2"
        />
      </svg>
    </div>
  )
} 