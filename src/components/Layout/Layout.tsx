import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/recommender-designer', label: 'Recommender Designer' },
  ]

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="logo">MAMMOTH</h1>
          <p className="tagline">Multi-App Platform</p>
        </div>
        <nav className="nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout
