import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Home from './pages/Home'
import RecommenderDesigner from './apps/RecommenderDesigner/RecommenderDesigner'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/recommender-designer" element={<RecommenderDesigner />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
