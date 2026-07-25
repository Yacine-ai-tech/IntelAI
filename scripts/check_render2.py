import os, time, json
import urllib.request

deploy_id = "dep-d9igdi4vikkc7397v8ag"
for _ in range(15):
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/srv-d9ct2ur7uimc73f1606g/deploys/{deploy_id}",
        headers={"Authorization": f"Bearer {os.environ['RENDER_API_KEY']}"}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        status = data['status']
        print("Status:", status)
        if status in ("live", "update_failed", "canceled"):
            break
    time.sleep(5)
