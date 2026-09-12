#include <Security/Security.h>
#include <assert.h>
#include <string.h>
static int lookups,descriptions,mode;
static OSStatus fakeDefault(SecKeychainRef *p){*p=(SecKeychainRef)1;return 0;}
static OSStatus fakeFind(CFTypeRef k,UInt32 sl,const char*s,UInt32 al,const char*a,UInt32*len,void**data,SecKeychainItemRef*i){assert(k==(void*)1);assert(sl==3&&al==3&&!memcmp(s,"svc",3)&&!memcmp(a,"ref",3));assert(!len&&!data&&i);lookups++;*i=(SecKeychainItemRef)2;return mode==1?-25293:0;}
static OSStatus fakeAccess(SecKeychainItemRef i,SecAccessRef *a){assert(i==(void*)2);*a=(SecAccessRef)3;return 0;}
static CFArrayRef fakeRules(SecAccessRef a,CFTypeRef tag){assert(a==(void*)3&&tag==kSecACLAuthorizationDecrypt);return (CFArrayRef)4;}
static CFIndex fakeCount(CFArrayRef a){assert(a==(void*)4||a==(void*)6);return a==(void*)4?1:(mode==3?0:2);}
static const void *fakeAt(CFArrayRef a,CFIndex i){assert(a==(void*)4&&i==0);return (void*)5;}
static OSStatus fakeContents(SecACLRef a,CFArrayRef *apps,CFStringRef *desc,SecKeychainPromptSelector *prompt){assert(a==(void*)5);*apps=mode==2?NULL:(CFArrayRef)6;*desc=(CFStringRef)7;*prompt=1;return mode==4?-25293:0;}
static void fakeRelease(CFTypeRef p){assert(p);if(p==(void*)7)descriptions++;}
#define SecKeychainCopyDefault fakeDefault
#define SecKeychainFindGenericPassword fakeFind
#define SecKeychainItemCopyAccess fakeAccess
#define SecAccessCopyMatchingACLList fakeRules
#define CFArrayGetCount fakeCount
#define CFArrayGetValueAtIndex fakeAt
#define SecACLCopyContents fakeContents
#define CFRelease fakeRelease
#include "../candidate/src/secure_credentials/metadata.c"
int main(void){for(mode=0;mode<5;mode++){LifeOSMetadata r;lookups=descriptions=0;lifeos_metadata((void*)"svc",3,(void*)"ref",3,&r);assert(lookups==1);if(mode==1){assert(r.stage==2&&r.status==-25293&&descriptions==0);}else{assert(descriptions==1);if(mode==4)assert(r.stage==5&&r.status==-25293);else{assert(r.stage==7&&r.count==1&&r.rules[0].prompt==1);assert(r.rules[0].list_kind==(mode==2?0:mode==3?1:2));}}}return 0;}
