import sys; sys.dont_write_bytecode = True

from datetime import date, datetime, timedelta

from flask import (Flask, flash, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from flask_login import LoginManager
from uuid import uuid4
from flask_compress import Compress
from flask_socketio import SocketIO
from threading import Thread
from time import sleep
from flask_migrate import Migrate
from models.staff import Staff
from models.member import Member

compress = Compress()

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SECRET_KEY"] = uuid4().hex

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = ''
    login_manager.needs_refresh_message = (u"Session timedout, please re-login")
    login_manager.needs_refresh_message_category = "info"

    db.init_app(app)
    compress.init_app(app)
    Migrate(app, db)

    return (app, db, login_manager, socketio, compress)


app, db, login_manager, socketio, compress = create_app()
fpsThread = None

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(username):
    return Staff.query.filter_by(username=username).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.form.get('next')
    if current_user.is_authenticated:
        return redirect(next_page if next_page else url_for('index'))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        if username:
            username = username.lower()
        password = form.password.data

        # Query the database to find a user with the provided username
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash(f'''User with username {username} doesn't exist. Please check your username and try again.''', 'danger')

        elif user and user.password == password:
            usr_session = UserSession(user=user) # add a new session to the user
            db.session.add(usr_session)
            db.session.commit()

            # If the user exists and the password is correct, log them in
            # and set the session default duration to one day.
            login_user(user, duration=timedelta(hours=4))

            flash('Login successful', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash(f'''Login failed. Please check your username and password.''', 'danger')

    return render_template('login.html', form=form) 


@app.route('/logout')
@login_required
def logout():
    current_user.sessions[-1].end_date = datetime.now()
    db.session.commit()
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    form = MemberForm()

    if request.method == 'POST' and form.validate_on_submit():
        """ date < datetime.date() """
        if form.end_date.data < datetime.now().date():
            flash('End date must be in the future.', 'warning')
            return redirect(url_for('add_member'))

        if Member.query.filter_by(member_id=form.member_id.data).first():
            flash('Member with this id already exists.', 'warning')
            return redirect(url_for('add_member'))

        if Member.query.filter_by(phone_number=form.phone_number.data).first():
            flash('Member with this phone number already exists.', 'warning')
            return redirect(url_for('add_member'))

        member = Member(
            member_id=form.member_id.data,
            phone_number=form.phone_number.data,
            full_name=form.full_name.data,
            membership=form.membership.data,
            email=form.email.data,
            created_by=current_user.username,
        )
        subscription = Subscription(member_id=member.id, period=form.period.data, end_date=form.end_date.data, created_by=current_user.username)
        subscription_record = SubscriptionHistory(subscription=subscription)
        member_history_record = MemberHistory(member=member, modBy=current_user.username)

        usrA = UserAction(username=current_user.username, action='إضافة عضو', details=f'{member.member_id}', path=f'/members/{member.member_id}')
        db.session.add_all([member, subscription, subscription_record, member_history_record, usrA])
        db.session.commit()
        flash(message='Member added successfully', category='success')
        return redirect(url_for('add_member'))

    return render_template('add_member.html', form=form, hMsg='إضافة عضو جديد')


# query all members
@app.route('/members', methods=['GET'])
@login_required
def members():
    members = Member.query.order_by(Member.created_at.desc()).all()


    members_data = [
        [
            member.member_id, member.fullname, member.phone_number,
            member.created_by, member.created_at, '✅' if bool(member.fingerprint) else '❌'
        ]
    for member in members]
    

    header = [
        "ID",
        "fullname",
        "phone number",
        "created by",
        "created at",
        "fingerprint"
    ]

    return render_template('show_records.html', rows=members_data, columns=header)



@app.route('/', methods=['GET', 'POST'])
@app.route('/query', methods=['GET', 'POST'])
@login_required
def index():
    query_form = QueryMemberForm()
    
    if (request.method == 'POST' and query_form.validate_on_submit() or request.method == 'GET' and request.args.get('id')) :
        if (isGet:=request.method == 'GET'):
            query_form.memberID_or_phoneNumber.data = request.args.get('id')

        memberID_or_phoneNumber = get_phone_number(query_form.memberID_or_phoneNumber.data)

        member = Member.query.filter(
            db.or_(
                Member.member_id    == memberID_or_phoneNumber,
                Member.phone_number == memberID_or_phoneNumber
            )).first()

        # check whether the member's subscription has expired or not
        if member:
            if member.subscription.end_date < datetime.now():
                member.subscription.active = False
                db.session.commit()

            mark_attend = (len(member.records)==0 or (datetime.now() - member.records[-1].attending_date).total_seconds()>60*60*12)
            if isGet:flash(f'تم التعرف على العضو ({member.full_name}) وتحضيرة', 'success')
            return render_template('index.html', query_form=query_form, member=member, mark_attend=mark_attend, isGet=isGet)
        else:
            flash('member with this id or phone number doesn\'t exist in the database.', 'info')

    # Render the home page with the Query Member form
    return render_template('index.html', query_form=query_form)


# socket on connect
@socketio.on('connect')
def connect():
    print('reconnected')
    socketio.emit('reviewed', {'state': 'cancel', 'fid': 1}, namespace='/fps')
    socketio.emit('connected', {'data': 'Connected'})


@socketio.on('init', namespace='/fps')
def connect_fps():
    members = Member.query.where(Member.finger_template != None).all()
    members_fingerprints = [[member.member_id, member.finger_template] for member in members]
    socketio.emit('membersFingerprints', {'data': True, 'members': members_fingerprints}, namespace='/fps')
    print('sent fingerprints')


@socketio.on('askForApproval', namespace='/fps')
def register(data):
    socketio.emit('approvalProc', data)


@socketio.on('reviewed')
def approved(data):
    socketio.emit('reviewed', data, namespace='/fps')


@app.route('/api/queryMember', methods=['POST'])
def query_member():
    id_or_phone = request.json['id_or_phone']
    member = Member.query.filter(
        db.or_(
            Member.member_id    == id_or_phone,
            Member.phone_number == id_or_phone
        )).first()
    

    if member:
        if bool(member.finger_template)==True:
            return jsonify({'data': 'exists', "member_id": member.member_id})
        return jsonify({'data': True, 'member_id': member.member_id, 'full_name': member.full_name, 'phone_number': member.phone_number, 'membership': member.membership.value, 'email': member.email, 'subscription': member.subscription.period, 'active': member.subscription.active, 'start_date': member.subscription.start_date, 'end_date': member.subscription.end_date, 'records': len(member.records)})
    else:
        return jsonify(data=False)



@socketio.on("identified", namespace='/fps')
def already_registered(data):
    member = Member.query.filter_by(member_id=data['fid']).first()
    if member:
        mark_attend = (len(member.records)==0 or (datetime.now() - member.records[-1].attending_date).total_seconds()>60*60*12)
        socketio.emit("identified", {'data': True, 'mark_attend': mark_attend, 'member_id': member.member_id, 'full_name': member.full_name, 'phone_number': member.phone_number})


@socketio.on('registering', namespace='/fps')
def registering_member(data):
    socketio.emit("message", data)


@socketio.on('registered', namespace='/fps')
def registered_member(data):
    regTemp = data['template']
    member_id = data['fid']
    member = Member.query.filter(
        db.or_(
            Member.member_id    == member_id,
            Member.phone_number == member_id
        )).first()
    member.finger_template = regTemp
    db.session.commit()
    mark_attend = (len(member.records)==0 or (datetime.now() - member.records[-1].attending_date).total_seconds()>60*60*12)
    socketio.emit("identified", {'data': True, 'mark_attend': mark_attend, 'member_id': member.member_id, 'full_name': member.full_name, 'phone_number': member.phone_number})


@socketio.on('deffirent_finger', namespace='/fps')
def deffirent_finger(data):
    socketio.emit("differentFinger", data)


@socketio.on('error', namespace='/fps')
def error(data):
    socketio.emit("errorMsg", data)

    if fpsThread is not None and fpsThread.is_alive():
        fps.keep_alive = False
        fpsThread.join()
        sleep(1)

    fps.keep_alive = True
    fpsThread.start()


# TODO:
# 1. make admins able to change ids and phone numbers of members
# 2. rightly conifugre the add_members via excel method



if __name__ == '__main__':
    print('RUNNING...')
    # fps = FingerprintScanner()
    # fpsThread = Thread(target=fps.listenToFingerprints)
    # fpsThread.start()
    # serve(app, port=8080, threads=12)
    app.run(port=8080, debug=True)
    # socketio.run(app, port=8080)
    fps.logger.warning('Server stopped. Shutting down fingerprint scanner...')
    fps.keep_alive = False
