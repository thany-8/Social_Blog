from flask import redirect,render_template,url_for,request,Blueprint
from flask_login import login_user, current_user,logout_user,login_required
from socialblog import db
from socialblog.models import User, BlogPost
from socialblog.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from socialblog.users.picture_handler import add_profile_pic
from flask import flash


users = Blueprint('users',__name__)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))



@users.route('/register', methods= ['GET', 'POST'])
def register():
    form = RegistrationForm()


    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                     password=form.password.data )
        
        db.session.add(user)
        db.seesion.commit()

        #flash('Thank for registration')

        return redirect(url_for('users.login'))
    
    return render_template('register.html', form=form)


@users.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.valite_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data) and user is not None:

            login_user(user)
            flash('Log in Success!')

            next = request.args.get('next')

            if next == None or not next[0]=='/':
                next = url_for('core.index')

            return redirect(next)
        
    return render_template('login.html', form=form)


@users.route('/account', methods= ['GET','POST'])
@login_required
def account():

    form = UpdateUserForm()
    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)


            


    


