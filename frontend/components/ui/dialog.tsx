'use client'

import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "./button"

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={() => onOpenChange(false)} />
      <div className="relative z-50 bg-background rounded-2xl shadow-lg max-w-lg w-full mx-4">
        {children}
      </div>
    </div>
  )
}

const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left p-6", className)} {...props} />
)

const DialogTitle = ({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h2 className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
)

const DialogContent = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement> & { onClose?: () => void }) => (
  <div className={cn("p-6", className)} {...props}>
    {children}
  </div>
)

const DialogClose = ({ onClose }: { onClose: () => void }) => (
  <Button
    variant="ghost"
    size="sm"
    className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100"
    onClick={onClose}
  >
    <X className="h-4 w-4" />
  </Button>
)

export { Dialog, DialogHeader, DialogTitle, DialogContent, DialogClose }

