from datetime import datetime, timedelta, timezone
from .main import Base,engine,SessionLocal,User,Ticket,SlaRule,Role,Status,pwd,reevaluate
def main():
 Base.metadata.create_all(engine);s=SessionLocal()
 for c,h in [('Electrical',24),('Plumbing',24),('IT/Network',12),('Hostel',48)]:
  if not s.query(SlaRule).filter_by(category=c).first():s.add(SlaRule(category=c,hours=h,risk_threshold=.7,grace_hours=6))
 users=[('Aishwarya Student','student@campus.test','STUDENT',None),('Elena Electrical','electrical@campus.test','STAFF','Electrical'),('Pranav Plumbing','plumbing@campus.test','STAFF','Plumbing'),('Ishan IT','it@campus.test','STAFF','IT/Network'),('Hema Hostel','hostel@campus.test','STAFF','Hostel'),('Campus Admin','admin@campus.test','ADMIN',None)]
 for n,e,r,d in users:
  if not s.query(User).filter_by(email=e).first():s.add(User(name=n,email=e,password_hash=pwd.hash('CampusDemo2026!'),role=r,department=d))
 s.commit();student=s.query(User).filter_by(email='student@campus.test').one()
 if not s.query(Ticket).first():
  now=datetime.now(timezone.utc); samples=[('Water is leaking from tap in hostel block B','Hostel B','Plumbing','HIGH','ESCALATED',30),('Wifi is not connecting in lab 3','Lab 3','IT/Network','MEDIUM','IN_PROGRESS',5),('Corridor lights are damaged at library','Library','Electrical','LOW','RESOLVED',40),('Broken bed frame in room 312','Room 312','Hostel','MEDIUM','OPEN',10)]
  for desc,loc,cat,pri,status,age in samples:s.add(Ticket(description=desc,location=loc,category=cat,priority=pri,department=cat,status=status,student_id=student.id,created_at=now-timedelta(hours=age),updated_at=now-timedelta(hours=1),deadline=now+timedelta(hours=12),risk_score=.8 if status in ['OPEN','ESCALATED'] else .2,risk_level='HIGH' if status in ['OPEN','ESCALATED'] else 'LOW',escalated_at=now if status=='ESCALATED' else None))
  s.commit()
 reevaluate(s);s.close();print('Seed data ready.')
if __name__=='__main__':main()
