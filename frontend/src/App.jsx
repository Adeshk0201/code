import { Routes, Route } from 'react-router-dom'
import IntakePage from './pages/IntakePage'
import AssessmentPage from './pages/AssessmentPage'
import ReportPage from './pages/ReportPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<IntakePage />} />
      <Route path="/assessment" element={<AssessmentPage />} />
      <Route path="/report" element={<ReportPage />} />
    </Routes>
  )
}