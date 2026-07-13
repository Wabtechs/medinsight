import { useState } from 'react'
import { Activity, CheckCircle, Clock } from 'lucide-react'
import {
  Card,
  CardContent,
} from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { RechartsChart } from '@/components/charts/recharts-chart'
import { mockChartData } from '@/lib/mock-data'
import { formatNumber } from '@/lib/utils'

const PERIODS = [
  { value: 'week', label: 'Cette Semaine' },
  { value: 'month', label: 'Ce Mois' },
  { value: 'quarter', label: 'Ce Trimestre' },
  { value: 'year', label: 'Cette Année' },
]

const statCards = [
  {
    title: 'Total Traitements',
    value: 247,
    icon: Activity,
    color: 'text-primary',
    bg: 'bg-primary/10',
  },
  {
    title: 'Taux de Succès',
    value: '78%',
    icon: CheckCircle,
    color: 'text-emerald-600',
    bg: 'bg-emerald-100',
  },
  {
    title: 'Cas en Cours',
    value: 42,
    icon: Clock,
    color: 'text-amber-600',
    bg: 'bg-amber-100',
  },
]

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('month')

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Tableau de Bord Statistiques
          </h1>
          <p className="text-muted-foreground">
            Analyse détaillée des performances et indicateurs clés.
          </p>
        </div>
        <Select value={period} onValueChange={setPeriod}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Période" />
          </SelectTrigger>
          <SelectContent>
            {PERIODS.map((p) => (
              <SelectItem key={p.value} value={p.value}>
                {p.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card
              key={stat.title}
              className="transition-shadow hover:shadow-md"
            >
              <CardContent className="flex items-center gap-4 p-6">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${stat.bg}`}
                >
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold">
                    {typeof stat.value === 'number'
                      ? formatNumber(stat.value)
                      : stat.value}
                  </p>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RechartsChart
          type="bar"
          data={mockChartData.casesByFacility}
          dataKey="value"
          xAxisKey="name"
          title="Cas par Établissement"
          description="Nombre de cas cliniques par établissement"
          height={320}
        />
        <RechartsChart
          type="pie"
          data={mockChartData.treatmentOutcomes}
          dataKey="value"
          xAxisKey="name"
          title="Résultats des Traitements"
          description="Répartition des issues thérapeutiques"
          height={320}
        />
        <RechartsChart
          type="line"
          data={mockChartData.casesByMonth}
          dataKey="value"
          xAxisKey="name"
          title="Évolution Mensuelle"
          description="Tendance du nombre de cas au fil du temps"
          height={320}
          color="#1e84b5"
        />
        <RechartsChart
          type="bar"
          data={mockChartData.casesByStatus}
          dataKey="value"
          xAxisKey="name"
          title="Cas par Statut"
          description="Distribution des cas selon leur statut actuel"
          height={320}
          color="#10b981"
        />
      </div>
    </div>
  )
}
