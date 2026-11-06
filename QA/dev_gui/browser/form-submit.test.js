import { describe, it, expect, beforeAll, afterEach, vi } from 'vitest';
import { userEvent } from 'vitest/browser';
import { css } from '@modules/modules-config.js';
import { AlertBox } from '@modules/alert-box.js';
import { FormSubmit } from '@modules/form-submit.js';

// Real Chromium: the browser compiles the pattern attribute with the 'v' flag, and ignores
// a pattern which is invalid in this mode, like the password regexp of the server.
// password_regexp sent by the server (ecotaxa_back BO/User.py USER_PWD_REGEXP) - it can change
const PASSWORD_REGEXP = '^(?:(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#?%^&+*-])).{8,64}$';

beforeAll(() => {
  // as index.js on every page: messages container of the alerts (form not submitted)
  AlertBox.applyTo(document);
});

afterEach(() => {
  document.querySelectorAll('.test-page').forEach((el) => el.remove());
  vi.restoreAllMocks();
});

// attribute value escaped as Jinja does
function attr(value) {
  return value.replace(/&/g, '&amp;').replace(/"/g, '&#34;');
}

function testForm(html, attrs = '') {
  const div = document.createElement('div');
  div.className = 'test-page';
  div.innerHTML = `<form class="js js-submit" data-required="this field is required" data-isinvalid="this field is invalid"
    onsubmit="return false" ${attrs}>${html}</form>`;
  document.body.append(div);
  const form = div.querySelector('form');
  return { form, fs: new FormSubmit(form) };
}

// same markup as the password box of users/_user.html: required for a new account only
function passwordForm(required = false) {
  const { form, fs } = testForm(`<fieldset class="tab"><div class="form-box">
    <label for="newpassword">New password</label>
    <input type="password" id="newpassword" name="newpassword" class="form-input" pattern="${attr(PASSWORD_REGEXP)}"
      ${required ? 'required' : ''} data-required="a password is required" placeholder="Password">
    <em class="password-regexp small text-xs">8 to 64 chars</em>
    <label for="passwordconfirm">Password confirmation</label>
    <input type="password" id="passwordconfirm" name="passwordconfirm" class="form-input" pattern="${attr(PASSWORD_REGEXP)}"
      data-match="newpassword" data-matchinvalid="password does not match" placeholder="Password confirmation">
    </div></fieldset><button type="submit" class="button is-primary">Save</button>`);
  return {
    fs,
    password: form.querySelector('#newpassword'),
    confirm: form.querySelector('#passwordconfirm'),
    tab: form.querySelector('.tab'),
  };
}

function labelOf(field) {
  return field.form.querySelector(`label[for="${field.id}"]`);
}

function flagged(field) {
  return labelOf(field).classList.contains(css.invalid);
}

describe('form-submit password fields', () => {
  it('checks the server regexp, ignored by the browser, while typing', async () => {
    const { fs, password, confirm } = passwordForm();
    password.value = 'weak';
    expect(password.validity.patternMismatch, 'pattern ignored by the browser').toBe(false);
    await userEvent.fill(password, 'weak');
    expect(flagged(password)).toBe(true);
    expect(labelOf(password).dataset.invalid).toBe('this field is invalid');
    await userEvent.fill(password, 'totO12457!');
    expect(flagged(password)).toBe(false);
    await userEvent.fill(confirm, 'totO12457!');
    expect(flagged(confirm)).toBe(false);
    expect(await fs.validateFields()).toBe(true);
  });

  it('rejects a weak password on submit', async () => {
    const { fs, password, confirm } = passwordForm();
    password.value = 'totO12457';
    confirm.value = 'totO12457';
    expect(await fs.validateFields()).toBe(false);
    expect(flagged(password)).toBe(true);
    expect(labelOf(password).dataset.invalid).toBe('this field is invalid');
  });

  it('flags a confirmation which does not match on its own label, until the password matches', async () => {
    const { fs, password, confirm, tab } = passwordForm();
    await userEvent.fill(password, 'totO12457!');
    await userEvent.fill(confirm, 'totO12457?');
    expect(flagged(confirm)).toBe(true);
    expect(labelOf(confirm).dataset.invalid).toBe('password does not match');
    expect(flagged(password)).toBe(false);
    // submit: same single message, the tab is marked
    expect(await fs.validateFields()).toBe(false);
    expect(labelOf(confirm).dataset.invalid).toBe('password does not match');
    expect(tab.classList.contains(css.error)).toBe(true);
    // the confirmation is checked again when the password changes
    await userEvent.fill(password, 'totO12457?');
    expect(flagged(confirm)).toBe(false);
    expect(await fs.validateFields()).toBe(true);
    expect(tab.classList.contains(css.error)).toBe(false);
  });

  it('does not flag an empty confirmation while the password is typed, only on submit', async () => {
    const { fs, password, confirm } = passwordForm();
    await userEvent.fill(password, 'totO12457!');
    expect(flagged(confirm)).toBe(false);
    expect(await fs.validateFields()).toBe(false);
    expect(labelOf(confirm).dataset.invalid).toBe('password does not match');
  });

  it('accepts both fields empty when the password is not required (profile)', async () => {
    const { fs } = passwordForm();
    expect(await fs.validateFields()).toBe(true);
  });

  it('requires the password of a new account', async () => {
    const { fs, password } = passwordForm(true);
    expect(await fs.validateFields()).toBe(false);
    expect(labelOf(password).dataset.invalid).toBe('* a password is required');
  });

  it('does not scroll while typing, scrolls once to the first invalid field on submit', async () => {
    const scrollTo = vi.spyOn(window, 'scrollTo');
    const scrollIntoView = vi.spyOn(Element.prototype, 'scrollIntoView');
    const { fs, password, confirm } = passwordForm();
    await userEvent.type(password, 'toto');
    await userEvent.type(confirm, 'tot');
    expect(flagged(password)).toBe(true);
    expect(flagged(confirm)).toBe(true);
    expect(scrollTo).not.toHaveBeenCalled();
    expect(scrollIntoView).not.toHaveBeenCalled();
    expect(await fs.submitForm()).toBe(false);
    expect(scrollTo).not.toHaveBeenCalled();
    expect(scrollIntoView).toHaveBeenCalledTimes(1);
    expect(scrollIntoView.mock.contexts[0]).toBe(labelOf(password));
    expect(scrollIntoView).toHaveBeenCalledWith({ block: 'center', behavior: 'smooth' });
  });
});

describe('form-submit pattern, compiled as the browser does', () => {
  function accepts(pattern, value) {
    const { form, fs } = testForm(`<div class="form-box"><label for="code">Code</label>
      <input type="text" id="code" name="code" class="form-input" pattern="${attr(pattern)}"></div>`);
    const field = form.querySelector('#code');
    field.value = value;
    return fs.validateField(field);
  }

  it('the server regexp', () => {
    expect(accepts(PASSWORD_REGEXP, 'totO12457!')).toBe(true);
    expect(accepts(PASSWORD_REGEXP, 'totO12457!' + 'a'.repeat(54))).toBe(true);
    expect(accepts(PASSWORD_REGEXP, 'totO12457!' + 'a'.repeat(55)), 'more than 64 chars').toBe(false);
    expect(accepts(PASSWORD_REGEXP, 'tO1!tO1'), 'less than 8 chars').toBe(false);
    expect(accepts(PASSWORD_REGEXP, 'totO12457'), 'no special char').toBe(false);
    expect(accepts(PASSWORD_REGEXP, 'TOTO12457!'), 'no lowercase').toBe(false);
  });

  it('anchors the whole pattern, alternatives included', () => {
    expect(accepts('^abc|def', 'abc')).toBe(true);
    expect(accepts('^abc|def', 'def')).toBe(true);
    expect(accepts('^abc|def', 'abcXYZ')).toBe(false);
    expect(accepts('^abc|def', 'XYZdef')).toBe(false);
  });

  it('reads unicode property classes', () => {
    expect(accepts('(?=.*\\p{Lu}).{8,}', 'Abcdefgh')).toBe(true);
    expect(accepts('(?=.*\\p{Lu}).{8,}', 'abcdefgh')).toBe(false);
  });

  it('does not check a pattern which is not a valid regexp: the server decides', () => {
    expect(accepts('\\A[a-z]+\\Z', '123')).toBe(true);
  });

  it('does not rewrite the value while typing, sanitizes it on change', async () => {
    const { form } = testForm(`<div class="form-box"><label for="code">Code</label>
      <input type="text" id="code" name="code" class="form-input" pattern=".*"></div>`);
    const field = form.querySelector('#code');
    await userEvent.type(field, 'a<img src=x onerror=y>');
    expect(field.value).toBe('a<img src=x onerror=y>');
    field.dispatchEvent(new Event('change'));
    expect(field.value).not.toContain('onerror');
  });
});

describe('form-submit field labels', () => {
  it('own label of each password field, group label of a checkbox', () => {
    const { form, fs } = testForm(`<div class="form-box">
      <label for="p1">Password</label><input type="password" id="p1" name="p1">
      <label for="p2">Confirmation</label><input type="password" id="p2" name="p2"></div>
      <div class="form-box"><div class="label" data-for="roles">Roles</div>
      <div class="form-group"><input type="checkbox" id="r1" name="roles" value="1"><label for="r1">One</label></div></div>`);
    expect(fs.getFieldLabel(form.querySelector('#p1'))).toBe(form.querySelector('label[for="p1"]'));
    expect(fs.getFieldLabel(form.querySelector('#p2'))).toBe(form.querySelector('label[for="p2"]'));
    expect(fs.getFieldLabel(form.querySelector('#r1'))).toBe(form.querySelector('.label'));
  });
});
