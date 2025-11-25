'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import StatCard from '@/components/StatCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { historyAPI } from '@/lib/api'
import { getToken } from '@/lib/auth'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, Award, UtensilsCrossed } from 'lucide-react'

export default function ReportsPage() {
  const router = useRouter()
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      router.push('/login')
      return
    }
    loadReport()
  }, [router])

  const loadReport = async () => {
    try {
      setLoading(true)
      const response = await historyAPI.getWeeklyReport()
      setReport(response.data)
    } catch (error) {
      console.error('Error loading report:', error)
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

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No data available yet. Start cooking to see reports!</p>
            </CardContent>
          </Card>
        </div>
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
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <BarChart3 className="h-8 w-8" />
            Weekly Report
          </h1>
          <p className="text-muted-foreground mb-8">Your health and nutrition insights</p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Calories"
            value={Math.round(report.total_calories)}
            icon={TrendingUp}
            description="This week"
          />
          <StatCard
            title="Variety Score"
            value={`${Math.round(report.variety_score)}%`}
            icon={Award}
            description="Recipe diversity"
          />
          <StatCard
            title="Meals Cooked"
            value={report.meals_count}
            icon={UtensilsCrossed}
            description="This week"
          />
          <StatCard
            title="Avg Calories"
            value={Math.round(report.avg_calories_per_meal)}
            icon={BarChart3}
            description="Per meal"
          />
        </div>

        {/* Top Ingredients */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Top Ingredients</CardTitle>
            <CardDescription>Most used ingredients this week</CardDescription>
          </CardHeader>
          <CardContent>
            {report.top_ingredients && report.top_ingredients.length > 0 ? (
              <div className="space-y-2">
                {report.top_ingredients.map((ing: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <span className="font-medium capitalize">{ing.name}</span>
                    <span className="text-sm text-muted-foreground">{ing.count} times</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No ingredient data available</p>
            )}
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>Tips based on your activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {report.variety_score < 70 && (
                <div className="p-3 bg-accent/10 rounded-lg">
                  <p className="text-sm">
                    <strong>Try more variety!</strong> Your variety score is {Math.round(report.variety_score)}%.
                    Explore different cuisines and ingredients.
                  </p>
                </div>
              )}
              {report.avg_calories_per_meal > 600 && (
                <div className="p-3 bg-primary/10 rounded-lg">
                  <p className="text-sm">
                    <strong>Watch portion sizes.</strong> Your average meal has {Math.round(report.avg_calories_per_meal)} calories.
                    Consider lighter options.
                  </p>
                </div>
              )}
              {report.meals_count < 7 && (
                <div className="p-3 bg-primary/10 rounded-lg">
                  <p className="text-sm">
                    <strong>Keep cooking!</strong> You've cooked {report.meals_count} meals this week.
                    Try to cook at least once a day for better health.
                  </p>
                </div>
              )}
              {report.variety_score >= 70 && report.meals_count >= 7 && (
                <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                  <p className="text-sm">
                    <strong>Great job!</strong> You're maintaining good variety and consistency. Keep it up!
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

