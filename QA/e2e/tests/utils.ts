import {expect, Page} from '@playwright/test';
var moment = require('moment');

export async function assertInNewUI(page: Page, where: string) {
    await expect(page.locator('#tool-item').getByRole('link').first(), "Not in new UI "+where).toBeVisible();
}

export async function assertInOldUI(page: Page, where: string) {
    await expect(page.locator('#divheadinfo').getByRole('link').first(), "Not in old UI "+where).toBeVisible();
}

export function delay(milliseconds: number) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

export function readableUniqueId(): string {
    return moment().format('hh:mm:ss');
}