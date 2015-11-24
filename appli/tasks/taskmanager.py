from appli import db,app,PrintInCharte,gvg,AddTaskSummaryForTemplate
from flask.ext.login import current_user
from flask import  render_template, g, flash,jsonify
import json,os,sys,datetime,shutil,flask,logging
from flask.ext.security import login_required
from appli.database import ExecSQL,GetAll

class Task(db.Model):
    __tablename__ = 'temp_tasks'
    id = db.Column(db.Integer(),db.Sequence('seq_temp_tasks'), primary_key=True)
    owner_id = db.Column(db.Integer(),db.ForeignKey('users.id'))
    owner_rel=db.relationship("users")
    taskclass = db.Column(db.String(80) )
    taskstate = db.Column(db.String(80) )
    taskstep = db.Column(db.Integer())
    progresspct = db.Column(db.Integer())
    progressmsg = db.Column(db.String() )
    inputparam = db.Column(db.String())
    creationdate = db.Column(db.DateTime())
    lastupdate = db.Column(db.DateTime())
    def __str__(self):
        return self.name

setattr(Task,"questiondata",db.Column(db.String()))
setattr(Task,"answerdata",db.Column(db.String()))

class AsyncTask:
    def __init__(self,task=None):
        if task is None:
            self.task=Task()
            self.task.taskclass=self.__class__.__name__
            self.task.taskstate="Question"
            self.task.taskstep=0
            self.task.creationdate=datetime.datetime.now()
        else:
            self.task=task
    def Process(self):
        pass

    def UpdateParam(self):
        if hasattr(self, 'param'):
            self.task.inputparam = json.dumps(self.param.__dict__)
        self.task.lastupdate=datetime.datetime.now()
        db.session.commit()

    def UpdateProgress(self,pct,msg=""):
        self.task.progresspct=pct
        self.task.progressmsg=msg
        self.UpdateParam()

    def GetWorkingDir(self):
        return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../temptask/task%06d"%(int(self.task.id))))
    def GetWorkingSchema(self):
        return  "task%06d"%(int(self.task.id))

    def LogErrorForUser(self,Msg):
        # On ne trace dans les 2 zones ques les milles premieres erreurs.
        if len(self.param.steperrors)<1000:
            self.param.steperrors.append(Msg)
            logging.warning("%s",Msg)
            # app.logging.warning("%s",Msg) c'est fait depuis la tache qui est dans un process séparé
        elif len(self.param.steperrors)==1000:
            self.param.steperrors.append("More errors truncated")
            logging.warning("More errors truncated")
            # app.logging.warning("More errors truncated")

    #Permet de lancer le sous process
    def StartTask(self,param=None,step=1,FileToSave=None,FileToSaveFileName=None):
        if param is not None:
            self.task.inputparam=json.dumps(param.__dict__)
        self.task.taskstep=step
        self.task.taskstate="Running"
        if self.task.id is None:
            db.session.add(self.task)
        db.session.commit()
        workingdir=self.GetWorkingDir()
        if not os.path.exists(workingdir):
            os.mkdir(workingdir)
        if FileToSave is not None:
            FileToSave.save(os.path.join(self.GetWorkingDir(),FileToSaveFileName))
        # cmd=os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../runtask.py"))
        cmdfull=app.PythonExecutable+" "+os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../runtask.py "+str(self.task.id)))
        app.logger.info("Start Task process : %s"%(cmdfull,))
        # os.spawnv(os.P_NOWAIT,  sys.executable, (sys.executable,cmd, str(self.task.id))) # Ne marche pas
        # system marche, mais c'est un appel bloquant donc on le met dans une thread separé
        # avec uwsgi il faut specifier l'option close-on-exec=true dans uwsgi.ini sinon c'est un appel bloquant.
        import _thread
        _thread.start_new_thread(os.system,(cmdfull,))
        flash("Taks %d subprocess Created "%(self.task.id,),"success")
        return render_template('task/monitor.html',TaskID=self.task.id)

    class Params:
        def __init__(self,InitStr=None):
            if InitStr:
                tmp=json.loads(InitStr)
                for k,v  in tmp.items():
                    setattr(self,k,tmp.get(k,''))

def TaskFactory(ClassName,task=None):
    from appli.tasks.test  import TaskTest
    if ClassName=="TaskTest":
        return TaskTest(task)
    from appli.tasks.taskimport import TaskImport
    if ClassName=="TaskImport":
        return TaskImport(task)
    from appli.tasks.taskclassifauto import TaskClassifAuto
    if ClassName=="TaskClassifAuto":
        return TaskClassifAuto(task)
    from appli.tasks.tasktaxoimport import TaskTaxoImport
    if ClassName=="TaskTaxoImport":
        return TaskTaxoImport(task)
    from appli.tasks.taskexporttxt import TaskExportTxt
    if ClassName=="TaskExportTxt":
        return TaskExportTxt(task)
    from appli.tasks.tasksubset import TaskSubset
    if ClassName=="TaskSubset":
        return TaskSubset(task)
    from appli.tasks.taskexportdb import TaskExportDb
    if ClassName=="TaskExportDb":
        return TaskExportDb(task)
    from appli.tasks.taskimportdb import TaskImportDB
    if ClassName=="TaskImportDB":
        return TaskImportDB(task)

    raise Exception("Invalid class name in TaskFactory : %s"%(ClassName,))

def LoadTask(taskid):
    """
    Permet de charger un tache à partir de la base de données
    :param taskid:
    :return:objet AsyncTask associé à la tache
    """
    task=Task.query.filter_by(id=taskid).first()
    if task is None:
        raise Exception("Task %d not exists in database"%(taskid,))
    return TaskFactory(task.taskclass,task)


@app.route('/Task/listall')
@login_required
def ListTasks(owner=None):
     g.headcenter="<H3>Task Monitor</h3>"
     AddTaskSummaryForTemplate()
     tasks=Task.query.filter_by(owner_id=current_user.id).order_by("id").all()
     txt=""
     if gvg("cleandone")=='Y' or gvg("cleanerror")=='Y' or gvg("cleanall")=='Y':
        txt="Cleanning process result :<br>"
        for t in tasks:
            if (gvg("cleandone")=='Y' and t.taskstate=='Done') or (gvg("cleanall")=='Y') \
            or (gvg("cleanerror")=='Y' and t.taskstate=='Error') :
                txt+=DoTaskClean(t.id)
        tasks=Task.query.filter_by(owner_id=current_user.id).order_by("id").all()
     txt += "<a class='btn btn-default'  href=?cleandone=Y>Clean All Done</a> <a class='btn btn-default' href=?cleanerror=Y>Clean All Error</a>   <a class='btn btn-default' href=?cleanall=Y>Clean All (warning !!!)</a>  Task count : "+str(len(tasks))
     return render_template('task/listall.html',tasks=tasks,header=txt)


@app.route('/Task/Create/<ClassName>', methods=['GET', 'POST'])
@login_required
def TaskCreateRouter(ClassName):
    AddTaskSummaryForTemplate()
    t=TaskFactory(ClassName)
    t.task.owner_id=current_user.get_id()
    return t.QuestionProcess()

@app.route('/Task/Question/<int:TaskID>', methods=['GET', 'POST'])
@login_required
def TaskQuestionRouter(TaskID):
    AddTaskSummaryForTemplate()
    task=LoadTask(TaskID)
    return task.QuestionProcess()

@app.route('/Task/Show/<int:TaskID>', methods=['GET'])
@login_required
def TaskShow(TaskID):
    AddTaskSummaryForTemplate()
    try:
        task=LoadTask(TaskID)
    except:
        return PrintInCharte("This task doesn't exists anymore, peraphs it was automaticaly purged")

    txt=""
    if gvg('log')=="Y":
        WorkingDir = task.GetWorkingDir()
        # app.send_static_file(os.path.join(WorkingDir,"TaskLog.txt"))
        return flask.send_from_directory(WorkingDir,"TaskLog.txt")
    if gvg('CustomDetails')=="Y":
        return task.ShowCustomDetails()
    if "GetResultFile" in dir(task):
        f=task.GetResultFile()
        if f is None:
            txt+="Error, final file not available"
        else:
            txt+="<a href='/Task/GetFile/%d/%s' class='btn btn-primary btn-sm ' role='button'>Get file %s</a>"%(TaskID,f,f)

    CustomDetailsAvail="ShowCustomDetails" in dir(task)
    try:
        decodedsteperrors=json.loads(task.task.inputparam).get("steperrors")
    except:
        decodedsteperrors=["Task Decoding Error"]
    return render_template('task/show.html',task=task.task,steperror=decodedsteperrors,CustomDetailsAvail=CustomDetailsAvail,extratext=txt)

@app.route('/Task/GetFile/<int:TaskID>/<filename>', methods=['GET'])
@login_required
def TaskGetFile(TaskID,filename):
    task=LoadTask(TaskID)
    WorkingDir = task.GetWorkingDir()
    return flask.send_from_directory(WorkingDir,task.GetResultFile())

@app.route('/Task/ForceRestart/<int:TaskID>', methods=['GET'])
@login_required
def TaskForceRestart(TaskID):
    AddTaskSummaryForTemplate()
    task=LoadTask(TaskID)
    return task.StartTask(step=task.task.taskstep)

@app.route('/Task/Clean/<int:TaskID>', methods=['GET'])
@login_required
def TaskClean(TaskID):
    AddTaskSummaryForTemplate()
    if gvg('thengotoproject')=='Y':
        task = LoadTask(TaskID)
        ProjectID=getattr(task.param,'ProjectId',None)
    else: ProjectID=''
    Msg = DoTaskClean(TaskID)
    Msg+='<br><a href="/Task/listall"><span class="label label-info"> Back to Task List</span></a>'
    if ProjectID:
        Msg+=""""<script>
            window.location.href = "/prj/%s"
        </script>"""%(ProjectID,)
    return PrintInCharte(Msg)

def DoTaskClean(TaskID):
    task = LoadTask(TaskID)
    ProjectID=getattr(task.param,'ProjectId',None)
    WorkingDir = task.GetWorkingDir()
    Msg = "Erasing Task %d <br>"%TaskID
    try:
        ExecSQL("DROP SCHEMA  IF EXISTS  task%06d CASCADE"%TaskID)
        if os.path.exists(WorkingDir):
            shutil.rmtree(WorkingDir)
            Msg += "Temp Folder Erased (%s)<br>"%WorkingDir
        db.session.delete(task.task)
        db.session.commit()
        Msg += "DB Record Erased<br>"
    except:
        flash("Error While erasing " + str(sys.exc_info()), 'error')
    if ProjectID:
        Msg += "<a href='/prj/%s'>Back to project</a><br>"%ProjectID
    return Msg


@app.route('/Task/GetStatus/<int:TaskID>', methods=['GET'])
def TaskGetStatus(TaskID):
    AddTaskSummaryForTemplate()
    try:
        task=LoadTask(TaskID)
        Progress=task.task.progresspct
        if Progress is None:
            Progress=0
        if task.task.progressmsg is None:
            task.task.progressmsg="In Progress"
        if task.task.taskstate=="Question":
            rep={'q':{
                'Message':"Question waiting your Answer",
                'Url': "/Task/Question/"+str(task.task.id)}}
        else:
            rep={'d':{
                'PercentComplete':Progress,
                'WorkDescription': task.task.progressmsg}}
            if task.task.taskstate=="Done":
                rep['d']['IsComplete']="Y"
                rep['d']['ExtraAction']="<a href='/Task/Show/%d' class='btn btn-primary btn-sm ' role='button'>Show Task</a>"%TaskID
                if "GetDoneExtraAction" in dir(task):
                    rep['d']['ExtraAction']=task.GetDoneExtraAction()
                if "GetResultFile" in dir(task):
                    f=task.GetResultFile()
                    if f is None:
                        rep['d']['ExtraAction']="Error, final file not available"
                    else:
                        rep['d']['ExtraAction']="<a href='/Task/GetFile/%d/%s' class='btn btn-primary btn-sm ' role='button'>Get file %s</a>"%(TaskID,f,f)
                        if getattr(task.param,'ProjectId',None):
                            rep['d']['ExtraAction']+=" <a href='/Task/Clean/%d?thengotoproject=Y' class='btn btn-primary btn-sm ' role='button'>FORCE Delete of %s and back to project (no danger for the original database) </a>"%(TaskID,f)
                        else:
                            rep['d']['ExtraAction']+=" <a href='/Task/Clean/%d' class='btn btn-primary btn-sm ' role='button'>FORCE Delete of %s (no danger for the original database) </a>"%(TaskID,f)


            if task.task.taskstate=="Error":
                rep['d']['IsError']="Y"
    except Exception as e:
        rep={'d':{'IsError':'Y','WorkDescription':str(e) }}
    #app.logger.info("Getstatus=%s",rep)
    return jsonify(rep)

@app.route('/Task/autoclean/')
def AutoCleanManual():
    return PrintInCharte(AutoClean())

def AutoClean():
    TaskList=GetAll("""SELECT id, owner_id, taskclass, taskstate, taskstep, progresspct, progressmsg,
       inputparam, creationdate, lastupdate, questiondata, answerdata
  FROM temp_tasks
  where lastupdate<current_timestamp - interval '7 days' or ( creationdate<current_timestamp - interval '1 days' and lastupdate is null)""")
    txt="Cleanning process result :<br>"
    for t in TaskList:
        txt+=DoTaskClean(t['id'])
    return txt
