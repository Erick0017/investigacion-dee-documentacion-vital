"""Short availability check only; never launches Word/LibreOffice or authors DOCX."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manual',type=Path,required=True)
    parser.add_argument('--salida',type=Path,required=True)
    parser.add_argument('--bundled-soffice',type=Path)
    args=parser.parse_args();p7=Path(__file__).resolve().parents[1]
    manual=args.manual.resolve(strict=True);out=args.salida.resolve()
    if not manual.is_relative_to(p7/'documentos') or not out.is_relative_to(p7/'documentos'):
        raise ValueError('Only current PI07 documentary staging/proof locations')
    if out.exists():raise FileExistsError(out)
    prior=p7.parent/'PROGRESION_INTEGRADA_06/documentos/DIAGNOSTICO_RENDER_PI06_R01.json'
    found=shutil.which('soffice.exe')
    bundled=None if args.bundled_soffice is None else {'path':str(args.bundled_soffice),'exists':args.bundled_soffice.is_file()}
    available=bool(found or bundled and bundled['exists'])
    result={'schema':'DEE.PI07.short_renderer_availability.v1',
            'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'status':'NOT_VALIDATED','validation_visual':'NOT_VALIDATED',
            'manual_sha256':hashlib.sha256(manual.read_bytes()).hexdigest(),
            'PATH_soffice':found,'bundled_candidate':bundled,'renderer_available':available,
            'renderer_launched':False,'Word_GUI_launched':False,
            'prior_actual_failure':{'path':str(prior),'sha256':hashlib.sha256(prior.read_bytes()).hexdigest()},
            'limitations':('Availability only. A renderer exists and still requires an actual render/visual review; no visual approval is inferred.'if available else
              'Short availability check found no executable renderer. The previous PI06 actual soffice failure is referenced; it was not repeated. No PDF/pages were generated. Pagination, clipping, tables, header/footer layout and visual index remain NOT_VALIDATED. Structural DOCX validation is separate.'),
            'rendered_pdf':None,'reviewed_images':[],'Native_ticks':0,'authoring_performed':False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(out),'renderer_available':available,'status':'NOT_VALIDATED'},ensure_ascii=False))


if __name__=='__main__':main()
