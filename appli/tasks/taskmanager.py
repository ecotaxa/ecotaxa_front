from appli import db,ObjectToStr,app,PrintInCharte
from flask.ext.login import current_user
from flask import Blueprint, render_template, g, flash,jsonify
import json,os,sys


class Task(db.Model):
    __tablename__ = 'temp_tasks'
    id = db.Column(db.Integer(),db.Sequence('seq_temp_tasks'), primary_key=True)
    owner_id = db.Column(db.Integer())
    taskclass = db.Column(db.String(80) )
    taskstate = db.Column(db.String(80) )
    taskstep = db.Column(db.Integer())
    progresspct = db.Column(db.Integer())
    progressmsg = db.Column(db.String() )
    inputparam = db.Column(db.String())
    def __str__(self):
        return self.name

setattr(Task,"questiondata",db.Column(db.String()))
setattr(Task,"answerdata",db.Column(db.String()))

class AsyncTask:
    def __init__(self,task=None):
        if task==None:
            self.task=Task()
            self.task.taskclass=self.__class__.__name__
            self.task.taskstate="Question"
            self.task.taskstep=0
        else:
            self.task=task
    def Process(self):
        pass

    def UpdateParam(self):
        if hasattr(self, 'param'):
            self.task.inputparam = json.dumps(self.param.__dict__)
        db.session.commit()

    def UpdateProgress(self,pct,msg=""):
        self.task.progresspct=pct
        self.task.progressmsg=msg
        self.UpdateParam()

    #Permet de lancer le sous process
    def StartTask(self,param=None,step=1):
        if param is not None:
            self.task.inputparam=json.dumps(param.__dict__)
        self.task.taskstep=step
        self.task.taskstate="Running"
        if self.task.id==None:
            db.session.add(self.task)
        db.session.commit()
        workingdir=os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../temptask/task%06d"%(int(self.task.id))))
        if not os.path.exists(workingdir):
            os.mkdir(workingdir)
        cmd=sys.executable+" "+os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../runtask.py "+str(self.task.id)))
        # os.spawnv(os.P_NOWAIT,  sys.executable, (sys.executable,cmd, str(self.task.id))) # Ne marche pas
        # system marche, mais c'est un appel bloquant donc on le met dans une thread separé
        import _thread
        _thread.start_new_thread(os.system,(cmd,));
        # flash("Taks %d Created : %s"%(self.task.id,cmd),"success")
        flash("Taks %d subprocess Created "%(self.task.id),"success")
        return render_template('task/monitor.html',TaskID=self.task.id)

    class Params:
        def __init__(self,InitStr=None):
            if InitStr:
                tmp=json.loads(InitStr)
                for k,v  in tmp.items():
                    setattr(self,k,tmp.get(k,''))

def TaskFactory(ClassName,task=None):
    from appli.tasks.taxosync import TaskTaxoSync
    if ClassName=="TaskTaxoSync":
        return TaskTaxoSync(task)
    from appli.tasks.test  import TaskTest
    if ClassName=="TaskTest":
        return TaskTest(task)
    from appli.tasks.taskimport import TaskImport
    if ClassName=="TaskImport":
        return TaskImport(task)
    raise Exception("Invalid class name in TaskFactory : %s"%(ClassName))

def LoadTask(taskid):
    """
    Permet de charger un tache à partir de la base de données
    :param taskid:
    :return:objet AsyncTask associé à la tache
    """
    task=Task.query.filter_by(id=taskid).first()
    if task==None:
        raise Exception("Task %d not exists in database"%(taskid))
    return TaskFactory(task.taskclass,task)


@app.route('/Task/listall')
def ListTasks(owner=None):
     tasks=Task.query.all()
     txt = str(tasks)
     for t in tasks:
         txt += "<br>"+str(t.taskclass)+"-"+str(t.id)+"-"+str(t.owner_id)+"-"+str(t.taskstate)
     txt += "<br>"+str(len(tasks))
     return render_template('task/listall.html',tasks=tasks)


@app.route('/Task/Create/<ClassName>', methods=['GET', 'POST'])
def TaskCreateRouter(ClassName):
    t=TaskFactory(ClassName)
    return t.QuestionProcess()

@app.route('/Task/Question/<int:TaskID>', methods=['GET', 'POST'])
def TaskQuestionRouter(TaskID):
    task=LoadTask(TaskID)
    return task.QuestionProcess()

@app.route('/Task/Show/<int:TaskID>', methods=['GET'])
def TaskShow(TaskID):
    task=LoadTask(TaskID)
    try:
        decodedsteperrors=json.loads(task.task.inputparam).get("steperrors")
    except:
        decodedsteperrors=["Task Decoding Error"]
    return render_template('task/show.html',task=task.task,steperror=decodedsteperrors)

@app.route('/Task/ForceRestart/<int:TaskID>', methods=['GET'])
def TaskForceRestart(TaskID):
    task=LoadTask(TaskID)
    return task.StartTask(step=task.task.taskstep)

@app.route('/Task/GetStatus/<int:TaskID>', methods=['GET'])
def TaskGetStatus(TaskID):
    try:
        task=LoadTask(TaskID)
        Progress=task.task.progresspct
        if Progress==None:
            Progress=0
        if task.task.progressmsg==None:
            task.task.progressmsg="In Progress"
        if task.task.taskstate=="Question":
            rep={'q':{
                'Message':"Question waiting your Answer",
                'Url': "/Task/Question/"+str(task.task.id)}}
        else:
            rep={'d':{
                'PercentComplete':Progress,
                'WorkDescription': task.task.progressmsg}}
            if task.task.taskstate=="Complete":
                rep['d']['IsComplete']="Y"
            if task.task.taskstate=="Error":
                rep['d']['IsError']="Y"
    except Exception as e:
        rep={'Error':str(e) }
    #app.logger.info("Getstatus=%s",rep)
    return jsonify(rep)

@app.route('/Task/Test', methods=['GET'])
def TaskTestRouter():
    return render_template('task/monitor.html',TaskID=38)