// Public SDK only. No password output, trusted-app export, or access mutation.
#include <Security/Security.h>
#include <stdint.h>
#include <string.h>
typedef struct { uint32_t list_kind, count, prompt; } LifeOSACLRule;
typedef struct { uint32_t stage; int32_t status; uint32_t found, count; LifeOSACLRule rules[32]; } LifeOSMetadata;
void lifeos_metadata(const uint8_t *service, uint32_t sl, const uint8_t *account, uint32_t al, LifeOSMetadata *out) {
 memset(out,0,sizeof(*out));
 SecKeychainRef chain=NULL; SecKeychainItemRef item=NULL; SecAccessRef access=NULL; CFArrayRef rules=NULL;
 out->stage=1; out->status=SecKeychainCopyDefault(&chain); if(out->status)goto done;
 out->stage=2;
 out->status=SecKeychainFindGenericPassword(chain,sl,(const char*)service,al,(const char*)account,NULL,NULL,&item);
 if(out->status)goto done; if(!item){out->stage=6;goto done;} out->found=1;
 out->stage=3; out->status=SecKeychainItemCopyAccess(item,&access);if(out->status)goto done;
 if(!access){out->stage=6;goto done;}
 out->stage=4; rules=SecAccessCopyMatchingACLList(access,kSecACLAuthorizationDecrypt);
 if(!rules){out->stage=6;goto done;}
 CFIndex n=CFArrayGetCount(rules);if(n<0||n>32){out->stage=6;goto done;}out->count=(uint32_t)n;
 for(CFIndex i=0;i<n;i++){
  CFArrayRef apps=NULL; CFStringRef description=NULL; SecKeychainPromptSelector prompt=0;
  out->stage=5;out->status=SecACLCopyContents((SecACLRef)CFArrayGetValueAtIndex(rules,i),&apps,&description,&prompt);
  // Description is opaque and immediately released, including failure paths.
  if(description)CFRelease(description);
  if(out->status){if(apps)CFRelease(apps);goto done;}
  CFIndex count=apps?CFArrayGetCount(apps):0;
  if(count<0||count>UINT32_MAX){if(apps)CFRelease(apps);out->stage=6;goto done;}
  out->rules[i]=(LifeOSACLRule){apps?(count?2:1):0,(uint32_t)count,(uint32_t)prompt};
  if(apps)CFRelease(apps);
 }
 out->stage=7;
 done: if(rules)CFRelease(rules);if(access)CFRelease(access);if(item)CFRelease(item);if(chain)CFRelease(chain);
}
