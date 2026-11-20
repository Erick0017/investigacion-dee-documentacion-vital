"""Independent integrity/technical-acceptance verifier, no physical oracle."""
import argparse
import base64
import csv
from email.parser import Parser
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import zipfile
import xml.etree.ElementTree as ET

KERNEL_SHA="fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
SCIENCE_SHA="f1f8b6b2f68517f003a21c2908adde49bf1194c7f5657b460563b91ad76f28f0"
WHEEL="dee_thinking-3.5.0-cp313-cp313-win_amd64.whl"
EVIDENCE="evidence/DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip"

def digest(b):return hashlib.sha256(b).hexdigest()

def safe(name):
    p=PurePosixPath(name)
    return bool(name) and "\\" not in name and not p.is_absolute() and ":" not in p.parts[0] and all(x not in (".","..") for x in p.parts) and p.as_posix()==name

def wheel_check(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None,"wheel CRC"
        names=z.namelist();assert len(names)==len(set(names))==len({x.casefold() for x in names});assert all(safe(x) for x in names)
        metadata=z.read("dee_thinking-3.5.0.dist-info/METADATA").decode()
        assert Parser().parsestr(metadata)['Version']=="3.5.0","wheel version"
        assert "Tag: cp313-cp313-win_amd64" in z.read("dee_thinking-3.5.0.dist-info/WHEEL").decode()
        native=[n for n in names if n.endswith(".pyd")];assert len(native)==1 and z.read(native[0])[:2]==b"MZ"
        assert digest(z.read(native[0]))!="333da509e19a9f31793df3a9d7fbc3c3809c1c8f69cd62a6b6423e3bb2a79a83","renamed old binary"
        stub=z.read("dee_thinking/_native.pyi").decode()
        for symbol in ("OrganizationalWorld","OrganizationRecipe","InputCodec","OutputDecoder","TraceSession","ResilienceObservation","EncounterObservation","BasalWorld","Runtime"):
            assert "class "+symbol in stub,symbol
        record="dee_thinking-3.5.0.dist-info/RECORD";covered=set()
        for name,encoded,size in csv.reader(io.StringIO(z.read(record).decode())):
            assert name not in covered;covered.add(name)
            if name==record:assert not encoded and not size
            else:
                b=z.read(name);assert encoded=="sha256="+base64.urlsafe_b64encode(hashlib.sha256(b).digest()).rstrip(b"=").decode();assert int(size)==len(b)
        assert covered==set(names)
        assert digest(z.read("dee_thinking/data/OBP_FRESH_VALIDATED_T32.deetsnap"))=="cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
        return {"sha256":digest(data),"native_sha256":digest(z.read(native[0])),"RECORD":True,"CRC":True}

def scientific_hashes(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None,"science CRC"
        counts={}
        for root in ("","02_REPERTORIO_NATIVO_Y_CIERRES/"):
            lines=z.read(root+"HASHES.sha256").decode("utf-8-sig").splitlines()
            for line in lines:
                if not line.strip():continue
                h,name=line.split("  ",1);assert digest(z.read(root+name))==h,(root,name)
            counts[root or "inherited_root"]=len(lines)
        parent=json.loads(z.read("02_REPERTORIO_NATIVO_Y_CIERRES/PARENT_MEMBERS.json"))
        for e in parent["members"]:
            b=z.read(e["name"]);assert len(b)==e["size"] and digest(b)==e["sha256"]
        return {"members":len(z.namelist()),"hash_entries_by_actual_root":counts,"parent_members_byte_exact":len(parent["members"])}

def verify(path,require_clean=True):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None,"delivery CRC"
        names=z.namelist();assert len(names)==len(set(names))==len({x.casefold() for x in names});assert all(safe(x) for x in names)
        hashes={}
        for line in z.read("HASHES.sha256").decode().splitlines():
            h,name=line.split("  ",1);assert name not in hashes;hashes[name]=h;assert digest(z.read(name))==h,name
        assert set(hashes)==set(names)-{"HASHES.sha256"},"hash scope"
        manifest=json.loads(z.read("MANIFEST.json"))
        for e in manifest["files"]:assert digest(z.read(e["path"]))==e["sha256"] and len(z.read(e["path"]))==e["size"]
        assert set(e["path"] for e in manifest["files"])==set(names)-{"MANIFEST.json","HASHES.sha256"}
        required={"README.md","PRODUCT_CONTRACT.json","source/CMakeLists.txt","source/pyproject.toml","source/setup.py","source/include/dee_thinking/organizational.hpp","source/src/organizational.cpp","source/src/organization_recipes.cpp","source/bindings/organizational_pybind.cpp","source/tests/organizational_tests.cpp","source/tests/python/test_organizational_api.py","source/examples/organizational_public.py","source/examples/external_3_5/main.cpp","source/tools/replay_primary_cases.py","source/tools/build_3_5.ps1","source/tools/package_3_5.py","source/tools/verify_delivery_3_5.py","install/lib/dee_thinking.lib","install/include/dee_thinking/organizational.hpp","install/lib/cmake/dee_thinking/dee_thinkingConfigVersion.cmake","docs/API_AND_SCOPE.md","docs/BUILD_AND_MIGRATION.md","validation/VALIDATION_REPORT.json",EVIDENCE,"wheel/"+WHEEL}
        assert required<=set(names),sorted(required-set(names))
        forbidden={"venv",".venv","__pycache__",".git",".pytest_cache","node_modules","build"}
        assert not any(forbidden.intersection(PurePosixPath(n).parts) or any(x.endswith(".egg-info") for x in PurePosixPath(n).parts) for n in names)
        assert not any(n.endswith(".docx") for n in names),"Word docs not requested"
        assert digest(z.read("source/src/kernel_v27.cpp"))==KERNEL_SHA
        assert digest(z.read(EVIDENCE))==SCIENCE_SHA
        assert 'VERSION 3.5.0' in z.read("source/CMakeLists.txt").decode()
        assert 'version = "3.5.0"' in z.read("source/pyproject.toml").decode()
        assert '"3.5.0"' in z.read("source/include/dee_thinking/version.hpp").decode()
        c=json.loads(z.read("PRODUCT_CONTRACT.json"));assert c["version"]=="3.5.0";assert {x["id"] for x in c["capabilities"]}=={f"F{i:02}" for i in range(1,10)}
        for cap in c["capabilities"]:
            assert all(cap.get(k) for k in ("API","implementation","experimental_sources","domain","tests","example","modalities","technical_status")),cap["id"]
        r=json.loads(z.read("validation/VALIDATION_REPORT.json"))
        assert r["status"] in (("RELEASE_VERIFIED",) if require_clean else ("CANDIDATE_VALIDATED","RELEASE_VERIFIED")) and not r["required_failed"] and not r["mandatory_tests_omitted"]
        assert r["cases"]["physical_reproduced_3_5"]==285 and r["cases"]["rereads_recalculated"]==3 and len(r["cases"]["source_not_recovered"])==1
        if require_clean:assert r["clean_extraction_verified"],"clean extraction unverified"
        assert r["kernel_preserved"] and r["cpp_external_consumer"] and r["clean_noneditable_install"] and r["cross_language_persistence"]
        junit=ET.fromstring(z.read("validation/FINAL_NATIVE_TESTS.xml"));testcases=list(junit.iter('testcase'))
        assert len(testcases)==20 and all(n.find('failure') is None and n.find('error') is None and n.find('skipped') is None for n in testcases)
        assert r['native_tests']['total']==20 and r['python_tests']['total']==39 and r['python_tests']['new']==14
        for item in r['command_documents']:
            data=z.read(item['path']);assert digest(data)==item['sha256']
            commands=json.loads(data);assert commands['summary']['failed']==0 and len(commands['commands'])==item['total']
            assert all(c['exit_code']==0 and c['status']=='passed' and not c['timed_out'] and not c['launch_error'] for c in commands['commands'])
        matrix=json.loads(z.read('validation/VALIDATION_CASE_MATRIX.json'));assert matrix['count']==len(matrix['records'])==289
        assert len({c['case'] for c in matrix['records']})==289
        for c in matrix['records']:
            record=json.loads(z.read(c['report_3_5']));assert record['status']=='PASS' and record['native_binary_sha256']==r['native_sha256']
        if require_clean:
            extracted=json.loads(z.read('validation/CLEAN_EXTRACTION_RESULT.json'))
            assert extracted['CRC_hash_manifest_verified'] and extracted['wheel_sha256']==r['wheel_sha256'] and extracted['native_sha256']==r['native_sha256']
            assert extracted['public_installed_walkthrough'] and extracted['external_cpp_consumer'] and extracted['cross_language_persistence']
        wc=wheel_check(z.read("wheel/"+WHEEL));assert wc["sha256"]==r["wheel_sha256"] and wc["native_sha256"]==r["native_sha256"]
        evidence=scientific_hashes(z.read(EVIDENCE))
        result={"CRC":True,"hashes":True,"manifest":True,"members":len(names),"wheel":wc,"scientific_evidence":evidence,"release_checks":True}
    with Path(path).open("rb") as f:result["zip_sha256"]=hashlib.file_digest(f,"sha256").hexdigest()
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--zip",type=Path,required=True);p.add_argument("--pre-extraction",action="store_true");a=p.parse_args()
    print(json.dumps(verify(a.zip,not a.pre_extraction),indent=2))
