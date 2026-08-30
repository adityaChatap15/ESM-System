import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-slate-900">
            Employee Salary Management
          </h1>
          <Button onClick={logout} className="bg-slate-200 text-slate-900 hover:bg-slate-300">
            Log out
          </Button>
        </div>
        <p className="text-slate-600">
          You're logged in as HR Manager. Employee list and analytics are coming in the next phases.
        </p>
      </div>
    </div>
  )
}
