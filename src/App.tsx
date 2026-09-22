import { Navigate, Route, Routes } from 'react-router'
import { StandingsPage } from '@/routes/StandingsPage'
import { AdminPage } from '@/routes/AdminPage'
import { LoginPage } from '@/routes/LoginPage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/men" replace />} />
      <Route path="/:gender" element={<StandingsPage />} />
      <Route path="/admin" element={<LoginPage />} />
      <Route path="/admin/:gender" element={<AdminPage />} />
      <Route path="*" element={<Navigate to="/men" replace />} />
    </Routes>
  )
}
