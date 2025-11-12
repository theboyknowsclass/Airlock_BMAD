# Airlock - Security-First Package Manager

Airlock is a gated package manager designed to prevent supply chain attacks in software dependencies. The system provides automated security and license checks combined with manual verification workflows, comprehensive package tracking, and controlled upgrade management.

## Project Status

**Current Phase:** Implementation - Epic 1: Foundation & Infrastructure

## Architecture

- **Backend:** Microservices architecture with FastAPI (Python)
- **Frontend:** React + TypeScript with Vite
- **Message Broker:** RabbitMQ for event-driven communication
- **Database:** PostgreSQL
- **Workflow Processing:** Celery

## Services

1. **API Gateway** - Request routing and authentication
2. **Auth Service** - Authentication and authorization
3. **User Service** - User management
4. **API Key Service** - API key management
5. **Submission Service** - Package submission handling
6. **Workflow Service** - Approval workflow orchestration
7. **Agents:**
   - Trivy Agent - Security vulnerability scanning
   - License Agent - License validation
   - Review Agent - Manual review workflow
8. **Storage Service** - Artifact storage integration
9. **Registry Service** - Package registry integration (NPM)
10. **Tracking Service** - Package usage tracking
11. **Frontend** - React web application

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 24.x (for frontend development)
- Python 3.12 (for backend development)

### Development Setup

1. **Project Structure:** ✅ Story 1.1 Complete
2. **Docker Compose:** ✅ Story 1.2 Complete
3. **Database Setup:** ⏳ Story 1.3 Pending
4. **RabbitMQ Setup:** ⏳ Story 1.4 Pending
5. **Service Scaffolding:** ⏳ Story 1.5 Pending
6. **Frontend Setup:** ⏳ Story 1.6 Pending
7. **Mock OAuth:** ⏳ Story 1.7 Pending
8. **Shared Libraries:** ⏳ Story 1.8 Pending

### Running the Application

**Development:**
```powershell
# Start all services (production + development overrides)
.\docker-compose-dev.ps1 up

# Start in detached mode
.\docker-compose-dev.ps1 up -Detached

# Build and start
.\docker-compose-dev.ps1 up -Build

# View logs
.\docker-compose-dev.ps1 logs

# Stop services
.\docker-compose-dev.ps1 down

# Rebuild services (after code changes)
.\docker-compose-rebuild.ps1              # Rebuild all services
.\docker-compose-rebuild.ps1 api-gateway  # Rebuild specific service
.\docker-compose-rebuild.ps1 -NoCache     # Rebuild all without cache
```

**Production:**
```powershell
# Start all services
.\docker-compose-prod.ps1 up

# Start in detached mode
.\docker-compose-prod.ps1 up -Detached

# Stop services
.\docker-compose-prod.ps1 down
```

**Note:** The development script runs both `docker-compose.prod.yml` and `docker-compose.dev.yml` together, with dev file providing only overrides and additions (no duplication).

**Development Tools:**
- **RabbitMQ Management UI:** http://localhost:15672 (credentials from .env.dev)
- **pgAdmin:** http://localhost:5050 
  - Email: `admin@airlock.dev` (from .env.dev)
  - Password: `admin` (from .env.dev)
  - To connect to PostgreSQL: Host: `postgres`, Port: `5432`, Database: `${POSTGRES_DB}`, Username: `${POSTGRES_USER}`, Password: `${POSTGRES_PASSWORD}`

## Documentation

- [Product Requirements Document](./docs/PRD.md)
- [Architecture Document](./docs/architecture.md)
- [UX Design Specification](./docs/ux-design-specification.md)
- [Epic Breakdown](./docs/epics.md)

## License

See [LICENSE](./LICENSE) file for details.

