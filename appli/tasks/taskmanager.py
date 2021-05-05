import datetime
import json
import logging
import os
import re
import shutil
import sys
from typing import Optional

import flask
from flask import render_template, g, flash, jsonify, request
from flask_login import current_user
from flask_security import login_required

from appli import db, app, PrintInCharte, gvg, AddTaskSummaryForTemplate, database, gvp, XSSEscape
from appli.database import ExecSQL, GetAll

# Environment variable for transmitting cookie, i.e. web session, to subprocess
ECOTAXA_COOKIE = "ECOTAXA_COOKIE"


class Task(db.Model):
    __tablename__ = 'temp_tasks'
    id = db.Column(db.Integer(), db.Sequence('seq_temp_tasks'), primary_key=True)
    owner_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    owner_rel = db.relationship("users")
    taskclass = db.Column(db.String(80))
    taskstate = db.Column(db.String(80))
    taskstep = db.Column(db.Integer())
    progresspct = db.Column(db.Integer())
    progressmsg = db.Column(db.String())
    inputparam = db.Column(db.String())
    creationdate = db.Column(db.DateTime())
    lastupdate = db.Column(db.DateTime())

    def __str__(self):
        return self.name

    # e.g. "ProjectId": "2990"
    PROJ_ID_RE = r"\"ProjectId\": \"(\d*)\""

    def project_id(self) -> Optional[str]:
        if self.inputparam is None:
            return None
        match = re.search(self.PROJ_ID_RE, self.inputparam)
        if match:
            return match.group(1)
        return None


setattr(Task, "questiondata", db.Column(db.String()))
setattr(Task, "answerdata", db.Column(db.String()))


class AsyncTask:
    """
        An asynchronous task, AKA a job.
        The same class is used in forked python processes and in flask app.
    """

    def __init__(self, task: Optional[Task] = None):
        if task is None:
            self.task = Task()
            self.task.taskclass = self.__class__.__name__
            self.task.taskstate = "Question"
            self.task.taskstep = 0
            self.task.creationdate = datetime.datetime.now()
        else:
            self.task = task
        self.cookie = None

    def Process(self):
        pass

    def UpdateParam(self):
        if hasattr(self, 'param'):
            self.task.inputparam = json.dumps(self.param.__dict__)
        self.task.lastupdate = datetime.datetime.now()
        db.session.commit()

    def UpdateProgress(self, pct, msg=""):
        self.task.progresspct = pct
        self.task.progressmsg = msg
        self.UpdateParam()

    def GetWorkingDir(self):
        return os.path.normpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../temptask/task%06d" % (int(self.task.id))))

    def GetWorkingSchema(self):
        return "task%06d" % (int(self.task.id))

    def LogErrorForUser(self, Msg):
        # On ne trace dans les 2 zones ques les mille premieres erreurs.
        if len(self.param.steperrors) < 1000:
            self.param.steperrors.append(Msg)
            logging.warning("%s", Msg)
            # app.logging.warning("%s",Msg) c'est fait depuis la tache qui est dans un process séparé
        elif len(self.param.steperrors) == 1000:
            self.param.steperrors.append("More errors truncated")
            logging.warning("More errors truncated")
            # app.logging.warning("More errors truncated")

    # Permet de lancer le sous process
    def StartTask(self, param=None, step=1, FileToSave=None, FileToSaveFileName=None):
        # Create/update DB task
        if param is not None:
            self.task.inputparam = json.dumps(param.__dict__)
        self.task.taskstep = step
        self.task.taskstate = "Running"
        if self.task.id is None:
            db.session.add(self.task)
        db.session.commit()

        # Get request cookie for session transmission
        cookie = request.cookies.get('session')
        if cookie is not None:
            os.environ[ECOTAXA_COOKIE] = cookie
        workingdir = self.GetWorkingDir()
        if not os.path.exists(workingdir):
            os.mkdir(workingdir)
        if FileToSave is not None:
            FileToSave.save(os.path.join(self.GetWorkingDir(), FileToSaveFileName))
        # cmd=os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../runtask.py"))
        cmdfull = app.PythonExecutable + " " + os.path.normpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../runtask.py " + str(self.task.id)))
        app.logger.info("Start Task process : %s" % (cmdfull,))
        # os.spawnv(os.P_NOWAIT,  sys.executable, (sys.executable,cmd, str(self.task.id))) # Ne marche pas
        # system marche, mais c'est un appel bloquant donc on le met dans une thread separé
        # avec uwsgi il faut specifier l'option close-on-exec=true dans uwsgi.ini sinon c'est un appel bloquant.
        import _thread
        _thread.start_new_thread(os.system, (cmdfull,))
        flash("Task %d subprocess Created " % (self.task.id,), "success")
        ProjectID = getattr(self.param, 'ProjectId', None)
        if ProjectID:
            Prj = database.Projects.query.filter_by(projid=ProjectID).first()
            g.headcenter = "<h4>Project : <a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, XSSEscape(Prj.title))
        return render_template('task/monitor.html', TaskID=self.task.id, RedirectToMonitor=True)

    class Params:
        def __init__(self, InitStr=None):
            if InitStr:
                tmp = json.loads(InitStr)
                for k, v in tmp.items():
                    setattr(self, k, tmp.get(k, ''))


def TaskFactory(ClassName, task=None):
    from appli.tasks.test import TaskTest
    if ClassName == "TaskTest":
        return TaskTest(task)
    # Tasks running in present component
    from appli.tasks.taskclassifauto2 import TaskClassifAuto2
    if ClassName == "TaskClassifAuto2":
        return TaskClassifAuto2(task)
    from appli.tasks.taskexporttxt import TaskExportTxt
    if ClassName == "TaskExportTxt":
        return TaskExportTxt(task)
    # Particle module tasks
    from .taskpartzooscanimport import TaskPartZooscanImport
    if ClassName == "TaskPartZooscanImport":
        return TaskPartZooscanImport(task)
    from .taskpartexport import TaskPartExport
    if ClassName == "TaskPartExport":
        return TaskPartExport(task)

    raise Exception("Invalid class name in TaskFactory : %s" % (ClassName,))


def LoadTask(taskid, cookie_from_env=False):
    """
    Permet de charger une tâche à partir de la base de données
    :param taskid:
    :return:objet AsyncTask associé à la tache
    """
    task = Task.query.filter_by(id=taskid).first()
    if task is None:
        raise Exception("Task %d not exists in database" % (taskid,))
    ret = TaskFactory(task.taskclass, task)
    # Amend the task with Web session cookie
    if cookie_from_env:
        # Find the cookie in environment variable
        ret.cookie = os.environ.get(ECOTAXA_COOKIE)
    else:
        # Get the cookie from HTTP client
        try:
            ret.cookie = request.cookies.get('session')
        except RuntimeError:
            ret.cookie = os.environ.get(ECOTAXA_COOKIE)
    return ret


@app.route('/Task/listall')
@login_required
def ListTasks():
    from appli.jobs.emul import _add_jobs_to_task_list, _clean_jobs
    g.headcenter = "<H3>Task Monitor</h3>"
    AddTaskSummaryForTemplate()

    seeall = ""
    is_admin = current_user.has_role(database.AdministratorLabel)
    wants_admin = gvg("seeall") == 'Y'
    if is_admin and wants_admin:
        tasks = Task.query.filter_by().order_by(Task.id.desc()).all()
        seeall = '&seeall=Y'
    else:
        tasks = Task.query.filter_by(owner_id=current_user.id).order_by(Task.id.desc()).all()

    txt = ""
    if gvg("cleandone") == 'Y' or gvg("cleanerror") == 'Y' or gvg("cleanall") == 'Y':
        txt = "Cleaning process result :<br>"
        clean_all = gvg("cleanall") == 'Y'
        clean_done = gvg("cleandone") == 'Y'
        clean_error = gvg("cleanerror") == 'Y'
        for t in tasks:
            if clean_all or (clean_done and t.taskstate == 'Done') or (clean_error and t.taskstate == 'Error'):
                txt += DoTaskClean(t.id)
        txt += _clean_jobs(clean_all, clean_done, clean_error, wants_admin)

    tasks = Task.query.filter_by(owner_id=current_user.id).order_by(Task.id.desc()).all()
    # txt += "<a class='btn btn-default'  href=?cleandone=Y>Clean All Done</a> <a class='btn btn-default'
    # href=?cleanerror=Y>Clean All Error</a>   <a class='btn btn-default' href=?cleanall=Y>Clean All
    # (warning !!!)</a>  Task count : "+str(len(tasks))
    _add_jobs_to_task_list(tasks, wants_admin)
    return render_template('task/listall.html', tasks=tasks, header=txt,
                           len_tasks=len(tasks), seeall=seeall,
                           IsAdmin=is_admin)


@app.route('/Task/Create/<ClassName>', methods=['GET', 'POST'])
@login_required
def TaskCreateRouter(ClassName):
    gvp('dummy')  # Protection bug flask connection reset si on fait post sans lire les champs
    AddTaskSummaryForTemplate()
    task = TaskFactory(ClassName)
    # Get the cookie from HTTP client
    task.cookie = request.cookies.get('session')
    task.task.owner_id = current_user.get_id()
    return task.QuestionProcess()


@app.route('/Task/Question/<int:TaskID>', methods=['GET', 'POST'])
@login_required
def TaskQuestionRouter(TaskID):
    AddTaskSummaryForTemplate()
    task = LoadTask(TaskID)
    return task.QuestionProcess()


@app.route('/Task/Show/<int:TaskID>', methods=['GET'])
@login_required
def TaskShow(TaskID):
    AddTaskSummaryForTemplate()
    # noinspection PyBroadException
    try:
        task = LoadTask(TaskID)
    except Exception:
        return PrintInCharte("This task doesn't exist anymore, perhaps it was automatically purged")

    txt = ""
    if gvg('log') == "Y":
        WorkingDir = task.GetWorkingDir()
        # app.send_static_file(os.path.join(WorkingDir,"TaskLog.txt"))
        return flask.send_from_directory(WorkingDir, "TaskLog.txt")
    if gvg('blog') == "Y":
        WorkingDir = task.GetWorkingDir()
        # app.send_static_file(os.path.join(WorkingDir,"TaskLog.txt"))
        return flask.send_from_directory(WorkingDir, "TaskLogBack.txt")
    if gvg('CustomDetails') == "Y":
        return task.ShowCustomDetails()
    if "GetResultFile" in dir(task):
        f = task.GetResultFile()
        if f is None:
            txt += "Error, final file not available"
        else:
            txt += "<a href='/Task/GetFile/%d/%s' class='btn btn-primary btn-sm ' role='button'>Get file %s</a>" % (
                TaskID, f, f)

    CustomDetailsAvail = "ShowCustomDetails" in dir(task)
    # noinspection PyBroadException
    try:
        decodedsteperrors = json.loads(task.task.inputparam).get("steperrors")
    except Exception:
        decodedsteperrors = ["Task Decoding Error"]
    ProjectID = getattr(task.param, 'ProjectId', None)
    if ProjectID:
        Prj = database.Projects.query.filter_by(projid=ProjectID).first()
        g.headcenter = "<h4>Project : <a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, XSSEscape(Prj.title))
    return render_template('task/show.html', task=task.task, steperror=decodedsteperrors,
                           CustomDetailsAvail=CustomDetailsAvail, extratext=txt)


# noinspection PyUnusedLocal
@app.route('/Task/GetFile/<int:TaskID>/<filename>', methods=['GET'])
@login_required
def TaskGetFile(TaskID, filename):
    task = LoadTask(TaskID)
    WorkingDir = task.GetWorkingDir()
    return flask.send_from_directory(WorkingDir, task.GetResultFile())


@app.route('/Task/ForceRestart/<int:TaskID>', methods=['GET'])
@login_required
def TaskForceRestart(TaskID):
    AddTaskSummaryForTemplate()
    task = LoadTask(TaskID)
    return task.StartTask(step=task.task.taskstep)


@app.route('/Task/Clean/<int:TaskID>', methods=['GET'])
@login_required
def TaskClean(TaskID):
    AddTaskSummaryForTemplate()
    if gvg('thengotoproject') == 'Y':
        task = LoadTask(TaskID)
        ProjectID = getattr(task.param, 'ProjectId', None)
    else:
        ProjectID = ''
    Msg = DoTaskClean(TaskID)
    Msg += '<br><a href="/Task/listall"><span class="label label-info"> Back to Task List</span></a>'
    if ProjectID:
        Msg += """"<script>
            window.location.href = "/prj/%s"
        </script>""" % (ProjectID,)
    return PrintInCharte(Msg)


def DoTaskClean(TaskID):
    task = LoadTask(TaskID)
    ProjectID = getattr(task.param, 'ProjectId', None)
    WorkingDir = task.GetWorkingDir()
    Msg = "Erasing Task %d <br>" % TaskID
    # noinspection PyBroadException
    try:
        ExecSQL("DROP SCHEMA  IF EXISTS  task%06d CASCADE" % TaskID)
        if os.path.exists(WorkingDir):
            shutil.rmtree(WorkingDir)
            Msg += "Temp Folder Erased (%s)<br>" % WorkingDir
        db.session.delete(task.task)
        db.session.commit()
        Msg += "DB Record Erased<br>"
    except Exception:
        flash("Error While erasing " + str(sys.exc_info()), 'error')
    if ProjectID:
        Msg += "<a href='/prj/%s'>Back to project</a><br>" % ProjectID
    CustomReturnURL = getattr(task.param, 'CustomReturnURL', None)
    CustomReturnLabel = getattr(task.param, 'CustomReturnLabel', None)
    if CustomReturnLabel and CustomReturnURL:
        Msg += "<a href='{0}'>{1}</a><br>".format(CustomReturnURL, CustomReturnLabel)
    return Msg


@app.route('/Task/GetStatus/<int:TaskID>', methods=['GET'])
def TaskGetStatus(TaskID):
    AddTaskSummaryForTemplate()
    try:
        task = LoadTask(TaskID)
        Progress = task.task.progresspct
        if Progress is None:
            Progress = 0
        if task.task.progressmsg is None:
            task.task.progressmsg = "In Progress"
        if task.task.taskstate == "Question":
            rep = {'q': {
                'Message': "Question waiting your Answer",
                'Url': "/Task/Question/" + str(task.task.id)}}
        else:
            rep = {'d': {
                'PercentComplete': Progress,
                'WorkDescription': task.task.progressmsg}}
            if len(task.param.steperrors):
                rep['d']['WorkDescription'] += "".join("<br>\n-" + s for s in task.param.steperrors)

            if task.task.taskstate == "Done":
                rep['d']['IsComplete'] = "Y"
                rep['d']['ExtraAction'] = "<a href='/Task/Show/%d' class='btn btn-primary btn-sm ' " \
                                          "role='button'>Show Task</a>" % TaskID
                if "GetDoneExtraAction" in dir(task):
                    rep['d']['ExtraAction'] = task.GetDoneExtraAction()
                if "GetResultFile" in dir(task):
                    f = task.GetResultFile()
                    if f is None:
                        rep['d']['ExtraAction'] = "Error, final file not available"
                    elif f == '':
                        pass  # Parfois l'export ne retourne pas de fichier car envoi sur FTP
                    else:
                        rep['d']['ExtraAction'] = "<a href='/Task/GetFile/%d/%s' class='btn btn-primary btn-sm ' " \
                                                  "role='button'>Get file %s</a>" \
                                                  % (TaskID, f, f)
                        if getattr(task.param, 'ProjectId', None):
                            rep['d']['ExtraAction'] += " <a href='/Task/Clean/%d?thengotoproject=Y' " \
                                                       "class='btn btn-primary btn-sm ' " \
                                                       "role='button'>FORCE Delete of %s and back to project " \
                                                       "(no danger for the original database) </a>" \
                                                       % (TaskID, f)
                        else:
                            rep['d']['ExtraAction'] += " <a href='/Task/Clean/%d' class='btn btn-primary btn-sm ' " \
                                                       "role='button'>FORCE Delete of %s (no danger for the " \
                                                       "original database) </a>" \
                                                       % (TaskID, f)
                        rep['d']['ExtraAction'] += "<br>Local users can also retrieve the file on the " \
                                                   "Ecotaxa folder temptask/task%06d (useful for huge files)" \
                                                   % (int(task.task.id))

            if task.task.taskstate == "Error":
                rep['d']['IsError'] = "Y"
    except Exception as e:
        rep = {'d': {'IsError': 'Y', 'WorkDescription': str(e)}}
    # app.logger.info("Getstatus=%s",rep)
    return jsonify(rep)


@app.route('/Task/autoclean/')
def AutoCleanManual():
    return PrintInCharte(AutoClean())


def AutoClean():
    """ Called from cron.py """
    TaskList = GetAll("""SELECT id, owner_id, taskclass, taskstate, taskstep, progresspct, progressmsg,
       inputparam, creationdate, lastupdate, questiondata, answerdata
  FROM temp_tasks
  where lastupdate<current_timestamp - interval '30 days'
      or ( lastupdate<current_timestamp - interval '7 days' and taskstate='Done' )
      or ( creationdate<current_timestamp - interval '1 days' and lastupdate is null)""")
    txt = "Cleanning process result :<br>"
    for t in TaskList:
        txt += DoTaskClean(t['id'])
    return txt


@app.route('/Task/Monitor/<int:TaskID>', methods=['GET'])
def TaskMonitor(TaskID):
    AddTaskSummaryForTemplate()
    # noinspection PyBroadException
    try:
        task = LoadTask(TaskID)
        ProjectID = getattr(task.param, 'ProjectId', None)
        if ProjectID:
            Prj = database.Projects.query.filter_by(projid=ProjectID).first()
            g.headcenter = "<h4>Project : <a href='/prj/{0}'>{1}</a></h4>".format(Prj.projid, XSSEscape(Prj.title))
        return render_template('task/monitor.html', TaskID=task.task.id)
    except Exception:
        return PrintInCharte("This task doesn't exist anymore, perhaps it was automaticaly purged")
