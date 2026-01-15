import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Arbitrage from './pages/Arbitrage.tsx';
import Futures from './pages/Futures.tsx';
import Airdrops from './pages/Airdrops.tsx';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="arbitrage" element={<Arbitrage />} />
          <Route path="futures" element={<Futures />} />
          <Route path="airdrops" element={<Airdrops />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;