import { Outlet } from '@tanstack/react-router'
import { Container } from '@mui/material'

function App() {
  return (
    <Container maxWidth="lg">
      <Outlet />
    </Container>
  )
}

export default App

