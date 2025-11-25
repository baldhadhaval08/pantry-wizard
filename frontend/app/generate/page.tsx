'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import RecipeCard from '@/components/RecipeCard'
import PantryCard from '@/components/PantryCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { recipesAPI, pantryAPI } from '@/lib/api'
import { getToken } from '@/lib/auth'
import { motion } from 'framer-motion'
import { Sparkles, Loader2 } from 'lucide-react'

export default function GeneratePage() {
  const router = useRouter()
  const [pantryItems, setPantryItems] = useState<any[]>([])
  const [generatedRecipe, setGeneratedRecipe] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [preferences, setPreferences] = useState({
    cuisine: 'any',
    spice_level: 'medium',
  })

  useEffect(() => {
    const token = getToken()
    if (!token) {
      router.push('/login')
      return
    }
    loadPantry()
  }, [router])

  const loadPantry = async () => {
    try {
      const response = await pantryAPI.list()
      setPantryItems(response.data)
    } catch (error) {
      console.error('Error loading pantry:', error)
    }
  }

  const handleGenerate = async () => {
    if (pantryItems.length === 0) {
      alert('Please add items to your pantry first!')
      return
    }

    setLoading(true)
    try {
      const response = await recipesAPI.generate({
        use_pantry: true,
        preferences,
        avoid_repeats: true,
      })
      setGeneratedRecipe(response.data)
    } catch (error) {
      console.error('Error generating recipe:', error)
      alert('Failed to generate recipe. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerate = () => {
    setGeneratedRecipe(null)
    handleGenerate()
  }

  const handleSave = async () => {
    if (!generatedRecipe) return
    try {
      await recipesAPI.save({
        recipe_json: generatedRecipe.recipe,
        calories: generatedRecipe.recipe.calories,
      })
      alert('Recipe saved to history!')
    } catch (error) {
      console.error('Error saving recipe:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold mb-2">Generate Recipe</h1>
          <p className="text-muted-foreground mb-8">
            Create a healthy recipe from your pantry ingredients
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Pantry & Preferences */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Your Pantry</CardTitle>
              </CardHeader>
              <CardContent>
                {pantryItems.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No items in pantry. <a href="/pantry" className="text-primary hover:underline">Add some!</a>
                  </p>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {pantryItems.map((item) => (
                      <div key={item.id} className="text-sm">
                        <span className="font-medium">{item.name}</span> - {item.quantity} {item.unit}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Preferences</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor="cuisine" className="block text-sm font-medium mb-2">
                    Cuisine
                  </label>
                  <select
                    id="cuisine"
                    value={preferences.cuisine}
                    onChange={(e) => setPreferences({ ...preferences, cuisine: e.target.value })}
                    className="flex h-10 w-full rounded-2xl border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="any">Any</option>
                    <option value="italian">Italian</option>
                    <option value="asian">Asian</option>
                    <option value="mexican">Mexican</option>
                    <option value="indian">Indian</option>
                    <option value="mediterranean">Mediterranean</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="spice" className="block text-sm font-medium mb-2">
                    Spice Level
                  </label>
                  <select
                    id="spice"
                    value={preferences.spice_level}
                    onChange={(e) => setPreferences({ ...preferences, spice_level: e.target.value })}
                    className="flex h-10 w-full rounded-2xl border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="mild">Mild</option>
                    <option value="medium">Medium</option>
                    <option value="spicy">Spicy</option>
                  </select>
                </div>
                <Button
                  onClick={handleGenerate}
                  disabled={loading || pantryItems.length === 0}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Recipe
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Generated Recipe */}
          <div className="lg:col-span-2">
            {generatedRecipe ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <RecipeCard
                  recipe={generatedRecipe.recipe}
                  imageUrl={generatedRecipe.image_url}
                  onSave={handleSave}
                  onCooked={handleSave}
                  onRegenerate={handleRegenerate}
                />
              </motion.div>
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <Sparkles className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    {pantryItems.length === 0
                      ? 'Add items to your pantry and click Generate Recipe to get started!'
                      : 'Click Generate Recipe to create a personalized recipe from your pantry!'}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

