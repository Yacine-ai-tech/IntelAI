import os, time, json
import urllib.request

for _ in range(30):
    req = urllib.request.Request(
        "https://api.render.com/v1/services/srv-d9ct2ur7uimc73f1606g/deploys?limit=1",
        headers={"Authorization": f"Bearer {os.environ['RENDER_API_KEY']}"}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        status = data[0]['deploy']['status']
        print("Status:", status)
        if status == "live":
            break
    time.sleep(10)
