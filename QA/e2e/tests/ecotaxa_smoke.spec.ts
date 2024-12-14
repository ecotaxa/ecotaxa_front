import {test, expect, Page} from '@playwright/test';
import * as path from "node:path";
import {assertInNewUI, assertInOldUI, delay, readableUniqueId} from './utils';

const user = {
    login: 'laurent.salinas@ik.me',
    password: 'toto12',
    name: 'Test LaurentCrea'
}

class Project {
    title: string;
}


const baseUrl = 'http://localhost:5001/';

//const baseUrl = 'https://ecotaxa.obs-vlfr.fr/';

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

async function logOutFromNewUI(page: Page, usr: typeof user) {
    const userMenu = page.locator("#main-navbar").getByRole('link', {name: usr.name});
    // if (await userMenu.isVisible()) {
    await userMenu.hover();
    await page.getByRole('link', {name: 'logout Logout'}).click();
    // } else {
    //     Legacy app, there is a direct link
    // await page.getByRole('link', {name: 'log out'}).click();
    // }
    // TODO an assert here
}

async function createProject(page: Page, prj: Project) {
    // There is an issue with too long project list
    await page.goto(baseUrl + "/gui/prj/create");
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
    // await delay(500000);

}

async function gotoProjectAnnotation(page: Page, usr: typeof user, prj: Project) {
    const userMenu = page.getByRole('link', {name: usr.name});
    const prjRe = new RegExp(prj.title);
    if (await userMenu.isVisible()) {
        await userMenu.hover();
        await page.getByRole('link', {name: prjRe}).click();
    } else {
        // Legacy app, there is a direct link
        await page.getByRole('button', {name: 'Toggle Dropdown', exact: true}).click();
        await page.getByRole('link', {name: 'Contribute to a project'}).hover();
        await page.getByRole('link', {name: prjRe}).click();
    }
    await expect(page.locator('#titledivtitle')).toContainText(prj.title);
}

async function gotoProjectAnnotationFromNewUI(page: Page, usr: typeof user, prj: Project) {
    const userMenu = page.getByRole('link', {name: usr.name});
    const prjRe = new RegExp(prj.title);
    await userMenu.hover();
    await page.getByRole('link', {name: prjRe}).click();
    await expect(page.locator('#titledivtitle')).toContainText(prj.title);
}

async function gotoProjectAboutFromOldUI(page: Page, usr: typeof user, prj: Project) {
    await assertInOldUI(page, "About");
    await page.getByRole('button', {name: 'Project'}).click();
    await page.getByRole('link', {name: 'About project'}).click();
    await expect(page.getByRole('heading', {name: 'About ' + prj.title})).toBeVisible();
}

async function mergeProject(page: Page, destPrj: Project, sourcePrj: Project) {
    await assertInNewUI(page, "Merge");
    await page.getByText('Tools', {exact: true}).hover({force: true});
    await page.getByRole('link', {name: 'Merge another project in this'}).click();
    await expect(page.getByRole('heading')).toContainText('Project Merge / Fusion '+destPrj.title);
    await page.getByPlaceholder('Search...').fill(sourcePrj.title);
    await page.getByPlaceholder('Search...').click(); // Search needs an event
    await page.getByRole('row', {name: sourcePrj.title}).getByRole('radio').check();
    await page.getByRole('button', {name: 'Validate before merge'}).click();
    await page.getByRole('button', {name: 'Start Project Fusion'}).click();
    // TODO: Bug here, it gets back to project home
    await page.getByRole('link', {name: 'Back to target project'}).click();
}

async function gotoProjectAboutFromNewUI(page: Page, usr: typeof user, prj: Project) {
    await assertInNewUI(page, "About");
    await page.locator('#navbar-menu').getByRole('link', {name: 'About'}).click();
    await expect(page.getByRole('heading', {name: 'About ' + prj.title})).toBeVisible();
}

async function filterInProjectPage(page: Page, prj: Project, nb_expected: number) {
    await page.goto(baseUrl)
    await page.getByRole('link', {name: 'Contribute to a project'}).click();
    const searchBox = page.getByPlaceholder('Search...');
    await searchBox.fill(prj.title);
    await searchBox.click(); // The box needs an event to trigger the search
    // Ensure the exact number of expected row
    await expect(page.locator('#table-projects-list').getByRole('link', {name: 'Annotate'})).toHaveCount(nb_expected, {timeout: 10000});
}

async function ensureProjectGone(page: Page, prj: Project) {
    await filterInProjectPage(page, prj, 0);
}

async function gotoProjectSettings(page: Page, usr: typeof user, prj: Project) {
    // Navigate from home
    // await page.getByRole('link', {name: 'Logo Ecotaxa'}).click(); // The logo is in NOT the same in both UIs
    await filterInProjectPage(page, prj, 1);
    await page.getByRole('row', {name: /Annotate Settings.*/}).getByRole('link').nth(1).click();
}

async function gotoSubsetFromNewUI(page: Page) {
    await assertInNewUI(page, "Subset");
    await page.getByText('Tools', {exact: true}).hover({force: true});
    await page.getByRole('link', {name: 'Extract Subset'}).click();
}

async function extractSubset(page: Page, prj: Project, subs: Project) {
    await assertInNewUI(page, "Subset");
    await expect(page.locator('#main-navbar')).toContainText(prj.title);
    await page.getByText('objects max.').first().click();
    await page.getByRole('textbox', {name: 'objects max.'}).fill('1000');
    await page.getByRole('textbox', {name: 'objects max.'}).press('Tab');
    await page.getByText('sample', {exact: true}).click();
    await page.getByLabel('Subset project title').fill(subs.title);
    await page.getByRole('button', {name: 'Start Task'}).click();
    // When task is done we can go to subset project Settings in new UI, and we do it
    await page.getByRole('link', {name: 'Go to Subset Project'}).click();

}

async function exportGeneral(page: Page, usr: typeof user, prj: Project) {
    await assertInNewUI(page, "Export");
    await page.getByText('Export', {exact: true}).hover({force: true});
    await page.getByRole('link', {name: 'General export'}).click();
    await expect(page.getByRole('heading')).toContainText('Export ' + prj.title);
    await page.getByRole('group', {name: 'General Export'}).locator('legend').click();
    // There are several "Yes" or "No" in the page, attempt below to specialize the click on a given section of the form
    // await page.locator('[class="group-radio"]').locator('[name="with_internal_ids"]').nth(0).setChecked(true);
    // _It doesn't work_: Call log:
    //   - waiting for locator('[class="group-radio"]').locator('[name="with_internal_ids"]').first()
    //   -   locator resolved to <input value="1" required="" type="radio" class="peer" data-listen="true" name="with_internal_ids" id="with_internal_ids_general_1"/>
    //   - attempting click action
    //   -   waiting for element to be visible, enabled and stable
    //   -   element is not visible
    await page.locator('#general').getByText('No', {exact: true}).nth(0).click(); // Only save objects' annotation
    await page.locator('#general').getByText('All images').click();
    await page.locator('#general').getByText('None').nth(0).click();
    await page.locator('#general').getByText('No', {exact: true}).nth(1).click(); // Internal DB Ids
    await page.locator('#general').getByText('No', {exact: true}).nth(2).click(); // Second line with types
    await page.locator('#general').getByText('Sample').click(); // Separate by
    await page.locator('#general').getByText('No', {exact: true}).nth(3).click(); // Copy to FTP
    await page.getByRole('button', {name: 'Start Task'}).click();
    // The task appears right away, wait for some sign it's finished
    await expect(page.locator('#progressbar')).toContainText('100%', {timeout: 5000});
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', {name: 'Get file'}).click();
    const download = await downloadPromise;
    const filePath = path.join(__dirname, download.suggestedFilename());
    download.saveAs(filePath);
}

async function deleteCurrentProject(page: Page, prj: Project) {
    await assertInNewUI(page, "Delete");
    await page.getByText('Tools', {exact: true}).hover({force: true});
    await page.getByRole('link', {name: 'Delete object or project'}).click()
    await expect(page.getByRole('heading')).toContainText('Erase objects tool ' + prj.title);
    await page.getByText('"DELETEALL"', {exact: true}).click();
    await page.getByLabel('DELETE project after "').check();
    await page.getByRole('button', {name: 'ERASE THESE OBJECTS !!!'}).click();
    await page.getByRole('button', {name: 'Ok'}).click();
    // Ensure green notif of OK
    const okMessage = page.getByText('SUCCESS:');
    await expect(okMessage).toBeVisible();
    await expect(okMessage).toHaveCount(0, {timeout: 10000});
}

async function answerImportQuestion(page: Page) {
    // This export has an unknown user
    await page.goto(baseUrl + '/gui/jobs/listall');
    const pendingOrRunning = page.getByRole('button', {name: 'Pending'}).or(page.getByRole('button', {name: 'Running'}));
    if (await pendingOrRunning.isVisible()) {
        await delay(1000);
        await answerImportQuestion(page);
        return;
    }
    await page.getByRole('button', {name: 'Question'}).click();
    await page.locator('#select2-userlb1-container').click();
    await page.getByRole('textbox').fill('admin');
    await page.getByRole('treeitem', {name: 'application administrator'}).click();
    await page.getByRole('button', {name: 'Continue'}).click();
}

async function uploadData(page: Page, zip: string, withQuestion: boolean) {
    await assertInOldUI(page, "Upload");
    await page.getByRole('button', {name: 'Project'}).click();
    await page.getByRole('link', {name: 'Import images and metadata'}).click();
    await page.locator('#uploadfile').setInputFiles(path.join(__dirname, zip));
    await page.getByRole('button', {name: 'Start import Images and TSV'}).click();
    if (withQuestion) {
        await answerImportQuestion(page);
    }
    // There is an auto-wait, the button will appear when task is OK
    const classifBtn = page.getByRole('button', {name: 'Go to Manual Classification'});
    await classifBtn.click();
}

async function viewAnImage(page: Page) {
    await page.locator('td:nth-child(4) > .ddet > .ddets > .glyphicon').first().click();
    await delay(1000);
    await page.getByRole('cell', {name: 'Close', exact: true}).getByRole('button').click();
}

async function filterToSample(page: Page, sampleName: string) {
    await assertInOldUI(page, "filterToSample");
    await page.getByRole('tab', {name: 'Other filters'}).click();
    await page.getByRole('list').first().click();
    await page.getByRole('treeitem', {name: sampleName}).click();
    await page.getByRole('cell', {name: 'Update view & apply filter'}).getByRole('button').click();
    await expect(page.getByRole('button', {name: 'Samples='})).toBeVisible();
}

test('smoke', async ({page}) => {
    const project: Project = {
        title: 'PR test ' + readableUniqueId()
    }

    const subsetProject = {
        title: project.title + " subset"
    }
    test.slow(); // 36s
    await siteIsUp(page, baseUrl);
    await logIn(page, user);
    // await logOut(page, user);
    // await logIn(page, user);
    await createProject(page, project);
    await gotoProjectAnnotation(page, user, project);
    await gotoProjectSettings(page, user, project);
    await gotoProjectAboutFromNewUI(page, user, project);
    await gotoProjectAnnotation(page, user, project);
    await uploadData(page, 'export_13539_20240728_0803.zip', true)
    await gotoProjectAnnotation(page, user, project);
    await viewAnImage(page);
    await gotoProjectAboutFromOldUI(page, user, project);
    await gotoProjectSettings(page, user, project);
    await exportGeneral(page, user, project);
    await gotoSubsetFromNewUI(page);
    await extractSubset(page, project, subsetProject);
    // Final cleanup
    await gotoProjectSettings(page, user, subsetProject);
    await deleteCurrentProject(page, subsetProject);
    await gotoProjectSettings(page, user, project);
    await deleteCurrentProject(page, project);
    await logOutFromNewUI(page, user);
    await delay(1000); // Just for the video :)
});

test('extract_reclassify_merge', async ({page}) => {
    const testId = readableUniqueId();
    const project: Project = {
        title: 'RECLASSIF test ' + testId
    }

    const subsetProject = {
        // Due to project list search tolerance, subset must _not_ contain words from test project
        title: 'SUBSET of ' + testId
    }
    test.slow(); // 36s
    await siteIsUp(page, baseUrl);
    await logIn(page, user);
    await createProject(page, project);
    await gotoProjectAnnotation(page, user, project);
    await uploadData(page, 'export_12576_20240802_0841.zip', false)
    await filterToSample(page, 'tara_oceans_2009_030_d_regent_680');
    await page.getByRole('button', {name: 'Filtered'}).click();
    await page.getByRole('link', {name: 'Extract Subset'}).click();
    await extractSubset(page, project, subsetProject);
    await gotoProjectAnnotationFromNewUI(page, user, project);
    await filterToSample(page, 'tara_oceans_2009_030_d_regent_680');
    await page.getByRole('button', {name: 'Filtered'}).click();
    await page.getByRole('link', {name: 'Delete objects'}).click();
    await expect(page.getByRole('main')).toContainText('USING Active Project Filters 13 objects');
    await page.getByRole('button', {name: 'ERASE THESE OBJECTS !!!'}).click();
    await page.getByRole('button', {name: 'Ok'}).click();
    // Ensure green notif of OK
    const okMessage = page.getByText('SUCCESS:');
    await expect(okMessage).toBeVisible();
    await expect(okMessage).toHaveCount(0, {timeout: 10000});
    await gotoProjectAnnotationFromNewUI(page, user, subsetProject);
    await expect(page.locator('#titlediv')).toContainText(subsetProject.title + ' (3 , 10 , 0 , 0 / 13)');
    for (const aRow of await page.getByRole('cell', {name: '.'}).all()) {
        await aRow.click();
    }
    await expect(page.locator('#topbar')).toContainText('13 Selected');
    await page.locator('#myTabs').getByLabel('', {exact: true}).click();
    await page.getByRole('textbox').fill('orth');
    await page.getByRole('treeitem', {name: 'Orthasterias', exact: true}).click();
    await page.getByRole('button', {name: ' Save pending changes [Ctrl+'}).click();
    await expect(page.locator('#titlediv')).toContainText(subsetProject.title + ' (13 , 0 , 0 , 0 / 13)');
    await expect(page.locator('#categtree')).toContainText('Orthasterias 13');
    await gotoProjectSettings(page, user, project);
    await mergeProject(page, project, subsetProject);
    await ensureProjectGone(page, subsetProject);
});

test('show_inactive_menu_bug', async ({page}) => {
    const project: Project = {
        title: 'Bug test ' + readableUniqueId()
    }
    await siteIsUp(page, baseUrl);
    await logIn(page, user);
    await createProject(page, project);
    await gotoProjectAnnotation(page, user, project);
    await gotoProjectAboutFromOldUI(page, user, project);
    await page.getByText('Tools', {exact: true}).hover({force: true});
    // Bug here, for some reason the menu is not clickable
    await expect(page.getByRole('link', {name: 'Extract Subset'})).toHaveClass('disabled');
    await logOutFromNewUI(page, user);
});
