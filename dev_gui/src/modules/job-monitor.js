import {
  fetchSettings,
} from '../modules/utils.js';

export function jobMonitor(item) {
  let intervalHandle;
  const jobid = item.dataset.id;
  if (!jobid) return;
  const spinner = item.querySelector('#spinner-icon');
  const statusdiv = item.querySelector("#statusdiv");
  let stop = false;
  const progress_bar = (show, percent = 0, description = ``) => {
    if (!percent) percent = 0;
    if (!description) description = "In progress";
    const progressbar = item.querySelector('#progressbar');
    if (show === false) {
      if (spinner) spinner.remove();
    } else {
      if (spinner) spinner.classList.remove('hidden');
      if (progressbar) progressbar.classList.remove('hidden');


    }

  }
  const display_errors = (errors, jobstate, msg = '') => {
    if (!errors || errors.length === 0) {
      if (msg.length) statusdiv.firstChild.innerHTML = msg;
      return;
    }
    if (errors.length && jobstate != 'E' && jobstate !== 'F') {
      const divalert = statusdiv.querySelector('.alert');
      if (divalert === null) statusdiv.insertAdjacentHTML('beforeend', `<div class="alert alert-danger inverse" data-dismissible="true">${errors.join(`<br>`)}</div> `);
      else divalert.insertAdjacentHTML('beforeend', errors.join(`<br>`));
    }
  }
  const display_next = async (url) => {
    fetch(url, fetchSettings()).then(response => response.text()).then(response => {
      statusdiv.lastChild.insertAdjacentHTML('beforeend', response);
    });

  }
  let html = [];
  const check_job_status = () => {
    fetch("/gui/job/status/" + jobid, fetchSettings).then(response => response.json()).then(job => {
      if (job.errors.length) {
        clearInterval(intervalHandle);
        progress_bar(false);
        display_errors(job.errors, job.state);
      }
      if (stop === true) return;

      if (job) {
        switch (job.state) {
          case "A":
            // question
            stop = true;
            display_next("/gui/job/question/" + job.id);
            progress_bar(false);
            clearInterval(intervalHandle);
            break;
          case "F":
            stop = true;
            progress_bar(false);
            if (spinner) spinner.remove();
            clearInterval(intervalHandle);
            if (job.finalaction) html.push(job.finalaction);
            if (job.description) statusdiv.firstChild.innerHTML = job.description;
            //  display_next("/gui/job/show/"+job.id+'?monitor=true');
            break;
          case "E":
            stop = true;
            progress_bar(false);
            spinner.remove();
            clearInterval(intervalHandle);

            break;
          case "P":
            // pending

            break;
          case "R":
            // running
            display_errors(job.errors, job.state, job.progress_msg);
            break;
        }
        progress_bar(true, job.progress_pct, job.progress_msg);
      }
      if (statusdiv) statusdiv.childNodes[1].innerHTML = html.join('');
      if (job.state && job.state == "E" || (job.state == 'F' && !job.out)) return;
      if (stop === false) setTimeout(check_job_status, 1000);
    });
  }
  check_job_status();
}