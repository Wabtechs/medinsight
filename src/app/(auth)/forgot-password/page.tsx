'use client'

import { Providers } from '@/app/providers'
import ForgotPassword from '@/views/auth/forgot-password'

export default function ForgotPasswordPage() {
  return (
    <Providers>
      <ForgotPassword />
    </Providers>
  )
}
