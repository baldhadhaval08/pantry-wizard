'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { authAPI } from '@/lib/api'
import { setToken } from '@/lib/auth'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { ChefHat, ArrowRight, ArrowLeft } from 'lucide-react'

type Step = 1 | 2 | 3

export default function RegisterPage() {
  const router = useRouter()
  const [step, setStep] = useState<Step>(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Step 1: Basic info
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  // Step 2: Profile
  const [heightCm, setHeightCm] = useState('')
  const [weightKg, setWeightKg] = useState('')
  const [age, setAge] = useState('')

  // Step 3: Preferences
  const [dietType, setDietType] = useState('omnivore')
  const [allergies, setAllergies] = useState('')
  const [goal, setGoal] = useState('maintain')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (step < 3) {
      setStep((step + 1) as Step)
      return
    }

    setError('')
    setLoading(true)

    try {
      const response = await authAPI.register({
        name,
        email,
        password,
        height_cm: heightCm ? parseFloat(heightCm) : null,
        weight_kg: weightKg ? parseFloat(weightKg) : null,
        age: age ? parseInt(age) : null,
        diet_type: dietType,
        allergies: allergies || null,
        goal,
      })
      setToken(response.data.access_token)
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 to-accent/10 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card>
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <ChefHat className="h-12 w-12 text-primary" />
            </div>
            <CardTitle className="text-3xl">Create Account</CardTitle>
            <CardDescription>Step {step} of 3</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <AnimatePresence mode="wait">
                {step === 1 && (
                  <motion.div
                    key="step1"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-4"
                  >
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium mb-2">
                        Full Name
                      </label>
                      <Input
                        id="name"
                        type="text"
                        placeholder="John Doe"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium mb-2">
                        Email
                      </label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="your@email.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="password" className="block text-sm font-medium mb-2">
                        Password
                      </label>
                      <Input
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        minLength={6}
                      />
                    </div>
                  </motion.div>
                )}

                {step === 2 && (
                  <motion.div
                    key="step2"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-4"
                  >
                    <div>
                      <label htmlFor="height" className="block text-sm font-medium mb-2">
                        Height (cm)
                      </label>
                      <Input
                        id="height"
                        type="number"
                        placeholder="170"
                        value={heightCm}
                        onChange={(e) => setHeightCm(e.target.value)}
                      />
                    </div>
                    <div>
                      <label htmlFor="weight" className="block text-sm font-medium mb-2">
                        Weight (kg)
                      </label>
                      <Input
                        id="weight"
                        type="number"
                        placeholder="70"
                        value={weightKg}
                        onChange={(e) => setWeightKg(e.target.value)}
                      />
                    </div>
                    <div>
                      <label htmlFor="age" className="block text-sm font-medium mb-2">
                        Age
                      </label>
                      <Input
                        id="age"
                        type="number"
                        placeholder="30"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                      />
                    </div>
                  </motion.div>
                )}

                {step === 3 && (
                  <motion.div
                    key="step3"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-4"
                  >
                    <div>
                      <label htmlFor="diet" className="block text-sm font-medium mb-2">
                        Diet Type
                      </label>
                      <select
                        id="diet"
                        value={dietType}
                        onChange={(e) => setDietType(e.target.value)}
                        className="flex h-10 w-full rounded-2xl border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="omnivore">Omnivore</option>
                        <option value="vegetarian">Vegetarian</option>
                        <option value="vegan">Vegan</option>
                        <option value="keto">Keto</option>
                        <option value="paleo">Paleo</option>
                      </select>
                    </div>
                    <div>
                      <label htmlFor="allergies" className="block text-sm font-medium mb-2">
                        Allergies (comma-separated)
                      </label>
                      <Input
                        id="allergies"
                        type="text"
                        placeholder="peanuts, shellfish"
                        value={allergies}
                        onChange={(e) => setAllergies(e.target.value)}
                      />
                    </div>
                    <div>
                      <label htmlFor="goal" className="block text-sm font-medium mb-2">
                        Health Goal
                      </label>
                      <select
                        id="goal"
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        className="flex h-10 w-full rounded-2xl border border-input bg-background px-3 py-2 text-sm"
                      >
                        <option value="weight_loss">Weight Loss</option>
                        <option value="muscle_gain">Muscle Gain</option>
                        <option value="maintain">Maintain Weight</option>
                        <option value="general_health">General Health</option>
                      </select>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {error && (
                <div className="bg-destructive/10 text-destructive p-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-2">
                {step > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setStep((step - 1) as Step)}
                    className="flex-1"
                  >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                  </Button>
                )}
                <Button type="submit" className="flex-1" disabled={loading}>
                  {step < 3 ? (
                    <>
                      Next
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </>
                  ) : loading ? (
                    'Creating Account...'
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </div>

              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <Link href="/login" className="text-primary hover:underline">
                  Sign in
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

