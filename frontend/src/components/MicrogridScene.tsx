'use client'

import dynamic from 'next/dynamic'
import { Suspense } from 'react'

// Dynamically import Three.js components to avoid SSR issues
const Scene = dynamic(() => import('./Scene'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] flex items-center justify-center bg-gray-100">
      Loading 3D Scene...
    </div>
  ),
})

export default function MicrogridScene() {
  return (
    <div className="w-full h-[400px]">
      <Scene />
    </div>
  )
} 