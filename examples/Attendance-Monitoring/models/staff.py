from .base import db, UserMixin

class Staff(db.Model, UserMixin):
    __tablename__ = 'staff'
    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(64), unique=True, index=True)
    password  = db.Column(db.String(64))
    fullname  = db.Column(db.String(64))
    is_admin  = db.Column(db.Boolean)

    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now()) # default value is current UTC time (may variy according to the db software used)
    created_by = db.Column(db.String(64), db.ForeignKey('staff.id'))

    admin = db.relationship("Staff", remote_side=[id])   # one-to-many
    members = db.relationship("Member", backref="staff") # one-to-many

