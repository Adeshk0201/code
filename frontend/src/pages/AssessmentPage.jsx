import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAssessment } from '../hooks/useAssessment'
import SectionBadge from '../components/SectionBadge'
import ProgressBar from '../components/ProgressBar'
import { Send, Wifi, WifiOff, Brain } from 'lucide-react'

export default function AssessmentPage() {
  const navigate = useNavigate()
  const { connected, error, connect, send, disconnect } = useAssessment()
  const [question, setQuestion] = useState('')
  const [section, setSection] = useState('orientation')
  const [qNum, setQNum] = useState(0)
  const [confidence, setConfidence] = useState(0)
  const [answer, setAnswer] = useState('')
  const [history, setHistory] = useState([])
  const [status, setStatus] = useState('connecting') // connecting | active | complete
  const [started, setStarted] = useState(false)
  const chatRef = useRef(null)

  useEffect(() => {
    const intake = JSON.parse(sessionStorage.getItem('intake') || 'null')
    if (!intake) { navigate('/'); return }

    connect((msg) => {
      if (msg.type === 'question') {
        setQuestion(msg.question)
        setSection(msg.section)
        setQNum(msg.question_number)
        const conf = msg.context_snapshot?.section_state?.confidence || 0
        setConfidence(conf)
        setStatus('active')
      }
      if (msg.type === 'complete') {
        sessionStorage.setItem('report', JSON.stringify(msg))
        setStatus('complete')
        disconnect()
        setTimeout(() => navigate('/report'), 1200)
      }
    })

    return () => disconnect()
  }, [])

  useEffect(() => {
    if (connected && !started) {
      const intake = JSON.parse(sessionStorage.getItem('intake'))
      send('start', intake)
      setStarted(true)
    }
  }, [connected])

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' })
  }, [history])

  const submitAnswer = () => {
    if (!answer.trim()) return
    setHistory(h => [...h, { q: question, a: answer, section }])
    send('answer', { answer })
    setAnswer('')
    setQuestion('...')
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitAnswer() }
  }

  const confPct = Math.round(confidence * 100)

  return (
    <div className="min-h-screen flex flex-col max-w-3xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 fade-in">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-xl">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white">CogniAssess</h1>
            <p className="text-xs text-slate-400">Live Assessment</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          {connected
            ? <><Wifi className="w-4 h-4 text-emerald-400" /><span className="text-emerald-400">Connected</span></>
            : <><WifiOff className="w-4 h-4 text-red-400" /><span className="text-red-400">Disconnected</span></>}
        </div>
      </div>

      {/* Section + Progress */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-5 mb-5 fade-in space-y-3">
        <div className="flex items-center justify-between">
          <SectionBadge section={section} />
          <span className="text-xs font-mono text-slate-400">Q{qNum} of 5</span>
        </div>
        <ProgressBar current={qNum} total={5} />
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-500">Confidence</span>
          <span className="text-xs font-mono text-emerald-400">{confPct}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1">
          <div
            className="bg-emerald-400 h-1 rounded-full transition-all duration-700"
            style={{ width: `${confPct}%` }}
          />
        </div>
      </div>

      {/* Chat history */}
      <div ref={chatRef} className="flex-1 overflow-y-auto space-y-4 mb-5 max-h-72 pr-1">
        {history.map((item, i) => (
          <div key={i} className="fade-in space-y-2">
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold shrink-0">A</div>
              <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-slate-200 max-w-[85%]">
                {item.q}
              </div>
            </div>
            <div className="flex gap-3 justify-end">
              <div className="bg-blue-600/20 border border-blue-500/30 rounded-2xl rounded-tr-sm px-4 py-3 text-sm text-blue-100 max-w-[85%]">
                {item.a}
              </div>
              <div className="w-7 h-7 rounded-full bg-slate-600 flex items-center justify-center text-xs font-bold shrink-0">P</div>
            </div>
          </div>
        ))}
      </div>

      {/* Current question */}
      {status === 'active' && (
        <div className="fade-in">
          <div className="bg-slate-800/80 border border-blue-500/30 rounded-2xl p-5 mb-4">
            <p className="text-xs text-blue-400 font-medium mb-2 uppercase tracking-wider">Current Question</p>
            <p className="text-white font-medium leading-relaxed">
              {question === '...'
                ? <span className="text-slate-400 animate-pulse">Generating question...</span>
                : question}
            </p>
          </div>
          <div className="flex gap-3">
            <textarea
              className="flex-1 bg-slate-800 border border-slate-700 rounded-2xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none text-sm"
              rows={2}
              placeholder="Type patient's response..."
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              onKeyDown={handleKey}
            />
            <button
              onClick={submitAnswer}
              disabled={!answer.trim()}
              className="px-5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-2xl transition flex items-center justify-center">
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-slate-600 mt-2 text-center">Press Enter to submit</p>
        </div>
      )}

      {status === 'complete' && (
        <div className="text-center py-8 fade-in">
          <div className="w-12 h-12 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">✓</span>
          </div>
          <p className="text-white font-semibold">Assessment Complete</p>
          <p className="text-slate-400 text-sm mt-1">Generating report...</p>
        </div>
      )}

      {status === 'connecting' && (
        <div className="text-center py-8 text-slate-400 text-sm">
          <div className="pulse-dot w-3 h-3 bg-blue-500 rounded-full mx-auto mb-3" />
          Connecting to assessment server...
        </div>
      )}

      {error && <p className="text-red-400 text-sm text-center mt-2">{error}</p>}
    </div>
  )
}