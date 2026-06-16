import urllib.request, time, os

base = "https://d8j0ntlcm91z4.cloudfront.net/user_3Ek1JHHvfr8D4qa9ou43dNuTnrN"
date = "20260616"
jobs = {
    "615f3b22-b981-40e9-9af1-b53a62a5004c": "shot_fast.mp4",
    "30f02c76-c4b3-4823-b288-f742fc4e9ced": "shot_end.mp4",
}

def find(job):
    for mm in range(38, 50):
        for ss in range(0, 60):
            ts = f"{date}_19{mm:02d}{ss:02d}"
            url = f"{base}/hf_{ts}_{job}.mp4"
            req = urllib.request.Request(url, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.status == 200:
                        return url
            except Exception:
                pass
    return None

done = {}
for attempt in range(60):
    for job, out in jobs.items():
        if out in done:
            continue
        if os.path.exists(out) and os.path.getsize(out) > 100000:
            done[out] = "cached"
            continue
        url = find(job)
        if url:
            urllib.request.urlretrieve(url, out)
            done[out] = url
            print("DOWNLOADED", out, url, flush=True)
    if len(done) == len(jobs):
        print("ALL_DONE", flush=True)
        break
    time.sleep(12)
else:
    print("TIMEOUT", {k: ("ok" if v else "miss") for k, v in done.items()}, flush=True)
