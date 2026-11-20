"""Public 3.5 integration tests. Expected values evaluate, never drive DEE."""
import gc
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import dee_thinking as d

def physical(w):
    r=w.runtime if hasattr(w,"runtime") else w
    return r.current_tick,r.raw_copy(),r.clock_copy()

def learned(**kw):
    w=d.create_organization("mobile_pair",**kw)
    for j,e in enumerate((7,11)):
        w.submit(f"l{j}.cue",5,0);w.submit(f"l{j}.teacher",e,0)
    w.run_until(6)
    return w

def probe_body(w,payload=7):
    f=w.fork();f.probe("body.common_query",payload,f.runtime.current_tick);f.advance(3)
    return f

class OrganizationalApiTests(unittest.TestCase):
    def test_f01_f06_named_io_history_and_sequential_resume(self):
        a=learned();b=d.create_organization("mobile_pair")
        for j,e in enumerate((11,7)):
            b.submit(f"l{j}.cue",5,0);b.submit(f"l{j}.teacher",e,0)
        b.run_until(6)
        decoder=d.OutputDecoder()
        for w in (a,b):
            w.probe("q0.query",13,6);w.probe("q1.query",13,6);w.run_until(11)
        self.assertEqual([a.decode(f"q{j}","response",decoder).integer for j in range(2)],[25,29])
        self.assertEqual([b.decode(f"q{j}","response",decoder).integer for j in range(2)],[29,25])
        w=learned();independent=[]
        for p in range(50):
            f=w.fork();f.probe("q0.query",p,6);f.probe("q1.query",p,6);f.run_until(11)
            independent.append([f.observe(f"q{j}","response").record.s_reg for j in range(2)])
        self.assertEqual(independent[-1],[61,65]);self.assertEqual(w.runtime.current_tick,6)
        w.start_mobile_sequence("sequential50",list(range(50)))
        w.run_until(37)
        with tempfile.TemporaryDirectory() as folder:
            file=str(Path(folder)/"mid.deetsnap");w.save_snapshot(file)
            copy=d.OrganizationalWorld.load_snapshot(file)
            w.run_until(256);copy.run_until(256)
            self.assertEqual(physical(w),physical(copy));self.assertEqual(copy.protocols[0].next_capture,50)
            self.assertEqual([o.record.s_reg for o in copy.protocols[0].steps[-1].captured],[1237,1241])
            self.assertEqual(len(w.runtime.receipts),len(copy.runtime.receipts))
        self.assertTrue(any("PHYSICAL_PROBE" in x for x in w.external_operations))

    def test_f01_latent_memory_access_and_missing_center(self):
        for h,delta,dx in ((d.BasalHistory.AB,1,1),(d.BasalHistory.BA,-1,-1),(d.BasalHistory.H0,0,0)):
            w=d.create_organization("relational",history=h);w.advance(250)
            obs=w.view("body").observe();self.assertEqual(obs.delta,delta)
            for payload in (0,7):self.assertEqual(probe_body(w,payload).observe("body","comparator").record.dx,dx)
            self.assertEqual(w.runtime.current_tick,282)
            e=d.ResearchStateEdit();e.coordinate=w.view("body").spec.a;e.raw=0;e.label="missing center"
            damaged=w.diagnostic_fork([e],True);self.assertIsNone(damaged.view("body").observe().delta)
            self.assertEqual(w.view("body").observe().delta,delta)

    def test_f02_native_transfer_and_assisted_reconstruction(self):
        for teacher,expected in ((7,25),(11,29)):
            w=d.create_organization("native_transfer",teacher0=teacher)
            w.probe("query",0,6);w.probe("receiver_query",13,16);w.run_until(21)
            self.assertEqual(w.observe("stage0","receiver_response").record.s_reg,expected)
            cut=d.create_organization("native_transfer",teacher0=teacher);cut.probe("query",0,6);cut.run_until(13)
            hub=cut.view("stage0").spec.ports["response"]
            q=d.Coordinate((hub.x-2)%127,(hub.y+2)%127,hub.z)
            e=d.ResearchStateEdit();e.coordinate=q;e.raw=0;e.label="late relay cut"
            cut=cut.diagnostic_fork([e],True);cut.probe("receiver_query",13,16);cut.run_until(21)
            self.assertEqual(cut.observe("stage0","receiver_response").record.s_reg,13)
        src=d.create_organization("relational");src.advance(3)
        dst=d.create_organization("relational",history=d.BasalHistory.H0);dst.advance(3)
        before=physical(dst);spec=d.ReconstructionSpec();spec.source_sites=[src.view("body").spec.a,src.view("body").spec.b];spec.destination_sites=spec.source_sites;spec.authorize_assisted_reconstruction=True
        rebuilt=dst.assisted_reconstruction(src,spec)
        self.assertEqual(physical(dst),before);self.assertEqual(rebuilt.view("body").observe().delta,1)
        self.assertEqual(rebuilt.diagnostic_edits[-1].modality,d.OperationModality.ASSISTED_RECONSTRUCTION)
        self.assertEqual(probe_body(rebuilt).observe("body","comparator").record.dx,1)
        spec.destination_sites=[spec.source_sites[0]]*2
        with self.assertRaises(ValueError):dst.assisted_reconstruction(src,spec)

    def test_f03_cascades_and_interfamily_bridge(self):
        for depth,expected in ((2,39),(4,73),(8,165)):
            w=d.create_organization("cascade",depth=depth);w.probe("query",13,6);w.run_until(11+5*(depth-1))
            self.assertEqual(w.observe(f"stage{depth-1}","response").record.s_reg,expected)
        w=d.create_organization("cascade",depth=4,omit=2);w.probe("query",13,6);w.run_until(26)
        self.assertEqual(w.observe("stage3","response").record.s_reg,57)
        w=d.create_organization("mobile_basal");plain=w.fork();t=d.TraceSession();t.sites={"comparator":w.view("body").spec.comparator};t.sample_budget=64;w.set_trace(t);w.advance(12);plain.advance(12)
        self.assertEqual(physical(w),physical(plain));self.assertEqual(w.observe("body","comparator").record.s_reg,12)
        self.assertEqual(probe_body(w).observe("body","comparator").record.s_reg,12)
        with tempfile.TemporaryDirectory() as folder:
            f=str(Path(folder)/"bridge.deetsnap");w.save_snapshot(f);c=d.OrganizationalWorld.load_snapshot(f)
            w.advance(88);c.advance(88);self.assertEqual(physical(w),physical(c));self.assertEqual(len(w.trace().samples),len(c.trace().samples))

    def test_f04_native_context_event_and_phase_access(self):
        w=d.create_organization("contextual");w.advance(131)
        gate=d.inspect_write_gate(w.runtime,w.view("body").spec.b,True)
        self.assertEqual((gate.local_clock,gate.n_active,gate.period),(391,6,391))
        w.advance();self.assertEqual(w.view("body").observe().delta,0)
        w=d.create_organization("contextual");i=d.InterfaceSpec();i.name="physical_event";ch=d.ChannelSpec();ch.name=i.name;ch.injection_site=d.Coordinate(16,16,15);ch.direction=d.Direction(0,0,1);i.channel=ch;w.declare_interface(i);w.submit(i.name,0,162);w.run_until(164)
        self.assertEqual(w.view("body").observe().delta,1)
        for mode,loads in ((0,[32,0]),(1,[0,32]),(2,[0,54])):
            w=d.create_organization("phase",mode=mode);w.run_until(40);got=[]
            for delay in (0,1):
                f=w.fork();f.probe("phase.access_query",13,40+delay);f.run_until(42+delay);got.append(f.observe("phase","access_response").record.s_reg)
            self.assertEqual(got,loads)

    def test_f05_tracking_budget_export_and_encounter(self):
        w=d.create_organization("competition");w.run_until(3)
        t=d.TraceSession();t.sample_budget=4;s=d.MobileSegment();s.id="declared_A";s.birth_site=w.view("encounter").spec.ports["hubA"];s.direction=d.Direction(0,1,0);s.birth_tick=3;s.expected_load=12;s.expected_semantic=1;t.segments=[s]
        w.set_trace(t);plain=w.fork();plain.set_trace(d.TraceSession());w.capture_trace();w.run_until(10);plain.run_until(10)
        self.assertEqual(physical(w),physical(plain));self.assertTrue(w.trace().segments[0].correspondence_stopped)
        self.assertIn("UNRESOLVED",w.trace().samples[-1].coverage)
        with tempfile.TemporaryDirectory() as folder:
            p=str(Path(folder)/"trace.deetrace");w.trace().export_trace(p);t2=d.TraceSession.load_trace(p);self.assertEqual(len(t2.samples),len(w.trace().samples))
            b=Path(p).read_bytes();Path(p).write_bytes(b[:16])
            with self.assertRaises((ValueError,RuntimeError)):d.TraceSession.load_trace(p)
        w=d.create_organization("competition");w.run_until(5);pre=w.runtime.fork();w.advance();report=d.observe_encounter(pre,w.runtime,w.view("encounter").spec.ports["meeting"])
        self.assertEqual(report.after.record.s_reg,36);self.assertEqual(len(report.direct_ballistic_contributors),2)
        t=d.TraceSession();t.sample_budget=2;t.sites={"one":d.Coordinate(1,1,1)};w.set_trace(t);w.advance(10);self.assertTrue(w.trace().capture_stopped);self.assertEqual(w.runtime.current_tick,16)

    def test_f06_codecs_receipts_and_errors(self):
        codec=d.InputCodec();codec.minimum=0;codec.maximum=17
        self.assertEqual(codec.encode_integer(17),17)
        for p in (-1,18,1<<63):
            with self.assertRaises((ValueError,TypeError,OverflowError)):codec.encode_integer(p)
        codec.type=d.CodecType.BOOLEAN;codec.maximum=1;self.assertEqual(codec.encode_integer(True),1)
        with self.assertRaises(ValueError):codec.encode_integer(2)
        codec.type=d.CodecType.REGISTERED_PATTERN;codec.symbols={"Sensor_Activo":7,"same_physics":7,"Other":11};self.assertFalse(codec.injective)
        w=d.create_organization("mobile_pair");i=d.InterfaceSpec();i.name="NamedSensor";i.channel=w.interfaces[0].channel;i.channel.name="NamedSensor";i.codec=codec;w.declare_interface(i)
        r=w.submit_symbol("NamedSensor","Sensor_Activo",0);self.assertEqual(r.status,d.EventStatus.SCHEDULED)
        second=w.submit_symbol("NamedSensor","Other",0);w.advance();self.assertEqual(w.runtime.receipt(r.id).status,d.EventStatus.REJECTED_CONFLICT);self.assertEqual(w.runtime.receipt(second.id).status,d.EventStatus.REJECTED_CONFLICT)
        late=w.submit_symbol("NamedSensor","Other",0);self.assertEqual(late.status,d.EventStatus.REJECTED_LATE)
        accepted=w.submit_symbol("NamedSensor","Sensor_Activo",1);w.advance();self.assertEqual(w.runtime.receipt(accepted.id).status,d.EventStatus.APPLIED)
        dec=d.OutputDecoder();dec.type=d.CodecType.ENUMERATION;dec.symbols=codec.symbols
        obs=w.runtime.observe(d.Coordinate(i.channel.injection_site.x-1,i.channel.injection_site.y,i.channel.injection_site.z));out=dec.decode(obs);self.assertTrue(out.ambiguous)
        w.declare_decoder("custom",dec)
        with tempfile.TemporaryDirectory() as folder:
            f=str(Path(folder)/"io.deetsnap");w.save_snapshot(f);c=d.OrganizationalWorld.load_snapshot(f);self.assertEqual(c.decoder("custom").symbols,dec.symbols);self.assertEqual(c.interfaces[-1].codec.symbols,codec.symbols)
        w=learned();i=d.InterfaceSpec();i.name="symbol_query";i.channel=next(x.channel for x in w.interfaces if x.name=="q0.query");i.channel.name=i.name;i.codec.type=d.CodecType.ENUMERATION;i.codec.symbols={"Sensor_Activo":13};w.declare_interface(i);w.probe_symbol(i.name,"Sensor_Activo",6);w.run_until(11);self.assertEqual(w.observe("q0","response").record.s_reg,25)
        # Occupied initial support: acceptance at schedule and effective rejection are distinct.
        w=d.create_organization("relational");r=w.probe("body.common_query",7,32);w.advance();self.assertEqual(w.runtime.receipt(r.id).status,d.EventStatus.APPLIED)
        w=d.create_organization("relational",keep_reader=True);i=d.InterfaceSpec();i.name="occupied";i.channel=d.ChannelSpec();i.channel.name=i.name;i.channel.injection_site=w.view("body").spec.a;w.declare_interface(i);r=w.submit(i.name,7,32);w.advance();self.assertEqual(w.runtime.receipt(r.id).status,d.EventStatus.REJECTED_OCCUPIED)

    def test_f07_action_and_information_interfaces(self):
        full=d.create_organization("contingent");full.advance(8);pre=physical(full);e=d.ResearchStateEdit();e.coordinate=full.view("body").spec.ports["action"];e.raw=0;e.label="late emitted product cut";cut=full.diagnostic_fork([e],True);self.assertEqual(physical(full),pre);full.advance(5);cut.advance(5)
        self.assertEqual(full.observe("body","environment").record.s_reg,48);self.assertEqual(cut.observe("body","environment").record.s_reg,30)
        for hidden,value in ((23,43),(25,45)):
            w=d.create_organization("information",hidden=hidden);w.advance(16);self.assertEqual(w.observe("body","downstream").record.s_reg,value)
        w=d.create_organization("information",history=d.BasalHistory.BA);w.advance(16);self.assertEqual(w.observe("body","downstream").record.s_reg,13)

    def test_f08_distributed_saturation_independent_availability(self):
        w=d.create_organization("distributed");w.submit("integration.A",8,0);w.submit("integration.B",9,0);w.run_until(700)
        self.assertEqual(w.observe("integration","q").record.s_reg,19664);self.assertEqual(w.view("history").observe().delta,1)
        self.assertIn("q",w.view("integration").resilience().ordinary_cap_sites)
        f=w.fork();f.probe("history.common_query",7,700);f.advance(3);self.assertEqual(f.view("history").observe().delta,1)
        # No implicit reconstruction after support loss.
        b=d.create_organization("relational");b.advance(3);e=d.ResearchStateEdit();e.coordinate=b.view("body").spec.supports[0];e.raw=0;e.label="support loss";f=b.diagnostic_fork([e],True);f.advance(170);self.assertFalse(f.view("body").observe().supports_intact);self.assertIsNone(f.view("body").observe().delta)

    def test_f09_joint_product_reuse_and_pending_snapshot(self):
        for arm,expected in (("both",36),("A_only",12),("B_only",24)):
            w=d.create_organization("competition",arm=arm);w.run_until(6);self.assertEqual(w.observe("encounter","meeting").record.s_reg,expected)
        w=d.create_organization("competition");w.probe("joint_query",13,6)
        with tempfile.TemporaryDirectory() as folder:
            file=str(Path(folder)/"before_contact.deetsnap");w.run_until(5);w.save_snapshot(file);c=d.OrganizationalWorld.load_snapshot(file);w.run_until(14);c.run_until(14);self.assertEqual(physical(w),physical(c))
        w.probe("later_query",17,14);w.run_until(20);self.assertEqual(w.observe("encounter","later_response").record.s_reg,66)
        for dest in ("material","protected"):
            w=d.create_organization("competition",destination=dest);w.advance(6);self.assertEqual(w.observe("encounter","meeting").record.s_reg,100)

    def test_lifetimes_inert_attach_custom_recipe_uint64(self):
        w=d.create_organization("relational");v=w.view("body");r=v.runtime;del w;gc.collect();r.advance();self.assertEqual(v.observe().delta,1)
        rt=d.Runtime(7);rec=d.OrganizationRecipe.research(7,[]);s=d.OrganizationSpec();s.id="inert";s.ports={"site":d.Coordinate(2,2,2)};before=physical(rt);a=d.OrganizationalWorld.attach(rt,rec,[s]);self.assertEqual(physical(a),before);self.assertEqual(rt.channel_names,[]);del rt;gc.collect();self.assertEqual(a.runtime.dimension,7)
        p=d.InitialPlacement();p.site=d.Coordinate(3,3,3);p.raw=d.pack_record(1,123,1,0,0,1);p.clock=(1<<63)+7
        rec=d.OrganizationRecipe.research(7,[p],1<<54);s.t0_tick=1<<54;rec.organizations=[s];c=d.OrganizationalWorld.create(rec)
        with tempfile.TemporaryDirectory() as folder:
            f=str(Path(folder)/"custom.deetsnap");c.save_snapshot(f);b=d.OrganizationalWorld.load_snapshot(f);self.assertEqual(physical(c),physical(b));self.assertEqual(b.runtime.current_tick,1<<54);self.assertEqual(b.runtime.observe(p.site).clock,(1<<63)+7)
            raw=Path(f).read_bytes();Path(f).write_bytes(raw[:-10])
            with self.assertRaises(RuntimeError):d.OrganizationalWorld.load_snapshot(f)
        with self.assertRaises(ValueError):d.OrganizationalWorld.create(d.OrganizationRecipe.research(7,[p,p]))
        with self.assertRaises(ValueError):d.create_organization("cascade",depth=20)
        with self.assertRaises(ValueError):d.OrganizationalWorld.create(d.OrganizationRecipe.research(10000,[]))
        with self.assertRaises(ValueError):learned().start_mobile_sequence("overflow",[1],(1<<64)-1)

    def test_backends_passivity_fork_isolation(self):
        w=learned();a=w.fork();b=w.fork();a.runtime.execution_options=d.TickOptions(d.Backend.DENSE_SEQUENTIAL,1);b.runtime.execution_options=d.TickOptions(d.Backend.DENSE_PARALLEL,2)
        for world in (w,a,b):world.probe("q0.query",13,6);world.run_until(11)
        self.assertEqual(physical(w),physical(a));self.assertEqual(physical(w),physical(b))
        before=physical(w)
        for _ in range(10):w.view("q0").observe();w.observe("q0","response")
        self.assertEqual(before,physical(w));c=w.fork();c.advance();self.assertEqual(before,physical(w))

    def test_transfer_bridge_toroidal_tracking_and_explicit_bounds(self):
        w=d.create_organization("native_transfer");w.probe("query",0,6);w.run_until(11)
        t=d.TraceSession();t.sample_budget=24;s=d.MobileSegment();s.id="observed_zero_relay";s.birth_site=w.view("stage0").spec.ports["response"];s.birth_tick=11;s.direction=d.Direction(-1,1,0);s.expected_load=12;t.segments=[s];w.set_trace(t);plain=w.fork();plain.set_trace(d.TraceSession());w.capture_trace();w.run_until(16);plain.run_until(16);self.assertEqual(physical(w),physical(plain));self.assertTrue(all("OBSERVED_DECLARED" in sample.coverage for sample in w.trace().samples))
        w=d.create_organization("mobile_basal");w.advance(3)
        t=d.TraceSession();s=d.MobileSegment();s.id="bridge_input";s.birth_site=w.view("mobile").spec.ports["hub"];s.birth_tick=35;s.direction=d.Direction(0,1,0);s.expected_load=12;t.segments=[s];w.set_trace(t);w.capture_trace();w.advance(4);self.assertGreaterEqual(len(w.trace().samples),2)
        w=d.create_organization("phase",mode=1);w.run_until(14)
        t=d.TraceSession();t.sample_budget=40;s=d.MobileSegment();s.id="wrapped_flux";s.birth_site=w.view("phase").spec.ports["hub"];s.birth_tick=14;s.direction=d.Direction(1,1,1);s.expected_load=41;t.segments=[s];w.set_trace(t);w.capture_trace();w.run_until(40)
        last=w.trace().samples[-1];self.assertEqual(list(last.unwrapped),[41,41,41]);self.assertEqual((last.observation.coordinate.x,last.observation.coordinate.y,last.observation.coordinate.z),(10,10,10));self.assertEqual(last.observation.record.s_reg,41)
        for recipe,params in (("cascade",{"omit":99}),("native_transfer",{"depth":4}),("competition",{"arm":"not_a_case"}),("competition",{"destination":"unknown"}),("mobile_pair",{"unused_output":25}),("predictive",{"paired":2})):
            with self.assertRaises(ValueError):d.create_organization(recipe,**params)

    def test_cross_process_restoration(self):
        w=learned();w.start_mobile_sequence("seq",[0,1,2]);w.run_until(13)
        with tempfile.TemporaryDirectory() as folder:
            input=str(Path(folder)/"input.deetsnap");output=str(Path(folder)/"output.deetsnap");w.save_snapshot(input)
            process=subprocess.run([sys.executable,"-I","-c","import dee_thinking as d,sys; w=d.OrganizationalWorld.load_snapshot(sys.argv[1]); w.run_until(21); w.save_snapshot(sys.argv[2])",input,output],capture_output=True,text=True,cwd=folder)
            self.assertEqual(process.returncode,0,process.stderr);w.run_until(21);c=d.OrganizationalWorld.load_snapshot(output);self.assertEqual(physical(w),physical(c));self.assertEqual(c.protocols[0].next_capture,3)

if __name__=="__main__":unittest.main()
