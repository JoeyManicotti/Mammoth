# Mammoth

A multi-application platform for system design and visualization, featuring a sleek black and white UI inspired by Palantir Foundry.

## Features

### Current Applications

#### 🎯 Recommender System Designer
A visual drag-and-drop tool for designing and prototyping recommender system architectures.

**Features:**
- Drag and drop components from the palette onto the canvas
- Multiple component types:
  - **Data Sources**: Data Source, User Profile, Item Catalog
  - **Processing**: Feature Extraction, Ranking
  - **Algorithms**: Collaborative Filter, Content Filter, Matrix Factorization, Deep Learning
  - **Output**: Output, Evaluation
- Move components around the canvas by dragging
- Connect components to show data flow
- Delete components via right-click menu
- Clear canvas to start fresh
- Real-time component and connection counters

### UI Features
- Dark theme with white and black color scheme
- Grid-based canvas for precise component placement
- Smooth animations and transitions
- Responsive sidebar navigation
- Visual feedback for drag operations

## Getting Started

You can run Mammoth either with Docker (recommended) or directly with Node.js.

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)

#### Quick Start with Docker

```bash
# Development mode (with hot reload)
docker compose -f docker-compose.dev.yml up --build

# Production mode
docker compose up mammoth-prod --build
```

The application will be available at:
- Development: `http://localhost:3000`
- Production: `http://localhost:3001`

For detailed Docker instructions, see [DOCKER.md](DOCKER.md)

### Option 2: Local Installation

#### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

#### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at `http://localhost:3000`

## Project Structure

```
mammoth/
├── src/
│   ├── apps/                    # Individual applications
│   │   └── RecommenderDesigner/ # Recommender system design tool
│   │       ├── components/      # App-specific components
│   │       ├── types.ts         # TypeScript definitions
│   │       └── *.css            # Component styles
│   ├── components/              # Shared components
│   │   └── Layout/             # Main layout wrapper
│   ├── pages/                   # Page components
│   │   └── Home.tsx            # Home/landing page
│   ├── App.tsx                  # Main app component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
├── public/                      # Static assets
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
└── vite.config.ts              # Vite config
```

## Technologies

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Navigation
- **React DnD** - Drag and drop functionality
- **HTML5 Backend** - DnD backend

## Adding New Applications

To add a new application to Mammoth:

1. Create a new folder in `src/apps/`
2. Build your application components
3. Add a route in `src/App.tsx`
4. Add a navigation item in `src/components/Layout/Layout.tsx`
5. Add an app card in `src/pages/Home.tsx`

## Usage

### Recommender System Designer

1. Navigate to the "Recommender Designer" from the home page
2. Browse components in the left sidebar (organized by category)
3. Drag components from the palette onto the canvas
4. Click and drag components to reposition them
5. Right-click components to access the context menu
6. Use "Connect" to create connections between components (coming soon)
7. Use "Delete" to remove components
8. Click "Clear Canvas" to reset the workspace

## Future Enhancements

- Save and load designs
- Export designs as images or JSON
- Enhanced connection drawing with visual controls
- Component configuration panels
- Collaborative editing
- Design templates
- Additional applications for other system design domains

## License

See LICENSE file for details.
