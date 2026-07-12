import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Calendar,
  User,
  Building2,
  Tag,
  Paperclip,
  MessageSquare,
  Clock,
  Edit,
  CheckCircle,
  AlertCircle,
  Stethoscope,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import {
  mockClinicalCases,
  mockPatients,
  mockFacilities,
  mockUsers,
} from '@/lib/mock-data'
import { formatDate, formatDateTime, getInitials } from '@/lib/utils'
import type { CaseStatus, CaseNote } from '@/types'

const statusLabels: Record<CaseStatus, string> = {
  draft: 'Brouillon',
  active: 'Actif',
  in_review: 'En Revu',
  resolved: 'Résolu',
  archived: 'Archivé',
}

const priorityLabels: Record<string, string> = {
  low: 'Faible',
  medium: 'Moyenne',
  high: 'Élevée',
  critical: 'Critique',
}

export default function ClinicalCaseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const clinicalCase = mockClinicalCases.find((c) => c.id === id)
  const [caseData, setCaseData] = useState(clinicalCase)
  const [noteContent, setNoteContent] = useState('')
  const [notes, setNotes] = useState<CaseNote[]>(clinicalCase?.notes ?? [])

  if (!caseData) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <AlertCircle className="mb-4 h-16 w-16 text-muted-foreground/40" />
        <h2 className="text-xl font-semibold text-foreground">
          Cas non trouvé
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Le cas clinique demandé n'existe pas ou a été supprimé.
        </p>
        <Button
          variant="outline"
          className="mt-6"
          onClick={() => navigate('/clinical-cases')}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour à la liste
        </Button>
      </div>
    )
  }

  const patient = mockPatients.find((p) => p.id === caseData.patientId)
  const doctor = mockUsers.find((u) => u.id === caseData.assignedDoctorId)
  const facility = mockFacilities.find((f) => f.id === caseData.facilityId)

  const handleAddNote = () => {
    if (!noteContent.trim()) return
    const newNote: CaseNote = {
      id: `note-${Date.now()}`,
      caseId: caseData.id,
      authorId: 'usr-001',
      author: mockUsers.find((u) => u.id === 'usr-001'),
      content: noteContent.trim(),
      createdAt: new Date().toISOString(),
    }
    setNotes((prev) => [newNote, ...prev])
    setNoteContent('')
  }

  const handleStatusChange = (newStatus: CaseStatus) => {
    setCaseData((prev) =>
      prev
        ? {
            ...prev,
            status: newStatus,
            updatedAt: new Date().toISOString(),
            resolvedAt:
              newStatus === 'resolved'
                ? new Date().toISOString()
                : prev.resolvedAt,
          }
        : prev
    )
  }

  const getAuthorName = (authorId: string) => {
    const user = mockUsers.find((u) => u.id === authorId)
    return user ? user.name : 'Inconnu'
  }

  const getAuthorAvatar = (authorId: string) => {
    const user = mockUsers.find((u) => u.id === authorId)
    return user?.avatar ?? ''
  }

  const statusActions: { label: string; status: CaseStatus; icon: React.ReactNode }[] = []
  if (caseData.status === 'draft') {
    statusActions.push({
      label: 'Passer en Actif',
      status: 'active',
      icon: <Clock className="mr-2 h-4 w-4" />,
    })
  }
  if (caseData.status === 'active') {
    statusActions.push({
      label: 'Passer en Revu',
      status: 'in_review',
      icon: <Edit className="mr-2 h-4 w-4" />,
    })
  }
  if (caseData.status === 'in_review') {
    statusActions.push({
      label: 'Marquer Résolu',
      status: 'resolved',
      icon: <CheckCircle className="mr-2 h-4 w-4" />,
    })
    statusActions.push({
      label: 'Réactiver',
      status: 'active',
      icon: <Clock className="mr-2 h-4 w-4" />,
    })
  }
  if (caseData.status === 'resolved') {
    statusActions.push({
      label: 'Archiver',
      status: 'archived',
      icon: <AlertCircle className="mr-2 h-4 w-4" />,
    })
    statusActions.push({
      label: 'Réactiver',
      status: 'active',
      icon: <Clock className="mr-2 h-4 w-4" />,
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 shrink-0"
            onClick={() => navigate('/clinical-cases')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              {caseData.title}
            </h1>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              <Badge variant={caseData.status}>
                {statusLabels[caseData.status]}
              </Badge>
              <Badge variant={caseData.priority}>
                {priorityLabels[caseData.priority]}
              </Badge>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {statusActions.map((action) => (
            <Button
              key={action.status}
              variant="outline"
              size="sm"
              onClick={() => handleStatusChange(action.status)}
            >
              {action.icon}
              {action.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {caseData.description}
              </p>
            </CardContent>
          </Card>

          {caseData.symptoms.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Symptômes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {caseData.symptoms.map((symptom) => (
                    <Badge key={symptom} variant="outline">
                      {symptom}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Diagnostic</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {caseData.diagnosis}
              </p>
            </CardContent>
          </Card>

          {caseData.treatment && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Traitement</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {caseData.treatment}
                </p>
              </CardContent>
            </Card>
          )}

          <Separator />

          <Tabs defaultValue="notes">
            <TabsList>
              <TabsTrigger value="notes" className="gap-1.5">
                <MessageSquare className="h-3.5 w-3.5" />
                Notes ({notes.length})
              </TabsTrigger>
              <TabsTrigger value="history" className="gap-1.5">
                <Clock className="h-3.5 w-3.5" />
                Historique
              </TabsTrigger>
            </TabsList>

            <TabsContent value="notes" className="space-y-4">
              <div className="rounded-lg border bg-muted/30 p-4">
                <Textarea
                  placeholder="Ajouter une note..."
                  rows={3}
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                />
                <div className="mt-2 flex justify-end">
                  <Button
                    size="sm"
                    onClick={handleAddNote}
                    disabled={!noteContent.trim()}
                  >
                    <MessageSquare className="mr-2 h-3.5 w-3.5" />
                    Ajouter une note
                  </Button>
                </div>
              </div>

              {notes.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  Aucune note pour ce cas.
                </p>
              ) : (
                <div className="space-y-3">
                  {notes.map((note) => (
                    <div
                      key={note.id}
                      className="rounded-lg border p-4"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={getAuthorAvatar(note.authorId)} />
                          <AvatarFallback>
                            {getInitials(getAuthorName(note.authorId))}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-foreground">
                            {getAuthorName(note.authorId)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatDateTime(note.createdAt)}
                          </p>
                        </div>
                      </div>
                      <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                        {note.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="history">
              <div className="relative ml-3 border-l-2 border-muted py-2 pl-6">
                <div className="relative mb-6">
                  <div className="absolute -left-[31px] flex h-4 w-4 items-center justify-center rounded-full border-2 border-background bg-primary">
                    <div className="h-1.5 w-1.5 rounded-full bg-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      Cas créé
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatDateTime(caseData.createdAt)}
                    </p>
                  </div>
                </div>
                {caseData.updatedAt !== caseData.createdAt && (
                  <div className="relative mb-6">
                    <div className="absolute -left-[31px] flex h-4 w-4 items-center justify-center rounded-full border-2 border-background bg-blue-500">
                      <div className="h-1.5 w-1.5 rounded-full bg-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        Dernière mise à jour
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(caseData.updatedAt)}
                      </p>
                    </div>
                  </div>
                )}
                {caseData.resolvedAt && (
                  <div className="relative mb-6">
                    <div className="absolute -left-[31px] flex h-4 w-4 items-center justify-center rounded-full border-2 border-background bg-green-500">
                      <div className="h-1.5 w-1.5 rounded-full bg-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        Cas résolu
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(caseData.resolvedAt)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Informations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <User className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Patient</p>
                  {patient ? (
                    <Link
                      to={`/patients/${patient.id}`}
                      className="text-sm font-medium text-foreground hover:underline"
                    >
                      {patient.firstName} {patient.lastName}
                    </Link>
                  ) : (
                    <p className="text-sm text-muted-foreground">Inconnu</p>
                  )}
                </div>
              </div>

              <Separator />

              <div className="flex items-start gap-3">
                <Stethoscope className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">
                    Médecin assigné
                  </p>
                  {doctor && (
                    <div className="mt-1 flex items-center gap-2">
                      <Avatar className="h-6 w-6">
                        <AvatarImage src={doctor.avatar} />
                        <AvatarFallback>
                          {getInitials(doctor.name)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-sm font-medium text-foreground">
                        {doctor.name}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <Separator />

              <div className="flex items-start gap-3">
                <Building2 className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">
                    Établissement
                  </p>
                  <p className="text-sm font-medium text-foreground">
                    {facility?.name ?? 'Inconnu'}
                  </p>
                </div>
              </div>

              <Separator />

              <div className="flex items-start gap-3">
                <Calendar className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Créé le</p>
                  <p className="text-sm text-foreground">
                    {formatDate(caseData.createdAt)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Clock className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">
                    Mis à jour le
                  </p>
                  <p className="text-sm text-foreground">
                    {formatDate(caseData.updatedAt)}
                  </p>
                </div>
              </div>

              {caseData.resolvedAt && (
                <div className="flex items-start gap-3">
                  <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                  <div>
                    <p className="text-xs text-muted-foreground">
                      Résolu le
                    </p>
                    <p className="text-sm text-foreground">
                      {formatDate(caseData.resolvedAt)}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {caseData.tags.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Tags</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {caseData.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      <Tag className="mr-1 h-3 w-3" />
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Pièces jointes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Paperclip className="h-4 w-4" />
                <span>
                  {caseData.attachments.length} pièce
                  {caseData.attachments.length !== 1 ? 's' : ''} jointe
                  {caseData.attachments.length !== 1 ? 's' : ''}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
