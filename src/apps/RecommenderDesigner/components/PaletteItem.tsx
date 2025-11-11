import { useDrag } from 'react-dnd'
import { ComponentDefinition } from '../types'
import './PaletteItem.css'

interface PaletteItemProps {
  definition: ComponentDefinition
}

const PaletteItem = ({ definition }: PaletteItemProps) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'component',
    item: { definition },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  }), [definition])

  return (
    <div
      ref={drag}
      className={`palette-item ${isDragging ? 'dragging' : ''}`}
      title={definition.description}
    >
      <span className="palette-item-icon">{definition.icon}</span>
      <span className="palette-item-label">{definition.label}</span>
    </div>
  )
}

export default PaletteItem
