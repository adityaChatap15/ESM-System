import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useApi } from '@/lib/useApi'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

const EDITABLE_FIELDS = ['name', 'department', 'role', 'country', 'join_date']

export default function EmployeeDetailPage() {
  const { id } = useParams()
  const request = useApi()

  const [employee, setEmployee] = useState(null)
  const [history, setHistory] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const [isEditing, setIsEditing] = useState(false)
  const [form, setForm] = useState(null)
  const [isSaving, setIsSaving] = useState(false)
  const [editError, setEditError] = useState('')

  const [salaryForm, setSalaryForm] = useState({ amount: '', effective_date: '', reason: '' })
  const [isSubmittingSalary, setIsSubmittingSalary] = useState(false)
  const [salaryError, setSalaryError] = useState('')

  useEffect(() => {
    loadEmployee()
    loadHistory()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  async function loadEmployee() {
    setIsLoading(true)
    setLoadError('')
    try {
      const data = await request(`/api/v1/employees/${id}`)
      setEmployee(data)
      setForm({
        name: data.name,
        department: data.department,
        role: data.role,
        country: data.country,
        join_date: data.join_date,
      })
    } catch (err) {
      setLoadError(err.message || 'Failed to load employee')
    } finally {
      setIsLoading(false)
    }
  }

  async function loadHistory() {
    try {
      const data = await request(`/api/v1/employees/${id}/salary-history`)
      setHistory(data)
    } catch {
      // non-critical - the rest of the page still works without history
    }
  }

  async function handleSaveEdit(event) {
    event.preventDefault()
    setIsSaving(true)
    setEditError('')
    try {
      const updated = await request(`/api/v1/employees/${id}`, { method: 'PUT', body: form })
      setEmployee((current) => ({ ...current, ...updated }))
      setIsEditing(false)
    } catch (err) {
      setEditError(err.message || 'Failed to update employee')
    } finally {
      setIsSaving(false)
    }
  }

  async function handleDeactivate() {
    const confirmed = window.confirm(`Deactivate ${employee.name}? Their records are kept, just hidden from the active list.`)
    if (!confirmed) return

    try {
      const updated = await request(`/api/v1/employees/${id}`, { method: 'DELETE' })
      setEmployee((current) => ({ ...current, ...updated }))
    } catch (err) {
      setLoadError(err.message || 'Failed to deactivate employee')
    }
  }

  async function handleAddSalary(event) {
    event.preventDefault()
    setIsSubmittingSalary(true)
    setSalaryError('')
    try {
      await request(`/api/v1/employees/${id}/salary`, {
        method: 'POST',
        body: {
          amount: salaryForm.amount,
          effective_date: salaryForm.effective_date,
          reason: salaryForm.reason || null,
        },
      })
      setSalaryForm({ amount: '', effective_date: '', reason: '' })
      await loadEmployee()
      await loadHistory()
    } catch (err) {
      setSalaryError(err.message || 'Failed to add salary record')
    } finally {
      setIsSubmittingSalary(false)
    }
  }

  if (isLoading) {
    return <p className="text-slate-500">Loading...</p>
  }

  if (loadError && !employee) {
    return (
      <div>
        <p className="mb-4 text-sm text-red-600">{loadError}</p>
        <Link to="/" className="text-sm text-slate-600 underline">
          Back to employees
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-sm text-slate-500 hover:underline">
          &larr; Back to employees
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">
            {employee.name}{' '}
            <span className="text-sm font-normal text-slate-400">({employee.employee_code})</span>
          </h2>
          <span
            className={`mt-1 inline-block rounded-full px-2 py-1 text-xs font-medium ${
              employee.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-600'
            }`}
          >
            {employee.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
        {employee.is_active && (
          <Button onClick={handleDeactivate} className="bg-red-50 text-red-700 hover:bg-red-100">
            Deactivate
          </Button>
        )}
      </div>

      {loadError && <p className="text-sm text-red-600">{loadError}</p>}

      <Card>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-slate-900">Employee Information</h3>
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)} className="bg-slate-200 text-slate-900 hover:bg-slate-300">
              Edit
            </Button>
          )}
        </div>

        {isEditing ? (
          <form onSubmit={handleSaveEdit} className="space-y-3">
            {EDITABLE_FIELDS.map((field) => (
              <div key={field}>
                <label className="mb-1 block text-sm font-medium capitalize text-slate-700">
                  {field.replace('_', ' ')}
                </label>
                <Input
                  type={field === 'join_date' ? 'date' : 'text'}
                  value={form[field]}
                  onChange={(event) => setForm({ ...form, [field]: event.target.value })}
                  required
                />
              </div>
            ))}
            {editError && <p className="text-sm text-red-600">{editError}</p>}
            <div className="flex gap-2">
              <Button type="submit" disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
              <Button
                type="button"
                onClick={() => setIsEditing(false)}
                className="bg-slate-200 text-slate-900 hover:bg-slate-300"
              >
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-slate-500">Department</dt>
              <dd className="text-slate-900">{employee.department}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Role</dt>
              <dd className="text-slate-900">{employee.role}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Country</dt>
              <dd className="text-slate-900">{employee.country}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Join Date</dt>
              <dd className="text-slate-900">{employee.join_date}</dd>
            </div>
          </dl>
        )}
      </Card>

      <Card>
        <h3 className="mb-4 font-semibold text-slate-900">Current Salary</h3>
        {employee.current_salary ? (
          <p className="text-2xl font-semibold text-slate-900">
            {employee.current_salary.amount} {employee.current_salary.currency}
            <span className="ml-2 text-sm font-normal text-slate-500">
              as of {employee.current_salary.effective_date}
            </span>
          </p>
        ) : (
          <p className="text-sm text-slate-500">No salary on record yet.</p>
        )}

        <form onSubmit={handleAddSalary} className="mt-4 flex flex-wrap items-end gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Amount</label>
            <Input
              type="number"
              step="0.01"
              min="0.01"
              value={salaryForm.amount}
              onChange={(event) => setSalaryForm({ ...salaryForm, amount: event.target.value })}
              required
              className="w-40"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Effective date</label>
            <Input
              type="date"
              value={salaryForm.effective_date}
              onChange={(event) => setSalaryForm({ ...salaryForm, effective_date: event.target.value })}
              required
              className="w-40"
            />
          </div>
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium text-slate-700">Reason</label>
            <Input
              type="text"
              placeholder="e.g. Annual raise, Promotion"
              value={salaryForm.reason}
              onChange={(event) => setSalaryForm({ ...salaryForm, reason: event.target.value })}
            />
          </div>
          <Button type="submit" disabled={isSubmittingSalary}>
            {isSubmittingSalary ? 'Saving...' : 'Record change'}
          </Button>
        </form>
        {salaryError && <p className="mt-2 text-sm text-red-600">{salaryError}</p>}
      </Card>

      <Card>
        <h3 className="mb-4 font-semibold text-slate-900">Salary History</h3>
        {history.length === 0 ? (
          <p className="text-sm text-slate-500">No salary history yet.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 text-slate-500">
              <tr>
                <th className="py-2">Effective Date</th>
                <th className="py-2">Amount</th>
                <th className="py-2">Reason</th>
              </tr>
            </thead>
            <tbody>
              {history.map((record) => (
                <tr key={record.id} className="border-b border-slate-100 last:border-0">
                  <td className="py-2">{record.effective_date}</td>
                  <td className="py-2">
                    {record.amount} {record.currency}
                  </td>
                  <td className="py-2 text-slate-500">{record.reason || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
