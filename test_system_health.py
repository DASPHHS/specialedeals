import datetime as dt
import unittest
from system_health import assess
class HealthTests(unittest.TestCase):
 def test_zero_personal_matches_are_not_marked_working(self):
  import tempfile, json
  from pathlib import Path
  from system_health import build
  now=dt.datetime.now(dt.timezone.utc)
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   (root/'live-deals.json').write_text(json.dumps({
    'updatedAt':now.isoformat(),'coverage':{'personalMatches':0},
    'sources':[{'status':'ok','items':30},{'status':'empty','items':0}]}))
   actual=build(root,now)['modules'][0]
   self.assertEqual(actual['state'],'gedeeltelijk')
   self.assertEqual(actual['personalMatches'],0)

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
