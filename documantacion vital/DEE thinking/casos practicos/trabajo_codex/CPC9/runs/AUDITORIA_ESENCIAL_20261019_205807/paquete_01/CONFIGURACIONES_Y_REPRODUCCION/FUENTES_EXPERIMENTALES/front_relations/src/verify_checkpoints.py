"""Data-only checkpoint byte/hash and gzip CRC check; no engine imported."""
import argparse,gzip,hashlib,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--front",type=Path,required=True);a=p.parse_args();rows=[]
    measurements=set((a.front/"resultados").glob("*/MEASUREMENTS.json"))|set((a.front/"resultados").glob("*/MEDICIONES.json"))
    for measurement in sorted(measurements):
        m=json.loads(measurement.read_text(encoding="utf8"))
        for item in m.get("snapshots",[]):
            name=item.get("path",item.get("name"))
            if not name:continue
            path=measurement.parent/Path(name).name
            record={"primary":str(measurement.relative_to(a.front)),"checkpoint":str(path.relative_to(a.front)),"exists":path.is_file(),"recorded_sha256":item.get("sha256"),"recorded_bytes":item.get("bytes"),"tick":item.get("tick")}
            if path.is_file():
                data=path.read_bytes();record.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
                record["hash_match"]=record["sha256"]==record["recorded_sha256"]
                record["size_match"]=record["recorded_bytes"]in(None,len(data))
                if data[:2]==b"\x1f\x8b":
                    try:expanded=gzip.decompress(data);record.update(gzip_crc_verified=True,expanded_bytes=len(expanded),expanded_sha256=hashlib.sha256(expanded).hexdigest())
                    except(OSError,EOFError)as error:record.update(gzip_crc_verified=False,error=repr(error))
                else:record.update(gzip_crc_verified=None,container_note="Not a gzip signature; hash check only")
            rows.append(record)
    report={"schema":"CPC9.front_relations.checkpoints.v1","engine_imported":False,"semantic_validation":False,
      "scope":"Recorded file identity and gzip lossless decompression CRC only. Separate native restore/continuation cases validate supported sessions.","checkpoints":rows,
      "counts":{"recorded":len(rows),"missing":sum(not r["exists"]for r in rows),"hash_mismatch":sum(r.get("hash_match")is False for r in rows),"gzip_crc_failures":sum(r.get("gzip_crc_verified")is False for r in rows)}}
    target=a.front/"revision/CHECKPOINTS_INTEGRIDAD.json";target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8");print(json.dumps(report["counts"]))
if __name__=="__main__":main()
