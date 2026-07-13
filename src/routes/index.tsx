import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { useAuthStore } from '@/store/auth-store'
import { Layout } from '@/components/layout/layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

const Landing = lazy(() => import('@/views/landing'))
const Login = lazy(() => import('@/views/auth/login'))
const ForgotPassword = lazy(() => import('@/views/auth/forgot-password'))
const Dashboard = lazy(() => import('@/views/dashboard'))
const Facilities = lazy(() => import('@/views/facilities'))
const FacilityDetail = lazy(() => import('@/views/facility-detail'))
const Users = lazy(() => import('@/views/users'))
const Patients = lazy(() => import('@/views/patients'))
const PatientDetail = lazy(() => import('@/views/patient-detail'))
const ClinicalCases = lazy(() => import('@/views/clinical-cases'))
const ClinicalCaseDetail = lazy(() => import('@/views/clinical-case-detail'))
const TreatmentHistory = lazy(() => import('@/views/treatment-history'))
const SyncCenter = lazy(() => import('@/views/sync-center'))
const Analytics = lazy(() => import('@/views/analytics'))
const Research = lazy(() => import('@/views/research'))
const Settings = lazy(() => import('@/views/settings'))
const Profile = lazy(() => import('@/views/profile'))
const AuditLog = lazy(() => import('@/views/audit-log'))
const Notifications = lazy(() => import('@/views/notifications'))

function PageLoader() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route
          path="/"
          element={
            <SuspenseWrapper>
              <Landing />
            </SuspenseWrapper>
          }
        />
        <Route
          path="/login"
          element={
            <SuspenseWrapper>
              <Login />
            </SuspenseWrapper>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <SuspenseWrapper>
              <ForgotPassword />
            </SuspenseWrapper>
          }
        />

        {/* Protected app routes */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<SuspenseWrapper><Dashboard /></SuspenseWrapper>} />
          <Route path="facilities" element={<SuspenseWrapper><Facilities /></SuspenseWrapper>} />
          <Route path="facilities/:id" element={<SuspenseWrapper><FacilityDetail /></SuspenseWrapper>} />
          <Route path="users" element={<SuspenseWrapper><Users /></SuspenseWrapper>} />
          <Route path="patients" element={<SuspenseWrapper><Patients /></SuspenseWrapper>} />
          <Route path="patients/:id" element={<SuspenseWrapper><PatientDetail /></SuspenseWrapper>} />
          <Route path="clinical-cases" element={<SuspenseWrapper><ClinicalCases /></SuspenseWrapper>} />
          <Route path="clinical-cases/:id" element={<SuspenseWrapper><ClinicalCaseDetail /></SuspenseWrapper>} />
          <Route path="treatment-history" element={<SuspenseWrapper><TreatmentHistory /></SuspenseWrapper>} />
          <Route path="sync" element={<SuspenseWrapper><SyncCenter /></SuspenseWrapper>} />
          <Route path="analytics" element={<SuspenseWrapper><Analytics /></SuspenseWrapper>} />
          <Route path="research" element={<SuspenseWrapper><Research /></SuspenseWrapper>} />
          <Route path="settings" element={<SuspenseWrapper><Settings /></SuspenseWrapper>} />
          <Route path="profile" element={<SuspenseWrapper><Profile /></SuspenseWrapper>} />
          <Route path="audit" element={<SuspenseWrapper><AuditLog /></SuspenseWrapper>} />
          <Route path="notifications" element={<SuspenseWrapper><Notifications /></SuspenseWrapper>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
