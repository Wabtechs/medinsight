'use client'

import dynamic from 'next/dynamic'
import { Providers } from '@/app/providers'

const Login = dynamic(() => import('@/views/auth/login'), { ssr: false })

export default function LoginPage() {
  return (
    <Providers>
      <Login />
    </Providers>
  )
}
