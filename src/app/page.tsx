'use client'

import dynamic from 'next/dynamic'
import { Providers } from './providers'

const Landing = dynamic(() => import('@/views/landing'), { ssr: false })

export default function LandingPage() {
  return (
    <Providers>
      <Landing />
    </Providers>
  )
}
