import {test, expect, Page} from '@playwright/test';
import * as path from "node:path";

const user = {
    login: 'laurent.salinas@ik.me',
    password: 'toto12',
    name: 'Test LaurentCrea'
}

const project = {
    title: 'PR test' + Date.now()
}

function delay(milliseconds) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

async function siteIsUp(page: Page, url: string) {
    await page.goto(url);
    await expect(page.getByRole('link', {name: 'Contribute to a project'})).toBeVisible();
    await expect(page.getByRole('link', {name: 'Particle module'})).toBeVisible();
}

async function getRidOfTaxoWarning(page: Page) {
    const maybePopup = page.locator('#alertmessage-warning i').nth(1);
    if (await maybePopup.isVisible()) {
        await maybePopup.click();
    }
}

async function logIn(page: Page, usr: typeof user) {
    await page.getByRole('link', {name: 'Log in'}).click();
    await page.getByPlaceholder('Email address').click();
    await page.getByPlaceholder('Email address').fill(usr.login);
    await page.getByPlaceholder('Email address').press('Tab');
    await page.getByPlaceholder('your password').fill(usr.password);
    await page.getByLabel('remember me').check();
    await page.getByRole('button', {name: 'Log in'}).click();
    await page.getByRole('link', {name: 'Logo Ecotaxa'}).click();
    await expect(page.getByRole('link', {name: usr.name})).toBeVisible();
    await getRidOfTaxoWarning(page);
}

async function logOut(page: Page, usr: typeof user) {
    const newMenu = page.getByRole('link', {name: usr.name});
    if (await newMenu.isVisible()) {
        await newMenu.hover();
        await page.getByRole('link', {name: 'logout Logout'}).click();
    } else {
        // Legacy app, there is a direct link
        await page.getByRole('link', {name: 'log out'}).click();
    }
}

async function createProject(page: Page, url: string, prj: typeof project) {
    // There is an issue with too long project list
    await page.goto(url + "/gui/prj/create");
    await getRidOfTaxoWarning(page);
    await page.getByPlaceholder('project title').click();
    await page.getByPlaceholder('project title').fill(prj.title);
    await page.keyboard.press('Tab');
    // TODO: Send to 'current field'?
    await page.getByPlaceholder('project description').fill('Description');
    await page.getByPlaceholder('project description').press('Tab');
    await page.getByPlaceholder('project comments').fill('Comment');
    await page.getByPlaceholder('project comments').press('Tab');

    await page.getByRole('combobox', {name: 'Instrument *'}).fill('zoo');
    await page.getByRole('option', {name: 'Zoo scan'}).click();

    await page.getByText('Annotate', {exact: true}).first().click();

    await page.getByLabel('Deep feature extractor').press('Tab');

    await page.getByLabel('CC0').press('ArrowRight');
    await page.getByLabel('CC BY 4.0').press('ArrowRight');
    await page.getByLabel('CC BY-NC').press('Enter');
    await page.getByLabel('CC BY-NC').press('Tab');
    await page.getByRole('button', {name: 'Save'}).press('ArrowDown');
    await page.getByRole('button', {name: 'Save'}).press('Tab');
    await page.getByRole('link', {name: 'Cancel'}).press('Shift+Tab');
    await page.getByRole('button', {name: 'Save'}).press('Enter');
    // No privs -> Error Popup
    await page.getByText('Privileges').click();
    await page.locator('body').press('Tab');
    await page.locator('#members_member_0-ts-control').press('Tab');
    await page.getByLabel('Manage').press('Tab');
    await page.locator('#members_contact_0').check();
    await page.locator('#members_contact_0').press('Tab');
    await page.getByRole('button', {name: 'New privilege'}).press('Tab');
    await page.getByRole('button', {name: 'Save'}).press('Enter');
    // Ensure green notif of OK
    await expect(page.getByText('SUCCESS:')).toBeVisible();
    await expect(page.getByText('SUCCESS:')).toBeHidden({timeout: 10000});

}

async function gotoProjectAnnotation(page: Page, usr: typeof user, prj: typeof project) {
    const newMenu = page.getByRole('link', {name: usr.name});
    const prjRe = new RegExp(prj.title);
    if (await newMenu.isVisible()) {
        await newMenu.hover();
        await page.getByRole('link', {name: prjRe}).click();
    } else {
        // Legacy app, there is a direct link
        await page.getByRole('button', {name: 'Toggle Dropdown', exact: true}).click();
        await page.getByRole('link', {name: 'Contribute to a project'}).hover();
        await page.getByRole('link', {name: prjRe}).click();
    }
    await expect(page.locator('#titledivtitle')).toContainText(prj.title);
}

async function gotoProjectSettings(page: Page, usr: typeof user, prj: typeof project) {
    await gotoProjectAnnotation(page, usr, prj);
    await page.getByRole('button', {name: 'Project'}).click();
    await page.getByRole('link', {name: 'About project'}).click();
    await expect(page.getByRole('heading', {name: 'About ' + prj.title})).toBeVisible();
}

async function answerQuestion(page: Page, url: string) {
    // This export has an unknown user
    await page.goto(url + '/gui/jobs/listall');
    const maybePending = page.getByRole('button', {name: 'Pending'});
    if (await maybePending.isVisible()) {
        await delay(1000);
        await answerQuestion(page, url);
        return;
    }
    const maybeRunning = page.getByRole('button', {name: 'Running'});
    if (await maybeRunning.isVisible()) {
        await delay(1000);
        await answerQuestion(page, url);
        return;
    }
    await page.getByRole('button', {name: 'Question'}).click();
    await page.locator('#select2-userlb1-container').click();
    await page.getByRole('textbox').fill('admin');
    await page.getByRole('treeitem', {name: 'application administrator'}).click();
    await page.getByRole('button', {name: 'Continue'}).click();
}

async function uploadData(page: Page, url: string, usr: typeof user, prj: typeof project) {
    await gotoProjectAnnotation(page, usr, prj);
    await page.getByRole('button', {name: 'Project'}).click();
    await page.getByRole('link', {name: 'Import images and metadata'}).click();
    await page.locator('#uploadfile').setInputFiles(path.join(__dirname, 'export_13539_20240728_0803.zip'));
    await page.getByRole('button', {name: 'Start import Images and TSV'}).click();
    await answerQuestion(page, url);
    const classifBtn = page.getByRole('button', {name: 'Go to Manual Classification'});
    // There is an auto-wait, the button will appear when task is OK
    await classifBtn.click();
}

async function viewAnImage(page: Page) {
    await page.locator('td:nth-child(4) > .ddet > .ddets > .glyphicon').first().click();
    await delay(2000);
    await page.getByRole('cell', {name: 'Close', exact: true}).getByRole('button').click();
}

test('smoke', async ({page}) => {
    const url = 'http://localhost:5001/';
    //const url = 'https://ecotaxa.obs-vlfr.fr/';
    await siteIsUp(page, url);
    await logIn(page, user);
    // await logOut(page, user);
    // await logIn(page, user);
    await createProject(page, url, project);
    await gotoProjectAnnotation(page, user, project);
    await gotoProjectSettings(page, user, project);
    await uploadData(page, url, user, project)
    await gotoProjectAnnotation(page, user, project);
    await viewAnImage(page);
    await logOut(page, user);
    await delay(1000);
});
