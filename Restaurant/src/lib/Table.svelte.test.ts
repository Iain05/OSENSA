import { page } from '@vitest/browser/context';
import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Table from './Table.svelte';

describe('Table Component', () => {
	describe('Rendering', () => {
		it('should render the table with the correct table number', async () => {
			render(Table, { tableNumber: 3 });
			
			const heading = page.getByText('Table 3');
			await expect.element(heading).toBeInTheDocument();
		});

		it('should render an input field for food items', async () => {
			render(Table, { tableNumber: 1 });
			
			const input = page.getByPlaceholder('Food item');
			await expect.element(input).toBeInTheDocument();
			await expect.element(input).toHaveAttribute('type', 'text');
			await expect.element(input).toHaveAttribute('maxlength', '50');
		});

		it('should render a "Place Order" button', async () => {
			render(Table, { tableNumber: 1 });
			
			const button = page.getByRole('button', { name: 'Place Order' });
			await expect.element(button).toBeInTheDocument();
		});

		it('should show "Received" section with no items initially', async () => {
			render(Table, { tableNumber: 1 });
			
			const receivedHeading = page.getByText('Received');
			const noItems = page.getByText('—');
			await expect.element(receivedHeading).toBeInTheDocument();
			await expect.element(noItems).toBeInTheDocument();
		});
	});

	describe('User Interactions', () => {
		it('should allow typing in the input field', async () => {
			render(Table, { tableNumber: 1, connected: true });
			
			const input = page.getByPlaceholder('Food item');
			await input.fill('Pizza');
			
			await expect.element(input).toHaveValue('Pizza');
		});

		it('should clear input after placing order', async () => {
			render(Table, { tableNumber: 1, connected: true });
			
			const input = page.getByPlaceholder('Food item');
			await input.fill('Salad');
			
			const button = page.getByRole('button', { name: 'Place Order' });
			await button.click();
			
			await expect.element(input).toHaveValue('');
		});
	});

	describe('addItem Method', () => {
		it('should add items to the received list', async () => {
			const { component } = render(Table, { tableNumber: 1 });
			
			component.addItem('Pasta');
			
			const item = page.getByText('Pasta');
			await expect.element(item).toBeInTheDocument();
		});

		it('should add multiple items and display them all', async () => {
			const { component } = render(Table, { tableNumber: 1 });
			
			component.addItem('Pizza');
			component.addItem('Burger');
			component.addItem('Fries');
			
			const pizza = page.getByText('Pizza');
			const burger = page.getByText('Burger');
			const fries = page.getByText('Fries');
			
			await expect.element(pizza).toBeInTheDocument();
			await expect.element(burger).toBeInTheDocument();
			await expect.element(fries).toBeInTheDocument();
		});
	});
});
