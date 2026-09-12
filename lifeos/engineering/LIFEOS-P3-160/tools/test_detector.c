// Offline real-model negative fixtures; no microphone, recordings, or speech success claim.
#include <stdint.h>
#include "c-api.h"
#include <stdio.h>
#include <stdlib.h>
typedef struct LifeOSDetector LifeOSDetector;
extern LifeOSDetector *lifeos_detector_create(const char*,const char*,const char*,const char*,const char*,const char*);
extern int32_t lifeos_detector_accept(LifeOSDetector*,const float*,int32_t,int32_t);
extern void lifeos_detector_destroy(LifeOSDetector*);
extern void lifeos_detector_reset(LifeOSDetector*);
int main(int argc,char**argv){if(argc!=6 && argc!=7)return 2;
 LifeOSDetector*d=lifeos_detector_create(argv[1],argv[2],argv[3],argv[4],"n ǐ h ǎo x iǎo ōu @你好小欧",argv[5]);if(!d)return 3;
 float pcm[320]={0};int wake=0,speech=0;uint32_t seed=17;
 for(int kind=0;kind<2;kind++){
  lifeos_detector_reset(d);
  for(int frame=0;frame<500;frame++){
   for(int i=0;i<320;i++){seed=seed*1664525u+1013904223u;pcm[i]=kind?(((seed>>16)/65535.0f)-0.5f)*0.01f:0.0f;}
   int flags=lifeos_detector_accept(d,pcm,320,1);if(flags<0)return 4;wake+=(flags&1)!=0;speech+=(flags&2)!=0;
  }
 }
 if(argc==7){
  lifeos_detector_reset(d);wake=0;speech=0;
  const SherpaOnnxWave *wave=SherpaOnnxReadWave(argv[6]);if(!wave||wave->sample_rate!=16000)return 5;
  for(int offset=0;offset<wave->num_samples+32000;offset+=320){
   for(int i=0;i<320;i++)pcm[i]=offset+i<wave->num_samples?wave->samples[offset+i]:0.0f;
   int flags=lifeos_detector_accept(d,pcm,320,1);if(flags<0)return 4;wake+=(flags&1)!=0;speech+=(flags&2)!=0;
  }
  SherpaOnnxFreeWave(wave);lifeos_detector_destroy(d);
  printf("{\"real_model_loaded\":true,\"local_synthetic_speech\":true,\"wake_events\":%d,\"vad_speech_frames\":%d,\"microphone_opened\":false}\n",wake,speech);return 0;
 }
 lifeos_detector_destroy(d);
 printf("{\"real_model_loaded\":true,\"synthetic_silence_seconds\":10,\"synthetic_noise_seconds\":10,\"wake_events\":%d,\"vad_speech_frames\":%d,\"positive_wake_verified\":false,\"microphone_opened\":false}\n",wake,speech);
 return wake||speech?1:0;
}
