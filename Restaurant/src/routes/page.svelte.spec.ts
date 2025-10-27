import { page } from '@vitest/browser/context';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Page from './+page.svelte';

// Create a mock MQTT client
let mockClient: any;
let connectCallback: Function;
let messageCallback: Function;

vi.mock('mqtt', () => ({
	default: {
		connect: vi.fn(() => {
			mockClient = {
				on: vi.fn((event: string, handler: Function) => {
					if (event === 'connect') {
						connectCallback = handler;
					} else if (event === 'message') {
						messageCallback = handler;
					}
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
		vi.clearAllMocks();
		connectCallback = () => {};
		messageCallback = () => {};
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
		it('should handle invalid FOOD message gracefully', async () => {
			render(Page);
			connectCallback();
			
			const invalidBuffer = { toString: () => 'invalid json' };
			messageCallback('FOOD', invalidBuffer);

			const errorMessage = page.getByText(/Bad FOOD payload/);
			await expect.element(errorMessage).toBeInTheDocument();
		});

		it('should publish ORDER message when user places order', async () => {
			render(Page);
			connectCallback();

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
