import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'
import ScoreCard from '../components/ScoreCard'
import { Brain, AlertTriangle, CheckCircle, FileText } from 'lucide-react'

const RISK_CONFIG = {
  low: { color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', icon: CheckCircle },
  moderate: { color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/30', icon: AlertTriangle },
  high: { color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/30', icon: AlertTriangle },
}

const SECTION_COLORS = { orientation: '#8b5cf6', memory: '#3b82f6', reasoning: '#10b981' }

export default function ReportPage() {
  const navigate = useNavigate()
  const [report, setReport] = useState(null)

  useEffect(() => {
    const data = JSON.parse(sessionStorage.getItem('report') || 'null')
    if (!data) { navigate('/'); return }
    setReport(data)
  }, [])

  if (!report) return null

  const scores = report.scores || {}
  const rep = report.report || {}
  const consistency = report.consistency || {}
  const riskKey = rep.risk_level || 'low'
  const Risk = RISK_CONFIG[riskKey]
  const RiskIcon = Risk.icon

  const radarData = Object.entries(scores).map(([section, data]) => ({
    subject: section.charAt(0).toUpperCase() + section.slice(1),
    score: Math.round((data.score || 0) * 100),
    confidence: Math.round((data.confidence || 0) * 100),
  }))

  const barData = Object.entries(scores).map(([section, data]) => ({
    name: section,
    score: Math.round((data.score || 0) * 100),
  }))

  const secColors = ['violet', 'blue', 'emerald']

  return (
    <div className="min-h-screen max-w-4xl mx-auto p-6 pb-16">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 fade-in">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-xl">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Assessment Report</h1>
            <p className="text-xs text-slate-400">Session: {report.session_id?.slice(0, 8)}...</p>
          </div>
        </div>
        <button
          onClick={() => { sessionStorage.clear(); navigate('/') }}
          className="text-xs text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 px-4 py-2 rounded-xl transition">
          New Assessment
        </button>
      </div>

      {/* Risk Banner */}
      <div className={`border rounded-2xl p-5 mb-6 flex items-center gap-4 fade-in ${Risk.bg}`}>
        <RiskIcon className={`w-8 h-8 ${Risk.color} shrink-0`} />
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-0.5">Risk Level</p>
          <p className={`text-2xl font-bold capitalize ${Risk.color}`}>{riskKey}</p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-xs text-slate-400">Total Questions</p>
          <p className="text-xl font-bold text-white">{report.total_questions}</p>
        </div>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 fade-in">
        {Object.entries(scores).map(([section, data], i) => (
          <ScoreCard
            key={section}
            title={section}
            score={data.score}
            confidence={data.confidence}
            questions={data.questions}
            color={secColors[i]}
          />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 fade-in">
        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Cognitive Radar</h3>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Radar name="Score" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
              <Radar name="Confidence" dataKey="confidence" stroke="#10b981" fill="#10b981" fillOpacity={0.1} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Section Scores</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} barSize={32}>
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 12, fontSize: 12 }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                {barData.map((entry) => (
                  <Cell key={entry.name} fill={SECTION_COLORS[entry.name] || '#3b82f6'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Consistency */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5 mb-6 fade-in">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Consistency Analysis</h3>
        <div className="flex items-center gap-4 mb-3">
          <div className="flex-1">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Patient vs Caretaker Report</span>
              <span>{Math.round((consistency.consistency_score || 1) * 100)}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-700"
                style={{ width: `${Math.round((consistency.consistency_score || 1) * 100)}%` }}
              />
            </div>
          </div>
        </div>
        {consistency.mismatches?.length > 0 && (
          <div className="space-y-1 mt-3">
            <p className="text-xs text-slate-400 mb-2">Detected Mismatches:</p>
            {consistency.mismatches.map((m, i) => (
              <div key={i} className="flex gap-2 text-xs text-yellow-300 bg-yellow-500/10 border border-yellow-500/20 rounded-lg px-3 py-2">
                <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                {m}
              </div>
            ))}
          </div>
        )}
        {consistency.summary && (
          <p className="text-xs text-slate-400 mt-3 italic">{consistency.summary}</p>
        )}
      </div>

      {/* Clinical Report */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5 mb-6 fade-in">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-slate-300">Clinical Report</h3>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
          {rep.report || 'No report generated.'}
        </p>
      </div>

      {/* Recommendations */}
      {rep.recommendations?.length > 0 && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5 fade-in">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Recommendations</h3>
          <div className="space-y-2">
            {rep.recommendations.map((r, i) => (
              <div key={i} className="flex gap-3 text-sm text-slate-300 bg-blue-500/5 border border-blue-500/20 rounded-xl px-4 py-3">
                <span className="text-blue-400 font-bold shrink-0">{i + 1}.</span>
                {r}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}