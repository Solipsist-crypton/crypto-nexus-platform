import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Arbitrage from './pages/Arbitrage'
import Futures from './pages/Futures'
import Airdrops from './pages/Airdrops'
import Dashboard from './pages/Dashboard'
import './styles/globals.css'

const App: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/arbitrage" element={<Arbitrage />} />
          <Route path="/futures" element={<Futures />} />
          <Route path="/airdrops" element={<Airdrops />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App