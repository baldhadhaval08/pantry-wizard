'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ChefHat, Home, ShoppingCart, Sparkles, History, BarChart3, LogOut } from 'lucide-react'
import { removeToken } from '@/lib/auth'
import { Button } from './ui/button'

export default function Navbar() {
  const router = useRouter()

  const handleLogout = () => {
    removeToken()
    router.push('/login')
  }

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <ChefHat className="h-6 w-6 text-primary" />
              <span className="text-xl font-semibold text-gray-900 dark:text-white">PantryWizard+</span>
            </Link>
          </div>
          <div className="flex items-center space-x-1">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <Home className="h-4 w-4" />
                <span className="hidden sm:inline">Dashboard</span>
              </Button>
            </Link>
            <Link href="/pantry">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <ShoppingCart className="h-4 w-4" />
                <span className="hidden sm:inline">Pantry</span>
              </Button>
            </Link>
            <Link href="/generate">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <Sparkles className="h-4 w-4" />
                <span className="hidden sm:inline">Generate</span>
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <History className="h-4 w-4" />
                <span className="hidden sm:inline">History</span>
              </Button>
            </Link>
            <Link href="/reports">
              <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span className="hidden sm:inline">Reports</span>
              </Button>
            </Link>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="flex items-center space-x-2">
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}

