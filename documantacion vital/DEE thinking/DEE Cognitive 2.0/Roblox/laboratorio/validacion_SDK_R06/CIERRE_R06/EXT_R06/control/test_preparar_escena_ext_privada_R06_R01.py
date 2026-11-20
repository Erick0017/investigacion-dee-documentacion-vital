"""Synthetic XML/credential fixture only. No real private scene, Native or HTTP."""
from pathlib import Path
import hashlib,json,re,sys,tempfile,unittest,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import preparar_escena_ext_privada_R06_R01 as h

def text(parent,name,value,klass='StringValue',referent=None):
    item=E.SubElement(parent,'Item',{'class':klass,**({'referent':referent} if referent else {})})
    p=E.SubElement(item,'Properties');E.SubElement(p,'string',{'name':'Name'}).text=name
    E.SubElement(p,'string',{'name':'Value'}).text=value
    return item

class SceneFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.i='SDK_DEMO_0123456789ABCDEF';self.source=self.root/'SYNTHETIC_CORE.rbxlx'
        root=E.Element('roblox',{'version':'4'})
        sss=h.service(root,'ServerScriptService','CORE_SSS')
        boot=E.SubElement(sss,'Item',{'class':'Script','referent':'CORE_START'})
        E.SubElement(h.props(boot),'string',{'name':'Name'}).text='SDK_Arranque'
        E.SubElement(h.props(boot),'ProtectedString',{'name':'Source'}).text='error("SYNTHETIC_NOT_EXECUTED")'
        module=E.SubElement(sss,'Item',{'class':'ModuleScript','referent':'CORE_MAIN'})
        E.SubElement(h.props(module),'string',{'name':'Name'}).text='Main_R06'
        E.SubElement(h.props(module),'ProtectedString',{'name':'Source'}).text='return {SYNTHETIC_ONLY=true}'
        ss=h.service(root,'ServerStorage','CORE_SS')
        folder=E.SubElement(ss,'Item',{'class':'Folder','referent':'CORE_PRIVATE'})
        E.SubElement(h.props(folder),'string',{'name':'Name'}).text='DEE_SDK_PrivateConnection_R06'
        text(folder,'InstanceId',self.i);text(folder,'Token','SYNTHETIC_NOT_A_REAL_SECRET_'+'x'*40)
        E.ElementTree(root).write(self.source,encoding='utf8',xml_declaration=True)
        self.connection=self.root/'SYNTHETIC_CAP.rbxmx'
        root=E.Element('roblox',{'version':'4'});folder=E.SubElement(root,'Item',{'class':'Folder','referent':'CORE_PRIVATE'})
        E.SubElement(h.props(folder),'string',{'name':'Name'}).text=h.FOLDER
        for n,v in [('BaseUrl','http://127.0.0.1:8899'),('InstanceId',self.i),('Token','SYNTHETIC_NOT_A_REAL_SECRET_'+'y'*40)]:
            text(folder,n,v,referent='SYNTHETIC_'+n)
        E.ElementTree(root).write(self.connection,encoding='utf8',xml_declaration=True)
        self.model=HERE.parent/'KIT_EXTENSION/conector/DEE_SDK_CAPACIDADES_EXT_R06.rbxmx'
        self.target=self.root/'SYNTHETIC_EXT_NEW.rbxlx'
        self.before=(h.sha(self.source),h.sha(self.connection),h.sha(self.model))
    def tearDown(self):self.tmp.cleanup()
    def prepare(self,instance=None):
        return h.prepare(self.source,self.connection,self.model,self.target,instance or self.i,source_sha256=self.before[0])
    def test_enabled_ext_disabled_core_literal_sources_and_scope(self):
        result=self.prepare();self.assertEqual(result['status'],'PREPARED_NOT_EXECUTED')
        root=E.parse(self.target).getroot()
        core=[x for x in root.iter('Item') if h.name(x)=='SDK_Arranque'][0]
        flags={x.get('name'):x.text for x in h.props(core) if x.tag=='bool'}
        self.assertEqual(flags['Disabled'],'true');self.assertEqual(flags['Enabled'],'false')
        self.assertEqual(h.named_source(core).text,'error("SYNTHETIC_NOT_EXECUTED")')
        config=[x for x in root.iter('Item') if h.name(x)=='Config_EXT_R06'][0]
        cfg=json.loads(re.search(r'\[=\[(.*?)\]=\]',h.named_source(config).text,re.S).group(1))
        self.assertTrue(cfg['Enabled']);self.assertTrue(cfg['NoAutomaticMaterial'])
        self.assertTrue(any(h.name(x)=='EXT_R06_ALCANCE_ASISTIDO' for x in root.iter('Item')))
        self.assertFalse(result['NativeExecutedByHelper']);self.assertFalse(result['HTTPRequestedByHelper'])
        self.assertFalse(result['currentWorldPairClaimed'])
        refs=[x.get('referent') for x in root.iter('Item') if x.get('referent')]
        self.assertEqual(len(refs),len(set(refs)))
        self.assertEqual((h.sha(self.source),h.sha(self.connection),h.sha(self.model)),self.before)
    def test_never_overwrite(self):
        self.target.write_text('SYNTHETIC_KEEP')
        with self.assertRaises(FileExistsError):self.prepare()
        self.assertEqual(self.target.read_text(),'SYNTHETIC_KEEP')
    def test_wrong_instance_no_scene(self):
        with self.assertRaises(ValueError):self.prepare('SDK_DEMO_FEDCBA9876543210')
        self.assertFalse(self.target.exists())
    def test_wrong_source_hash_no_scene(self):
        with self.assertRaises(ValueError):
            h.prepare(self.source,self.connection,self.model,self.target,self.i,source_sha256='0'*64)
        self.assertFalse(self.target.exists())
if __name__=='__main__':unittest.main(verbosity=2)
