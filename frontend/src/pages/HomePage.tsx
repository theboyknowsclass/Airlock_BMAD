import { Box, Typography, Paper } from '@mui/material'

function HomePage() {
  return (
    <Box sx={{ my: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Airlock
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Package Management System
        </Typography>
        <Typography variant="body2" sx={{ mt: 2 }}>
          Welcome to Airlock. This is the home page.
        </Typography>
      </Paper>
    </Box>
  )
}

export default HomePage

