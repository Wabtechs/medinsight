'use client'

import { Providers } from '@/app/providers'
import Login from '@/views/auth/login'

export default function LoginPage() {
  return (
    <Providers>
      <Login />
    </Providers>
  )
}
