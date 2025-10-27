import { page } from '@vitest/browser/context';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Page from './+page.svelte';

// Create a mock MQTT client
let mockClient: any;
let eventHandlers: Record<string, Function> = {};

vi.mock('mqtt', () => ({
	default: {
		connect: vi.fn(() => {
			mockClient = {
				on: vi.fn((event: string, handler: Function) => {
					eventHandlers[event] = handler;
				}),
				subscribe: vi.fn((topic: string, callback: Function) => {
					callback(null); // Success
				}),
				publish: vi.fn(),
				end: vi.fn()
			};
			return mockClient;
		})
	}
}));

describe('/+page.svelte', () => {
	beforeEach(() => {
		eventHandlers = {};
	});

	describe('Rendering', () => {
		it('should render the page title', async () => {
			render(Page);

			const heading = page.getByRole('heading', { level: 1 });
			await expect.element(heading).toBeInTheDocument();
			await expect.element(heading).toHaveTextContent('The Mosquitto Diner');
		});

		it('should render the welcome message', async () => {
			render(Page);

			const welcomeText = page.getByText(/Welcome to the Mosquitto Diner/);
			await expect.element(welcomeText).toBeInTheDocument();
		});

		it('should render 4 table components', async () => {
			render(Page);

			const table1 = page.getByText('Table 1');
			const table2 = page.getByText('Table 2');
			const table3 = page.getByText('Table 3');
			const table4 = page.getByText('Table 4');

			await expect.element(table1).toBeInTheDocument();
			await expect.element(table2).toBeInTheDocument();
			await expect.element(table3).toBeInTheDocument();
			await expect.element(table4).toBeInTheDocument();
		});

		it('should render the debug messages section', async () => {
			render(Page);

			const debugHeading = page.getByRole('heading', { name: 'Debug Messages' });
			await expect.element(debugHeading).toBeInTheDocument();
		});
	});

	describe('Connection Status', () => {
		it('should show disconnected status initially', async () => {
			render(Page);

			const disconnectedText = page.getByText('Disconnected');
			await expect.element(disconnectedText).toBeInTheDocument();
		});
	});

	describe('MQTT Interactions', () => {
		it('should display received food items when MQTT broker sends valid FOOD message', async () => {
			render(Page);

			// Simulate MQTT connection
			eventHandlers['connect']();

			// Simulate receiving a FOOD message
			const foodMessage = JSON.stringify({ table: 1, food: 'Pizza' });
			eventHandlers['message']('FOOD', Buffer.from(foodMessage));

			// Check that the food item appears in Table 1
			const foodItem = page.getByText('Pizza');
			await expect.element(foodItem).toBeInTheDocument();
		});

		it('should handle invalid FOOD message gracefully', async () => {
			render(Page);
			eventHandlers['connect']();
			eventHandlers['message']('FOOD', Buffer.from('invalid json'));

			const errorMessage = page.getByText(/Bad FOOD payload/);
			await expect.element(errorMessage).toBeInTheDocument();
		});

		it('should publish ORDER message when user places order', async () => {
			render(Page);
			eventHandlers['connect']();

			const inputs = page.getByPlaceholder('Food item');
			const inputElements = await inputs.all();
			await inputElements[0].fill('Burger');

			const buttons = page.getByRole('button', { name: 'Place Order' });
			const buttonElements = await buttons.all();
			await buttonElements[0].click();

			expect(mockClient.publish).toHaveBeenCalledWith(
				'ORDER',
				JSON.stringify({ food: 'Burger', table: 1 })
			);
		});
	});
});
