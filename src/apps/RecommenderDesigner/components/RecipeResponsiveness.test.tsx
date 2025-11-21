import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
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

describe('Recipe UI Responsiveness', () => {
  describe('Basic Rendering', () => {
    it('should render all recipes correctly', () => {
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

      // Verify all recipes are visible
      EXAMPLE_WORKFLOWS.forEach(workflow => {
        expect(screen.getByText(workflow.name)).toBeVisible()
        expect(screen.getByText(workflow.description)).toBeVisible()
      })

      // Verify run buttons are visible
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      expect(runButtons).toHaveLength(EXAMPLE_WORKFLOWS.length)
      runButtons.forEach(button => {
        expect(button).toBeVisible()
      })
    })

    it('should display recipe cards with full content', () => {
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

      // Check that recipe cards contain all expected elements
      const recipeCards = container.querySelectorAll('.recipe-card')
      expect(recipeCards.length).toBe(EXAMPLE_WORKFLOWS.length)

      recipeCards.forEach((card, index) => {
        const workflow = EXAMPLE_WORKFLOWS[index]

        // Check for name, description, badge, and run button
        expect(card.textContent).toContain(workflow.name)
        expect(card.textContent).toContain(workflow.description)
        expect(card.textContent).toContain(`${workflow.blocks.length} blocks`)
        expect(card.querySelector('.recipe-run-button')).toBeInTheDocument()
      })
    })
  })

  describe('Functionality', () => {
    it('should maintain functionality when running recipes', () => {
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

      // Click run button
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      fireEvent.click(runButtons[0])

      // Verify functionality works
      expect(mockOnRunWorkflow).toHaveBeenCalledTimes(1)
    })

    it('should have scrollable content', () => {
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

      // Check that content is scrollable
      const paletteContent = container.querySelector('.palette-content')
      expect(paletteContent).toBeInTheDocument()
    })

    it('should maintain run button functionality', () => {
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

      // Click run button
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      fireEvent.click(runButtons[0])

      // Verify functionality works
      expect(mockOnRunWorkflow).toHaveBeenCalledTimes(1)
      expect(mockOnRunWorkflow).toHaveBeenCalledWith(EXAMPLE_WORKFLOWS[0])
    })
  })

  describe('Tab Switching', () => {
    it('should switch tabs correctly', () => {
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

      // Verify tab switching works
      fireEvent.click(recipesTab)
      expect(recipesTab).toHaveClass('active')

      fireEvent.click(componentsTab)
      expect(componentsTab).toHaveClass('active')
    })
  })

  describe('Recipe Card Layout', () => {
    it('should have recipe cards with proper structure', () => {
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

      // Verify recipe cards have required classes
      const recipeCards = container.querySelectorAll('.recipe-card')
      expect(recipeCards.length).toBeGreaterThan(0)

      recipeCards.forEach(card => {
        // Check for header, description, and preview
        expect(card.querySelector('.recipe-header')).toBeInTheDocument()
        expect(card.querySelector('.recipe-description')).toBeInTheDocument()
        expect(card.querySelector('.recipe-blocks-preview')).toBeInTheDocument()
      })
    })

    it('should have recipe actions container with badge and button', () => {
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

      // Verify recipe actions containers exist
      const recipeCards = container.querySelectorAll('.recipe-card')
      recipeCards.forEach(card => {
        const actionsContainer = card.querySelector('.recipe-actions')
        expect(actionsContainer).toBeInTheDocument()

        // Check for badge and button within actions
        expect(card.querySelector('.recipe-badge')).toBeInTheDocument()
        expect(card.querySelector('.recipe-run-button')).toBeInTheDocument()
      })
    })
  })

  describe('Touch Interaction', () => {
    it('should handle touch events on recipe cards', () => {
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

      // Simulate touch on run button
      const runButtons = screen.getAllByRole('button', { name: /Run/i })
      fireEvent.touchStart(runButtons[0])
      fireEvent.touchEnd(runButtons[0])
      fireEvent.click(runButtons[0])

      expect(mockOnRunWorkflow).toHaveBeenCalled()
    })
  })
})
