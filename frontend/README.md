# AutoGKB Prompt Tester - Frontend

A modern React + TypeScript frontend for testing and managing LLM prompts with multiple tasks and outputs.

## Technology Stack

- **React 19.1.1** - UI library
- **TypeScript** - Type-safe development
- **Vite 7.1.9** - Fast build tool and dev server
- **Tailwind CSS 3.4.11** - Utility-first CSS framework
- **shadcn/ui** - High-quality React component library built on Radix UI
- **Radix UI** - Accessible, unstyled UI primitives

## Project Structure

```
frontend/
├── public/
│   └── fonts/                    # Custom fonts (PP Editorial New, ABC Oracle, Cambria)
├── src/
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── select.tsx
│   │   │   ├── separator.tsx
│   │   │   └── textarea.tsx
│   │   ├── OutputsSidebar.tsx    # Right sidebar showing prompt outputs
│   │   ├── PromptDetails.tsx     # Prompt configuration form
│   │   └── PromptsSidebar.tsx    # Left sidebar with prompts list
│   ├── hooks/
│   │   └── usePrompts.ts         # Main state management hook
│   ├── lib/
│   │   └── utils.ts              # Utility functions (cn() for class merging)
│   ├── App.tsx                   # Main application component
│   ├── index.css                 # Tailwind directives + theme variables
│   ├── main.tsx                  # Application entry point
│   └── types.ts                  # TypeScript type definitions
├── components.json               # shadcn/ui configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite configuration
└── package.json                  # Project dependencies
```

## Styling Architecture

### Design System

The frontend uses a **CSS variables-based theme system** for consistent styling:

```css
/* Theme colors (defined in src/index.css) */
--background: 0 0% 98%;           /* Page background */
--foreground: 0 0% 9%;            /* Text color */
--primary: 209 91% 43%;           /* Primary blue */
--card: 0 0% 100%;                /* Card backgrounds */
--border: 0 0% 89%;               /* Border colors */
--muted: 0 0% 96%;                /* Muted backgrounds */
```

### Tailwind Utilities

All components use **Tailwind utility classes** for styling:

```tsx
// Example from PromptDetails.tsx
<div className="p-4 bg-card rounded-lg border">
  <h3 className="text-lg font-semibold mb-4">Configure Prompt</h3>
  <div className="flex flex-col gap-2">
    <Label>Prompt:</Label>
    <Textarea className="min-h-[120px]" />
  </div>
</div>
```

### shadcn/ui Components

Components are built using **shadcn/ui** which provides:
- Accessible components built on Radix UI
- Full control over styling with Tailwind
- Type-safe component APIs
- Customizable variants (via class-variance-authority)

### Custom Fonts

Three custom font families are included:
- **PP Editorial New** - Display font (weights: 100, 900)
- **ABC Oracle** - Sans-serif font (weights: 300, 400, 500, 700)
- **Cambria** - Serif fallback

## Component Architecture

### Main Components

#### `App.tsx`
Main application container with three-column layout:
- Left: `PromptsSidebar` - Task and prompt management
- Center: Form inputs and `PromptDetails`
- Right: `OutputsSidebar` - Prompt outputs

#### `PromptsSidebar.tsx`
Features:
- Task selector dropdown (shadcn/ui Select)
- Task management panel (create, rename, delete tasks)
- Prompt cards with best prompt indicator (⭐)
- Editable prompt names
- "Save All Prompts" action button

#### `PromptDetails.tsx`
Prompt configuration form with:
- Response format textarea (JSON schema)
- Prompt textarea
- Run button with loading state

#### `OutputsSidebar.tsx`
Displays outputs for all prompts in current task:
- Output cards showing prompt results
- Save individual prompt outputs
- "Run All Prompts" button
- "Run Best Prompts" button (requires best prompt selected for all tasks)

### State Management

#### `usePrompts.ts` Hook

Central hook managing all application state:

```typescript
const {
  prompts,              // All prompts across tasks
  filteredPrompts,      // Prompts for selected task
  tasks,                // List of task names
  selectedTask,         // Currently selected task
  selectedPromptIndex,  // Currently selected prompt
  loading,              // Global loading state
  error,                // Error messages
  bestPrompts,          // Map of task -> best prompt ID

  // Actions
  addNewPrompt,
  updatePrompt,
  deletePrompt,
  runPrompt,
  runAllPrompts,
  savePrompt,
  saveAllPrompts,
  setSelectedPromptIndex,
  setSelectedTask,
  addTask,
  deleteTask,
  renameTask,
  setBestPrompt,
  runBestPrompts
} = usePrompts()
```

#### Data Flow

1. **Load prompts** from backend on mount (`/prompts` endpoint)
2. **User interactions** trigger hook actions
3. **API calls** to backend:
   - `POST /test-prompt` - Run single prompt
   - `POST /save-prompt` - Save prompt output
   - `POST /save-all-prompts` - Save all prompts
   - `POST /run-best-prompts` - Run best prompts for all tasks
4. **State updates** trigger re-renders

### Type Definitions

```typescript
// src/types.ts
interface Prompt {
  id: number
  task: string
  name: string
  prompt: string
  model: string
  responseFormat: string
  output: string | null
  loading: boolean
}

interface BestPrompts {
  [task: string]: number  // task name -> prompt ID
}
```

## Development

### Setup

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Key Configuration Files

#### `tailwind.config.ts`
- Custom theme colors, fonts, gradients
- Design tokens (shadows, transitions)
- Plugin configuration (tailwindcss-animate, @tailwindcss/typography)

#### `components.json`
- shadcn/ui configuration
- Component installation settings
- Path aliases (`@/components`, `@/lib`, etc.)

#### `vite.config.ts`
- Path alias: `@/` → `./src`
- React plugin configuration

#### `tsconfig.json`
- TypeScript compiler options
- Path mappings for imports
- References to app and node configs

## Adding New Components

### Using shadcn/ui CLI

```bash
# Add a new component (e.g., Dialog)
npx shadcn@latest add dialog

# Component will be added to src/components/ui/dialog.tsx
```

### Manual Component Creation

```tsx
// src/components/MyComponent.tsx
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export function MyComponent() {
  return (
    <Card className="p-4">
      <Button variant="default">Click me</Button>
    </Card>
  )
}
```

## Styling Guidelines

### Use Tailwind Utilities

✅ **Do:**
```tsx
<div className="flex items-center gap-4 p-6 bg-card rounded-lg border">
```

❌ **Don't:**
```tsx
<div style={{ display: 'flex', padding: '24px' }}>
```

### Use Theme Colors

✅ **Do:**
```tsx
<Button className="bg-primary text-primary-foreground">
```

❌ **Don't:**
```tsx
<Button className="bg-blue-500 text-white">
```

### Use shadcn/ui Components

✅ **Do:**
```tsx
import { Input } from '@/components/ui/input'
<Input type="text" />
```

❌ **Don't:**
```tsx
<input type="text" className="..." />
```

## Path Aliases

The `@/` alias points to `./src`:

```typescript
// Use this:
import { Button } from '@/components/ui/button'
import { usePrompts } from '@/hooks/usePrompts'
import { cn } from '@/lib/utils'

// Instead of:
import { Button } from '../components/ui/button'
import { usePrompts } from '../hooks/usePrompts'
```

## Utility Functions

### `cn()` - Class Name Merger

Combines Tailwind classes intelligently (handles conflicts):

```typescript
import { cn } from '@/lib/utils'

<div className={cn(
  "base-class",
  condition && "conditional-class",
  "override-class"
)} />
```

## Design Tokens

### Gradients
- `bg-gradient-primary` - Primary blue gradient
- `bg-gradient-secondary` - Subtle gray gradient
- `bg-gradient-hero` - Hero section gradient
- `bg-gradient-subtle` - Light background gradient

### Shadows
- `shadow-soft` - Subtle shadow
- `shadow-medium` - Medium shadow
- `shadow-strong` - Strong shadow

### Transitions
- `transition-smooth` - Smooth cubic-bezier
- `transition-bounce` - Bounce effect

## Best Practices

1. **Always use TypeScript types** - No `any` types
2. **Use shadcn/ui components** - Don't recreate basic components
3. **Follow the established patterns** - Check existing components
4. **Use semantic color variables** - `bg-card`, not `bg-white`
5. **Keep components focused** - Single responsibility
6. **Extract reusable logic** - Use hooks for shared state
7. **Test responsiveness** - Ensure mobile works

## Troubleshooting

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules dist
npm install
npm run build
```

### Type Errors

```bash
# Check TypeScript errors
npx tsc --noEmit
```

### Styling Issues

1. Check Tailwind config is correct
2. Verify `@tailwind` directives in `src/index.css`
3. Ensure component uses theme variables
4. Check for CSS class conflicts

## Backend Integration

The frontend expects a backend server running on `http://localhost:8000` with these endpoints:

- `GET /prompts` - Load saved prompts
- `POST /test-prompt` - Run a single prompt
- `POST /save-prompt` - Save prompt output
- `POST /save-all-prompts` - Save all prompts
- `POST /run-best-prompts` - Run best prompts for all tasks

Request/response schemas should match the `Prompt` type definition.
