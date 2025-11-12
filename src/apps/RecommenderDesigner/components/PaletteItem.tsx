import { useDrag } from 'react-dnd'
import { ComponentDefinition } from '../types'
import { SimplifiedComponentDefinition, getComponentColor } from '../simplifiedComponents'
import './PaletteItem.css'

interface PaletteItemProps {
  definition: ComponentDefinition | SimplifiedComponentDefinition
}

const PaletteItem = ({ definition }: PaletteItemProps) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'component',
    item: { definition },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  }), [definition])

  // Get category and color if using simplified components
  const category = 'category' in definition ? definition.category : undefined
  const colors = category ? getComponentColor(category) : undefined

  return (
    <div
      ref={drag}
      className={`palette-item ${category ? `palette-item-${category}` : ''} ${isDragging ? 'dragging' : ''}`}
      style={colors ? {
        background: colors.gradient,
        borderColor: colors.border,
        color: colors.text
      } : undefined}
      title={definition.description}
    >
      <span className="palette-item-icon">{definition.icon}</span>
      <span className="palette-item-label">{definition.label}</span>
    </div>
  )
}

export default PaletteItem
