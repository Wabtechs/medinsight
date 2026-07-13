'use client'

import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, UserRound, Calendar, Phone, MapPin, Mail, Heart, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table'
import { mockPatients, mockFacilities, mockClinicalCases, mockUsers } from '@/lib/mock-data'
import { cn, formatDate } from '@/lib/utils'
import type { CaseStatus, CasePriority } from '@/types'

const bloodTypeColors: Record<string, string> = {
  'A+': 'bg-red-100 text-red-800 border-red-200',
  'A-': 'bg-red-50 text-red-700 border-red-200',
  'B+': 'bg-blue-100 text-blue-800 border-blue-200',
  'B-': 'bg-blue-50 text-blue-700 border-blue-200',
  'AB+': 'bg-purple-100 text-purple-800 border-purple-200',
  'AB-': 'bg-purple-50 text-purple-700 border-purple-200',
  'O+': 'bg-green-100 text-green-800 border-green-200',
  'O-': 'bg-green-50 text-green-700 border-green-200',
}

const statusLabels: Record<CaseStatus, string> = {
  draft: 'Brouillon',
  active: 'Actif',
  in_review: 'En revue',
  resolved: 'Résolu',
  archived: 'Archivé',
}

const statusColors: Record<CaseStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-blue-100 text-blue-800',
  in_review: 'bg-yellow-100 text-yellow-800',
  resolved: 'bg-green-100 text-green-800',
  archived: 'bg-purple-100 text-purple-800',
}

const priorityLabels: Record<CasePriority, string> = {
  low: 'Faible',
  medium: 'Moyen',
  high: 'Élevé',
  critical: 'Critique',
}

const priorityColors: Record<CasePriority, string> = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
}

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()

  const patient = mockPatients.find((p) => p.id === id)

  if (!patient) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
          <UserRound className="h-8 w-8 text-muted-foreground" />
        </div>
        <h1 className="text-2xl font-bold">Patient non trouvé</h1>
        <p className="text-muted-foreground">
          Le patient demandé n'existe pas ou a été supprimé.
        </p>
        <Button asChild>
          <Link href="/patients">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour à la liste
          </Link>
        </Button>
      </div>
    )
  }

  const facility = mockFacilities.find((f) => f.id === patient.facilityId)
  const cases = mockClinicalCases.filter((c) => c.patientId === patient.id)
  const getDoctorName = (doctorId: string) =>
    mockUsers.find((u) => u.id === doctorId)?.name ?? '—'

  return (
    <div className="space-y-6">
      <Button variant="ghost" onClick={() => router.push('/patients')} className="w-fit">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour à la liste
      </Button>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <Avatar className="h-20 w-20">
          <AvatarImage src={patient.email ? `https://api.dicebear.com/7.x/avataaars/svg?seed=${patient.id}` : undefined} />
          <AvatarFallback className="text-2xl">
            {patient.firstName[0]}
            {patient.lastName[0]}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">
              {patient.firstName} {patient.lastName}
            </h1>
            <Badge
              variant={patient.isActive ? 'default' : 'secondary'}
              className={cn(
                patient.isActive
                  ? 'bg-green-100 text-green-800 hover:bg-green-100'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-100'
              )}
            >
              {patient.isActive ? 'Actif' : 'Inactif'}
            </Badge>
          </div>
          <p className="mt-1 font-mono text-sm text-muted-foreground">
            {patient.medicalRecordNumber}
          </p>
        </div>
      </div>

      <Separator />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations Personnelles</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Date de Naissance</p>
                  <p className="text-sm font-medium">{formatDate(patient.dateOfBirth)}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                  <UserRound className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Sexe</p>
                  <p className="text-sm font-medium">
                    {patient.gender === 'M' ? 'Masculin' : 'Féminin'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Groupe Sanguin</p>
                  <Badge
                    variant="outline"
                    className={cn('font-mono', bloodTypeColors[patient.bloodType])}
                  >
                    {patient.bloodType}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Téléphone</p>
                  <p className="text-sm font-medium">{patient.phone}</p>
                </div>
              </div>
              {patient.email && (
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Email</p>
                    <p className="text-sm font-medium">{patient.email}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3 sm:col-span-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Adresse</p>
                  <p className="text-sm font-medium">{patient.address}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Informations Médicales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="mb-2 text-xs font-medium text-muted-foreground">Allergies</p>
              <div className="flex flex-wrap gap-2">
                {patient.allergies.length > 0 ? (
                  patient.allergies.map((allergy) => (
                    <Badge key={allergy} variant="destructive" className="font-normal">
                      {allergy}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">Aucune allergie connue</p>
                )}
              </div>
            </div>
            <Separator />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs text-muted-foreground">Établissement</p>
                <p className="text-sm font-medium">{facility?.name ?? '—'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Dernière Visite</p>
                <p className="text-sm font-medium">
                  {patient.lastVisit ? formatDate(patient.lastVisit) : '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Date de Création</p>
                <p className="text-sm font-medium">{formatDate(patient.createdAt)}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">N° Dossier</p>
                <p className="font-mono text-sm font-medium">{patient.medicalRecordNumber}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <Tabs defaultValue="cases">
        <TabsList>
          <TabsTrigger value="cases" className="gap-2">
            <FileText className="h-4 w-4" />
            Cas Cliniques
            <Badge variant="secondary" className="ml-1 text-xs">
              {cases.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="history" className="gap-2">
            <Calendar className="h-4 w-4" />
            Historique
          </TabsTrigger>
        </TabsList>

        <TabsContent value="cases" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Titre</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Priorité</TableHead>
                    <TableHead className="hidden sm:table-cell">Date de Création</TableHead>
                    <TableHead className="hidden md:table-cell">Médecin Assigné</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {cases.length > 0 ? (
                    cases.map((c) => (
                      <TableRow
                        key={c.id}
                        className="cursor-pointer"
                        onClick={() => router.push(`/clinical-cases/${c.id}`)}
                      >
                        <TableCell className="font-medium">{c.title}</TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={cn('font-normal', statusColors[c.status])}
                          >
                            {statusLabels[c.status]}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={cn('font-normal', priorityColors[c.priority])}
                          >
                            {priorityLabels[c.priority]}
                          </Badge>
                        </TableCell>
                        <TableCell className="hidden text-sm text-muted-foreground sm:table-cell">
                          {formatDate(c.createdAt)}
                        </TableCell>
                        <TableCell className="hidden text-sm md:table-cell">
                          {getDoctorName(c.assignedDoctorId)}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                        Aucun cas clinique pour ce patient.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="mt-4">
          <Card>
            <CardContent className="space-y-4 py-6">
              {[
                {
                  date: '2026-07-10T09:00:00Z',
                  title: 'Consultation de routine',
                  description: 'Contrôle annuel, résultats dans les normes.',
                },
                {
                  date: '2026-04-15T14:30:00Z',
                  title: 'Renouvellement ordonnance',
                  description: 'Renouvellement du traitement chronique.',
                },
                {
                  date: '2025-12-20T11:00:00Z',
                  title: 'Bilan sanguin complet',
                  description: 'Bilan biologique annuel réalisé au laboratoire.',
                },
              ].map((entry, i) => (
                <div key={i} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="h-3 w-3 rounded-full bg-primary" />
                    {i < 2 && <div className="w-px flex-1 bg-border" />}
                  </div>
                  <div className="pb-4">
                    <p className="text-xs text-muted-foreground">{formatDate(entry.date)}</p>
                    <p className="text-sm font-medium">{entry.title}</p>
                    <p className="text-sm text-muted-foreground">{entry.description}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
