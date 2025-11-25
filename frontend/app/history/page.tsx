'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import RecipeCard from '@/components/RecipeCard'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { historyAPI } from '@/lib/api'
import { getToken } from '@/lib/auth'
import { motion } from 'framer-motion'
import { History as HistoryIcon } from 'lucide-react'

export default function HistoryPage() {
  const router = useRouter()
  const [recipes, setRecipes] = useState<any[]>([])
  const [filter, setFilter] = useState<string>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      router.push('/login')
      return
    }
    loadHistory()
  }, [router, filter])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const period = filter === 'all' ? undefined : filter
      const response = await historyAPI.list(period)
      setRecipes(response.data)
    } catch (error) {
      console.error('Error loading history:', error)
    } finally {
      setLoading(false)
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
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
                <HistoryIcon className="h-8 w-8" />
                Recipe History
              </h1>
              <p className="text-muted-foreground">View your saved and cooked recipes</p>
            </div>
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'week' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('week')}
              >
                This Week
              </Button>
              <Button
                variant={filter === 'month' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('month')}
              >
                This Month
              </Button>
            </div>
          </div>

          {recipes.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <HistoryIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No recipes in history yet. Start cooking!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {recipes.map((item, idx) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: idx * 0.1 }}
                >
                  <RecipeCard
                    recipe={item.recipe_json}
                    imageUrl={undefined}
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    Cooked on {new Date(item.created_at).toLocaleDateString()}
                    {item.calories && ` • ${item.calories} calories`}
                  </p>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

