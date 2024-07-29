import {expect, Page} from '@playwright/test';
var moment = require('moment');

export async function assertInNewUI(page: Page) {
    await expect(page.locator('#tool-item').getByRole('link').first()).toBeVisible();
}

export function delay(milliseconds: number) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

export function readableUniqueId(): string {
    return moment().format('hh:mm:ss');
}