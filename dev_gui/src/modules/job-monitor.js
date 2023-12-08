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
  const display_errors = (errors) => {
    const erroone = errors.shift();
    const other = (errors.lentgh) ? `<a class="font-btn triggershow" data-action="toggle"  data-target=".alert-errors" data-show="View" data-hide="Hide">{{_('all errors...')}}</a><div class="alert-errors hide">${errors.join(`<br>`)}</div>` : ``;
    statusdiv.firstChild.innerHTML = `<div class="alert alert-danger" data-dismissible="true">${errorone} ${other}</div>`;
  }
  const display_next = async (url) => {
    fetch(url, fetchSettings()).then(response => response.text()).then(response => {
      statusdiv.lastChild.insertAdjacentHTML('beforeend', response);
    });

  }
  let html = [];
  const check_job_status = () => {
    fetch("/gui/job/status/" + jobid, fetchSettings).then(response => response.json()).then(job => {

      if (job.errors.length && job.state != 'E') {
        clearInterval(intervalHandle);
        progress_bar(false);
        display_errors(job.errors);
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
            display_errors(job.errors);
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