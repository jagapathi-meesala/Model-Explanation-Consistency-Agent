import json, tempfile, unittest
from pathlib import Path
from core.engine import validate_records

class ModelExplanationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
  self.p=self.root/"pred.csv"; self.e=self.root/"exp.csv"; self.c=self.root/"config.json"
  self.c.write_text(json.dumps({"id_column":"id","prediction_label_column":"label","explanation_label_column":"label","feature_names_column":"features","attributions_column":"attrs"}))
 def tearDown(self): self.tmp.cleanup()
 def runcheck(self, p, e):
  self.p.write_text(p); self.e.write_text(e)
  return validate_records(self.p,self.e,self.c)
 def test_missing_column(self):
  r=self.runcheck("id\n1\n","id,label,features,attrs\n1,a,\"[x]\",\"[0.2]\"\n")
  self.assertIn("MEC001",[x["rule_id"] for x in r["findings"]])
 def test_missing_counterpart(self):
  r=self.runcheck("id,label\n1,a\n","id,label,features,attrs\n2,a,\"[x]\",\"[0.2]\"\n")
  ids=[x["rule_id"] for x in r["findings"]]
  self.assertIn("MEC005",ids); self.assertIn("MEC006",ids)
 def test_label_disagreement(self):
  r=self.runcheck("id,label\n1,a\n","id,label,features,attrs\n1,b,\"[x]\",\"[0.2]\"\n")
  self.assertIn("MEC007",[x["rule_id"] for x in r["findings"]])
 def test_attribution_length(self):
  r=self.runcheck("id,label\n1,a\n","id,label,features,attrs\n1,a,x;y,0.2\n")
  self.assertIn("MEC010",[x["rule_id"] for x in r["findings"]])
 def test_duplicate_id(self):
  r=self.runcheck("id,label\n1,a\n1,b\n","id,label,features,attrs\n1,a,\"[x]\",\"[0.2]\"\n")
  self.assertIn("MEC003",[x["rule_id"] for x in r["findings"]])

if __name__=="__main__": unittest.main()
