import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import ComponentPalette from './ComponentPalette'
import { EXAMPLE_WORKFLOWS } from '../simplifiedComponents'

// Helper to render with DndProvider
const renderWithDnd = (component: React.ReactElement) => {
  return render(
    <DndProvider backend={HTML5Backend}>
      {component}
    </DndProvider>
  )
}

describe('ComponentPalette - Recipe Run Functionality', () => {
  describe('Run Button Rendering', () => {
    it('should render run buttons for all recipes', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Check that all recipe cards have run buttons
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      expect(runButtons).toHaveLength(EXAMPLE_WORKFLOWS.length)
    })

    it('should display run button with play icon', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Check that run buttons contain play icon
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      runButtons.forEach(button => {
        expect(button.textContent).toContain('▶')
        expect(button.textContent).toContain('Run')
      })
    })
  })

  describe('Run Button Functionality', () => {
    it('should call onRunWorkflow when run button is clicked', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Click the first run button
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      fireEvent.click(runButtons[0])

      // Verify onRunWorkflow was called with the first workflow
      expect(mockOnRunWorkflow).toHaveBeenCalledTimes(1)
      expect(mockOnRunWorkflow).toHaveBeenCalledWith(EXAMPLE_WORKFLOWS[0])
    })

    it('should not call onLoadWorkflow when run button is clicked', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Click the first run button
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      fireEvent.click(runButtons[0])

      // Verify onLoadWorkflow was NOT called (event should have stopped propagation)
      expect(mockOnLoadWorkflow).not.toHaveBeenCalled()
    })

    it('should call onLoadWorkflow when recipe card is clicked', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Click the first recipe card (but not the run button)
      const recipeCards = screen.getAllByTitle('Click to load this workflow')
      const firstCard = recipeCards[0]

      // Find a safe area to click (recipe name)
      const recipeName = within(firstCard).getByText(EXAMPLE_WORKFLOWS[0].name)
      fireEvent.click(recipeName)

      // Verify onLoadWorkflow was called
      expect(mockOnLoadWorkflow).toHaveBeenCalledTimes(1)
      expect(mockOnLoadWorkflow).toHaveBeenCalledWith(EXAMPLE_WORKFLOWS[0])
    })
  })

  describe('Run Button for Each Recipe', () => {
    EXAMPLE_WORKFLOWS.forEach((workflow, index) => {
      it(`should run "${workflow.name}" recipe correctly`, () => {
        const mockOnLoadWorkflow = vi.fn()
        const mockOnRunWorkflow = vi.fn()

        renderWithDnd(
          <ComponentPalette
            onLoadWorkflow={mockOnLoadWorkflow}
            onRunWorkflow={mockOnRunWorkflow}
          />
        )

        // Switch to recipes tab
        const recipesTab = screen.getByText(/Recipes/i)
        fireEvent.click(recipesTab)

        // Find and click the specific recipe's run button
        const runButtons = screen.getAllByRole('button', { name: /Run/i })
        fireEvent.click(runButtons[index])

        // Verify onRunWorkflow was called with the correct workflow
        expect(mockOnRunWorkflow).toHaveBeenCalledWith(workflow)
        expect(mockOnRunWorkflow).toHaveBeenCalledTimes(1)

        // Verify workflow has expected structure
        expect(workflow).toHaveProperty('name')
        expect(workflow).toHaveProperty('description')
        expect(workflow).toHaveProperty('blocks')
        expect(Array.isArray(workflow.blocks)).toBe(true)
        expect(workflow.blocks.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Recipe Tab Toggle', () => {
    it('should show recipes tab when clicked', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Initially on components tab
      expect(screen.queryByText(/Click any recipe to load it onto the canvas/i)).not.toBeInTheDocument()

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Verify recipes are shown
      expect(screen.getByText(/Click any recipe to load it onto the canvas, or click "Run" to load and execute/i)).toBeInTheDocument()

      // Verify all recipes are displayed
      EXAMPLE_WORKFLOWS.forEach(workflow => {
        expect(screen.getByText(workflow.name)).toBeInTheDocument()
        expect(screen.getByText(workflow.description)).toBeInTheDocument()
      })
    })

    it('should switch between components and recipes tabs', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      const componentsTab = screen.getByRole('button', { name: /Components/i })
      const recipesTab = screen.getByRole('button', { name: /Recipes/i })

      // Start on components tab
      expect(componentsTab).toHaveClass('active')
      expect(recipesTab).not.toHaveClass('active')

      // Switch to recipes
      fireEvent.click(recipesTab)
      expect(recipesTab).toHaveClass('active')
      expect(componentsTab).not.toHaveClass('active')

      // Switch back to components
      fireEvent.click(componentsTab)
      expect(componentsTab).toHaveClass('active')
      expect(recipesTab).not.toHaveClass('active')
    })
  })

  describe('Recipe Card Information Display', () => {
    it('should display recipe name, description, and block count', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Check each recipe has required information
      EXAMPLE_WORKFLOWS.forEach(workflow => {
        expect(screen.getByText(workflow.name)).toBeInTheDocument()
        expect(screen.getByText(workflow.description)).toBeInTheDocument()
      })

      // Check that all block counts are displayed (some may be duplicates)
      EXAMPLE_WORKFLOWS.forEach(workflow => {
        const blockCountText = `${workflow.blocks.length} blocks`
        const elements = screen.queryAllByText(blockCountText)
        expect(elements.length).toBeGreaterThan(0)
      })
    })

    it('should display block preview icons for recipes', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      const { container } = renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Verify block preview elements exist
      const blockPreviews = container.querySelectorAll('.recipe-blocks-preview')
      expect(blockPreviews.length).toBe(EXAMPLE_WORKFLOWS.length)
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels and titles', () => {
      const mockOnLoadWorkflow = vi.fn()
      const mockOnRunWorkflow = vi.fn()

      renderWithDnd(
        <ComponentPalette
          onLoadWorkflow={mockOnLoadWorkflow}
          onRunWorkflow={mockOnRunWorkflow}
        />
      )

      // Switch to recipes tab
      const recipesTab = screen.getByText(/Recipes/i)
      fireEvent.click(recipesTab)

      // Check run buttons have proper titles
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      runButtons.forEach(button => {
        expect(button).toHaveAttribute('title', 'Load and run this workflow')
      })

      // Check recipe cards have proper titles
      const recipeCards = screen.getAllByTitle('Click to load this workflow')
      expect(recipeCards.length).toBe(EXAMPLE_WORKFLOWS.length)
    })
  })
})
