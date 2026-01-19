import eventlet
eventlet.monkey_patch()

from app import create_app, db, socketio
from app.models import Provider, User # Added User import

app = create_app()

def seed_data():
    if not Provider.query.first():
        providers = [
            Provider(name="Kariuki Electricals", service="Electrical", location="Embu Town", description="Domestic and industrial wiring specialist.", phone="+254 711 000 111", latitude=-0.5312, longitude=37.4513, verified=True),
            Provider(name="Mama Jane Cleaning", service="Plumbing", location="Blue Valley", description="Reliable plumbing and drainage solutions.", phone="+254 722 000 222", latitude=-0.5401, longitude=37.4621, verified=True),
            Provider(name="Digital Fixers Ltd", service="Fiber & Networking", location="Ganjas", description="High-speed internet installation and networking.", phone="+254 733 000 333", latitude=-0.5285, longitude=37.4450, verified=True),
            Provider(name="Wanjiku General Works", service="General Fundi", location="Majimbo", description="All-around repair and maintenance for homes.", phone="+254 744 000 444", latitude=-0.5350, longitude=37.4550, verified=True),
        ]
        db.session.bulk_save_objects(providers)
        db.session.commit()
        print("Database seeded with local providers!")

    # Create default admin if doesn't exist
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin')
        admin.set_password('password') # Assuming User model has a set_password method
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin/password")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    socketio.run(app, debug=True)
