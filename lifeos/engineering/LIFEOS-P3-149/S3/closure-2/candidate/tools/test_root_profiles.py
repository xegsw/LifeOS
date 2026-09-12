"""Dynamic guards use only the selected owned root. Alternate selection is configuration only."""
import unittest,subprocess,os,json,sys,time
from pathlib import Path
from task_root import ROOT,PROFILE,verify,verify_binary
BIN=ROOT/'initial-build-cache/debug/lifeos-p3-147'
class RootProfiles(unittest.TestCase):
 def test_compiled_profile_is_explicit(self):
  self.assertIn(PROFILE,('engineering','independent-review'));verify();self.assertTrue(verify_binary(BIN))
 def test_bad_runtime_environment_rejected_before_database(self):
  other='independent-review' if PROFILE=='engineering' else 'engineering'
  cases=[('LIFEOS_P3_147_BUILD_PROFILE',other),('LIFEOS_P3_147_BUILD_PROFILE','unknown'),('LIFEOS_RUNTIME_ROOT','/arbitrary/root'),('LIFEOS_P3_147_ROOT','/arbitrary/root'),('LIFEOS_P3_147_ROOT_PROFILE','independent-review'),('LIFEOS_P3_145_ROOT_PROFILE','synthetic'),('LIFEOS_P3_147_PROFILE','real')]
  for n,(key,value) in enumerate(cases):
   with self.subTest(key=key,value=value):
    fixture='root-deny-'+str(time.time_ns())+'-'+str(n)
    result=subprocess.run([str(BIN),'--repository-stdio',fixture],input=json.dumps({'ipc':'get_source_status','request':{'version':1,'payload':{}}})+'\n',env={**os.environ,key:value},capture_output=True,text=True,timeout=10)
    self.assertEqual(json.loads(result.stdout)['error']['code'],'profile_rejected')
    self.assertFalse((ROOT/(fixture+'.sqlite')).exists())
 def test_review_configuration_only_no_root_access(self):
  tool=Path(__file__).with_name('task_root.py')
  result=subprocess.run([sys.executable,'-B',str(tool),'describe'],env={**os.environ,'LIFEOS_P3_147_BUILD_PROFILE':'independent-review'},capture_output=True,text=True,check=True)
  spec=json.loads(result.stdout)
  self.assertEqual(spec['profile'],'independent-review');self.assertEqual(spec['root'],json.loads((Path(__file__).parents[1]/'root_profiles.json').read_text())['independent-review']['root']);self.assertEqual(spec['marker']['root'],spec['root'])
 def test_tool_unknown_profile_and_arbitrary_root(self):
  tool=Path(__file__).with_name('task_root.py')
  for patch in [{'LIFEOS_P3_147_BUILD_PROFILE':'bogus'},{'LIFEOS_RUNTIME_ROOT':'/arbitrary/root'}]:
   result=subprocess.run([sys.executable,'-B',str(tool),'describe'],env={**os.environ,**patch},capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
if __name__=='__main__':unittest.main(verbosity=2)
