import datetime as dt
import unittest
from system_health import assess
class HealthTests(unittest.TestCase):
 def test_fresh_file_with_all_sources_failed_is_not_success(self):
  now=dt.datetime.now(dt.timezone.utc)
  row=assess('test',{'at':now.isoformat(),'rows':[{'status':'error'}]},'at','rows',{'ok'},8,now)
  self.assertEqual(row['state'],'mislukt')
 def test_old_success_is_stale(self):
  now=dt.datetime.now(dt.timezone.utc)
  row=assess('test',{'at':(now-dt.timedelta(hours=9)).isoformat(),'rows':[{'status':'ok'}]},'at','rows',{'ok'},8,now)
  self.assertEqual(row['state'],'verouderd')
 def test_partial_success_is_visible(self):
  now=dt.datetime.now(dt.timezone.utc)
  row=assess('test',{'at':now.isoformat(),'rows':[{'status':'ok'},{'status':'error'}]},'at','rows',{'ok'},8,now)
  self.assertEqual(row['state'],'gedeeltelijk')
