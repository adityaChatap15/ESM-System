import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'

function navLinkClass({ isActive }) {
  return `rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'
  }`
}

export function Layout() {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold text-slate-900">Employee Salary Management</h1>
          <nav className="flex items-center gap-2">
            <NavLink to="/" end className={navLinkClass}>
              Employees
            </NavLink>
            <NavLink to="/analytics" className={navLinkClass}>
              Analytics
            </NavLink>
            <Button onClick={logout} className="bg-slate-200 text-slate-900 hover:bg-slate-300">
              Log out
            </Button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
