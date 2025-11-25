'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import StatCard from '@/components/StatCard'
import RecipeCard from '@/components/RecipeCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { authAPI, recipesAPI, pantryAPI, historyAPI } from '@/lib/api'
import { getToken } from '@/lib/auth'
import { motion } from 'framer-motion'
import { UtensilsCrossed, Flame, ShoppingCart, Sparkles } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [dailyRecipe, setDailyRecipe] = useState<any>(null)
  const [stats, setStats] = useState({
    mealsCount: 0,
    totalCalories: 0,
    pantrySize: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      router.push('/login')
      return
    }

    loadDashboard()
  }, [router])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const [userRes, pantryRes, historyRes, dailyRes] = await Promise.all([
        authAPI.getProfile().catch(() => null),
        pantryAPI.list().catch(() => ({ data: [] })),
        historyAPI.getWeeklyReport().catch(() => ({ data: { meals_count: 0, total_calories: 0 } })),
        recipesAPI.getDaily().catch(() => null),
      ])

      if (userRes) setUser(userRes.data)
      if (pantryRes) setStats((s) => ({ ...s, pantrySize: pantryRes.data.length }))
      if (historyRes) {
        setStats((s) => ({
          ...s,
          mealsCount: historyRes.data.meals_count || 0,
          totalCalories: historyRes.data.total_calories || 0,
        }))
      }
      if (dailyRes) setDailyRecipe(dailyRes.data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveRecipe = async () => {
    if (!dailyRecipe) return
    try {
      await recipesAPI.save({
        recipe_json: dailyRecipe.recipe,
        calories: dailyRecipe.recipe.calories,
      })
      loadDashboard()
    } catch (error) {
      console.error('Error saving recipe:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
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
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.name || 'User'}!
          </h1>
          <p className="text-muted-foreground mb-8">
            Here's your daily recipe suggestion and quick stats
          </p>
        </motion.div>

        {/* Daily Recipe - Prominent */}
        {dailyRecipe && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-8"
          >
            <Card className="border-2 border-primary">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl flex items-center gap-2">
                      <Sparkles className="h-6 w-6 text-primary" />
                      Today's Recipe
                    </CardTitle>
                    <CardDescription>Your personalized daily suggestion</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <RecipeCard
                  recipe={dailyRecipe.recipe}
                  imageUrl={dailyRecipe.image_url}
                  onCooked={handleSaveRecipe}
                />
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <StatCard
              title="Meals This Week"
              value={stats.mealsCount}
              icon={UtensilsCrossed}
              description="Cooked recipes"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <StatCard
              title="Total Calories"
              value={Math.round(stats.totalCalories)}
              icon={Flame}
              description="This week"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <StatCard
              title="Pantry Items"
              value={stats.pantrySize}
              icon={ShoppingCart}
              description="Available ingredients"
            />
          </motion.div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button
            onClick={() => router.push('/pantry')}
            variant="outline"
            className="h-20 text-lg"
          >
            <ShoppingCart className="h-5 w-5 mr-2" />
            Manage Pantry
          </Button>
          <Button
            onClick={() => router.push('/generate')}
            className="h-20 text-lg bg-primary"
          >
            <Sparkles className="h-5 w-5 mr-2" />
            Generate Recipe
          </Button>
        </div>
      </div>
    </div>
  )
}

