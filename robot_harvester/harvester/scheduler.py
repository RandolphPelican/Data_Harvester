import schedule
import time
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, func, frequency="daily"):
        """
        frequency: 'daily', 'weekly', 'hourly', 'monthly'
        """
        if frequency == "daily":
            job = schedule.every().day.at("00:00").do(func)
        elif frequency == "weekly":
            job = schedule.every().monday.at("00:00").do(func)
        elif frequency == "hourly":
            job = schedule.every().hour.do(func)
        elif frequency == "monthly":
            job = schedule.every(4).weeks.do(func)
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
        self.jobs.append(job)

    def run(self):
        print(f"[{datetime.now()}] Scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(10)
