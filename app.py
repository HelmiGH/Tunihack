# import time
# from absl import app, logging
# import cv2
# import numpy as np
# import tensorflow as tf

from flask import Flask, request, Response, jsonify, send_from_directory, abort,render_template,make_response,redirect,url_for,flash
import os
from random import randint
import json
#Login
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length,ValidationError
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text


# Initialize Flask application
app = Flask(__name__)
#variable globale 
global coord_blocs
coord_blocs=[]
global ww
global hh

# @app.route('/')
# @app.route('/home')
# def home():
#     if current_user.is_authenticated:
#         if current_user.type=="admin":
#             users=User.query.count()-1
#             achievements= Project.query.count()
#             contrib=Project.query.filter(Project.annotation!="").count()
#             satisfaction=Project.query.filter(Project.rate != 0).with_entities(func.avg(Project.rate).label('average')).first()
#             # sql=text('Select user.firstname, count(annotation) as nb_count from project,user where user.id=project.owner and project.annotation<>'' group by owner order by nb_count desc Limit 6')
#             # top_contrib=db.engine.execute(sql)
#             contributers= Project.query.join(User,User.id==Project.owner).with_entities(User.firstname.label('name1') ,User.lastname.label('name2'),func.count(Project.annotation).label('nb_annot')).filter(Project.annotation!="").group_by(Project.owner).all()
#             t_contrib=list()
        
#             for con in contributers:
#                 t_contrib.append([con.nb_annot,con.name1,con.name2])
                
#             t_contrib.sort(reverse=True)
#             a=len(t_contrib)
#             return render_template('dashboard.html',users=users,achievements=achievements,contrib=contrib,satis=int(satisfaction[0]),t_contrib=t_contrib,a=a,msg="home")
#         else:
#             login="Log Out"
#             link="logout"
#     else:
#         login="Login"
#         link="login"
#     return render_template('home.html',login=login,link=link)
# @app.route('/upgrade')
# def upgrade():
#     if current_user.is_authenticated:
#         login="Log Out"
#         link="logout"
#     else:
#         login="Login"
#         link="login"
#     return render_template('upgrade.html',login=login,link=link)
# @app.route('/payment')
# def payment():
#     return render_template('payment.html')    


# @app.route('/test')
# def test():
#     return render_template('test.html')

# @app.route('/visualizer',methods=['POST','GET'])
# @login_required
# def visualizer():
#     if current_user.is_authenticated:
#         login="Log Out"
#         link="logout"
#     else:
#         login="Login"
#         link="login"
#     content=   request.form.get('code')  
#     if(content==None):
#         cont=request.form.get('resultat')                  
#         print("blooooooooocs:",ww,hh)
#         l=cov_afterannotation(cont)
#         content=test1(coord_blocs,l,ww,hh)
#         id_pr=request.form.get('id_pr')
#         project = Project.query.filter_by(id=id_pr).first()
#         project.annotation = cont
#         db.session.commit()
        
    
    # f = open("static/result.html", "w",encoding='utf-8')
    # f.write(content)
    # f.close()
    
    # return render_template('visualizer.html',content=content,login=login,link=link)
# Login
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\MSI\\Documents\\Ossec Hackathon\\Tunihack\\database.db'
# app.config['SQLALCHEMY_DATABASE_URI']="mysql://root@localhost/database"
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False

db = SQLAlchemy(app)                                     
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "info"
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String(80))
    last_donation=db.Column(db.DateTime, default=datetime.datetime.utcnow)
    nb_donnation=db.Column(db.Integer,default=0)
    wallet=db.Column(db.Float,default=0)
    Phone=db.Column(db.Integer,default=0)
    def __init__(self, firstname, lastname,email,password):
        self.firstname = firstname
        self.phone = phone
        self.email = email
        self.password = password
class Hospital(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(50), unique=True,nullable=False)
    region = db.Column(db.String(50),nullable=False)
    nb_donnations = db.Column(db.Integer,default=0)
    total_donnations=db.Column(db.Float,default=0)
    description=db.Column(db.Text(),nullable=False)

class achievements(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    Montant=db.Column(db.Float,default=0)
    region=db.Column(db.String(50),nullable=False)
    description=db.Column(db.Text(),nullable=False)
    ddl=db.Column(db.DateTime, nullable=False)
    reason=db.Column(db.Text(),nullable=False)
    expect=db.Column(db.Text(),nullable=False)
    progress_donation=db.Column(db.Float,default=0)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'),Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    

class RegisterForm_user(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    firstname = StringField('firstname', validators=[InputRequired(), Length(min=5, max=20)])
    phone = StringField('phone', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class RegisterForm_Hospital(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    name = StringField('firstname', validators=[InputRequired(), Length(min=5, max=20)])
    region = StringField('phone', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    description=StringField('phone', validators=[InputRequired(), Length(min=0, max=60)])
class GeneralForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    firstname = StringField('firstname', validators=[InputRequired(),Length(min=4, max=15)])
    lastname = StringField('lastname', validators=[InputRequired(),Length(min=4, max=15)])
    
class SecurityForm(FlaskForm):
    old_password = PasswordField('old_password', validators=[InputRequired(),Length(min=8, max=80)])
    new_password = PasswordField('new_password', validators=[InputRequired(),Length(min=8, max=80)])

@app.route('/')
@app.route('/home')
def home():

    return render_template('index.html')
    
@app.route('/hospitals',methods=['POST','GET'])
def hospitals():      

    return render_template('hospitals.html')

@app.route('/services_details',methods=['POST','GET'])
def services_details():      

    return render_template('services-details.html')

@app.route('/profile',methods=['POST','GET'])
def profile():      

    return render_template('profile.html')

@app.route('/needs',methods=['POST','GET'])
def needs():      

    return render_template('needs.html')

@app.route('/my_account',methods=['POST','GET'])
def my_account():      

    return render_template('my-account.html')

@app.route('/make_donation',methods=['POST','GET'])
def make_donation():      

    return render_template('make_donation.html')

@app.route('/hospital_details',methods=['POST','GET'])
def hospital_details():      

    return render_template('hospital-details.html')

@app.route('/contact',methods=['POST','GET'])
def contact():      

    return render_template('contact.html')

@app.route('/change_password',methods=['POST','GET'])
def change_password():      

    return render_template('change-password.html')

@app.route('/change_password',methods=['POST','GET'])
def achievements():      

    return render_template('achievements.html')

@app.route('/invoices',methods=['POST','GET'])
def invoices():      

    return render_template('invoices.html')
  
# def rate_mean(rates):
#     return sum(rates)/len(rates)


# @app.route('/login',methods=['POST','GET'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('profile'))
    
#     admin_account=User.query.filter(User.type=="admin").first()
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             if check_password_hash(user.password, form.password.data):
#                 login_user(user)
#                 flash('Welcome '+str(user.firstname).capitalize()+' !', 'success')
#                 if form.email.data == admin_account.email:
#                     return redirect(url_for('dashboard'))
#                 return redirect(url_for('profile'))
#         flash('Wrong Credentials ! Try again.', 'danger')
#         return redirect(url_for('login'))

#     return render_template('login.html',form=form)


# @app.route('/sign_up',methods=['POST','GET'])
# def sign_up():
#     if current_user.is_authenticated:
#         return redirect(url_for('profile'))
#     form = RegisterForm()
#     dupl_email=""
#     if User.query.filter(User.email==form.email.data).first():
#         dupl_email= "Email already exists"
#     if form.validate_on_submit():
#         hashed_password = generate_password_hash(form.password.data, method='sha256')
#         new_user = User(firstname=form.firstname.data,lastname=form.lastname.data, email=form.email.data, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         user = User.query.filter_by(email=form.email.data).first()
#         login_user(user)
#         flash('Welcome aboard '+str(user.firstname).capitalize()+' !', 'success')
#         return redirect(url_for('profile'))
    
        

#     return render_template('sign_up.html', form=form,dupl_email=dupl_email)

# @app.route('/profile',methods=['POST','GET'])
# @login_required
# def profile():
#     if(request.form.get('pay') != None):
#         user = User.query.filter_by(id=current_user.id).first()
#         user.premium = True
#         db.session.commit()
#     premium=current_user.premium
#     print('premium ou nn :', premium)
#     if current_user.type != "admin":
#         achievements= Project.query.filter_by(owner=current_user.id).all()
#         nb_achievements=Project.query.filter_by(owner=current_user.id).count()
#         rate=Project.query.with_entities(func.avg(Project.rate).label('rate')).filter(Project.owner==current_user.id).first()
#         annot=Project.query.with_entities(Project.annotation.label('annotation')).filter(Project.owner==current_user.id).all()
#         if rate[0] == None:
#             rate_final=0
#         else:
#             rate_final=int(rate[0])
#         #contrib=0
#         #for i in annot:
#         #    if all(i):
#         #        contrib+=1
#         #print(contrib)
#         contrib=Project.query.filter(Project.owner==current_user.id,Project.annotation!="").count()

        
#         form_g = GeneralForm()
#         form_s=SecurityForm()
#         action=request.form.get('action')
#         if action=="general":
            
#             #user = User.query.filter_by(email=form.email.data).first()
#             if form_g.validate_on_submit():
#                 current_user.firstname = form_g.firstname.data
#                 current_user.lastname = form_g.lastname.data
#                 db.session.commit()
#                 flash('Your account has been updated!', 'success')
#                 return redirect(url_for('profile'))
#             else:
#                 flash('Something went wrong. Try again!', 'danger')
#                 return redirect(url_for('profile'))
                    
#         elif action=="security":
            
#             if form_s.validate_on_submit():
#                 if check_password_hash(current_user.password, form_s.old_password.data):
                        
#                     current_user.password = generate_password_hash(form_s.new_password.data, method='sha256')
#                     db.session.commit()
#                     flash('Your password has been updated!', 'success')
#                     return redirect(url_for('profile'))
#                 else:
#                     flash('Wrong Password', 'danger')
#                     return redirect(url_for('profile'))
#             else:
#                 flash('Your password is too small. Try again!', 'danger')
#                 return redirect(url_for('profile')) 
        
#         return render_template('profile.html', form_g=form_g,form_s=form_s,achievements=achievements,nb_achievements=nb_achievements,rate_mean=rate_final,contrib=contrib,premium=premium)   
#     else:
#             users=User.query.count()-1
#             achievements= Project.query.count()
#             contrib=Project.query.filter(Project.annotation!="").count()
#             satisfaction=Project.query.filter(Project.rate != 0).with_entities(func.avg(Project.rate).label('average')).first()
#             contributers= Project.query.join(User,User.id==Project.owner).with_entities(User.firstname.label('name1') ,User.lastname.label('name2'),func.count(Project.annotation).label('nb_annot')).filter(Project.annotation!="").group_by(Project.owner).all()
#             t_contrib=list()
        
#             for con in contributers:
#                 t_contrib.append([con.nb_annot,con.name1,con.name2])
                
#             t_contrib.sort(reverse=True)
#             a=len(t_contrib)
#             return render_template('dashboard.html',users=users,achievements=achievements,contrib=contrib,satis=int(satisfaction[0]),t_contrib=t_contrib,a=a,msg="profile")
        

# @app.route('/rate',methods=['POST'] )
# @login_required
# def rate():
#     input=str(request.form.get('input'))+".jpg"
#     output=request.form.get('output')
#     rate=request.form.get('rate')
#     annotation=""
#     new_project = Project(owner=current_user.id,input=input,output=output,rate=rate,annotation=annotation)

#     db.session.add(new_project)
#     db.session.commit()
#     flash('New project added with success!', 'success')
#     return redirect(url_for('profile'))

# @app.route('/save',methods=['POST'] )
# @login_required
# def save():
#     input=str(request.form.get('input'))+".jpg"
#     output=request.form.get('output')
#     rate=0
#     annotation=" "
#     new_project = Project(owner=current_user.id,input=input,output=output,rate=rate,annotation=annotation)

#     db.session.add(new_project)
#     db.session.commit()
#     flash('New project added with success!', 'success')
#     return redirect(url_for('profile'))

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('home'))




# @app.route('/dashboard',methods=['POST','GET'])
# @login_required
# def dashboard():
#     users=User.query.count()-1
#     achievements= Project.query.count()
#     contrib=Project.query.filter(Project.annotation!="").count()
#     satisfaction=Project.query.filter(Project.rate != 0).with_entities(func.avg(Project.rate).label('average')).first()
#     # sql=text('Select user.firstname, count(annotation) as nb_count from project,user where user.id=project.owner and project.annotation<>'' group by owner order by nb_count desc Limit 6')
#     # top_contrib=db.engine.execute(sql)
#     contributers= Project.query.join(User,User.id==Project.owner).with_entities(User.firstname.label('name1') ,User.lastname.label('name2'),func.count(Project.annotation).label('nb_annot')).filter(Project.annotation!="").group_by(Project.owner).all()
#     t_contrib=list()
   
#     for con in contributers:
#         t_contrib.append([con.nb_annot,con.name1,con.name2])
        
#     t_contrib.sort(reverse=True)
#     a=len(t_contrib)
        
#     return render_template('dashboard.html',users=users,achievements=achievements,contrib=contrib,satis=int(satisfaction[0]),t_contrib=t_contrib,a=a,msg="oui")

# @app.route('/achievements',methods=['POST','GET'])
# @login_required
# def achievements():
#     achievements= Project.query.join(User, User.id==Project.owner).add_columns(Project.id, User.firstname,User.lastname,Project.input,Project.creation_date,Project.rate,Project.annotation).all()
#     return render_template('achievements.html',achievements=achievements)

# @app.route('/users',methods=['POST','GET'])
# @login_required
# def users():
#     # contrib=Project.query.filter(Project.annotation!="").with_entities(Project.owner, func.count(Project.id).label('cont')).group_by(Project.owner).all()
#     # nb_achievements=Project.query.with_entities(Project.owner, func.count(Project.id).label('cont')).group_by(Project.owner).all()
#     Users= User.query.all()

#     infos=list()
#     for user in Users:
#         nb_achievements=0
#         if (Project.query.filter(Project.owner==user.id).count()!=0):
#             nb_achievements=Project.query.filter(Project.owner==user.id).count()
#         contrib=0

#         if (Project.query.filter(Project.owner==user.id,Project.annotation!="").count()!=0):
#             contrib=contrib=Project.query.filter(Project.owner==user.id,Project.annotation!="").count()

#         satisfaction=Project.query.filter(Project.owner==user.id,Project.rate != 0).with_entities(func.avg(Project.rate).label('average')).first()
#         if satisfaction.average is None:
#             satis=0
#         else:
#             satis=satisfaction
#         #satisfaction=db.session.execute('SELECT avg(rate) as avg_rate FROM project WHERE owner= :val', {'val':user.id})
        
        
#         print("aaaaaaaaaatiiiis",type(satis))
#         #float(str(satis).strip('(').strip(')').strip(',').split('.')[0])
#         infos.append([user.id,user.firstname,user.lastname,user.email,nb_achievements,contrib,float(str(satis).strip('(').strip("Decimal('").strip(')').strip(',').split('.')[0])])
            

#     return render_template('Users.html',infos=infos)



# # API that returns JSON with classes found in images
# @app.route('/detections', methods=['POST','GET'])
# def get_detections():
#     raw_images = []
#     images = request.files.getlist("images")
#     image_names = []
#     for image in images:

#         image_name = image.filename
#         image_names.append(image_name)
#         image.save(os.path.join(os.getcwd(), image_name))
#         img_raw = tf.image.decode_image(
#             open(image_name, 'rb').read(), channels=3)
#         raw_images.append(img_raw)
        
#     num = 0
    
#     # create list for final response
#     response = []

#     for j in range(len(raw_images)):
#         # create list of responses for current image
#         responses = []
#         raw_img = raw_images[j]
#         num+=1
#         img = tf.expand_dims(raw_img, 0)
#         img = transform_images(img, size)

#         t1 = time.time()
#         boxes, scores, classes, nums = yolo(img)
#         t2 = time.time()
#         print('time: {}'.format(t2 - t1))

#         print('detections:')
#         for i in range(nums[0]):
#             print('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
#                                             np.array(scores[0][i]),
#                                             np.array(boxes[0][i])))
#             responses.append({
#                 "class": class_names[int(classes[0][i])],
#                 "confidence": float("{0:.2f}".format(np.array(scores[0][i])*100))
#             })
#         response.append({
#             "image": image_names[j],
#             "detections": responses
#         })
#         img = cv2.cvtColor(raw_img.numpy(), cv2.COLOR_RGB2BGR)
#         img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
#         cv2.imwrite(output_path + 'detection' + str(num) + '.jpg', img)
#         print('output saved to: {}'.format(output_path + 'detection' + str(num) + '.jpg'))

#     #remove temporary images
#     for name in image_names:
#         os.remove(name)
#     try:
#         l=jsonify({"response":response})
#         return render_template('detections.html',result=l)
#     except FileNotFoundError:
#         abort(404)

# # API that returns image with detections on it
# @app.route('/image', methods= ['POST','GET'])
# def get_image():
#     global coord_blocs
#     global ww
#     global hh
#     if current_user.is_authenticated:
#         login="Log Out"
#         link="logout"
#     else:
#         login="Login"
#         link="login"
#     image = request.files["images"]
#     image_name = image.filename
#     #parag(os.path.join(os.getcwd(), image_name))
#     image.save(os.path.join(os.getcwd(), image_name))
#     copyfile(os.path.join(os.getcwd(), image_name), "static/input.jpg")
#     image_number=str(randint(1,10000))
#     copyfile(os.path.join(os.getcwd(), image_name), "static/inputs/input"+image_number+".jpg")

#     img_raw = tf.image.decode_image(
#         open(image_name, 'rb').read(), channels=3)

#     ###################YOLO1 : Blocs #############################################
#     img = tf.expand_dims(img_raw, 0)
#     img = transform_images(img, size)

#     t1 = time.time()
#     boxes, scores, classes, nums = yolo(img)
#     t2 = time.time()
#     print('time: {}'.format(t2 - t1))

#     print('detections:')
#     list_res=[]
#     for i in range(nums[0]):
        
#         list_res.append({
#                 "class": str(class_names[int(classes[0][i])]),   
#                 "score": str(float("{0:.2f}".format(np.array(scores[0][i])*100))),
#                 "boxes": ' '.join(map(str, np.array(boxes[0][i]).tolist() )) 
#             })
        
#         print('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
#                                         np.array(scores[0][i]),
#                                         np.array(boxes[0][i])))

#     print(list_res)
#     img = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
#     # img = conv(img, (boxes, scores, classes, nums), class_names)
#     img,coord_blocs= draw_outputs(img, (boxes, scores, classes, nums), class_names)
#     print("Les coordonnée du bloc sont: ", coord_blocs)
#     n="detect"+str(randint(1,1000))+".jpg"
#     cv2.imwrite(output_path + n, img)
#     print('output saved to: {}'.format(output_path + n))
#     # prepare image for response
#     _, img_encoded = cv2.imencode('.png', img)
#     response = img_encoded.tostring()



#     #######################YOLO 2 ######################################
#     img2 = tf.expand_dims(img_raw, 0)
#     img2 = transform_images2(img2, size)

#     t1 = time.time()
#     boxes2, scores2, classes2, nums2 = yolo2(img2)
#     t2 = time.time()
#     print('time: {}'.format(t2 - t1))

#     print('detections:')
#     list_res2=[]
#     for i in range(nums2[0]):
        
#         list_res2.append({
#                 "class": str(class_names2[int(classes2[0][i])]),   
#                 "score": str(float("{0:.2f}".format(np.array(scores2[0][i])*100))),
#                 "boxes": ' '.join(map(str, np.array(boxes2[0][i]).tolist() )) 
#             })
        
#         print('\t{}, {}, {}'.format(class_names2[int(classes2[0][i])],
#                                         np.array(scores2[0][i]),
#                                         np.array(boxes2[0][i])))

#     print(list_res2)
#     img2 = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
#     # img = conv(img, (boxes2, scores2, classes2, nums2), class_names2)
#     img2,coord_elements= draw_outputs2(img2, (boxes2, scores2, classes2, nums2), class_names2)
#     print('Les coodonnées des élements sont: ', coord_elements)
#     n2="detect"+str(randint(1,1000))+".jpg"
#     cv2.imwrite(output_path2 + n2, img2)
#     print('output saved to: {}'.format(output_path2 + n2))
#     hh, ww, cc = img.shape
    
    
#     # prepare image for response
#     _, img_encoded = cv2.imencode('.png', img2)
#     response = img_encoded.tostring()
    
#     #remove temporary image
#     os.remove(image_name)
#     #os.remove("static/input.jpg")
#     s=test1(coord_blocs,coord_elements,ww,hh)
#     content=s
#     try:
#         #Response(response=response, status=200, mimetype='image/png')
#         return render_template('detections.html',res=n,res2=n2,cord=list_res2,content=content,login=login,link=link,image_number=image_number)
#     except FileNotFoundError:
#         abort(404)



# @app.route('/index',methods= ['POST'])
# @login_required
# def index():
#     if(current_user.premium==True):
#         image_name = "label_img.jpg" 
#         #parag(os.path.join(os.getcwd(), image_name))
#         copyfile("static/inputs/"+request.form.get("images"),os.path.join(os.getcwd(), "label_img.jpg"))
#         copyfile(os.path.join(os.getcwd()+"\\static\\inputs", request.form.get("images")), "static/input.jpg")

#         img_raw = tf.image.decode_image(
#             open(image_name, 'rb').read(), channels=3)

#         ###################YOLO1 : Blocs #############################################
#         img = tf.expand_dims(img_raw, 0)
#         img = transform_images(img, size)

#         t1 = time.time()
#         boxes, scores, classes, nums = yolo(img)
#         t2 = time.time()
#         print('time: {}'.format(t2 - t1))

#         print('detections:')
#         list_res=[]
#         for i in range(nums[0]):
            
#             list_res.append({
#                     "class": str(class_names[int(classes[0][i])]),   
#                     "score": str(float("{0:.2f}".format(np.array(scores[0][i])*100))),
#                     "boxes": ' '.join(map(str, np.array(boxes[0][i]).tolist() )) 
#                 })
            
#             print('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
#                                             np.array(scores[0][i]),
#                                             np.array(boxes[0][i])))

#         print(list_res)
#         img = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
#         # img = conv(img, (boxes, scores, classes, nums), class_names)
#         img,coord_blocs= draw_outputs(img, (boxes, scores, classes, nums), class_names)
#         print("Les coordonnée du bloc sont: ", coord_blocs)
#         n="detect"+str(randint(1,1000))+".jpg"
#         cv2.imwrite(output_path + n, img)
#         print('output saved to: {}'.format(output_path + n))
#         # prepare image for response
#         _, img_encoded = cv2.imencode('.png', img)
#         response = img_encoded.tostring()



#         #######################YOLO 2 ######################################
#         img2 = tf.expand_dims(img_raw, 0)
#         img2 = transform_images2(img2, size)

#         t1 = time.time()
#         boxes2, scores2, classes2, nums2 = yolo2(img2)
#         t2 = time.time()
#         print('time: {}'.format(t2 - t1))

#         print('detections:')
#         list_res2=[]
#         for i in range(nums2[0]):
            
#             list_res2.append({
#                     "class": str(class_names2[int(classes2[0][i])]),   
#                     "score": str(float("{0:.2f}".format(np.array(scores2[0][i])*100))),
#                     "boxes": ' '.join(map(str, np.array(boxes2[0][i]).tolist() )) 
#                 })
            
#             print('\t{}, {}, {}'.format(class_names2[int(classes2[0][i])],
#                                             np.array(scores2[0][i]),
#                                             np.array(boxes2[0][i])))

#         print(list_res2)
#         img2 = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
#         # img = conv(img, (boxes2, scores2, classes2, nums2), class_names2)
#         img2,coord_elements= draw_outputs2(img2, (boxes2, scores2, classes2, nums2), class_names2)
#         print('Les coodonnées des élements sont: ', coord_elements)
#         n2="detect"+str(randint(1,1000))+".jpg"
#         cv2.imwrite(output_path2 + n2, img2)
#         print('output saved to: {}'.format(output_path2 + n2))
#         hh, ww, cc = img.shape
        
        
#         # prepare image for response
#         _, img_encoded = cv2.imencode('.png', img2)
#         response = img_encoded.tostring()
        
#         #remove temporary image
#         os.remove(image_name)
#         #os.remove("static/input.jpg")

#         a=cov_labellingData(coord_elements)
#         b='[{"width":'+str(ww)+',"height":'+str(hh)+'}]'
#         print(a)
        
#         input=str(request.form.get('images'))
#         output=request.form.get('output')
#         rate=0
#         annotation=" "
#         new_project = Project(owner=current_user.id,input=input,output=output,rate=rate,annotation=annotation)
#         db.session.add(new_project)
#         db.session.commit()
#         id_pr=new_project.id
#         print('idddd',id_pr)
#         try:
#             #Response(response=response, status=200, mimetype='image/png')
#             return render_template('index.html',a=a,b=b,id_pr=id_pr)
#         except FileNotFoundError:
#             abort(404)
#     else:
#         return render_template('upgrade.html',login="Log Out",link="logout")


if __name__ == '__main__':
    app.run(debug=True, host = '127.0.0.1', port=5000)