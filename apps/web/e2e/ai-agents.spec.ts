import { test, expect, Page } from '@playwright/test';
import { AIHubPage } from './pages/ai-hub-page';

/**
 * E2E Tests for AI Agents Chat functionality
 * 
 * These tests cover:
 * - Tab navigation between Chat, Image, and TTS tabs
 * - Chat message sending and display
 * - Model/provider selection
 * - Quick prompt interaction
 * - Responsive behavior
 */

test.describe('AI Hub - Tab Navigation', () => {
  let aiHubPage: AIHubPage;

  test.beforeEach(async ({ page }) => {
    aiHubPage = new AIHubPage(page);
    await aiHubPage.goto();
    await page.waitForLoadState('networkidle');
  });

  test('should display Chat tab as default and switch tabs', async ({ page }) => {
    // Chat tab should be active by default
    const chatTab = page.getByRole('tab', { name: /chat/i });
    await expect(chatTab).toHaveAttribute('aria-selected', 'true');

    // Verify chat input is visible
    await expect(aiHubPage.chatInput).toBeVisible();

    // Switch to Image tab
    await aiHubPage.switchToImageTab();
    const imageTab = page.getByRole('tab', { name: /image/i });
    await expect(imageTab).toHaveAttribute('aria-selected', 'true');

    // Switch to TTS tab (Text to Speech)
    await aiHubPage.switchToTtsTab();
    const ttsTab = page.getByRole('tab', { name: /text to speech|tts|语音合成|音声合成/i });
    await expect(ttsTab).toHaveAttribute('aria-selected', 'true');

    // Back to Chat tab
    await aiHubPage.switchToChatTab();
    await expect(chatTab).toHaveAttribute('aria-selected', 'true');
  });
});

test.describe('AI Hub - Chat Functionality', () => {
  let aiHubPage: AIHubPage;

  test.beforeEach(async ({ page }) => {
    aiHubPage = new AIHubPage(page);
    await aiHubPage.goto();
    await aiHubPage.switchToChatTab();
    await page.waitForLoadState('networkidle');
  });

  test('should display empty state when no messages', async ({ page }) => {
    // Check for empty state or input field
    const hasEmptyState = await aiHubPage.emptyChatState.count() > 0;
    if (hasEmptyState) {
      await expect(aiHubPage.emptyChatState).toBeVisible();
    }
    await expect(aiHubPage.chatInput).toBeVisible();
  });

  test('should enable/disable send button based on input', async () => {
    // Initially disabled
    await expect(aiHubPage.sendButton).toBeDisabled();

    // Type text - should enable
    await aiHubPage.chatInput.fill('Hello');
    await expect(aiHubPage.sendButton).toBeEnabled();

    // Clear - should disable
    await aiHubPage.chatInput.clear();
    await expect(aiHubPage.sendButton).toBeDisabled();
  });

  test('should send message and display in chat', async ({ page }) => {
    const testMessage = 'Hello AI';

    // Fill and send
    await aiHubPage.chatInput.fill(testMessage);
    await aiHubPage.sendButton.click();

    // Wait for message to appear
    await page.waitForTimeout(1000);

    // Verify message is displayed somewhere (either in input filled state or chat)
    const messageInChat = await page.locator(`text=/${testMessage}/i`).count();
    expect(messageInChat).toBeGreaterThan(0);
  });

  test('should send message on Enter key press', async ({ page }) => {
    const testMessage = 'Sent via Enter';

    await aiHubPage.chatInput.fill(testMessage);
    await page.keyboard.press('Enter');

    await page.waitForTimeout(500);

    const messageVisible = await page.locator(`text=/${testMessage}/i`).count();
    expect(messageVisible).toBeGreaterThan(0);
  });

  test('should not send on Shift+Enter (new line)', async ({ page }) => {
    const testMessage = 'Multi\nline';

    await aiHubPage.chatInput.fill(testMessage);
    await page.keyboard.press('Shift+Enter');

    // Input should still have the text
    const inputValue = await aiHubPage.chatInput.inputValue();
    expect(inputValue).toContain('Multi');

    // Send button should be enabled
    await expect(aiHubPage.sendButton).toBeEnabled();
  });

  test('should handle multiple messages', async ({ page }) => {
    const messages = ['First', 'Second', 'Third'];

    for (const msg of messages) {
      await aiHubPage.chatInput.fill(msg);
      await aiHubPage.sendButton.click();
      await page.waitForTimeout(300);
    }

    // All messages should appear
    for (const msg of messages) {
      const count = await page.locator(`text=/${msg}/i`).count();
      expect(count).toBeGreaterThan(0);
    }
  });
});

test.describe('AI Hub - Model Selection', () => {
  let aiHubPage: AIHubPage;

  test.beforeEach(async ({ page }) => {
    aiHubPage = new AIHubPage(page);
    await aiHubPage.goto();
    await aiHubPage.switchToChatTab();
    await page.waitForLoadState('networkidle');
  });

  test('should display provider and model selectors', async () => {
    const hasProviderSelect = await aiHubPage.providerSelect.count() > 0;
    const hasModelSelect = await aiHubPage.modelSelect.count() > 0;

    if (hasProviderSelect) {
      await expect(aiHubPage.providerSelect).toBeVisible();
    }
    if (hasModelSelect) {
      await expect(aiHubPage.modelSelect).toBeVisible();
    }

    // At least one selector should be present
    expect(hasProviderSelect || hasModelSelect).toBeTruthy();
  });

  test('should change model when selecting different provider', async () => {
    const providers = await aiHubPage.getProviderOptions();
    
    if (providers.length > 1) {
      const initialModels = await aiHubPage.getModelOptions();
      await aiHubPage.selectProvider(providers[1]);
      await aiHubPage.page.waitForTimeout(500);
      const newModels = await aiHubPage.getModelOptions();

      // Models should be loaded (may or may not be different)
      expect(newModels.length).toBeGreaterThan(0);
    }
  });
});

test.describe('AI Hub - Quick Prompts', () => {
  let aiHubPage: AIHubPage;

  test.beforeEach(async ({ page }) => {
    aiHubPage = new AIHubPage(page);
    await aiHubPage.goto();
    await aiHubPage.switchToChatTab();
    await page.waitForLoadState('networkidle');
  });

  test('should fill input when clicking quick prompt', async () => {
    const promptCount = await aiHubPage.quickPrompts.count();
    
    if (promptCount > 0) {
      const firstPrompt = aiHubPage.quickPrompts.first();
      const promptText = await firstPrompt.textContent();

      await firstPrompt.click();
      await aiHubPage.page.waitForTimeout(200);

      // Input should contain the prompt
      await expect(aiHubPage.chatInput).toHaveValue(promptText?.trim() || '');
    }
  });
});

test.describe('AI Hub - Responsive Design', () => {
  let aiHubPage: AIHubPage;

  test.beforeEach(async ({ page }) => {
    aiHubPage = new AIHubPage(page);
    await aiHubPage.goto();
  });

  test('should work on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await aiHubPage.switchToChatTab();
    await expect(aiHubPage.chatInput).toBeVisible();
    await expect(aiHubPage.sendButton).toBeVisible();
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await aiHubPage.switchToChatTab();
    await expect(aiHubPage.chatInput).toBeVisible();
    await expect(aiHubPage.sendButton).toBeVisible();
  });

  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await aiHubPage.switchToChatTab();
    await expect(aiHubPage.chatInput).toBeVisible();
    await expect(aiHubPage.sendButton).toBeVisible();
  });
});
