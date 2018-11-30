# Django Management Scheduler

__Note__: This package is in pre-alpha stage, and is not ready for production use!

A management command for Django quickly convert management commands into scheduled tasks. Powered by [APScheduler](https://apscheduler.readthedocs.io/en/latest/).

## Configuration

Configuration is done in Django's `settings.py`:

```python
MANAGEMENT_SCHEDULER = {
    "invalidate_stale_sessions": ("interval", {"minutes": 40}),
    "delete_old_jobs": ("cron", {"hour": 7}),
}
```

The key is the name of the management command, and the value is a tuple, describing the trigger, and the arguments to the trigger. For more documentation on triggers, and other valid arguments, check out the [APScheduler documentation](https://apscheduler.readthedocs.io/en/latest/userguide.html#choosing-the-right-scheduler-job-store-s-executor-s-and-trigger-s).

The scheduler can then be started using `manage.py scheduler`.

## Code of conduct

For guidelines regarding the code of conduct when contributing to this repository please review [https://www.dabapps.com/open-source/code-of-conduct/](https://www.dabapps.com/open-source/code-of-conduct/)
