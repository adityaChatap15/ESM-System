import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApi } from '@/lib/useApi'

const PAGE_SIZE = 25

export default function EmployeeListPage() {
  const request = useApi()
  const navigate = useNavigate()

  const [employees, setEmployees] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('')
  const [country, setCountry] = useState('')
  const [role, setRole] = useState('')
  const [includeInactive, setIncludeInactive] = useState(false)

  const [filterOptions, setFilterOptions] = useState({ departments: [], countries: [], roles: [] })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // Debounce free-text search so we don't fire a request on every keystroke.
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 300)
    return () => clearTimeout(timeoutId)
  }, [searchInput])

  useEffect(() => {
    request('/api/v1/employees/filters')
      .then(setFilterOptions)
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    setIsLoading(true)
    setError('')

    const params = new URLSearchParams({
      page: String(page),
      page_size: String(PAGE_SIZE),
    })
    if (search) params.set('search', search)
    if (department) params.set('department', department)
    if (country) params.set('country', country)
    if (role) params.set('role', role)
    if (includeInactive) params.set('include_inactive', 'true')

    request(`/api/v1/employees?${params.toString()}`)
      .then((data) => {
        setEmployees(data.items)
        setTotal(data.total)
      })
      .catch((err) => setError(err.message || 'Failed to load employees'))
      .finally(() => setIsLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, department, country, role, includeInactive])

  function handleFilterChange(setter) {
    return (event) => {
      setter(event.target.value)
      setPage(1)
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div>
      <h2 className="mb-4 text-xl font-semibold text-slate-900">Employees</h2>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Search by name or employee code..."
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
          className="w-64 rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
        />
        <select
          value={department}
          onChange={handleFilterChange(setDepartment)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All departments</option>
          {filterOptions.departments.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <select
          value={country}
          onChange={handleFilterChange(setCountry)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All countries</option>
          {filterOptions.countries.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <select
          value={role}
          onChange={handleFilterChange(setRole)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All roles</option>
          {filterOptions.roles.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(event) => {
              setIncludeInactive(event.target.checked)
              setPage(1)
            }}
          />
          Show inactive
        </label>
      </div>

      {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-3">Employee Code</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Country</th>
              <th className="px-4 py-3">Join Date</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td className="px-4 py-6 text-slate-400" colSpan={7}>
                  Loading...
                </td>
              </tr>
            ) : employees.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-slate-400" colSpan={7}>
                  No employees found.
                </td>
              </tr>
            ) : (
              employees.map((employee) => (
                <tr
                  key={employee.id}
                  onClick={() => navigate(`/employees/${employee.id}`)}
                  className="cursor-pointer border-b border-slate-100 last:border-0 hover:bg-slate-50"
                >
                  <td className="px-4 py-3">{employee.employee_code}</td>
                  <td className="px-4 py-3">{employee.name}</td>
                  <td className="px-4 py-3">{employee.department}</td>
                  <td className="px-4 py-3">{employee.role}</td>
                  <td className="px-4 py-3">{employee.country}</td>
                  <td className="px-4 py-3">{employee.join_date}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium ${
                        employee.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-slate-200 text-slate-600'
                      }`}
                    >
                      {employee.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
        <span>
          {total} employee{total === 1 ? '' : 's'} total
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            disabled={page <= 1}
            className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
          >
            Previous
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
            disabled={page >= totalPages}
            className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
