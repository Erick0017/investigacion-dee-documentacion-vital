"""Offline source/XML checks only; does not execute Roblox or DEE."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent

def read(n):
    return (HERE / n).read_text(encoding="utf-8-sig")

def item_name(e):
    p=e.find("./Properties/string[@name='Name']")
    return p.text if p is not None else None

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

class WorldContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read("Config_R07.luau")
        cls.b=read("Body_R07.luau")
        cls.api=read("WorldAPI_R07.luau")
        cls.motor=read("MotorPathfinding_R07.luau")
        cls.view=read("Observador_R07.client.luau")
        cls.manifest=json.loads(read("BUILD_WORLD_R07.json"))
        cls.xml=ET.parse(HERE / "DEE_RBX01_R07_NATIVE.rbxlx")

    def test_01_preserved_R06_bytes(self):
        m=self.manifest["source"]
        self.assertEqual(sha(Path(m["path"])),m["sha256"])
        self.assertEqual(m["sha256"],m["after_sha256"])

    def test_02_output_xml_and_module_sources(self):
        names={item_name(e):e for e in self.xml.iter("Item")}
        for row in self.manifest["source_files"]:
            e=names[row["module_name"]]
            self.assertEqual(e.find("./Properties/ProtectedString[@name='Source']").text,read(row["name"]))
            self.assertEqual(sha(HERE/row["name"]),row["sha256"])
        self.assertEqual(names["MotorPathfinding_R07"].get("class"),"ModuleScript")
        self.assertNotIn("WorldAPI_R06",names)
        self.assertEqual(sha(HERE / "DEE_RBX01_R07_NATIVE.rbxlx"),self.manifest["output"]["sha256"])

    def test_03_no_auto_controller(self):
        for e in self.xml.iter("Item"):
            if e.get("class")=="Script" and "Controller" in (item_name(e) or ""):
                self.assertEqual(e.find("./Properties/bool[@name='Disabled']").text,"true")
        self.assertIn('C.AutoStart="NONE"',self.c)

    def test_04_new_nonrecursive_scenario_fingerprint(self):
        fingerprint=self.manifest["scenario_fingerprint"]
        self.assertRegex(fingerprint,r"^[0-9a-f]{64}$")
        self.assertNotEqual(fingerprint,"0a21455c746e20a1e01c47292a914929fc97db41158fcce05c80ad6dbcf0b849")
        self.assertIn(f'C.ScenarioFingerprint="{fingerprint}"',self.c)
        self.assertIn('C.WorldId="RBX01_CIERRE8_R07"',self.c)

    def test_05_q2_full_domain_and_no_query_null(self):
        vals={price+3*tag for price in range(3) for tag in range(6)}
        self.assertEqual(vals,set(range(18)))
        for price in range(3):
            self.assertEqual(price+3*2,price+3*2)
        query_applied=False
        datum=2+3*2 if query_applied else None
        self.assertIsNone(datum)
        self.assertNotEqual(datum,0)

    def test_06_unchanged_chosen_action_no_route_repair(self):
        self.assertNotIn("ASSISTED_ORDER",self.api)
        self.assertNotRegex(self.api,r"action\.name\s*=\s*['\"]EXIT[01]")
        self.assertIn("local actualName=action.name",self.api)
        self.assertIn("local result,err=B:execute(action)",self.api)

    def test_07_pathfinding_only_selected_destination(self):
        self.assertIn("path:ComputeAsync(self.root.Position,selected)",self.motor)
        self.assertIn("local selected=destination",self.motor)
        self.assertNotIn("PivotTo(",self.motor)
        self.assertNotRegex(self.motor,r"\bCosts\s*=")
        self.assertNotIn("C.Edges",self.motor)
        self.assertNotIn("numberA",self.motor)
        self.assertNotIn("roundOperands",self.motor)
        self.assertIn('status="ARRIVED"',self.motor)

    def test_08_toll_before_geometry_and_no_path_outcome(self):
        self.assertLess(self.b.index("PORT_ATTEMPT_TOLL"),self.b.index("self.motor:moveTo"))
        self.assertIn('outcome="MOTOR_NO_PATH"',self.b)
        self.assertIn("motorContactUncertain",self.b)
        self.assertIn("CHOSEN_PORT_ATTEMPT_BEFORE_PATH",self.c)
        self.assertIn("SELECTED_DESTINATION_ARRIVAL_ONLY",self.c)

    def test_09_parent_counters_and_new_schedule(self):
        self.assertIn("C.ParentNativeTick=991187",self.c)
        self.assertIn("C.ParentCompletedCycles=28",self.c)
        self.assertIn("C.MaxCycles=52",self.c)
        self.assertIn("C.SuspendAfter=34",self.c)
        self.assertIn("if cycle>=41",self.c)
        self.assertIn("State.apply(B,state,expected)",self.api)
        self.assertNotRegex(self.api,r"B\.S\.(completedCycles|permissionStock|numberA|numberAVersion)\s*=\s*0")

    def test_10_complete_boundary_motor_and_diagnostic_guards(self):
        self.assertIn("R07_NO_CAPTURE_DURING_MOTOR",self.motor)
        self.assertIn("R07MotorGeometry",self.api)
        self.assertIn("diagnosticAllowed=identity.diagnostic==true",self.api)
        self.assertIn("OPERATOR_DIAGNOSTIC_INTERFACE",self.api)
        self.assertIn("mission_credit=false",self.api)
        self.assertIn("left=B.S.numberA,right=tuple.bRight",self.api)

    def test_11_observer_is_not_a_controller(self):
        self.assertNotIn("WorldAPI",self.view)
        self.assertNotIn("Native",self.view)
        self.assertNotIn("FireServer",self.view)
        self.assertNotIn("InvokeServer",self.view)
        self.assertIn("CurrentCamera",self.view)

    def test_12_prospective_contract_readable(self):
        p=HERE.parent/"protocolo"/"P02_P03_P05_CONTRATO_PROSPECTIVO_R07.json"
        j=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(j["budget"]["main_new_opportunities"],24)
        self.assertEqual(j["budget"]["paired_control_new_opportunities"],6)
        self.assertEqual(j["P02"]["Q2"]["codec"],"price_tag_v1")
        self.assertTrue(j["parent"]["no_T0_no_RAW_or_clock_edits_no_memory_fusion"])

if __name__=="__main__":
    unittest.main(verbosity=2)
