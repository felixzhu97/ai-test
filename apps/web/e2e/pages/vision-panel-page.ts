import type { Page, Locator } from '@playwright/test';

export class VisionPanelPage {
  readonly page: Page;
  
  // Tab controls
  readonly captionTab: Locator;
  readonly detectTab: Locator;
  readonly ocrTab: Locator;
  
  // Image area elements
  readonly imageArea: Locator;
  readonly dropZone: Locator;
  readonly previewImage: Locator;
  readonly clearButton: Locator;
  readonly zoomHint: Locator;
  readonly fileInput: Locator;
  
  // Result panel elements
  readonly resultPanel: Locator;
  readonly emptyState: Locator;
  readonly resultText: Locator;
  
  // Action elements
  readonly analyzeButton: Locator;
  
  // Image zoom modal
  readonly zoomModal: Locator;
  readonly zoomModalImage: Locator;
  readonly zoomModalClose: Locator;
  
  // Panel titles
  readonly imagePanelTitle: Locator;
  readonly resultPanelTitle: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Tab controls - use role-based selectors
    this.captionTab = page.getByRole('tab', { name: /caption/i });
    this.detectTab = page.getByRole('tab', { name: /detect/i });
    this.ocrTab = page.getByRole('tab', { name: /ocr/i });
    
    // Image area - use CSS class selectors
    this.imageArea = page.locator('[class*="ImageArea"]').first();
    this.dropZone = page.locator('[class*="DropZone"]').first();
    this.previewImage = page.locator('[class*="PreviewImage"]').first();
    this.clearButton = page.locator('[class*="ClearButton"]').first();
    this.zoomHint = page.locator('[class*="ZoomHint"]').first();
    this.fileInput = page.locator('input[type="file"]').first();
    
    // Result panel - use CSS class selectors
    this.resultPanel = page.locator('[class*="Result"]').first();
    this.emptyState = page.locator('[class*="EmptyState"]').first();
    this.resultText = page.locator('[class*="ResultContent"], [class*="ResultText"]').first();
    
    // Action elements
    this.analyzeButton = page.locator('[class*="ActionArea"] button, button').filter({ hasText: /analyz|分析/i }).first();
    
    // Zoom modal - use CSS class
    this.zoomModal = page.locator('[class*="ZoomModal"], [class*="zoom"]').first();
    this.zoomModalImage = page.locator('img').first();
    this.zoomModalClose = page.locator('[class*="CloseButton"]').first();
    
    // Panel titles
    this.imagePanelTitle = page.locator('[class*="PanelTitle"]').first();
    this.resultPanelTitle = page.locator('[class*="PanelTitle"]').nth(1);
  }

  async navigateToVision() {
    await this.page.goto('/');
    await this.switchToTab('caption');
  }

  async switchToTab(tabName: 'caption' | 'detect' | 'ocr') {
    switch (tabName) {
      case 'caption':
        await this.captionTab.click();
        break;
      case 'detect':
        await this.detectTab.click();
        break;
      case 'ocr':
        await this.ocrTab.click();
        break;
    }
    await this.page.waitForTimeout(300);
  }

  async uploadImage(filePath: string) {
    const [fileChooser] = await Promise.all([
      this.page.waitForEvent('filechooser'),
      this.dropZone.click(),
    ]);
    await fileChooser.setFiles(filePath);
    await this.page.waitForTimeout(500);
  }

  async clearImage() {
    await this.clearButton.click();
    await this.page.waitForTimeout(300);
  }

  async clickAnalyze() {
    await this.analyzeButton.click();
  }

  async waitForLoading(timeout = 10000) {
    const spinner = this.page.locator('[class*="Spinner"]');
    if (await spinner.isVisible()) {
      await spinner.waitFor({ state: 'hidden', timeout });
    }
  }

  async openZoomModal() {
    if (await this.previewImage.isVisible()) {
      await this.previewImage.click();
      await this.page.waitForTimeout(300);
    }
  }

  async closeZoomModal() {
    if (await this.zoomModalClose.isVisible()) {
      await this.zoomModalClose.click();
      await this.page.waitForTimeout(200);
    }
  }

  async isImageUploaded(): Promise<boolean> {
    return this.previewImage.isVisible().catch(() => false);
  }

  async isDropZoneVisible(): Promise<boolean> {
    return this.dropZone.isVisible().catch(() => false);
  }

  async getResultText(): Promise<string> {
    const text = await this.resultText.textContent();
    return text ?? '';
  }

  async isAnalyzeButtonEnabled(): Promise<boolean> {
    const isDisabled = await this.analyzeButton.getAttribute('disabled');
    return isDisabled === null;
  }
}
