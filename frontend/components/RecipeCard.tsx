'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { ChevronDown, ChevronUp, Save, ChefHat, RefreshCw } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface RecipeCardProps {
  recipe: {
    name: string
    description: string
    ingredients: Array<{ name: string; amount: string }>
    steps: string[]
    time_minutes: number
    difficulty: string
    calories: number
    macros: { protein_g: number; carbs_g: number; fat_g: number }
    health_justification: string
  }
  imageUrl?: string
  onSave?: () => void
  onCooked?: () => void
  onRegenerate?: () => void
}

export default function RecipeCard({ recipe, imageUrl, onSave, onCooked, onRegenerate }: RecipeCardProps) {
  const [stepsExpanded, setStepsExpanded] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="overflow-hidden">
        {imageUrl && (
          <div className="relative h-48 w-full bg-gray-200 overflow-hidden">
            <img
              src={imageUrl.startsWith('http') ? imageUrl : `http://localhost:8000${imageUrl}`}
              alt={recipe.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.src = 'https://via.placeholder.com/400x200?text=Recipe+Image'
              }}
            />
          </div>
        )}
        <CardHeader>
          <CardTitle className="text-2xl">{recipe.name}</CardTitle>
          <CardDescription>{recipe.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Calories</p>
                <p className="text-lg font-semibold">{recipe.calories}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Protein</p>
                <p className="text-lg font-semibold">{recipe.macros.protein_g}g</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Carbs</p>
                <p className="text-lg font-semibold">{recipe.macros.carbs_g}g</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Fat</p>
                <p className="text-lg font-semibold">{recipe.macros.fat_g}g</p>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Ingredients:</p>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {recipe.ingredients.map((ing, idx) => (
                  <li key={idx}>
                    {ing.name} - {ing.amount}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <Button
                variant="ghost"
                onClick={() => setStepsExpanded(!stepsExpanded)}
                className="w-full flex items-center justify-between"
              >
                <span>Steps ({recipe.steps.length})</span>
                {stepsExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
              <AnimatePresence>
                {stepsExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <ol className="list-decimal list-inside space-y-2 mt-2 text-sm">
                      {recipe.steps.map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="bg-primary/10 p-3 rounded-lg">
              <p className="text-sm text-primary font-medium">{recipe.health_justification}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              {onSave && (
                <Button onClick={onSave} variant="outline" size="sm">
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
              )}
              {onCooked && (
                <Button onClick={onCooked} className="bg-primary">
                  <ChefHat className="h-4 w-4 mr-2" />
                  Mark as Cooked
                </Button>
              )}
              {onRegenerate && (
                <Button onClick={onRegenerate} variant="ghost" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Regenerate
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

