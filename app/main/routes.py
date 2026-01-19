from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import emit, join_room
import math
from app import db, limiter, socketio
from app.models import Provider, ServiceRequest, User, Message, ContactInquiry
from app.main.forms import RequestForm, LoginForm, ProviderForm, ContactForm
from app.main import bp
from app.email import send_contact_inquiry_email
from app.sms import notify_admin_new_request, notify_customer_status_update

@bp.route("/")
def index():
    unique_services = [r[0] for r in db.session.query(Provider.service).distinct().all()]
    return render_template("index.html", services=unique_services)

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        inquiry = ContactInquiry(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(inquiry)
        db.session.commit()
        send_contact_inquiry_email(inquiry)
        flash('Thank you! Your message has been sent successfully.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)

@bp.route("/providers")
def get_providers():
    service_filter = request.args.get('service')
    location_filter = request.args.get('location')

    query = Provider.query
    if service_filter:
        query = query.filter_by(service=service_filter)
    if location_filter:
        query = query.filter_by(location=location_filter)
    
    providers = query.all()

    # Proximity Sorting
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)

    if user_lat is not None and user_lon is not None:
        def get_distance(p):
            if p.latitude is None or p.longitude is None:
                return float('inf')
            # Haversine formula
            R = 6371  # Earth radius in km
            dlat = math.radians(p.latitude - user_lat)
            dlon = math.radians(p.longitude - user_lon)
            a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(user_lat)) * math.cos(math.radians(p.latitude)) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            p.distance = R * c
            return p.distance
        
        providers.sort(key=get_distance)
    else:
        for p in providers:
            p.distance = None

    # Get unique for dropdowns
    unique_services = [r[0] for r in db.session.query(Provider.service).distinct()]
    unique_locations = [r[0] for r in db.session.query(Provider.location).distinct()]

    return render_template("providers.html", providers=providers, services=unique_services, locations=unique_locations)

@bp.route("/requests", methods=['GET', 'POST'])
def request_service():
    form = RequestForm()
    unique_services = [r[0] for r in db.session.query(Provider.service).distinct().all()]
    form.service_needed.choices = [(s, s) for s in unique_services]
    
    if form.validate_on_submit():
        service_request = ServiceRequest(
            full_name=form.full_name.data,
            service_needed=form.service_needed.data,
            location=form.location.data,
            phone=form.phone_number.data
        )
        db.session.add(service_request)
        db.session.commit()
        notify_admin_new_request(service_request)
        flash("Your service request has been submitted successfully!", "success")
        return redirect(url_for('main.request_service'))
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")
    
    return render_template("request.html", form=form)

@bp.route("/provider/<int:id>")
def provider_detail(id):
    provider = Provider.query.get_or_404(id)
    return render_template("provider_detail.html", provider=provider)

@bp.route("/admin", defaults={'path': ''})
@bp.route("/admin/<path:path>")
def admin_legacy_redirect(path):
    return redirect(url_for('main.login'))

@bp.route("/portal-secure-access", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.admin_requests'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.admin_requests'))
    return render_template('admin/login.html', title='Sign In', form=form)

@bp.route("/portal-logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route("/portal-requests")
@login_required
def admin_requests():
    requests = ServiceRequest.query.order_by(ServiceRequest.timestamp.desc()).all()
    return render_template("admin_requests.html", requests=requests)

@bp.route("/portal-request/<int:id>/status", methods=['POST'])
@login_required
def update_request_status(id):
    req = ServiceRequest.query.get_or_404(id)
    status = request.form.get('status')
    if status in ['Pending', 'In Progress', 'Completed', 'Cancelled']:
        req.status = status
        db.session.commit()
        notify_customer_status_update(req)
        flash(f'Request #{id} status updated to {status}', 'success')
    return redirect(url_for('main.admin_requests'))

@bp.route("/portal-providers")
@login_required
def admin_providers():
    providers = Provider.query.all()
    return render_template("admin/providers.html", providers=providers)

@bp.route("/portal-provider/add", methods=['GET', 'POST'])
@login_required
def add_provider():
    form = ProviderForm()
    if form.validate_on_submit():
        provider = Provider(
            name=form.name.data,
            service=form.service.data,
            location=form.location.data,
            description=form.description.data,
            phone=form.phone.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            verified=form.verified.data
        )
        db.session.add(provider)
        db.session.commit()
        flash('Provider added successfully!', 'success')
        return redirect(url_for('main.admin_providers'))
    return render_template('admin/provider_form.html', title='Add Provider', form=form)

@bp.route("/portal-provider/<int:id>/edit", methods=['GET', 'POST'])
@login_required
def edit_provider(id):
    provider = Provider.query.get_or_404(id)
    form = ProviderForm(obj=provider)
    if form.validate_on_submit():
        provider.name = form.name.data
        provider.service = form.service.data
        provider.location = form.location.data
        provider.description = form.description.data
        provider.phone = form.phone.data
        provider.latitude = form.latitude.data
        provider.longitude = form.longitude.data
        provider.verified = form.verified.data
        db.session.commit()
        flash('Provider updated successfully!', 'success')
        return redirect(url_for('main.admin_providers'))
    return render_template('admin/provider_form.html', title='Edit Provider', form=form)

@bp.route("/portal-provider/<int:id>/delete", methods=['POST'])
@login_required
def delete_provider(id):
    provider = Provider.query.get_or_404(id)
    db.session.delete(provider)
    db.session.commit()
    flash('Provider deleted successfully!', 'success')
    return redirect(url_for('main.admin_providers'))

# Real-time Chat Routes
@bp.route("/chat/<int:request_id>")
def chat(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    messages = req.messages.order_by(Message.timestamp.asc()).all()
    is_admin = current_user.is_authenticated
    return render_template("chat.html", request=req, messages=messages, is_admin=is_admin)

# SocketIO Events
@socketio.on('join')
def on_join(data):
    room = f"request_{data['request_id']}"
    join_room(room)
    print(f"DEBUG: User joined room: {room}")

@socketio.on('message')
def handle_message(data):
    request_id = data['request_id']
    content = data['content']
    sender = 'admin' if current_user.is_authenticated else 'customer'
    print(f"DEBUG: Received message from {sender} for request {request_id}: {content}")
    
    # Save to database
    msg = Message(request_id=request_id, sender=sender, content=content)
    db.session.add(msg)
    db.session.commit()
    
    # Broadcast to room
    room = f"request_{request_id}"
    print(f"DEBUG: Broadcasting message to room: {room}")
    emit('new_message', {
        'content': content,
        'sender': sender,
        'timestamp': msg.timestamp.strftime('%H:%M')
    }, room=room)
