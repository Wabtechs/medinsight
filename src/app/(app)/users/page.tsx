'use client'

import dynamic from 'next/dynamic'

const Users = dynamic(() => import('@/views/users'), { ssr: false })

export default function UsersPage() {
  return <Users />
}
