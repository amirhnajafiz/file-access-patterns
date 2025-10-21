.PHONY: test chmod-tests run-tests

# Main target to run all tests
test: chmod-tests run-tests

# Make all test scripts executable
chmod-tests:
	@echo "Making test scripts executable..."
	@chmod +x tests/image-build.sh
	@chmod +x tests/e2e.sh
	@chmod +x tests/cleanup.sh
	@echo "Done setting permissions."
	@echo ""

# Run all test scripts in order
run-tests:
	@echo "=========================================="
	@echo "Running tests/image-build.sh"
	@echo "=========================================="
	@bash tests/image-build.sh
	@echo ""
	@echo "=========================================="
	@echo "Running tests/e2e.sh"
	@echo "=========================================="
	@bash tests/e2e.sh
	@echo ""
	@echo "=========================================="
	@echo "Running tests/cleanup.sh"
	@echo "=========================================="
	@bash tests/utils/cleanup.sh
	@echo ""
	@echo "All tests completed!"
