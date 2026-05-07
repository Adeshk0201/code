const COLORS = {
  orientation: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
  memory: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  reasoning: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
}

export default function SectionBadge({ section }) {
  return (
    <span className={`text-xs font-medium px-3 py-1 rounded-full border uppercase tracking-widest ${COLORS[section] || 'bg-slate-700 text-slate-300 border-slate-600'}`}>
      {section}
    </span>
  )
}