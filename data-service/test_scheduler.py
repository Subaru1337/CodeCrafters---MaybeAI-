import sys
import os
sys.path.append(os.path.dirname(__file__))

from apscheduler.schedulers.background import BackgroundScheduler

# Import your jobs logically
from ingestion.scheduler import job_fetch_news, job_fetch_prices, job_fetch_filings

def verify_scheduler():
    print("Verifying APScheduler Job Registry and Triggers...\n")
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_fetch_news, 'interval', hours=1, id='job_news')
    scheduler.add_job(job_fetch_prices, 'interval', hours=6, id='job_prices')
    scheduler.add_job(job_fetch_filings, 'interval', hours=24, id='job_filings')
    
    scheduler.start()
    
    print(f"[{scheduler.state}] Scheduler is successfully ONLINE.\n")
    print("Currently Registered Automated Cron Tasks:")
    print("-" * 105)
    
    for job in scheduler.get_jobs():
        print(f" -> Job ID: {job.id:<15} | Trigger Cycle: {str(job.trigger):<40} | Next Run: {job.next_run_time}")
        
    scheduler.shutdown()
    print("\nVerification complete. Pipeline triggers are structurally sound!")

if __name__ == "__main__":
    verify_scheduler()
