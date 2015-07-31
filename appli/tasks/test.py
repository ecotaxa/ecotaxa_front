# -*- coding: utf-8 -*-
from appli import db,app, database , ObjectToStr,PrintInCharte,gvp
from flask import Blueprint, render_template, g, flash
from io import StringIO
import html,functools,logging,json,time
from datetime import datetime
from appli.tasks.taskmanager import AsyncTask,LoadTask
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class TaskTest(AsyncTask):
    class Params (AsyncTask.Params):
        def __init__(self,InitStr=None):
            super().__init__(InitStr)
            if InitStr==None: # Valeurs par defaut ou vide pour init
                self.InData='My In Data'

    def __init__(self,task=None):
        super().__init__(task)
        if task==None:
            self.param=self.Params()
        else:
            self.param=self.Params(task.inputparam)

    def SPCommon(self):
        logging.info("Execute SPCommon")


    def SPStep1(self):
        logging.info("Input Param = %s"%(self.param.__dict__))
        logging.info("Start Step 1")
        progress=0
        for i in range(10):
            time.sleep(0.5)
            progress+=2
            self.UpdateProgress(progress,"My Message %d"%(progress))
        logging.info("End Step 1")
        self.task.taskstate="Question"
        db.session.commit()


    def SPStep2(self):
        logging.info("Start Step 2")
        for i in range(20,102,2):
            time.sleep(0.1)
            self.UpdateProgress(i,"My Step 2 Message %d"%(i))
        logging.info("End Step 2")


    def QuestionProcess(self):
        txt="<h1>Test Task</h1>"
        if self.task.taskstep==0:
            txt+="<h3>Task Creation</h3>"
            if gvp('starttask')=="Y":
                for k,v  in self.param.__dict__.items():
                    setattr(self.param,k,gvp(k))
                # Verifier la coherence des données
                if(len(self.param.InData)<5):
                    flash("Champ In Data trop court","error")
                else:
                    return self.StartTask(self.param)
            return render_template('task/testcreate.html',header=txt,data=self.param)
        if self.task.taskstep==1:
            txt+="<h3>Task Question 1</h3>"
            if gvp('starttask')=="Y":
                self.param.InData2=gvp("InData2")
                # Verifier la coherence des données
                if(len(self.param.InData2)<5):
                    flash("Champ In Data 2 trop court","error")
                else:
                    return self.StartTask(self.param,step=2)
            return render_template('task/testquestion1.html',header=txt,data=self.param)


        return PrintInCharte(txt)




if __name__ == '__main__':
    t=LoadTask(1)
    t.Process()
