"""Offline execution of the actual contract with a small transactional host double.
Not a replacement for GenVM execution or live validator consensus.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import pytest

class UserError(Exception):
    pass

class Return:
    def __init__(self, calldata): self.calldata = calldata

class Decorator:
    def __call__(self, fn): return fn
    payable = property(lambda self: self)

class Base:
    def __init_subclass__(cls): pass
    def __new__(cls, *args):
        obj = super().__new__(cls)
        obj.audits, obj.history, obj.credits = {}, {}, {}
        return obj

class Address(str): pass

ctx = types.SimpleNamespace(sender_address=Address('sponsor'), contract_address=Address('contract'), value=0)
host = types.SimpleNamespace(Contract=Base, message=ctx,
    public=types.SimpleNamespace(write=Decorator(), view=Decorator()),
    vm=types.SimpleNamespace(UserError=UserError, Return=Return),
    nondet=types.SimpleNamespace(web=types.SimpleNamespace(), exec_prompt=None),
    evm=types.SimpleNamespace(contract_interface=lambda cls: cls))
fake = types.ModuleType('genlayer')
fake.gl, fake.Address, fake.u256, fake.u32, fake.TreeMap = host, Address, int, int, dict
sys.modules['genlayer'] = fake
spec = importlib.util.spec_from_file_location('auditbond', Path(__file__).parents[1] / 'contracts/auditbond.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
BODY = (Path(__file__).parents[1] / 'evidence/synthetic-audit.txt').read_bytes()
URL = 'https://raw.githubusercontent.com/ANZA24k/AuditBond/' + 'a'*40 + '/evidence/synthetic-audit.txt'
POLICY = {'title':'Synthetic access and deletion checks', 'criteria':['Unprivileged access to the test record is denied without exposing contents.', 'Deleted test account is unavailable and its access token is rejected.'], 'evidence_requirements':'Public synthetic test observations with explicit HTTP outcomes for both checks.'}
MANIFEST = [{'url':URL, 'sha256':hashlib.sha256(BODY).hexdigest(), 'bytes':len(BODY)}]

@pytest.fixture
def env(monkeypatch):
    ctx.sender_address, ctx.value = Address('sponsor'), 100
    clock = [1000]
    monkeypatch.setattr(m, 'now', lambda: clock[0])
    a = m.AuditBond()
    a.create_audit(json.dumps(POLICY), 10, 1100, 1200)
    monkeypatch.setattr(host.nondet.web, 'get', lambda url: types.SimpleNamespace(status_code=200, body=BODY), raising=False)
    calls = []
    statuses = ['PASS', 'PASS']
    quotes = ['The service denied the request with\nHTTP 403 and returned no record contents.', 'The access token for that account was rejected with HTTP 401.']
    def prompt(p, **kw):
        calls.append(p)
        return {'findings':[{'criterion':i,'status':s,'evidence':0 if s!='UNKNOWN' else -1,'quote':quotes[i] if s!='UNKNOWN' else ''} for i,s in enumerate(statuses)]}
    monkeypatch.setattr(host.nondet, 'exec_prompt', prompt)
    def consensus(leader, validator):
        result = leader()
        assert validator(Return(result)), 'independent validator disagreed'
        return result
    monkeypatch.setattr(host.vm, 'run_nondet_unsafe', consensus, raising=False)
    return a, clock, statuses, calls


def submit(a):
    ctx.sender_address, ctx.value = Address('submitter'), 10
    a.submit('0', json.dumps(MANIFEST))


def tx(a, fn):
    # Emulate transaction rollback on error, as GenVM does.
    snapshot = copy.deepcopy(a.__dict__)
    try: return fn()
    except Exception:
        a.__dict__ = snapshot
        raise


@pytest.mark.parametrize('statuses,verdict,credits', [
    (['PASS','PASS'],'COMPLIANT',(0,110)),
    (['PASS','UNKNOWN'],'PARTIAL',(50,60)),
    (['PASS','FAIL'],'NON_COMPLIANT',(110,0)),
    (['UNKNOWN','UNKNOWN'],'INSUFFICIENT',(100,10))])
def test_verdict_and_conservation(env,statuses,verdict,credits):
    a,clock,current,calls=env
    submit(a); current[:]=statuses
    h=a.evaluate('0')
    record=json.loads(a.get_verdict('0',1))
    assert record['verdict']==verdict and len(calls)==2
    payload={k:v for k,v in record.items() if k not in ('decision_hash','findings','evaluated_at')}
    assert m.digest(payload)==h
    clock[0]=1200; a.settle('0')
    assert (a.get_credit('sponsor'),a.get_credit('submitter'))==credits
    assert sum(credits)==110 and a.liability==110
    with pytest.raises(UserError): a.settle('0')


def test_append_only_revisions(env):
    a,clock,statuses,_=env; submit(a)
    h1=a.evaluate('0'); original=a.get_verdict('0',1)
    statuses[:]=['PASS','UNKNOWN']; h2=a.evaluate('0')
    assert h1!=h2 and a.get_verdict('0',1)==original
    assert json.loads(a.get_verdict('0',2))['previous_hash']==h1
    a.evaluate('0')
    with pytest.raises(UserError): a.evaluate('0')


@pytest.mark.parametrize('submitted', [False, True])
def test_expiry_recovers_funds_without_consensus(env,submitted):
    a,clock,_,_=env
    if submitted: submit(a)
    clock[0]=1200; a.settle('0')
    assert a.get_credit('sponsor')==100
    assert a.get_credit('submitter')==(10 if submitted else 0)
    with pytest.raises(UserError): a.evaluate('0')


def test_deadlines_authorization_exact_bond_replay(env):
    a,clock,_,_=env
    ctx.value=10
    with pytest.raises(UserError): a.submit('0',json.dumps(MANIFEST))
    ctx.sender_address=Address('submitter'); ctx.value=9
    with pytest.raises(UserError): a.submit('0',json.dumps(MANIFEST))
    ctx.value=10; clock[0]=1100
    with pytest.raises(UserError): a.submit('0',json.dumps(MANIFEST))
    clock[0]=1099; submit(a)
    with pytest.raises(UserError): a.submit('0',json.dumps(MANIFEST))
    with pytest.raises(UserError): a.settle('0')
    clock[0]=1200
    with pytest.raises(UserError): a.evaluate('0')


@pytest.mark.parametrize('tail', ['/../file.txt','//file.txt','/file.txt?x=1','/file.txt#x','/file%2etxt','/file.html'])
def test_url_aliases_rejected(tail):
    with pytest.raises(UserError): m.validate_url(URL.rsplit('/',1)[0]+tail)


@pytest.mark.parametrize('url', ['http://raw.githubusercontent.com/a/b/'+'a'*40+'/x.txt', 'https://127.0.0.1/x.txt','https://raw.githubusercontent.com/a/b/main/x.txt', 'https://user@raw.githubusercontent.com/a/b/'+'a'*40+'/x.txt'])
def test_noncanonical_hosts_and_mutable_refs(url):
    with pytest.raises(UserError): m.validate_url(url)


def test_manifest_policy_limits():
    m.validate_manifest(json.dumps(MANIFEST)); m.validate_policy(json.dumps(POLICY))
    for items in [[], MANIFEST*2, [{'url':URL,'sha256':'bad','bytes':10}], [{'url':URL,'sha256':'a'*64,'bytes':True}], [{'url':URL,'sha256':'a'*64,'bytes':16385}]]:
        with pytest.raises(UserError): m.validate_manifest(json.dumps(items))
    for p in [{**POLICY,'criteria':[]},{**POLICY,'criteria':['x']*2},{**POLICY,'criteria':['x'*401]},{**POLICY,'extra':True}]:
        with pytest.raises(UserError): m.validate_policy(json.dumps(p))
    items=[{'url':URL.replace('synthetic-audit',str(i)), 'sha256':'a'*64,'bytes':16000} for i in range(3)]
    with pytest.raises(UserError): m.validate_manifest(json.dumps(items))


@pytest.mark.parametrize('status,body',[(404,b''),(200,BODY+b'x'),(200,b'x'*len(BODY)),(302,BODY)])
def test_integrity_failure_never_judges_partial_bundle(env,monkeypatch,status,body):
    a,_,_,calls=env; submit(a)
    monkeypatch.setattr(host.nondet.web,'get',lambda url:types.SimpleNamespace(status_code=status,body=body))
    a.evaluate('0')
    assert json.loads(a.get_verdict('0',1))['verdict']=='INSUFFICIENT' and calls==[]


@pytest.mark.parametrize('status',[408,429,500,503])
def test_transient_failure_does_not_create_verdict(env,monkeypatch,status):
    a,_,_,_=env; submit(a)
    monkeypatch.setattr(host.nondet.web,'get',lambda url:types.SimpleNamespace(status_code=status,body=b''))
    with pytest.raises(UserError): tx(a,lambda:a.evaluate('0'))
    assert a.history=={} and json.loads(a.get_audit('0'))['revision']==0


def test_validator_rejects_forged_outcomes_and_citations(env,monkeypatch):
    a,_,_,_=env; submit(a)
    def attack(leader,validator):
        result=leader()
        wrong=copy.deepcopy(result); wrong['statuses']=['UNKNOWN','UNKNOWN']
        assert not validator(Return(wrong))
        wrong=copy.deepcopy(result); wrong['findings'][0]['quote']='fabricated quotation'
        assert not validator(Return(wrong))
        assert not validator(types.SimpleNamespace(message='failure'))
        return result
    monkeypatch.setattr(host.vm,'run_nondet_unsafe',attack)
    a.evaluate('0')


def test_malformed_llm_does_not_settle(env,monkeypatch):
    a,_,_,_=env; submit(a)
    monkeypatch.setattr(host.nondet,'exec_prompt',lambda *args,**kw:{'findings':[]})
    with pytest.raises(UserError): tx(a,lambda:a.evaluate('0'))
    assert a.history=={}


def test_withdraw_checks_effects_and_no_replay(env,monkeypatch):
    a,clock,_,_=env; submit(a); a.evaluate('0'); clock[0]=1200; a.settle('0')
    transfers=[]
    class Payment:
        def __init__(self,addr): self.addr=addr
        def emit_transfer(self,*,value):
            assert a.get_credit(str(self.addr))==0
            transfers.append((self.addr,value))
    monkeypatch.setattr(m,'Payout',Payment)
    a.withdraw(); assert transfers==[('submitter',110)] and a.liability==0
    with pytest.raises(UserError): a.withdraw()


def test_failed_emission_rolls_back_credit(env,monkeypatch):
    a,clock,_,_=env; submit(a); clock[0]=1200; a.settle('0')
    class Payment:
        def __init__(self,addr): pass
        def emit_transfer(self,**kw): raise UserError('emission failure')
    monkeypatch.setattr(m,'Payout',Payment)
    with pytest.raises(UserError): tx(a,a.withdraw)
    assert a.get_credit('submitter')==10 and a.liability==110


def test_integer_rounding_and_hash_domain():
    assert m.allocation(101,10,'PARTIAL',1,3)==(68,43)
    assert m.digest({'a':1,'b':2})==m.digest({'b':2,'a':1})
    assert m.digest({'contract':'a'})!=m.digest({'contract':'b'})
