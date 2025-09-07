/**
 * Demo Configuration
 * Controls whether to use mock data or real contracts
 */

// Set to true for demo mode (uses mocks), false for production
export const DEMO_MODE = true;

// Demo app IDs (not real, just for display)
export const DEMO_INSURANCE_APP_ID = 12345n;
export const DEMO_DISPUTE_APP_ID = 67890n;

// Demo wallet connection (simulates connected wallet)
export const DEMO_WALLET_CONNECTED = true;

console.log(`🎭 AgriGuard running in ${DEMO_MODE ? 'DEMO' : 'PRODUCTION'} mode`);
