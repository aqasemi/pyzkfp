from .base import db



class Member(db.Model):
    __tablename__ = 'member'

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(10), index=True, unique=True)
    fullname     = db.Column(db.String(50), nullable=False)
    created_by   = db.Column(db.String(64), db.ForeignKey('staff.id'), default='admin')
    created_at   = db.Column(db.DateTime(timezone=True), default=db.func.now()) # defautls to current UTC time (may vary according to db sotfware used)
    fingerprint  = db.Column(db.LargeBinary)