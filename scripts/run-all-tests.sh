#!/bin/bash
#
# Run all service tests in the Airlock project
#
# Usage:
#   ./scripts/run-all-tests.sh                    # Run all tests
#   ./scripts/run-all-tests.sh api-key-service    # Run specific service
#   ./scripts/run-all-tests.sh --sequential       # Run sequentially
#   ./scripts/run-all-tests.sh --verbose          # Verbose output
#   ./scripts/run-all-tests.sh --coverage         # Generate coverage reports

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default options
SEQUENTIAL=false
VERBOSE=false
COVERAGE=false
SERVICES=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --sequential)
            SEQUENTIAL=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options] [service1] [service2] ..."
            echo ""
            echo "Options:"
            echo "  --sequential    Run tests sequentially instead of in parallel"
            echo "  --verbose, -v   Show verbose output from pytest"
            echo "  --coverage, -c  Generate coverage reports"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 api-key-service                    # Run specific service"
            echo "  $0 --sequential --verbose             # Run all sequentially with verbose output"
            exit 0
            ;;
        *)
            SERVICES+=("$1")
            shift
            ;;
    esac
done

# Find all services with pytest.ini
find_testable_services() {
    local services_dir="$ROOT_DIR/services"
    local services=()
    
    for dir in "$services_dir"/*; do
        if [[ -d "$dir" && -f "$dir/pytest.ini" ]]; then
            services+=("$(basename "$dir")")
        fi
    done
    
    echo "${services[@]}"
}

# Run tests for a single service
run_service_tests() {
    local service_name="$1"
    local service_dir="$ROOT_DIR/services/$service_name"
    
    if [[ ! -d "$service_dir" ]]; then
        echo "Warning: Service directory not found: $service_name" >&2
        return 1
    fi
    
    echo ""
    echo "========================================"
    echo "Testing: $service_name"
    echo "========================================"
    echo ""
    
    cd "$service_dir"
    
    local pytest_args=("pytest" "tests/features/")
    
    if [[ "$VERBOSE" == "true" ]]; then
        pytest_args+=("-v")
    else
        pytest_args+=("-q")
    fi
    
    if [[ "$COVERAGE" == "true" ]]; then
        pytest_args+=("--cov=src" "--cov-report=html:htmlcov" "--cov-report=term-missing" "--cov-report=xml")
    fi
    
    pytest_args+=("--tb=short")
    
    if python -m "${pytest_args[@]}"; then
        echo "✓ $service_name tests passed"
        return 0
    else
        echo "✗ $service_name tests failed"
        return 1
    fi
}

# Main execution
echo ""
echo "========================================"
echo "Airlock Service Test Runner"
echo "========================================"
echo ""

# Get list of services to test
ALL_SERVICES=($(find_testable_services))

if [[ ${#SERVICES[@]} -gt 0 ]]; then
    # Filter to requested services
    SERVICES_TO_TEST=()
    for requested in "${SERVICES[@]}"; do
        for available in "${ALL_SERVICES[@]}"; do
            if [[ "$requested" == "$available" ]]; then
                SERVICES_TO_TEST+=("$requested")
                break
            fi
        done
    done
    
    if [[ ${#SERVICES_TO_TEST[@]} -eq 0 ]]; then
        echo "Warning: No matching services found. Available services: ${ALL_SERVICES[*]}" >&2
        exit 1
    fi
else
    SERVICES_TO_TEST=("${ALL_SERVICES[@]}")
fi

echo "Services to test: ${SERVICES_TO_TEST[*]}"
echo "Mode: $([ "$SEQUENTIAL" == "true" ] && echo "Sequential" || echo "Parallel")"
echo ""

# Run tests
FAILED=0
PASSED=0

if [[ "$SEQUENTIAL" == "true" ]]; then
    # Run tests sequentially
    for service in "${SERVICES_TO_TEST[@]}"; do
        if run_service_tests "$service"; then
            ((PASSED++))
        else
            ((FAILED++))
        fi
    done
else
    # Run tests in parallel using background jobs
    PIDS=()
    RESULTS=()
    
    for service in "${SERVICES_TO_TEST[@]}"; do
        (
            if run_service_tests "$service"; then
                exit 0
            else
                exit 1
            fi
        ) &
        PIDS+=($!)
        RESULTS+=("$service")
    done
    
    # Wait for all jobs
    for i in "${!PIDS[@]}"; do
        if wait "${PIDS[$i]}"; then
            ((PASSED++))
        else
            ((FAILED++))
        fi
    done
fi

# Summary
echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo ""

TOTAL=$((PASSED + FAILED))
echo "Total: $TOTAL | Passed: $PASSED | Failed: $FAILED"

if [[ $FAILED -eq 0 ]]; then
    echo ""
    echo "All tests passed! ✓"
    
    if [[ "$COVERAGE" == "true" ]]; then
        echo ""
        echo "========================================"
        echo "Coverage Reports Generated"
        echo "========================================"
        echo ""
        
        for service in "${SERVICES_TO_TEST[@]}"; do
            service_dir="$ROOT_DIR/services/$service"
            htmlcov_path="$service_dir/htmlcov/index.html"
            
            if [[ -f "$htmlcov_path" ]]; then
                echo "  $service: $htmlcov_path"
            fi
        done
        
        echo ""
        echo "Open the HTML files in your browser to view detailed coverage reports."
    fi
    
    exit 0
else
    echo ""
    echo "Some tests failed. See output above for details."
    exit 1
fi

