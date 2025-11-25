'use client'

import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Edit, Trash2 } from 'lucide-react'
import { motion } from 'framer-motion'

interface PantryCardProps {
  id: number
  name: string
  quantity: number
  unit: string
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}

export default function PantryCard({ id, name, quantity, unit, onEdit, onDelete }: PantryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg">{name}</h3>
              <p className="text-sm text-muted-foreground">
                {quantity} {unit}
              </p>
            </div>
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm" onClick={() => onEdit(id)}>
                <Edit className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => onDelete(id)}>
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

