# XinHaiAgents Design System

## 设计理念

### "心海" Sea of Minds

XinHai (心海) represents the ocean of minds - where multiple consciousnesses flow, interact, and evolve together. Our design reflects:

- **Fluidity**: Like water, thoughts and interactions flow naturally
- **Depth**: Layers of meaning and complexity
- **Clarity**: Despite the depth, navigation remains clear
- **Evolution**: Systems grow and adapt organically

## Brand Identity

### Logo Concept

```
心海
XinHai

Visual: A stylized wave/mind ripple
Colors: Deep ocean blue to bright cyan gradient
Shape: Circular, representing wholeness and cycles
```

### Color Palette

#### Primary Colors

| Name | HEX | Usage |
|------|-----|-------|
| Ocean Deep | `#0A1628` | Background, depth |
| Sea Blue | `#1E3A5F` | Cards, containers |
| Wave Cyan | `#00D4FF` | Primary accent, links |
| Mind Coral | `#FF6B6B` | Warnings, alerts |
| Clarity White | `#F0F9FF` | Text, contrast |

#### Secondary Colors

| Name | HEX | Usage |
|------|-----|-------|
| Foam Light | `#E6F7FF` | Hover states |
| Depth Purple | `#4A5568` | Secondary text |
| Success Teal | `#38B2AC` | Success states |
| Agent Glow | `#9F7AEA` | AI/Agent highlights |
| Connection Gold | `#F6E05E` | Network connections |

#### Gradients

```css
/* Primary Gradient */
background: linear-gradient(135deg, #0A1628 0%, #1E3A5F 50%, #00D4FF 100%);

/* Agent Card Gradient */
background: linear-gradient(180deg, rgba(30,58,95,0.9) 0%, rgba(10,22,40,0.95) 100%);

/* Active State Glow */
box-shadow: 0 0 20px rgba(0,212,255,0.3);
```

### Typography

#### Font Stack

```css
/* Headings */
font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;

/* Body */
font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;

/* Code/Monospace */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

#### Type Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| H1 | 48px / 3rem | 700 | Page titles |
| H2 | 36px / 2.25rem | 600 | Section headers |
| H3 | 24px / 1.5rem | 600 | Card titles |
| H4 | 20px / 1.25rem | 500 | Subsection |
| Body | 16px / 1rem | 400 | Main text |
| Small | 14px / 0.875rem | 400 | Labels, meta |
| Tiny | 12px / 0.75rem | 400 | Timestamps |

### Spacing System

```
4px  - xs
8px  - sm
16px - md
24px - lg
32px - xl
48px - 2xl
64px - 3xl
```

### Border Radius

```
4px   - sharp (buttons, inputs)
8px   - soft (cards, panels)
12px  - round (modals)
50%   - circular (avatars, icons)
```

## Design Principles

### 1. Immersive Depth

Create a sense of being underwater/in the mind-space:
- Layered backgrounds with parallax
- Subtle animations suggesting water movement
- Glass-morphism effects for depth

### 2. Flow-Based Navigation

Navigation should feel like currents:
- Smooth transitions between views
- Connection lines showing data flow
- Progress indicators as wave animations

### 3. Agent Visualization

Agents should feel like distinct entities:
- Unique avatars/colors per agent
- Visual connections showing relationships
- Thought bubbles or ripples for activity

### 4. Responsive Clarity

Maintain clarity across all sizes:
- Mobile-first approach
- Touch-friendly interactions (min 44px)
- Collapsible sidebars

## Animation Guidelines

### Timing

```
Instant: 0ms (state changes)
Fast: 150ms (hovers, micro-interactions)
Normal: 300ms (transitions, reveals)
Slow: 500ms (page transitions, major changes)
Ambient: 8-20s (background animations)
```

### Easing

```css
/* Standard */
transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);

/* Enter (decelerate) */
transition-timing-function: cubic-bezier(0, 0, 0.2, 1);

/* Exit (accelerate) */
transition-timing-function: cubic-bezier(0.4, 0, 1, 1);

/* Bounce */
transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Micro-interactions

- **Button hover**: Scale 1.02, glow effect
- **Card hover**: Lift with shadow, slight border glow
- **Input focus**: Border color change, subtle glow
- **Loading**: Wave animation, not spinner
- **Success**: Ripple effect from center

## Component Library

### Buttons

```vue
<!-- Primary Button -->
<XhButton variant="primary" size="md">
  Start Simulation
</XhButton>

<!-- Secondary Button -->
<XhButton variant="secondary" size="sm">
  Configure
</XhButton>

<!-- Ghost Button -->
<XhButton variant="ghost" size="lg">
  Learn More
</XhButton>
```

**States:**
- Default: Solid fill
- Hover: Scale + glow
- Active: Pressed state
- Loading: Wave animation
- Disabled: Opacity 0.5

### Cards

```vue
<XhCard 
  title="Therapy Session"
  subtitle="CBT with anxiety patient"
  :agents="3"
  status="running"
>
  <template #actions>
    <XhButton variant="ghost">View</XhButton>
  </template>
</XhCard>
```

**Features:**
- Glass morphism background
- Border glow on hover
- Status indicator (pulse animation)
- Agent avatars stack

### Agent Avatar

```vue
<XhAgentAvatar 
  name="Therapist"
  role="CBT_Counselor"
  :isActive="true"
  :isSpeaking="false"
/>
```

**States:**
- Idle: Subtle breathing animation
- Active: Glow ring
- Speaking: Sound wave visualization
- Thinking: Ripple effect

### Message Bubble

```vue
<XhMessage
  :agent="message.agent"
  :content="message.content"
  :timestamp="message.timestamp"
  :isCurrentUser="false"
/>
```

**Features:**
- Color-coded by agent
- Smooth appearance animation
- Expandable for long content
- Reactions support

### Network Graph

```vue
<XhNetworkGraph
  :nodes="agents"
  :edges="interactions"
  :layout="'force-directed'"
  @node-click="onAgentClick"
/>
```

**Features:**
- Interactive nodes
- Animated connections
- Zoom and pan
- Mini-map

## Layout Patterns

### Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Sidebar    │  Main Content Area                     │
│  (200px)    │                                        │
│             │  ┌──────────────────────────────────┐ │
│  Logo       │  │  Header + Stats Cards            │ │
│             │  └──────────────────────────────────┘ │
│  Navigation │                                        │
│  - Home     │  ┌──────────┐ ┌──────────┐ ┌───────┐ │
│  - Sessions │  │ Active   │ │ Recent   │ │ Quick │ │
│  - Agents   │  │ Sims     │ │ Activity │ │ Stats │ │
│  - Analytics│  └──────────┘ └──────────┘ └───────┘ │
│  - Settings │                                        │
│             │  ┌──────────────────────────────────┐ │
│  User       │  │ Visualization / Graph            │ │
│  Profile    │  └──────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────┘
```

### Simulation Layout

```
┌─────────────────────────────────────────────────────┐
│  Header: Scenario Name + Controls                    │
├──────────────────┬──────────────────────────────────┤
│                  │                                  │
│  Agent List      │  Conversation Flow               │
│  (250px)         │                                  │
│                  │  ┌────────────────────────────┐ │
│  - Agent 1       │  │ Message 1                  │ │
│  - Agent 2       │  └────────────────────────────┘ │
│  - Agent 3       │  ┌────────────────────────────┐ │
│                  │  │ Message 2                  │ │
│  [+] Add Agent   │  └────────────────────────────┘ │
│                  │                                  │
├──────────────────┼──────────────────────────────────┤
│  Topology View   │  Input / Controls                │
│  (Mini)          │                                  │
└──────────────────┴──────────────────────────────────┘
```

## Dark Mode (Default)

XinHaiAgents uses dark mode as default to reduce eye strain and create an immersive experience:

```css
:root {
  --bg-primary: #0A1628;
  --bg-secondary: #1E3A5F;
  --bg-tertiary: #2D4A6F;
  --text-primary: #F0F9FF;
  --text-secondary: #94A3B8;
  --accent-primary: #00D4FF;
  --accent-secondary: #9F7AEA;
  --border-color: rgba(0, 212, 255, 0.2);
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.15);
}
```

## Accessibility

- **Color Contrast**: Minimum 4.5:1 for text
- **Focus Indicators**: Visible focus rings
- **Screen Readers**: Proper ARIA labels
- **Keyboard Navigation**: Full keyboard support
- **Reduced Motion**: Respect prefers-reduced-motion

## Responsive Breakpoints

```
Mobile:     < 640px
Tablet:     640px - 1024px
Desktop:    1024px - 1440px
Large:      > 1440px
```

## File Structure

```
frontend/src/
├── styles/
│   ├── variables.css      # CSS custom properties
│   ├── animations.css     # Keyframe animations
│   └── utilities.css      # Utility classes
├── components/
│   ├── ui/                # Base UI components
│   │   ├── XhButton.vue
│   │   ├── XhCard.vue
│   │   ├── XhInput.vue
│   │   └── ...
│   ├── agents/            # Agent-related
│   │   ├── XhAgentAvatar.vue
│   │   ├── XhAgentCard.vue
│   │   └── XhAgentList.vue
│   └── visualizations/    # Data viz
│       ├── XhNetworkGraph.vue
│       ├── XhTimeline.vue
│       └── XhMetrics.vue
└── views/
    ├── Dashboard.vue
    ├── Simulation.vue
    ├── Analytics.vue
    └── Settings.vue
```

---

*This design system should evolve with the project. Update as needed.*
