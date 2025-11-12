# Airlock Frontend

React + TypeScript frontend application for the Airlock package management system.

## Tech Stack

- **React** 19.2.0 - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Material UI** - Component library
- **TanStack Router** - Type-safe routing
- **TanStack Query** - Server state management
- **Zustand** - Global state management
- **React Hook Form** - Form handling
- **Axios** - HTTP client
- **Storybook** - Component testing
- **Vitest** - Unit testing
- **Cucumber.js** - BDD testing
- **axe-core** - Accessibility testing

## Getting Started

### Prerequisites

- Node.js 24.x or later
- npm

### Installation

```bash
npm install --legacy-peer-deps
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview

```bash
npm run preview
```

### Testing

```bash
# Run unit tests
npm test

# Run tests with UI
npm run test:ui

# Run tests in watch mode
npm run test:watch

# Run Storybook
npm run storybook
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── atoms/          # Basic building blocks
│   │   ├── molecules/      # Simple component groups
│   │   ├── organisms/      # Complex UI sections
│   │   └── templates/      # Page layouts
│   ├── pages/              # Full page components
│   ├── services/           # API services
│   ├── store/              # Zustand stores
│   ├── utils/              # Utility functions
│   ├── types/              # TypeScript types
│   ├── hooks/              # Custom React hooks
│   └── config/             # Configuration files
├── .storybook/             # Storybook configuration
└── public/                 # Static assets
```

## Atomic Design Pattern

The application follows the atomic design pattern:

- **Atoms**: Smallest components (use Material UI directly)
- **Molecules**: Simple combinations of atoms
- **Organisms**: Complex sections (DataTable, Navigation)
- **Templates**: Page layouts (DashboardLayout, FormLayout)
- **Pages**: Full page components (HomePage, SubmissionPage)

**Note**: We use Material UI components directly rather than creating unnecessary wrappers. Custom components should add value (custom styling, logic, or composition).

## Path Aliases

The following path aliases are configured:

- `@/` - `src/`
- `@/components` - `src/components`
- `@/pages` - `src/pages`
- `@/services` - `src/services`
- `@/store` - `src/store`
- `@/utils` - `src/utils`
- `@/types` - `src/types`
- `@/hooks` - `src/hooks`
- `@/config` - `src/config`

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Docker

Build the Docker image:

```bash
docker build -t airlock-frontend .
```

Run the container:

```bash
docker run -p 80:80 airlock-frontend
```

## Testing

### Unit Tests

Unit tests are co-located with components:

```
components/atoms/Button/
  Button.tsx
  Button.test.tsx
  Button.stories.tsx
```

### Storybook

Storybook is used for component testing and documentation:

```bash
npm run storybook
```

### BDD Tests

BDD tests using Cucumber.js are located in `features/`:

```bash
npm test
```

### Accessibility Tests

Accessibility testing is integrated with Storybook using axe-core.

## License

MIT
