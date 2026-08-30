import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useApi } from '@/lib/useApi'
import { Card } from '@/components/ui/card'

// Fixed categorical order (validated for CVD separation) - never reassigned
// per render, so "average" and "median" always mean the same color.
const COLOR_SERIES_1 = '#2a78d6' // average / primary series
const COLOR_SERIES_2 = '#1baf7a' // median / secondary series
const GRIDLINE = '#e1e0d9'
const AXIS_TEXT = '#898781'

const DIMENSIONS = ['country', 'department', 'role']

function groupByCurrency(items) {
  const groups = {}
  for (const item of items) {
    if (!groups[item.currency]) groups[item.currency] = []
    groups[item.currency].push(item)
  }
  return groups
}

function ExtremeTable({ title, rows }) {
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">{title}</p>
      <table className="w-full text-left text-sm">
        <tbody>
          {rows.map((row) => (
            <tr key={row.employee_id} className="border-b border-slate-100 last:border-0">
              <td className="py-1.5 pr-2">
                {row.name}
                <span className="ml-1 text-xs text-slate-400">({row.department})</span>
              </td>
              <td className="py-1.5 text-right font-medium text-slate-900">
                {row.amount} {row.currency}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function AnalyticsPage() {
  const request = useApi()

  const [department, setDepartment] = useState('')
  const [country, setCountry] = useState('')
  const [role, setRole] = useState('')
  const [dimension, setDimension] = useState('country')
  const [filterOptions, setFilterOptions] = useState({ departments: [], countries: [], roles: [] })

  const [summary, setSummary] = useState([])
  const [distribution, setDistribution] = useState([])
  const [extremes, setExtremes] = useState([])
  const [headcountPayroll, setHeadcountPayroll] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    request('/api/v1/employees/filters')
      .then(setFilterOptions)
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    setIsLoading(true)
    setError('')

    const filterParams = new URLSearchParams()
    if (department) filterParams.set('department', department)
    if (country) filterParams.set('country', country)
    if (role) filterParams.set('role', role)
    const filterQuery = filterParams.toString()

    const summaryParams = new URLSearchParams(filterQuery)
    summaryParams.set('dimension', dimension)

    Promise.all([
      request(`/api/v1/analytics/summary?${summaryParams.toString()}`),
      request(`/api/v1/analytics/distribution?${filterQuery}`),
      request(`/api/v1/analytics/extremes?limit=5&${filterQuery}`),
      request(`/api/v1/analytics/headcount-payroll?${filterQuery}`),
    ])
      .then(([summaryData, distributionData, extremesData, headcountData]) => {
        setSummary(summaryData)
        setDistribution(distributionData)
        setExtremes(extremesData)
        setHeadcountPayroll(headcountData)
      })
      .catch((err) => setError(err.message || 'Failed to load analytics'))
      .finally(() => setIsLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [department, country, role, dimension])

  const summaryByCurrency = groupByCurrency(summary)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Pay Insights</h2>
        <p className="text-sm text-slate-500">
          Every figure below stays in each employee's local currency - amounts are never summed or
          averaged across currencies (see docs/requirements.md).
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <select
          value={dimension}
          onChange={(event) => setDimension(event.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          {DIMENSIONS.map((option) => (
            <option key={option} value={option}>
              Group by {option}
            </option>
          ))}
        </select>
        <select
          value={department}
          onChange={(event) => setDepartment(event.target.value)}
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
          onChange={(event) => setCountry(event.target.value)}
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
          onChange={(event) => setRole(event.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">All roles</option>
          {filterOptions.roles.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {isLoading && <p className="text-sm text-slate-400">Loading analytics...</p>}

      <Card>
        <h3 className="mb-4 font-semibold text-slate-900">
          Average &amp; Median Salary by {dimension}
        </h3>
        {summary.length === 0 && !isLoading ? (
          <p className="text-sm text-slate-500">No data for this filter.</p>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {Object.entries(summaryByCurrency).map(([currency, items]) => (
              <div key={currency}>
                <p className="mb-2 text-sm font-medium text-slate-600">{currency}</p>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={items}>
                    <CartesianGrid stroke={GRIDLINE} vertical={false} />
                    <XAxis dataKey="group" tick={{ fontSize: 11, fill: AXIS_TEXT }} />
                    <YAxis tick={{ fontSize: 11, fill: AXIS_TEXT }} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <Bar dataKey="average_salary" name="Average" fill={COLOR_SERIES_1} radius={[3, 3, 0, 0]} isAnimationActive={false} />
                    <Bar dataKey="median_salary" name="Median" fill={COLOR_SERIES_2} radius={[3, 3, 0, 0]} isAnimationActive={false} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <h3 className="mb-4 font-semibold text-slate-900">Salary Distribution</h3>
        {distribution.length === 0 && !isLoading ? (
          <p className="text-sm text-slate-500">No data for this filter.</p>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {distribution.map((group) => (
              <div key={group.currency}>
                <p className="mb-2 text-sm font-medium text-slate-600">{group.currency}</p>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={group.bands}>
                    <CartesianGrid stroke={GRIDLINE} vertical={false} />
                    <XAxis
                      dataKey="range_label"
                      tick={{ fontSize: 9, fill: AXIS_TEXT }}
                      angle={-20}
                      textAnchor="end"
                      height={45}
                    />
                    <YAxis tick={{ fontSize: 11, fill: AXIS_TEXT }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="headcount" name="Employees" fill={COLOR_SERIES_1} radius={[3, 3, 0, 0]} isAnimationActive={false} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <h3 className="mb-4 font-semibold text-slate-900">Headcount by Country</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={headcountPayroll}>
            <CartesianGrid stroke={GRIDLINE} vertical={false} />
            <XAxis
              dataKey="country"
              tick={{ fontSize: 11, fill: AXIS_TEXT }}
              angle={-20}
              textAnchor="end"
              height={60}
            />
            <YAxis tick={{ fontSize: 11, fill: AXIS_TEXT }} allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="headcount" name="Employees" fill={COLOR_SERIES_1} radius={[3, 3, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <h3 className="mb-1 font-semibold text-slate-900">Total Payroll Cost by Country</h3>
        <p className="mb-4 text-xs text-slate-500">
          Shown per local currency, not summed across countries.
        </p>
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 text-slate-500">
            <tr>
              <th className="py-2">Country</th>
              <th className="py-2">Headcount</th>
              <th className="py-2">Total Payroll</th>
            </tr>
          </thead>
          <tbody>
            {headcountPayroll.map((row) => (
              <tr key={row.country} className="border-b border-slate-100 last:border-0">
                <td className="py-2">{row.country}</td>
                <td className="py-2">{row.headcount}</td>
                <td className="py-2 font-medium text-slate-900">
                  {row.total_payroll} {row.currency}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card>
        <h3 className="mb-4 font-semibold text-slate-900">Highest &amp; Lowest Paid</h3>
        <div className="space-y-6">
          {extremes.map((group) => (
            <div key={group.currency}>
              <p className="mb-2 text-sm font-medium text-slate-600">{group.currency}</p>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <ExtremeTable title="Highest paid" rows={group.highest} />
                <ExtremeTable title="Lowest paid" rows={group.lowest} />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
