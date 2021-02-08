import subprocess
import requests

url = 'https://us-central1-gcp-book-1.cloudfunctions.net/function-2'


def token():
    proc = subprocess.Popen(
        ["gcloud",  "auth", "print-identity-token"],
        stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode('utf-8').strip('\n')


resp = requests.post(
        url,
        json={"message": "hello from a programming language"},
        headers={"Authorization": f"Bearer {token()}"})

print(resp.text)
