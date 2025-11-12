import { createRouter, createRootRoute, createRoute } from '@tanstack/react-router'
import App from '../App'
import HomePage from '../pages/HomePage'

// Create root route
const rootRoute = createRootRoute({
  component: App,
})

// Create index route
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

// Create route tree
const routeTree = rootRoute.addChildren([indexRoute])

// Create router
export const router = createRouter({ 
  routeTree,
})

// Register router types for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
