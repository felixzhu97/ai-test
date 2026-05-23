import { test as base, Page, Locator } from '@playwright/test';

export class ButtonPage {
  readonly page: Page;

  // Primary buttons
  readonly primarySmallBtn: Locator;
  readonly primaryMediumBtn: Locator;
  readonly primaryLargeBtn: Locator;

  // Secondary buttons
  readonly secondarySmallBtn: Locator;
  readonly secondaryMediumBtn: Locator;
  readonly secondaryLargeBtn: Locator;

  // Ghost buttons
  readonly ghostSmallBtn: Locator;
  readonly ghostMediumBtn: Locator;
  readonly ghostLargeBtn: Locator;

  // Danger buttons
  readonly dangerSmallBtn: Locator;
  readonly dangerMediumBtn: Locator;
  readonly dangerLargeBtn: Locator;

  // Special states
  readonly loadingBtn: Locator;
  readonly disabledBtn: Locator;
  readonly fullWidthBtn: Locator;
  readonly iconBtn: Locator;

  constructor(page: Page) {
    this.page = page;

    // Primary buttons - locate by role and text pattern
    this.primarySmallBtn = page.getByRole('button', { name: /primary/i }).first();
    this.primaryMediumBtn = page.getByRole('button', { name: /primary/i }).first();
    this.primaryLargeBtn = page.getByRole('button', { name: /primary/i }).first();

    // Secondary buttons
    this.secondarySmallBtn = page.getByRole('button', { name: /secondary/i }).first();
    this.secondaryMediumBtn = page.getByRole('button', { name: /secondary/i }).first();
    this.secondaryLargeBtn = page.getByRole('button', { name: /secondary/i }).first();

    // Ghost buttons
    this.ghostSmallBtn = page.getByRole('button', { name: /ghost/i }).first();
    this.ghostMediumBtn = page.getByRole('button', { name: /ghost/i }).first();
    this.ghostLargeBtn = page.getByRole('button', { name: /ghost/i }).first();

    // Danger buttons
    this.dangerSmallBtn = page.getByRole('button', { name: /danger/i }).first();
    this.dangerMediumBtn = page.getByRole('button', { name: /danger/i }).first();
    this.dangerLargeBtn = page.getByRole('button', { name: /danger/i }).first();

    // Special state buttons - locate by button text content
    this.loadingBtn = page.getByRole('button', { name: /loading/i }).first();
    this.disabledBtn = page.getByRole('button', { name: /disabled/i }).first();
    this.fullWidthBtn = page.getByRole('button', { name: /fullwidth|full width/i }).first();
    this.iconBtn = page.locator('button').filter({ has: page.locator('svg') }).first();
  }

  async clickButton(btn: Locator): Promise<void> {
    await btn.click();
  }

  async getButtonText(btn: Locator): Promise<string> {
    return btn.textContent() || '';
  }

  async isButtonDisabled(btn: Locator): Promise<boolean> {
    return await btn.isDisabled();
  }

  async isButtonVisible(btn: Locator): Promise<boolean> {
    return await btn.isVisible();
  }

  async hoverButton(btn: Locator): Promise<void> {
    await btn.hover();
  }

  async pressButton(btn: Locator): Promise<void> {
    await btn.press('Enter');
  }
}

export class CardPage {
  readonly page: Page;

  // Card variants - locate by card-related class patterns
  readonly defaultCard: Locator;
  readonly elevatedCard: Locator;
  readonly outlinedCard: Locator;
  readonly glassCard: Locator;

  // Hoverable and clickable cards
  readonly hoverableCard: Locator;
  readonly clickableCard: Locator;

  constructor(page: Page) {
    this.page = page;

    this.defaultCard = page.locator('[class*="card"]').first();
    this.elevatedCard = page.locator('[class*="card"]').first();
    this.outlinedCard = page.locator('[class*="card"]').first();
    this.glassCard = page.locator('[class*="glass"]').first();
    this.hoverableCard = page.locator('[class*="card"][class*="hover"]').first();
    this.clickableCard = page.locator('[class*="card"][class*="clickable"]').first();
  }

  async isCardVisible(card: Locator): Promise<boolean> {
    return await card.isVisible();
  }

  async clickCard(card: Locator): Promise<void> {
    await card.click();
  }

  async hoverCard(card: Locator): Promise<void> {
    await card.hover();
  }

  async getCardText(card: Locator): Promise<string> {
    return card.textContent() || '';
  }
}

export class SegmentedControlPage {
  readonly page: Page;

  readonly container: Locator;
  readonly option1: Locator;
  readonly option2: Locator;
  readonly option3: Locator;

  constructor(page: Page) {
    this.page = page;

    // The SegmentedControl uses role="tablist"
    this.container = page.getByRole('tablist').first();
    this.option1 = page.getByRole('tab', { name: /chat/i }).first();
    this.option2 = page.getByRole('tab', { name: /image/i }).first();
    this.option3 = page.getByRole('tab', { name: /tts|speech|voice/i }).first();
  }

  async clickOption(option: Locator): Promise<void> {
    await option.click();
  }

  async isOptionSelected(option: Locator): Promise<boolean> {
    const dataActive = await option.getAttribute('data-active');
    return dataActive === 'true';
  }

  async isOptionVisible(option: Locator): Promise<boolean> {
    return await option.isVisible();
  }

  async getOptionText(option: Locator): Promise<string> {
    return option.textContent() || '';
  }

  async getSelectedOptionText(): Promise<string> {
    const selected = this.container.locator('button[data-active="true"]');
    return selected.textContent() || '';
  }
}

// Extended test fixture with page objects
export class ComponentsPage {
  readonly page: Page;
  readonly button: ButtonPage;
  readonly card: CardPage;
  readonly segmentedControl: SegmentedControlPage;

  constructor(page: Page) {
    this.page = page;
    this.button = new ButtonPage(page);
    this.card = new CardPage(page);
    this.segmentedControl = new SegmentedControlPage(page);
  }

  async goto(path: string = ''): Promise<void> {
    await this.page.goto(path);
  }

  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }
}

export const test = base.extend<{ componentsPage: ComponentsPage }>({
  componentsPage: async ({ page }, use) => {
    const componentsPage = new ComponentsPage(page);
    await use(componentsPage);
  },
});

export { expect } from '@playwright/test';
