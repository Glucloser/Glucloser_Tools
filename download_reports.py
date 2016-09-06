import io
import os
import tempfile
import Carelink

session = Carelink.startSession()

CARELINK_USER = os.environ['carelink_user']
CARELINK_PW = os.environ['carelink_pw']

if not Carelink.login(session, CARELINK_USER, CARELINK_PW):
    sys.stderr.write("Unable to log in")
    exit(1)

reportsURL = Carelink.request_all_reports(session)
reportBytes = Carelink.download(session, reportsURL)

reportFile = tempfile.NamedTemporaryFile(delete=False)
print(reportFile.name)
reportFile.write(reportBytes)
reportFile.close()