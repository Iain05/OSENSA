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
 - Rendering
    - Render with correct table numbers
    - Render an input field for food items
    - Render a Place Order button
    - Show initially empty 'Received' section
 - User Interactions
    - Allow typing in input
    - Clear input after order
 - addItem()
    - Add item to received list
    - Add multiple items and display them all

### Main and MQTT Tests (`page.svelte.test.ts`)
 - Rendering
    - Renders 4 tables
    - Renders debug section
 - Connection Status
    - Initially disconnected
 - MQTT Interactions
    - Handles invalid FOOD messages
    - Publish ORDER message when placing order