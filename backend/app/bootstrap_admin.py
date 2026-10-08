"""Promote a previously registered account to recruiter from the server shell.
Usage: python -m app.bootstrap_admin candidate@example.com
"""
import sys
from .database import SessionLocal, User
if len(sys.argv)!=2:
    raise SystemExit('Usage: python -m app.bootstrap_admin <registered-email>')
db=SessionLocal()
try:
    user=db.query(User).filter_by(email=sys.argv[1].lower()).first()
    if not user: raise SystemExit('No account found for that email. Register it first.')
    user.role='admin'; db.commit(); print(f'Recruiter role assigned to {user.email}.')
finally: db.close()
