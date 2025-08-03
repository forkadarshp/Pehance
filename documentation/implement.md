# Frontend Revamp Action Plan - Mantine UI Integration

## 1. Objectives

- Transform the current MVP UI into a polished, production-grade experience using Mantine UI.
- Leverage Mantine's 120+ components and 70+ hooks for rapid development.
- Align visual design with modern web trends while preserving usability and accessibility.
- Embed brand messaging: **"Built with Pehance."**

## 2. Design & Brand System with Mantine

1. **Mantine Theme Configuration**
   - Primary: Deep Navy `#0F172A`
   - Accent: Electric Indigo `#6366F1`
   - Utilize Mantine's color system with custom brand colors
   - Configure responsive breakpoints and spacing scale
2. **Typography**
   - Leverage Mantine's built-in typography system
   - Heading font: `Inter` (variable) — clean, high-legibility
   - Body font: `Inter` 400/500
3. **Component Tokens**
   - Radius: Mantine's default radius system
   - Spacing scale: Mantine's spacing tokens
4. **Logo & Tagline**
   - Add footer badge: "Built with Pehance — Prompt Engineering Excellence."

## 3. Layout & UX Overhaul with Mantine Components

| Page Section            | Mantine Components Used                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| **Hero**                | `Stack`, `Title`, `Text`, `Button` - Minimal hero with gradient background               |
| **Prompt Panel**        | `Textarea`, `Grid`, `Paper`, `LoadingOverlay` - Responsive layout with loading states    |
| **Analytics Dashboard** | `Grid`, `Card`, `Badge`, `Group` - 4-grid responsive layout with Mantine card components |
| **Footer**              | `Group`, `ActionIcon`, `Text` - Dark strip with brand badge and theme toggle             |

## 4. Component Migration (Next.js 15 + Mantine UI v8)

- **Replace Custom Components**: Migrate from custom atoms to Mantine components
  - `Button` → `@mantine/core/Button`
  - `Card` → `@mantine/core/Card`
  - `Badge` → `@mantine/core/Badge`
  - `LoadingSpinner` → `@mantine/core/Loader`
- **Leverage Mantine Hooks**: Replace custom logic with Mantine hooks
  - Theme switching: `useMantineColorScheme`
  - Form handling: `@mantine/form`
  - Notifications: `@mantine/notifications`
- **Server Components**: Convert pages to Server Components where possible
- **Dark Mode**: Use Mantine's built-in `ColorSchemeProvider` and theme system

## 5. Mantine-Specific Features Integration

- **Responsive Design**: Utilize Mantine's responsive props and breakpoint system
- **Accessibility**: Leverage Mantine's built-in WCAG 2.1 AA compliance
- **Form Management**: Integrate `@mantine/form` for robust form handling
- **Icons**: Use `@tabler/icons-react` for consistent iconography
- **Styling**: Use Mantine's CSS-in-JS solution with PostCSS preset

## 6. Performance & SEO Enhancements

- Replace standard images with `next/image` and enable **priority** for LCP images
- Leverage **Incremental Static Regeneration** for landing page content
- **Bundle Optimization**: Tree-shake unused Mantine components
- Enable **Turbopack** in development for faster builds
- **Mantine Styles**: Optimize CSS delivery with Mantine's CSS extraction

## 7. Accessibility (WCAG 2.1 AA) - Enhanced with Mantine

- **Built-in Accessibility**: Leverage Mantine's accessibility-first component design
- **Keyboard Navigation**: All Mantine components support keyboard navigation out of the box
- **ARIA Labels**: Mantine components include proper ARIA attributes
- **Color Contrast**: Use Mantine's color system for compliant contrast ratios
- **Screen Reader Support**: Enhanced with Mantine's semantic HTML structure

## 8. Quality Assurance

- **Unit & Integration Tests** with Jest + React Testing Library + Mantine Testing Library
- **E2E Tests** with Playwright (core flows)
- **Mantine Component Testing**: Test Mantine component interactions and states
- Automated Lighthouse CI in GitHub Actions

## 9. Rollout Timeline - Mantine Migration

| Phase               | Duration | Deliverables                                        |
| ------------------- | -------- | --------------------------------------------------- |
| Mantine Setup       | **2 d**  | Install packages, configure theme, PostCSS setup    |
| Component Migration | **4 d**  | Replace custom components with Mantine equivalents  |
| Page Integration    | **3 d**  | Hero, prompt panel, analytics, footer with Mantine  |
| Advanced Features   | **2 d**  | Forms, notifications, modals, advanced interactions |
| Perf & SEO          | **2 d**  | Image optimization, caching, Lighthouse ≥ 90        |
| QA & Polish         | **2 d**  | Tests, accessibility audit, copy review             |

## 10. Success Metrics

- Lighthouse scores: **Performance ≥ 90**, **Accessibility ≥ 95**
- CLS < 0.1, INP < 200 ms on desktop/mobile
- ≤ 120 KB JS on initial load (including Mantine core)
- **Developer Experience**: Faster development with Mantine's component library

## 11. Mantine-Specific Dependencies

```json
{
  "dependencies": {
    "@mantine/core": "^8.2.1",
    "@mantine/hooks": "^8.2.1",
    "@mantine/form": "^8.2.1",
    "@mantine/notifications": "^8.2.1",
    "@tabler/icons-react": "^3.34.1"
  },
  "devDependencies": {
    "postcss-preset-mantine": "^1.18.0",
    "postcss-simple-vars": "^7.0.1"
  }
}
```

## 12. Key Mantine Advantages

- **120+ Components**: Comprehensive component library reduces development time
- **70+ Hooks**: Powerful hooks for common UI patterns and behaviors
- **Built-in Accessibility**: WCAG 2.1 AA compliance out of the box
- **Dark Theme Support**: Seamless light/dark mode switching
- **TypeScript Support**: Full TypeScript support with excellent IntelliSense
- **Performance**: CSS-in-JS with zero runtime overhead
- **Flexibility**: Easy customization while maintaining design consistency

## 13. Next Steps

1. Approve this updated plan with Mantine integration
2. Spin up `feature/mantine-migration` branch
3. Begin Mantine setup and theme configuration
4. Migrate existing components to Mantine equivalents

## 14. Resources

- [Mantine Documentation](https://mantine.dev/)
- [Mantine Components Gallery](https://mantine.dev/components/)
- [Mantine Hooks Reference](https://mantine.dev/hooks/)
- [PostCSS Preset Mantine](https://mantine.dev/styles/postcss-preset/)
