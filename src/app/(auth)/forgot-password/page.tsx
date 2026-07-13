'use client'

import dynamic from 'next/dynamic'
import { Providers } from '@/app/providers'

const ForgotPassword = dynamic(() => import('@/views/auth/forgot-password'), { ssr: false })

export default function ForgotPasswordPage() {
  return (
    <Providers>
      <ForgotPassword />
    </Providers>
  )
}
