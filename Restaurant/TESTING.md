# Testing Guide

This project uses **Vitest** with browser mode to test Svelte components.

## Test Structure

### Unit Tests
- `src/lib/Table.svelte.test.ts` - Tests for the Table component
- `src/routes/page.svelte.spec.ts` - Tests for the main page

## Running Tests

### Run all tests once
```bash
npm test
```

### Run tests in watch mode (interactive)
```bash
npm run test:unit
```

### Run tests with UI
```bash
npm run test:unit -- --ui
```

## Test Coverage

### Table Component Tests (`Table.svelte.test.ts`)


### Main and MQTT Tests (`page.svelte.test.ts`)