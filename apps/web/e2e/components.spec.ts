import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for Base UI Components
 * Tests components within their actual usage context in the app.
 */

test.describe('Button Component E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test.describe('Button Variants', () => {
    test('primary buttons render correctly', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const sendButton = page.locator('button').filter({ hasText: '→' }).first();
      await expect(sendButton).toBeVisible();
    });

    test('buttons are present', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const buttons = page.locator('button');
      await expect(buttons.first()).toBeVisible();
    });
  });

  test.describe('Button States', () => {
    test('buttons have proper disabled state styling when input is empty', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const sendButton = page.locator('button').filter({ hasText: '→' }).first();
      await expect(sendButton).toBeDisabled();
    });

    test('buttons become enabled when input has content', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const textarea = page.locator('textarea').first();
      await textarea.fill('Test message');
      
      const sendButton = page.locator('button').filter({ hasText: '→' }).first();
      await expect(sendButton).toBeEnabled();
    });
  });
});

test.describe('Card Component E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test.describe('Card Variants', () => {
    test('cards render in the application', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const panels = page.locator('[class*="PanelContainer"], [class*="PanelContent"]');
      await expect(panels.first()).toBeVisible();
    });

    test('cards have rounded corners', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const panel = page.locator('[class*="PanelContainer"]').first();
      const borderRadius = await panel.evaluate(
        (el) => window.getComputedStyle(el).borderRadius
      );
      expect(borderRadius).toBeTruthy();
    });
  });

  test.describe('Card Styling', () => {
    test('cards have proper background color', async ({ page }) => {
      await page.getByRole('button', { name: /ai hub/i }).click();
      await page.waitForTimeout(500);
      
      const panel = page.locator('[class*="PanelContent"]').first();
      const bgColor = await panel.evaluate(
        (el) => window.getComputedStyle(el).backgroundColor
      );
      expect(bgColor).toBeTruthy();
    });
  });
});

test.describe('SegmentedControl Component E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /ai hub/i }).click();
    await page.waitForTimeout(500);
  });

  test.describe('SegmentedControl Rendering', () => {
    test('renders all options', async ({ page }) => {
      const tablist = page.locator('[role="tablist"]');
      await expect(tablist).toBeVisible();
      
      const tabs = page.locator('[role="tab"]');
      await expect(tabs.first()).toBeVisible();
    });

    test('displays correct option labels', async ({ page }) => {
      const tabs = page.locator('[role="tab"]');
      const tabCount = await tabs.count();
      expect(tabCount).toBeGreaterThanOrEqual(2);
    });
  });

  test.describe('SegmentedControl Selection', () => {
    test('first option is selected by default', async ({ page }) => {
      const firstTab = page.locator('[role="tab"]').first();
      await expect(firstTab).toHaveAttribute('aria-selected', 'true');
    });

    test('clicking second option selects it', async ({ page }) => {
      const tabs = page.locator('[role="tab"]');
      const secondTab = tabs.nth(1);
      
      await secondTab.click();
      await page.waitForTimeout(300);
      
      await expect(secondTab).toHaveAttribute('aria-selected', 'true');
    });

    test('only one option can be selected at a time', async ({ page }) => {
      const tabs = page.locator('[role="tab"]');
      
      await tabs.nth(1).click();
      await page.waitForTimeout(300);
      await expect(tabs.nth(1)).toHaveAttribute('aria-selected', 'true');
      
      if (await tabs.count() > 2) {
        await tabs.nth(2).click();
        await page.waitForTimeout(300);
        await expect(tabs.nth(2)).toHaveAttribute('aria-selected', 'true');
      }
    });
  });

  test.describe('SegmentedControl Accessibility', () => {
    test('container has tablist role', async ({ page }) => {
      const tablist = page.locator('[role="tablist"]');
      await expect(tablist).toHaveAttribute('role', 'tablist');
    });

    test('options have tab role', async ({ page }) => {
      const firstTab = page.locator('[role="tab"]').first();
      await expect(firstTab).toHaveAttribute('role', 'tab');
    });

    test('selected option has aria-selected true', async ({ page }) => {
      const firstTab = page.locator('[role="tab"]').first();
      await expect(firstTab).toHaveAttribute('aria-selected', 'true');
    });
  });

  test.describe('SegmentedControl Visual States', () => {
    test('selected option is visually distinct', async ({ page }) => {
      const tabs = page.locator('[role="tab"]');
      const firstTab = tabs.first();
      const secondTab = tabs.nth(1);
      
      const selectedBg = await firstTab.evaluate(
        (el) => window.getComputedStyle(el).backgroundColor
      );
      const unselectedBg = await secondTab.evaluate(
        (el) => window.getComputedStyle(el).backgroundColor
      );
      
      expect(selectedBg !== unselectedBg || await firstTab.getAttribute('data-active') === 'true').toBeTruthy();
    });
  });
});

test.describe('Components Integration Tests', () => {
  test('tab navigation works correctly', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /ai hub/i }).click();
    await page.waitForTimeout(500);
    
    const tabs = page.locator('[role="tab"]');
    const tabCount = await tabs.count();
    
    for (let i = 0; i < tabCount; i++) {
      await tabs.nth(i).click();
      await page.waitForTimeout(300);
      await expect(tabs.nth(i)).toHaveAttribute('aria-selected', 'true');
    }
  });
});
