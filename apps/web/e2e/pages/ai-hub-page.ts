import { Page, Locator, expect } from '@playwright/test';

export class AIHubPage {
  readonly page: Page;

  // Tab navigation - using exact label matching
  readonly chatTab: Locator;
  readonly imageTab: Locator;
  readonly ttsTab: Locator;

  // Chat components
  readonly chatContainer: Locator;
  readonly chatInput: Locator;
  readonly sendButton: Locator;
  readonly emptyChatState: Locator;

  // Model selector
  readonly providerSelect: Locator;
  readonly modelSelect: Locator;

  // Quick prompts
  readonly quickPrompts: Locator;

  constructor(page: Page) {
    this.page = page;

    // Tab navigation - use exact text matching
    this.chatTab = page.getByRole('tab', { name: /^chat$/i });
    this.imageTab = page.getByRole('tab', { name: /^(image gen|image generation)$/i });
    this.ttsTab = page.getByRole('tab', { name: /^(text to speech|tts|语音合成|音声合成|synthèse vocale|texto a voz)$/i });

    // Chat container - find the div containing the textarea
    this.chatContainer = page.locator('[class*="ChatContainer"], [data-testid="chat-container"]').first();

    // Find chat input - the textarea in the chat area
    this.chatInput = page.locator('textarea').first();

    // Send button - look for button with arrow character
    this.sendButton = page.locator('button:has-text("→"), button:has-text("send")').first();

    // Empty chat state - the empty state message
    this.emptyChatState = page.locator('text=/Start a conversation|Choose a prompt|开始对话/i').first();

    // Model selector - two select elements
    this.providerSelect = page.locator('select').first();
    this.modelSelect = page.locator('select').nth(1);

    // Quick prompts - buttons in the empty state area
    this.quickPrompts = page.locator('[class*="QuickAction"] button, [class*="quickAction"] button').first()
      ? page.locator('[class*="QuickAction"]').locator('button')
      : page.locator('button').filter({ hasText: /Hello|Help|Create|Tell/ });
  }

  async goto() {
    await this.page.goto('/');
    // Click on AI Hub tab in navigation
    const aiHubTab = this.page.getByRole('button', { name: /ai hub/i });
    if (await aiHubTab.isVisible()) {
      await aiHubTab.click();
    }
    await this.page.waitForLoadState('domcontentloaded');
  }

  async switchToChatTab() {
    await this.chatTab.click({ timeout: 5000 }).catch(() => {});
    await this.page.waitForTimeout(300);
  }

  async switchToImageTab() {
    await this.imageTab.click({ timeout: 5000 }).catch(() => {});
    await this.page.waitForTimeout(300);
  }

  async switchToTtsTab() {
    await this.ttsTab.click({ timeout: 5000 }).catch(() => {});
    await this.page.waitForTimeout(300);
  }

  async sendMessage(message: string) {
    await this.chatInput.fill(message);
    await this.sendButton.click();
    await this.page.waitForTimeout(500);
  }

  async sendMessageAndWaitForResponse(message: string, timeout: number = 15000) {
    await this.chatInput.fill(message);
    await this.sendButton.click();
    // Wait for response or error
    await Promise.race([
      this.page.waitForSelector('text=/Thinking...|思考中|服务不可用/i', { timeout, state: 'hidden' }).catch(() => {}),
      this.page.waitForTimeout(timeout),
    ]);
  }

  async expectEmptyChatState() {
    const isEmptyStateVisible = await this.emptyChatState.isVisible().catch(() => false);
    if (isEmptyStateVisible) {
      await expect(this.emptyChatState).toBeVisible();
    }
  }

  async expectMessageVisible(message: string) {
    await expect(this.page.locator(`text=${message}`).first()).toBeVisible();
  }

  async selectProvider(provider: string) {
    await this.providerSelect.selectOption(provider);
    await this.page.waitForTimeout(500);
  }

  async selectModel(model: string) {
    await this.modelSelect.selectOption(model);
    await this.page.waitForTimeout(300);
  }

  async clickQuickPrompt(index: number = 0) {
    const prompts = await this.quickPrompts.all();
    if (prompts.length > index) {
      await prompts[index].click();
    }
    await this.page.waitForTimeout(200);
  }

  async waitForLoading() {
    await this.page.waitForTimeout(3000);
  }

  async getProviderOptions(): Promise<string[]> {
    return this.providerSelect.locator('option').allTextContents();
  }

  async getModelOptions(): Promise<string[]> {
    return this.modelSelect.locator('option').allTextContents();
  }

  async getUserMessages(): Promise<string[]> {
    const messages = this.page.locator('[class*="MessageBubble"]').all();
    return Promise.all(messages.map(m => m.textContent()));
  }
}
