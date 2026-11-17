================================================================================
SMARTCOMMERCE AI: ENTERPRISE MULTIMODAL E-COMMERCE PLATFORM
PRODUCTION-GRADE ENGINEERING & "SHOP CONSTELLATION" DESIGN SPECIFICATION
================================================================================

### 1.1 Design Philosophy: "Floating Constellation on White Marble"
The interface abandons rigid bordered grid tables. Products float as large, heavily-rounded 
white cards (`--radius-cards: 28px`) over Canvas Mist (`#f2f4f5`). 
There are NO harsh borders or dark containers; visual separation is achieved solely through 
dual-layer soft shadows. Saturated color is restricted exclusively to Shop Violet (`#5433eb`) 
for primary submission actions and brand highlights.

### 1.2 Design Tokens
```css
:root {
  /* Colors */
  --color-canvas-mist: #f2f4f5;
  --color-pure-white: #ffffff;
  --color-ink-black: #000000;
  --color-faint-border: #ebebeb;
  --color-muted-gray: #787574;
  --color-cool-stone: #cccccc;
  --color-warm-fog: #acb0aa;
  --color-shop-violet: #5433eb;
  --color-violet-wash: #c0b5f3;
  --color-slate-ink: #332f2d;
  --color-ash-veil: #665a54;

  /* Typography Scale & Tracking (GT Standard system) */
  --font-gt-standard: 'GT Standard', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  --text-caption: 11px;
  --tracking-caption: -0.017em;
  --text-body-sm: 12px;
  --tracking-body-sm: -0.017em;
  --text-body: 14px;
  --tracking-body: -0.014em;
  --text-body-lg: 16px;
  --tracking-body-lg: -0.031em;
  --text-display: 20px;
  --tracking-display: -0.05em;

  /* Spacing */
  --spacing-section: 64px;
  --spacing-element: 12px;

  /* Radii */
  --radius-cards: 28px;
  --radius-inner-image: 20px;
  --radius-pill: 9999px;

  /* Elevation Shadows */
  --shadow-card-soft: rgba(0, 0, 0, 0.1) 0px 4px 6px -1px, rgba(0, 0, 0, 0.1) 0px 2px 4px -2px;
  --shadow-pill-subtle: rgba(0, 0, 0, 0.06) 0px 2px 8px 0px;
  --shadow-violet-glow: rgba(69, 36, 219, 0.34) 0px 4px 24px 0px;
}
```
