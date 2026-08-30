import { Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Layout } from '@/components/Layout'
import LoginPage from '@/pages/LoginPage'
import EmployeeListPage from '@/pages/EmployeeListPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<EmployeeListPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
