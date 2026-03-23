from harvester.scheduler import Scheduler
from harvester.harvester import Harvester

def job_runner():
    email = "your_email@example.com"
    harvester = Harvester(email=email)
    docket_path = "config/api_config.yaml"
    harvester.run_docket(docket_path)

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.add_job(job_runner, frequency="weekly")
    scheduler.run()
