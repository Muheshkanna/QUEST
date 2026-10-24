# DESIGN.md — QUEST Visual Direction & Design System

<!-- impeccable:design-schema 1 -->

## 1. Brand Identity & Creative Direction

**Brand**: QUEST — A premium fantasy RPG-inspired educational adventure.
**Tone**: Atmospheric, heroic, motivating, scholarly yet adventurous. Blends the gravitas of ancient arcanum archives with the sleek, focused ergonomics of a modern command center.
**Art Direction**:
- **Atmospheric Realms**: Deep cosmic skies, ancient limestone and gilded sanctuary halls, bioluminescent flora, and crystalline celestial orreries.
- **Restrained Arcana**: Magical cues are purposeful and tactile (subtle gold ambient glows, prismatic celestial borders, faint starlight particle drifts) rather than chaotic visual clutter.
- **Clarity Over Clutter**: The gamification elements amplify motivation and comprehension without obscuring study goals, stats, or learning milestones.

---

## 2. Color System & Roles

The color palette is derived directly from the canonical brand guidelines, structured into dark-mode background strata, interactive accents, state indicators, and realm signatures.

### Primary Brand Palette
- **Midnight Navy (`#101B35`)**: The core dark void; primary ground and canvas background.
- **Deep Abyss (`#0B1327`)**: Recessed canvas, sidebar rails, and subtle sunken wells.
- **Sapphire (`#193D65`)**: Elevated structural surfaces, card backgrounds, navigation containers.
- **Antique Gold (`#D9B66F`)**: Primary prestige accent; used for XP bars, rank seals, streak crowns, primary CTAs, and active highlights.
- **Parchment (`#F1E8D6`)**: High-contrast, warm legible text and primary narrative headings.
- **Emerald (`#28745B`)**: Life, resilience, mastery badges, completed quests, and successful checks.
- **Mystic Violet (`#9C8AD6`)**: Arcane knowledge, mana/focus meters, special challenge nodes, and celestial wisdom.

### Design Tokens (CSS Variables)

```css
:root {
  /* Brand Primitives */
  --quest-midnight: #101B35;
  --quest-abyss: #0B1327;
  --quest-sapphire: #193D65;
  --quest-sapphire-light: #235288;
  --quest-gold: #D9B66F;
  --quest-gold-glow: rgba(217, 182, 111, 0.25);
  --quest-gold-muted: #8E743F;
  --quest-parchment: #F1E8D6;
  --quest-parchment-muted: #B8B0A2;
  --quest-parchment-faint: #7A746B;
  --quest-emerald: #28745B;
  --quest-emerald-glow: rgba(40, 116, 91, 0.28);
  --quest-violet: #9C8AD6;
  --quest-violet-glow: rgba(156, 138, 214, 0.25);

  /* Semantic Surfaces */
  --surface-base: var(--quest-midnight);
  --surface-sunken: var(--quest-abyss);
  --surface-card: rgba(25, 61, 101, 0.65);
  --surface-card-hover: rgba(35, 82, 136, 0.75);
  --surface-card-border: rgba(217, 182, 111, 0.22);
  --surface-card-border-glow: rgba(217, 182, 111, 0.5);
  --surface-overlay: rgba(11, 19, 39, 0.85);

  /* Text & Ink */
  --text-primary: var(--quest-parchment);
  --text-secondary: var(--quest-parchment-muted);
  --text-tertiary: var(--quest-parchment-faint);
  --text-accent: var(--quest-gold);

  /* Borders & Dividers */
  --border-subtle: rgba(217, 182, 111, 0.12);
  --border-medium: rgba(217, 182, 111, 0.28);
  --border-strong: rgba(217, 182, 111, 0.6);

  /* Shadows & Illuminations */
  --shadow-sm: 0 2px 4px rgba(5, 10, 22, 0.5);
  --shadow-md: 0 4px 16px rgba(5, 10, 22, 0.65), 0 0 1px rgba(217, 182, 111, 0.2);
  --shadow-lg: 0 10px 32px rgba(5, 10, 22, 0.8), 0 0 20px rgba(217, 182, 111, 0.12);
  --shadow-glow-gold: 0 0 24px rgba(217, 182, 111, 0.35);
  --shadow-glow-emerald: 0 0 20px rgba(40, 116, 91, 0.4);
  --shadow-glow-violet: 0 0 20px rgba(156, 138, 214, 0.35);

  /* Spacing Scale */
  --space-2xs: 4px;
  --space-xs: 8px;
  --space-sm: 12px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* Corner Radii (Chiseled yet ergonomic) */
  --radius-xs: 3px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Typography Stacks */
  --font-display: 'Cinzel', 'Cinzel Decorative', Georgia, 'Times New Roman', serif;
  --font-body: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

---

## 3. Typography Hierarchy

| Style / Role | Font Family | Size / Line Height | Weight | Letter Spacing | Case | Usage |
|---|---|---|---|---|---|---|
| **Display Hero (H1)** | `Cinzel` | 32px - 40px / 1.15 | 700 Bold | +0.05em | Title / Small-caps | Command Center titles, Realm titles |
| **Section Header (H2)** | `Cinzel` | 20px - 24px / 1.25 | 600 SemiBold | +0.03em | Title | Quest blocks, Mastery overview |
| **Widget Title (H3)** | `Plus Jakarta Sans` | 15px - 17px / 1.3 | 700 Bold | +0.01em | None | Card headers, module labels |
| **Body Primary** | `Plus Jakarta Sans` | 14px - 15px / 1.6 | 400 Regular | 0 | None | Descriptions, quest lore, instructions |
| **Body Accent / Strong** | `Plus Jakarta Sans` | 14px / 1.5 | 600 SemiBold | 0 | None | Key metadata, student status |
| **Caption / Kicker** | `Cinzel` or `Plus Jakarta Sans` | 11px - 12px / 1.4 | 600 SemiBold | +0.08em | Uppercase | Category tags, subheadings, rarity |
| **Numerical Data / Badges**| `Plus Jakarta Sans` | 13px - 14px / 1 | 700 Bold | +0.02em | None | XP counts, level indicators, streak stats |

---

## 4. Component Token Specifications

### 4.1 Buttons & Interactive Actions
- **Primary Action ("Continue Adventure")**:
  - Background: Linear gradient `(135deg, #D9B66F 0%, #B89246 100%)`.
  - Color: `#101B35` (maximum contrast ink).
  - Border: 1px solid rgba(255, 255, 255, 0.4), subtle inner highlight.
  - Hover: Scale `1.02`, glow `0 0 20px rgba(217, 182, 111, 0.45)`.
  - Active: Scale `0.98`.
- **Secondary Action ("Inspect Quest", "Review Lore")**:
  - Background: `rgba(25, 61, 101, 0.4)`.
  - Color: `#F1E8D6`.
  - Border: 1px solid rgba(217, 182, 111, 0.3).
  - Hover: Background `rgba(35, 82, 136, 0.65)`, border `rgba(217, 182, 111, 0.6)`.
- **Ghost Action**:
  - Background: Transparent.
  - Color: `#B8B0A2`.
  - Hover: Color `#F1E8D6`, text glow.

### 4.2 Cards & Containers
- **Standard Card Surface**:
  - Background: `rgba(25, 61, 101, 0.45)` with backdrop filter `blur(12px)`.
  - Border: 1px solid rgba(217, 182, 111, 0.18).
  - Corner Accent: Inset top-gold edge or ornamental notch highlights.
  - Padding: 20px - 24px desktop, 16px mobile.
  - Shadow: `0 8px 24px rgba(5, 10, 22, 0.6)`.
- **Active / Featured Card (Daily Trial)**:
  - Border: 1px solid rgba(217, 182, 111, 0.45).
  - Ambient illumination: Subtle radial gradient originating from top-right in Mystic Violet or Antique Gold.

### 4.3 Progress Indicators & Gauges
- **XP Bar (Level Progress)**:
  - Track: Height 10px, background `rgba(11, 19, 39, 0.8)`, border `1px solid rgba(217, 182, 111, 0.2)`, radius `var(--radius-full)`.
  - Fill: Linear gradient `(90deg, #D9B66F 0%, #F5DE9C 100%)`.
  - Glow: Active leading edge pip with pulse animation.
- **Mastery Rings**:
  - Circular SVG indicator with stroke width 4px–6px.
  - Emerald (`#28745B`) for mastered topics, Sapphire-Violet for in-progress.

### 4.4 Badges & Rarity Tags
- **Common / Scholar**: Border `rgba(184, 176, 162, 0.3)`, text `#B8B0A2`.
- **Rare / Master (Emerald)**: Border `rgba(40, 116, 91, 0.5)`, background `rgba(40, 116, 91, 0.2)`, text `#7AE0BF`.
- **Epic / Mystic (Violet)**: Border `rgba(156, 138, 214, 0.5)`, background `rgba(156, 138, 214, 0.2)`, text `#D4C9FF`.
- **Legendary / Paragon (Gold)**: Border `rgba(217, 182, 111, 0.6)`, background `rgba(217, 182, 111, 0.2)`, text `#F5DE9C`, subtle box-shadow glow.

---

## 5. Dashboard Composition & Layout Topology

The Quest Command Center is composed of a responsive 3-column / structured grid architecture:

```
+---------------------------------------------------------------------------------------------------+
|  QUEST TOPBAR / HUD: Brand Crest | Active Realm | Streak Fire | Level & XP Meter | Student Avatar |
+---------------------------------------------------------------------------------------------------+
|  HERO BANNER: "Continue Adventure" Primary Callout & Ambient Realm Portal                         |
+---------------------------------------------------------------+-----------------------------------+
|  MAIN ADVENTURE LANE (2 cols on desktop)                      |  CHARACTER CODEX (1 col desktop)  |
|                                                               |                                   |
|  [Daily Trial Challenge Card]                                 |  [Student Profile & Archetype]    |
|  - Topic, difficulty, XP reward, timer, CTA                   |  - Level, Class Title, Avatar     |
|                                                               |  - Total XP, Next Milestone       |
|  [The Three Core Realm Gates]                                 |                                   |
|  1. Enchanted Forest (Foundations & Natural Sciences)         |  [Streak & Activity Hearth]       |
|  2. Temple of Wisdom (Logic, Math & Ancient Arcana)           |  - Current Streak, Freeze shields |
|  3. Celestial Frontier (Advanced Code, Cosmic Exploration)    |                                   |
|                                                               |  [Topic Mastery Matrix]           |
|  [Recent Achievements & Badges Vault]                         |  - Skill tree radar / status bars |
|  - Unlocked medals, next unlockable preview                   |                                   |
+---------------------------------------------------------------+-----------------------------------+
```

### 5.1 Three Realm Cards
1. **The Enchanted Forest**:
   - Signature Palette: Emerald (`#28745B`) + Forest Moss + Antique Gold borders.
   - Theme: Foundational learning, living biology, ecological discovery.
   - Lore Tag: *Verdant Archives of the First Sprouts*.
2. **The Temple of Wisdom**:
   - Signature Palette: Antique Gold (`#D9B66F`) + Sandstone Parchment + Deep Sapphire.
   - Theme: Logic, mathematics, architecture, philosophy, ancient puzzles.
   - Lore Tag: *The Sunken Halls of Axioms*.
3. **The Celestial Frontier**:
   - Signature Palette: Mystic Violet (`#9C8AD6`) + Deep Starlight Abyss + Cosmic Sapphire.
   - Theme: Computer science, astrophysics, algorithmic mastery, future technologies.
   - Lore Tag: *The Astral Forge of Stellar Architects*.

---

## 6. Accessibility & System Constraints

- **Contrast Ratios**:
  - Primary text (`#F1E8D6`) on Midnight Navy (`#101B35`) achieves **11.4:1** contrast (exceeding WCAG AAA).
  - Secondary text (`#B8B0A2`) on Midnight Navy achieves **6.2:1** contrast (exceeding WCAG AA).
  - Gold Action ink (`#101B35`) on Antique Gold (`#D9B66F`) achieves **8.1:1** contrast (exceeding WCAG AAA).
- **Keyboard Navigation**:
  - Explicit high-visibility focus ring: `2px solid #D9B66F` with `3px` offset (`rgba(16, 27, 53, 0.9)` backdrop).
  - Full tab-index flow through topbar HUD, Continue Adventure CTA, Realm Cards, and Daily Quests.
  - Skip links for main content.
- **Reduced Motion (`prefers-reduced-motion: reduce`)**:
  - Ambient particle drifting disabled.
  - Scale transforms on hover removed in favor of instant subtle border illumination.
  - Confetti and celebration cues replaced with polite static notification badges.
- **Responsive Breakpoints**:
  - Mobile (`< 768px`): Single column stack, compact HUD with collapsible stats drawer, vertical realm card carousel.
  - Tablet (`768px - 1024px`): 2-column layout with character codex below realm cards.
  - Desktop (`> 1024px`): Full panoramic 3-column command dashboard.
