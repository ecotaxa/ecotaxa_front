import {
  fetchSettings,
  html_spinner,
  create_box
} from '../modules/utils.js';
import {
  css
} from '../modules/modules-config.js';

export function jobMonitor(item, options = {}) {
  const jobOptions = {
    url: "/gui/job/status/"
  }
  options = { ...jobOptions,
    ...options
  }
  const jobid = item.dataset.id;
  const jobStates = {
    E: 'Error',
    F: 'Done',
    R: 'Running',
    A: 'Question',
    P: 'Waiting'
  }
  if (!jobid) return;
  const populates = (item.dataset.populate) ? JSON.parse(item.dataset.populate) : {};
  if (item.dataset.state && ['E', 'F', 'A'].indexOf(item.dataset.state) >= 0) return;
  const divstate = document.getElementById("divstate");
  let responsediv = document.getElementById("responsediv");
  if (responsediv === null) {
    responsediv = document.createElement('div');
    responsediv.id = 'responsediv';
    item.prepend(responsediv);
  }


  let stop = false;
  let cl = 'is-pending';
  const progress_bar = function(state, percent = 0, msg = "") {
    if (!percent) percent = 0;
    const progressbar = document.getElementById('progressbar');
    responsediv.textContent = msg;
    if (divstate) divstate.textContent = msg;
    if (progressbar !== null) {
      progressbar.firstChild.textContent = percent + '%';
      const progressbarsz = progressbar.querySelector('.percent');
      if (progressbarsz) {
        progressbarsz.classList.remove(cl);
        cl = 'is-running';
        switch (state) {
          case 'E':
            cl = 'is-error';
            break;
          case 'F':
            cl = 'is-done';
            break;
          case 'A':
            cl = 'is-warning';
            break;
        }
        if (!progressbarsz.classList.contains(cl)) progressbarsz.classList.add(cl);
        progressbarsz.style.width = percent + '%';

      }
    }
  }

  function spinner_icon(state) {
    const spinner = document.getElementById('spinner-icon');
    if (spinner === null) return;
    switch (state) {
      case 'R':
      case 'P':
        if (spinner) spinner.classList.remove(css.hide);
        const svg = spinner.querySelector('svg');
        if (svg === null) spinner.insertAdjacentHTML('afterbegin', html_spinner('text-stone-700'));
        break;
      default:
        spinner.remove();
        break;
    }
  }

  function display_errors(errors, jobstate) {
    if (!errors || errors.length === 0) return;
    if (errors.length && jobstate != 'E' && jobstate !== 'F') {
      const divalert = responsediv.querySelector('.alert');
      if (divalert === null) responsediv.insertAdjacentHTML('beforeend', `<div class="alert danger inverse" data-dismissible="true">${errors.join(`<br>`)}</div> `);
      else divalert.insertAdjacentHTML('beforeend', errors.join(`<br>`));
    }

  }

  function go_next(url, title, type = "secondary") {
    return `<a href="${url}" class="button  is-${type}">${title}</a>`;
  }

  function set_jobstate(state) {
    if (!divstate) return;
    divstate.innerText = jobStates[state];
  }

  function set_joberrors(errors) {
    if (!divstate) return;
    divstate.innerText = jobStates[state];
  }

  function set_jobinfo(job, key) {
    if (Object.keys(populates).indexOf(key) < 0) return;
    const divinfo = document.getElementById(populates[key]);
    if (!divinfo) return;
    switch (key) {
      case "state":
        divinfo.innerText = jobStates[job.state];
        break;
      case "errors":
        const trigger = divinfo.querySelector('[data-action="toggle"]');
        if (trigger) {
          if (job.errors.length === 0) {
            trigger.classList.add(css.hide);
            return;
          } else {
            trigger.classList.remove(css.hide);
            trigger.click();
          }
        }
        display_errors(job.errors, job.state);
        const list = create_box('ul', {}, create_box('div', {
          class: (divinfo.dataset.target) ? divinfo.dataset.target.replace('.', '') : "collapseerrors"
        }, divinfo));
        job.errors.forEach(error => {
          const li = create_box('li', {
            text: error
          }, list);
        });
        break;
      default:
        divinfo.innerText = (job[key]) ? job[key] : '';
        break;
    }

  }

  function display_infos(job) {
    spinner_icon(job.state);
    progress_bar(job.state, job.progress_pct, job.progress_msg);
    Object.keys(populates).forEach(info => {
      set_jobinfo(job, info);
    });
  }
  let html = [];

  function check_job_status() {
    fetch(options.url + jobid, fetchSettings).then(response => response.json()).then(job => {

      if (job) {
        if (job.state) {
          display_infos(job);
        }

        switch (job.state) {
          case "A":
            // question
            stop = true;
            //window.location.href = window.location.origin + "/Job/Question/" + job.id;
            responsediv.innerHTML = `Question waiting for an answer ` + go_next(window.location.origin + "/Job/Question/" + job.id, 'Go', 'warning');
            populate("questiondata");

            break;
          case "F":
            stop = true;
            if (job.finalaction) html.push(job.finalaction);
            break;
          case "E":

            stop = true;
            break;
          case "P":
            // pending
            break;
          case "R":
            // running
            break;
        }

        if (job.state && job.state === "E" || job.state === 'F' || job.type === "Prediction") {
          //  display_final(job.finalaction);
          if (responsediv) {
            responsediv.insertAdjacentHTML('afterbegin', html.join(''));
            responsediv.classList.remove(css.hide);
          }
          stop = true;
        }
      } else stop = true;

      if (stop === false) setTimeout(check_job_status, 1000);
      return;
    }).catch((err) => {
      console.log('err', err);
    });
  }
  check_job_status();
}