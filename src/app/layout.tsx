import type { Metadata } from 'next'
import '../index.css'

export const metadata: Metadata = {
  title: 'MedInsight - Gestion de Cas Cliniques',
  description: 'PWA de gestion de cas cliniques pour les hopitaux algeriens',
  manifest: '/manifest.json',
  icons: { icon: '/favicon.ico' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}
