import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, ChevronRight } from 'lucide-react'

const INITIAL = {
  patient: { patient_id: '', name: '', age: '', gender: 'male' },
  caretaker: {
    reported_memory_issues: false,
    duration_of_symptoms: '',
    known_conditions: '',
  },
}

export default function IntakePage() {
  const [form, setForm] = useState(INITIAL)
  const navigate = useNavigate()

  const set = (group, key, val) =>
    setForm(f => ({ ...f, [group]: { ...f[group], [key]: val } }))

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = {
      patient: { ...form.patient, age: parseInt(form.patient.age) },
      caretaker: {
        reported_memory_issues: form.caretaker.reported_memory_issues,
        duration_of_symptoms: form.caretaker.duration_of_symptoms,
        known_conditions: form.caretaker.known_conditions
          ? form.caretaker.known_conditions.split(',').map(s => s.trim())
          : [],
      },
    }
    sessionStorage.setItem('intake', JSON.stringify(payload))
    navigate('/assessment')
  }

  const inputClass = "w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
  const labelClass = "block text-sm font-medium text-slate-400 mb-1.5"

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-2xl fade-in">
        {/* Header */}
        <div className="flex items-center gap-3 mb-10">
          <div className="p-3 bg-blue-600 rounded-2xl">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">CogniAssess</h1>
            <p className="text-xs text-slate-400">Cognitive Assessment System</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Patient Info */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-wider">Patient Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className={labelClass}>Full Name</label>
                <input required className={inputClass} placeholder="Patient full name"
                  value={form.patient.name}
                  onChange={e => set('patient', 'name', e.target.value)} />
              </div>
              <div>
                <label className={labelClass}>Patient ID</label>
                <input required className={inputClass} placeholder="e.g. PT-001"
                  value={form.patient.patient_id}
                  onChange={e => set('patient', 'patient_id', e.target.value)} />
              </div>
              <div>
                <label className={labelClass}>Age</label>
                <input required type="number" min="1" className={inputClass} placeholder="Age"
                  value={form.patient.age}
                  onChange={e => set('patient', 'age', e.target.value)} />
              </div>
              <div className="col-span-2">
                <label className={labelClass}>Gender</label>
                <select className={inputClass}
                  value={form.patient.gender}
                  onChange={e => set('patient', 'gender', e.target.value)}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Caretaker Info */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-semibold text-violet-400 uppercase tracking-wider">Caretaker Report</h2>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <input type="checkbox" id="mem"
                  className="w-4 h-4 accent-blue-500"
                  checked={form.caretaker.reported_memory_issues}
                  onChange={e => set('caretaker', 'reported_memory_issues', e.target.checked)} />
                <label htmlFor="mem" className="text-sm text-slate-300">
                  Caretaker has reported memory issues
                </label>
              </div>
              <div>
                <label className={labelClass}>Duration of Symptoms</label>
                <input className={inputClass} placeholder="e.g. 6 months, 2 years"
                  value={form.caretaker.duration_of_symptoms}
                  onChange={e => set('caretaker', 'duration_of_symptoms', e.target.value)} />
              </div>
              <div>
                <label className={labelClass}>Known Conditions (comma-separated)</label>
                <input className={inputClass} placeholder="e.g. Diabetes, Hypertension"
                  value={form.caretaker.known_conditions}
                  onChange={e => set('caretaker', 'known_conditions', e.target.value)} />
              </div>
            </div>
          </div>

          <button type="submit"
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-2xl flex items-center justify-center gap-2 transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/20">
            Begin Assessment
            <ChevronRight className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  )
}