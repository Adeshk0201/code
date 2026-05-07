export default function ScoreCard({ title, score, confidence, questions, color = 'blue' }) {
  const pct = Math.round((score || 0) * 100)
  const confPct = Math.round((confidence || 0) * 100)

  const ring = {
    blue: 'stroke-blue-500',
    violet: 'stroke-violet-500',
    emerald: 'stroke-emerald-500',
  }[color]

  const circumference = 2 * Math.PI * 28
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">{title}</h3>
        <span className="text-xs text-slate-500">{questions} Qs</span>
      </div>
      <div className="flex items-center gap-4">
        <svg width="72" height="72" viewBox="0 0 72 72">
          <circle cx="36" cy="36" r="28" fill="none" stroke="#1e293b" strokeWidth="6" />
          <circle
            cx="36" cy="36" r="28" fill="none"
            className={ring}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 36 36)"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
          <text x="36" y="40" textAnchor="middle" fontSize="14" fontWeight="600" fill="#f1f5f9">
            {pct}%
          </text>
        </svg>
        <div className="flex flex-col gap-1">
          <p className="text-xs text-slate-400">Confidence</p>
          <div className="w-28 bg-slate-700 rounded-full h-1.5">
            <div
              className="bg-emerald-400 h-1.5 rounded-full transition-all duration-700"
              style={{ width: `${confPct}%` }}
            />
          </div>
          <p className="text-xs text-slate-300 font-mono">{confPct}%</p>
        </div>
      </div>
    </div>
  )
}