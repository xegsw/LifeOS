#include <Security/Security.h>
#include <assert.h>
#include <string.h>
static int lookups,descriptions,mode;
static OSStatus fakeDefault(SecKeychainRef *p){*p=(SecKeychainRef)1;return 0;}
static OSStatus fakeFind(CFTypeRef k,UInt32 sl,const char*s,UInt32 al,const char*a,UInt32*len,void**data,SecKeychainItemRef*i){assert(k==(void*)1);assert(sl==strlen("com.lifeos.p3-152.aead-key.v1")&&!memcmp(s,"com.lifeos.p3-152.aead-key.v1",sl));assert(al==43&&!memcmp(a,"p3-152-key-",11));assert(!len&&!data&&i);lookups++;*i=(SecKeychainItemRef)2;return mode==1?-25293:0;}
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
#define lifeos_metadata lifeos_metadata_fake
#include "metadata.c"
int lifeos_metadata_fake_calls(void){return lookups;}
int lifeos_metadata_fake_releases(void){return descriptions;}
