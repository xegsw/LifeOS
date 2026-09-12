"""D-0672: explicitly authorized login identity full B bundle recipe; no signing without an explicit identity.
Default prints a plan only. --execute requires the PM/user-authorized certificate
SHA-1 identifier; never discovers identities, creates certificates, or changes ACL.
No launch, replacement, timestamp server, notarization, or provider access.
"""
from pathlib import Path
import argparse, hashlib, json, os, plistlib, re, shutil, subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = Path('/private/tmp/lifeos-p3-158-main-chain-v1')
OWNER = dict(task='P3-158', root=str(ROOT), owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
IDENTIFIER = 'local.lifeos.p3-158.main-chain'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity-sha1', help='Explicitly authorized persistent signing certificate fingerprint; not a private key')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--rebuild', action='store_true', help='Use the independently rebuilt online-synthetic binary and matching receipt')
    parser.add_argument('--build-tag', default='D0672-B-terminal', help='New exclusive staging directory, never overwritten')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,48}', args.build_tag):
        parser.error('invalid build tag')
    if args.identity_sha1 and not re.fullmatch(r'[0-9A-Fa-f]{40}', args.identity_sha1):
        parser.error('require exact certificate SHA-1 fingerprint; ad-hoc and ambiguous names are rejected')
    if args.execute and not args.identity_sha1:
        parser.error('persistent signing identity has not been explicitly supplied; no filesystem mutation or signing')
    binary = ROOT/('build/online-rebuild/debug/lifeos-p3-152' if args.rebuild else 'build/online/debug/lifeos-p3-152')
    helper = ROOT/'online-synthetic/source-engine/alias_metadata'
    stage_parent = ROOT/'build/signing-v1'
    stage = stage_parent / args.build_tag
    app = stage/'LifeOS P3-158 Online Test.app'
    identity = args.identity_sha1 or '<AUTHORIZED_D0672_CERTIFICATE_SHA1>'
    keychain = '/Users/xxe/Library/Keychains/login.keychain-db'
    requirement = lambda identifier: f'=designated => identifier \"{identifier}\" and anchor H\"{identity}\"' 
    commands = [
        ['/usr/bin/codesign', '--force', '--sign', identity, '--keychain', keychain, '--requirements', requirement(IDENTIFIER+'.alias-metadata'), '--identifier', IDENTIFIER+'.alias-metadata', '--timestamp=none', str(app/'Contents/Resources/alias_metadata')],
        ['/usr/bin/codesign', '--force', '--sign', identity, '--keychain', keychain, '--requirements', requirement(IDENTIFIER), '--identifier', IDENTIFIER, '--timestamp=none', str(app)],
        ['/usr/bin/codesign', '--verify', '--strict', '--verbose=2', str(app/'Contents/Resources/alias_metadata')],
        ['/usr/bin/codesign', '--verify', '--strict', '--verbose=2', str(app)],
        ['/usr/bin/codesign', '--display', '--verbose=4', '--requirements', '-', str(app)],
    ]
    plan = dict(mode='online-synthetic', identifier=IDENTIFIER, app=str(app), binarySource=str(binary), helperSource=str(helper), commands=commands,
                executed=False, trustedKeychainAccess='Unknown; requires separate actual verification', replacesExistingApp=False)
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2)); return
    os.umask(0o077)
    allowed_sha1='7490dc97208f45420c4dfc9c48ddf6f59113b6f4'
    allowed_sha256='77aeaaa16f719d1394d36442fbb9732f9d6e5ea7903954d292cd445df372357d'
    public=json.loads((BASE/'signing/D0671-login-public-certificate.json').read_text())
    if args.identity_sha1.lower()!=allowed_sha1 or public['exactMatchCount']!=1 or public['matches'][0]['sha1']!=allowed_sha1 or public['matches'][0]['sha256']!=allowed_sha256:
        raise SystemExit('identity differs from D0672 authorized public certificate')
    k=Path(keychain)
    if k.is_symlink() or not k.is_file() or k.stat().st_uid!=os.getuid():
        raise SystemExit('explicit login keychain is not an owned ordinary file')
    if ROOT.is_symlink() or json.loads((ROOT/'.owner.json').read_text()) != OWNER:
        raise SystemExit('owner root mismatch')
    if ROOT.stat().st_mode & 0o777 != 0o700:
        raise SystemExit('root permissions mismatch')
    for source in [binary, helper]:
        if source.is_symlink() or not source.is_file() or not os.access(source, os.X_OK):
            raise SystemExit('missing ordinary executable build input')
    config = json.loads((BASE/'candidate/tauri.conf.json').read_text())
    if config['identifier'] != IDENTIFIER:
        raise SystemExit('compiled configuration identifier drift')
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    receipt_path=BASE/('evidence/D0672-rebuild-identity.json' if args.rebuild else 'evidence/D0672-B-terminal-build-identity.json')
    receipt = json.loads(receipt_path.read_text())
    current = {str(p.relative_to(BASE/'candidate')):sha(p) for p in sorted((BASE/'candidate').rglob('*')) if p.is_file()}
    if receipt['candidateFiles'] != current or receipt['onlineBinarySha256'] != sha(binary) or receipt['helperSha256'] != sha(helper):
        raise SystemExit('build identity changed; rebuild and record a fresh reviewed build receipt before signing')
    # Exclusive staging: failed signing artifacts remain for diagnosis, never reused.
    marker={'task':'P3-158','authorization':'D0672','purpose':'exclusive signing stages','root':str(stage_parent)}
    if not stage_parent.exists():
        stage_parent.mkdir(mode=0o700)
        (stage_parent/'.owner.json').write_text(json.dumps(marker)+'\n')
    if stage_parent.is_symlink() or json.loads((stage_parent/'.owner.json').read_text())!=marker:
        raise SystemExit('signing staging owner mismatch')
    stage.mkdir()
    (stage/'input-identity.json').write_text(json.dumps({'receipt':str(receipt_path),'receiptSha256':sha(receipt_path),'authorizedCertificateSha1':identity},indent=2)+'\n')
    (app/'Contents/MacOS').mkdir(parents=True)
    (app/'Contents/Resources').mkdir()
    shutil.copy2(binary, app/'Contents/MacOS/lifeos-p3-152')
    shutil.copy2(helper, app/'Contents/Resources/alias_metadata')
    (app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(
        CFBundleExecutable='lifeos-p3-152', CFBundleIdentifier=IDENTIFIER,
        CFBundleName='LifeOS P3-158 Online Test', CFBundlePackageType='APPL',
        CFBundleVersion=config['version'], CFBundleShortVersionString=config['version'],
        NSHighResolutionCapable=True)))
    for index, command in enumerate(commands):
        with (stage/f'codesign-{index}.log').open('w') as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    for target in [app/'Contents/Resources/alias_metadata',app]:
        subprocess.run(['/usr/bin/codesign','--verify','--strict','--test-requirement','=certificate leaf = H"'+identity+'"',str(target)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
    details = (stage/'codesign-4.log').read_text()
    if 'Signature=adhoc' in details or 'Authority=' not in details or 'Sealed Resources version=' not in details or 'Info.plist entries=' not in details or 'Info.plist=not bound' in details:
        raise SystemExit('full persistent signature metadata incomplete; app not approved')
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    plan.update(executed=True, inputBinarySha256=sha(binary), inputHelperSha256=sha(helper),
                bundleFiles={str(p.relative_to(app)):sha(p) for p in sorted(app.rglob('*')) if p.is_file()})
    (stage/'manifest.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(app=str(app), signatureVerified=True, launched=False, keychainTrust='Unknown')))

if __name__ == '__main__':
    main()
