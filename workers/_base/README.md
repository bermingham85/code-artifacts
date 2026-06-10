# BASE WORKER

Every Python worker in the Bermech system inherits from `base_worker.py`.

## What it provides (so individual workers never have to)

- Reads its own MANIFEST.json on startup
- Validates all incoming tickets against the manifest schema
- Sends structured NEEDS_INFO response if required fields are missing
- Sends structured FAILED response on any processing error
- Sends structured COMPLETE response on success
- Writes output to the worker's own outbox
- Moves tickets from inbox → working → completed
- Sets up logging to the worker's own log folder

## To create a new worker

1. Get a ref code from DC Agent first
2. Create `workers/[WORKER_ID]/` folder
3. Copy `templates/MANIFEST-TEMPLATE.json` → `workers/[WORKER_ID]/MANIFEST.json`
4. Fill in the manifest
5. Create `workers/[WORKER_ID]/[worker_id].py`:

```python
from workers._base.base_worker import BaseWorker

class MyWorker(BaseWorker):
    def execute_job(self, ticket: dict, payload: dict) -> dict:
        # Your logic here
        # Return a result dict
        # Raise any exception on failure — base class handles it
        return {"result": "done"}

if __name__ == "__main__":
    MyWorker().run()
```

That's it. Everything else is handled.
