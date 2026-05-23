# E2E Tests for AI Agents

This directory contains end-to-end tests for the AI Agents chat functionality using Playwright.

## Directory Structure

```
e2e/
├── pages/
│   └── ai-hub-page.ts    # Page Object for AI Hub
├── ai-agents.spec.ts      # Test specifications
└── README.md              # This file
```

## Setup

1. **Install dependencies** (already done):
   ```bash
   pnpm add -D @playwright/test
   pnpm exec playwright install chromium
   ```

2. **Run tests**:
   ```bash
   # Run all tests
   pnpm run test:e2e

   # Run with UI mode (headed browser)
   pnpm run test:e2e:ui

   # Run in headed mode (non-UI)
   pnpm run test:e2e:headed

   # Show test report
   pnpm run test:e2e:report
   ```

## Test Coverage

### Tab Navigation
- Switch between Chat, Image, and TTS tabs
- Verify correct tab is active

### Chat Functionality
- Display empty state when no messages
- Enable/disable send button based on input
- Send messages via button click
- Send messages via Enter key
- Handle Shift+Enter for new lines
- Support multiple messages

### Model Selection
- Display provider and model selectors
- Change model when selecting different provider

### Quick Prompts
- Fill input when clicking quick prompt buttons

### Responsive Design
- Desktop viewport (1280x720)
- Tablet viewport (768x1024)
- Mobile viewport (375x667)

## Writing Tests

### Using Page Object

```typescript
import { test, expect } from '@playwright/test';
import { AIHubPage } from './pages/ai-hub-page';

test('example test', async ({ page }) => {
  const aiHubPage = new AIHubPage(page);
  await aiHubPage.goto();
  await aiHubPage.switchToChatTab();
  
  await aiHubPage.chatInput.fill('Hello');
  await aiHubPage.sendButton.click();
  
  await expect(page.locator('text=Hello')).toBeVisible();
});
```

### Selectors Used

- `role=tab` - Tab navigation (Chat, Image, TTS)
- `textarea` - Chat input field
- `button` with text `→` - Send button
- `text=/Start a conversation/i` - Empty chat state
- `select` - Provider/model dropdowns

## Notes

- Tests run against `http://localhost:5173` (dev server)
- Web server is automatically started by Playwright config
- Screenshots are captured on test failure
- Traces are captured on first retry
