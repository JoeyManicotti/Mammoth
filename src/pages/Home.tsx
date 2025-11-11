import { Link } from 'react-router-dom'
import './Home.css'

const Home = () => {
  const apps = [
    {
      id: 'recommender-designer',
      title: 'Recommender Designer',
      description: 'Design and visualize recommender system architectures with drag-and-drop components',
      path: '/recommender-designer',
      status: 'active'
    },
    {
      id: 'future-app-1',
      title: 'Coming Soon',
      description: 'More applications will be added here',
      path: '#',
      status: 'coming-soon'
    },
  ]

  return (
    <div className="home">
      <div className="home-header">
        <h1>Welcome to Mammoth</h1>
        <p>A multi-application platform for system design and visualization</p>
      </div>
      <div className="apps-grid">
        {apps.map((app) => (
          <div key={app.id} className={`app-card ${app.status}`}>
            {app.status === 'active' ? (
              <Link to={app.path} className="app-card-link">
                <h3>{app.title}</h3>
                <p>{app.description}</p>
                <span className="app-status">{app.status}</span>
              </Link>
            ) : (
              <div className="app-card-disabled">
                <h3>{app.title}</h3>
                <p>{app.description}</p>
                <span className="app-status">{app.status}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Home
