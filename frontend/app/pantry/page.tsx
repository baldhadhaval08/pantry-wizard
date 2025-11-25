'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import PantryCard from '@/components/PantryCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from '@/components/ui/dialog'
import { pantryAPI } from '@/lib/api'
import { getToken } from '@/lib/auth'
import { motion } from 'framer-motion'
import { Plus, Search } from 'lucide-react'

const QUICK_ITEMS = [
  { name: 'Tomato', quantity: 5, unit: 'pieces' },
  { name: 'Onion', quantity: 2, unit: 'pieces' },
  { name: 'Chicken', quantity: 500, unit: 'grams' },
  { name: 'Rice', quantity: 1, unit: 'kg' },
  { name: 'Eggs', quantity: 6, unit: 'pieces' },
  { name: 'Milk', quantity: 1, unit: 'liter' },
]

export default function PantryPage() {
  const router = useRouter()
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<any>(null)
  const [formData, setFormData] = useState({ name: '', quantity: '', unit: '' })

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
      setLoading(true)
      const response = await pantryAPI.list()
      setItems(response.data)
    } catch (error) {
      console.error('Error loading pantry:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingItem(null)
    setFormData({ name: '', quantity: '', unit: '' })
    setDialogOpen(true)
  }

  const handleEdit = (id: number) => {
    const item = items.find((i) => i.id === id)
    if (item) {
      setEditingItem(item)
      setFormData({ name: item.name, quantity: item.quantity.toString(), unit: item.unit })
      setDialogOpen(true)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return
    try {
      await pantryAPI.delete(id)
      loadPantry()
    } catch (error) {
      console.error('Error deleting item:', error)
    }
  }

  const handleQuickAdd = async (item: typeof QUICK_ITEMS[0]) => {
    try {
      await pantryAPI.add(item)
      loadPantry()
    } catch (error) {
      console.error('Error adding item:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingItem) {
        await pantryAPI.update(editingItem.id, {
          name: formData.name,
          quantity: parseFloat(formData.quantity),
          unit: formData.unit,
        })
      } else {
        await pantryAPI.add({
          name: formData.name,
          quantity: parseFloat(formData.quantity),
          unit: formData.unit,
        })
      }
      setDialogOpen(false)
      loadPantry()
    } catch (error) {
      console.error('Error saving item:', error)
    }
  }

  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
              <h1 className="text-3xl font-bold mb-2">My Pantry</h1>
              <p className="text-muted-foreground">Manage your available ingredients</p>
            </div>
            <Button onClick={handleAdd} className="w-full sm:w-auto">
              <Plus className="h-4 w-4 mr-2" />
              Add Item
            </Button>
          </div>

          {/* Search */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search pantry items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Quick Add */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Quick Add</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {QUICK_ITEMS.map((item, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickAdd(item)}
                  >
                    + {item.name}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Items Grid */}
          {filteredItems.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">
                  {searchQuery ? 'No items found' : 'Your pantry is empty. Add some ingredients!'}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredItems.map((item) => (
                <PantryCard
                  key={item.id}
                  id={item.id}
                  name={item.name}
                  quantity={item.quantity}
                  unit={item.unit}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogClose onClose={() => setDialogOpen(false)} />
          <DialogHeader>
            <DialogTitle>{editingItem ? 'Edit Item' : 'Add Item'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">
                Name
              </label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div>
              <label htmlFor="quantity" className="block text-sm font-medium mb-2">
                Quantity
              </label>
              <Input
                id="quantity"
                type="number"
                step="0.1"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                required
              />
            </div>
            <div>
              <label htmlFor="unit" className="block text-sm font-medium mb-2">
                Unit
              </label>
              <Input
                id="unit"
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                placeholder="grams, pieces, cups..."
                required
              />
            </div>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" className="flex-1">
                {editingItem ? 'Update' : 'Add'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

