from app import create_app

app = create_app()
celery = app.celery_app


def celery_watchgod():
    from watchgod import run_process
    import subprocess

    def run_worker():
        subprocess.call(
            subprocess.call(
                [
                    "celery",
                    "-A",
                    "app.main.celery",
                    "worker",
                    "-c",
                    "1",
                    "--loglevel=info",
                ]
            )
        )

    run_process("./app", run_worker)


if __name__ == "__main__":
    celery_watchgod()
