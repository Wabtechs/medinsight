import { Providers } from './providers'
import { AppRouter } from '@/routes'
import { Toaster } from '@/components/ui/toaster'

export default function App() {
  return (
    <Providers>
      <AppRouter />
      <Toaster />
    </Providers>
  )
}
