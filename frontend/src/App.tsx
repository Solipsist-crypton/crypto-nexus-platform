// frontend/src/App.tsx
import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Arbitrage from './pages/Arbitrage'
import Futures from './pages/Futures'
import Airdrops from './pages/Airdrops'
import Dashboard from './pages/Dashboard'
import Layout from './components/layout/Layout'
import ProfilePage from './features/profile/ProfilePage';
import './styles/globals.css'

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout><Home /></Layout>} />
        <Route path="/arbitrage" element={<Layout><Arbitrage /></Layout>} />
        <Route path="/futures" element={<Layout><Futures /></Layout>} />
        <Route path="/airdrops" element={<Layout><Airdrops /></Layout>} />
        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
        <Route path="/profile" element={<Layout><ProfilePage /></Layout>} />
      </Routes>
    </Router>
  )
}

export default App