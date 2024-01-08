import {
  fetchSettings,
} from '../modules/utils.js';

export function jobMonitor(item) {
  const jobid = item.dataset.id;
  const jobStates = {
    E: 'Error',
    F: 'Done',
    R: 'Running',
    A: 'Question',
    P: 'Waiting'
  }
  if (!jobid) return;
  const spinner = document.getElementById('spinner-icon');
  const divstate = document.getElementById("divstate");
  let responsediv = document.getElementById("responsediv");
  if (responsediv === null) {
    responsediv = document.createElement('div');
    responsediv.id = 'responsediv';
    item.prepend(responsediv);
  }
  let stop = false;
  let cl = 'is-pending';
  const progress_bar = (state, percent = 0, msg = "") => {
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
  const display_errors = (errors, jobstate) => {
    if (!errors || errors.length === 0) return;
    if (errors.length && jobstate != 'E' && jobstate !== 'F') {
      const divalert = responsediv.querySelector('.alert');
      if (divalert === null) responsediv.insertAdjacentHTML('beforeend', `<div class="alert alert-danger inverse" data-dismissible="true">${errors.join(`<br>`)}</div> `);
      else divalert.insertAdjacentHTML('beforeend', errors.join(`<br>`));
    }
  }
  const display_next = async (url) => {
    fetch(url, fetchSettings()).then(response => response.text()).then(response => {
      responsediv.insertAdjacentHTML('beforeend', response);
    });

  }
  const go_next = (url, title, type = "secondary") => {
    return `<a href="${url}" class="button  is-${type}">${title}</a>`;
  }
  const set_jobstate = (job) => {
    if (!divstate) return;
    divstate.innerText = jobStates[job.state];
  }
  let html = [];
  const check_job_status = () => {

    fetch("/gui/job/status/" + jobid, fetchSettings).then(response => response.json()).then(job => {

      if (job) {
        set_jobstate(job);
        if (spinner) spinner.classList.remove('hidden');
        progress_bar(job.state, job.progress_pct, job.progress_msg);
        switch (job.state) {
          case "A":
            // question
            stop = true;
            if (spinner) spinner.remove();
            //window.location.href = window.location.origin + "/Job/Question/" + job.id;
            responsediv.innerHTML = `Question waiting for an answer ` + go_next(window.location.origin + "/Job/Question/" + job.id, 'Go', 'warning')
            break;
          case "F":
            stop = true;
            if (spinner) spinner.remove();
            if (job.finalaction) html.push(job.finalaction);
            break;
          case "E":
            if (job.errors.length) {
              display_errors(job.errors, job.state);
            }
            stop = true;
            if (spinner) spinner.remove();
            break;
          case "P":
            // pending
            break;
          case "R":
            // running
            display_errors(job.errors, job.state);
            break;
        }

        if (job.state && job.state == "E" || (job.state == 'F' && !job.out)) {
          if (responsediv) {
            responsediv.insertAdjacentHTML('afterbegin', html.join(''));
            responsediv.classList.remove('hidden');
          }
          return;
        }
      }
      if (stop === false) setTimeout(check_job_status, 1000);
      return;
    });
  }
  check_job_status();
}