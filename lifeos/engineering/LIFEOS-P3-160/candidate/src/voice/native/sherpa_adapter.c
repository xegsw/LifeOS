// Compiled against the pinned sherpa-onnx 1.13.7 C API (Apache-2.0).
// Audio-only library, called from a serialized host audio worker, never IPC directly.
#include "c-api.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef struct {
 const SherpaOnnxKeywordSpotter *kws;
 const SherpaOnnxOnlineStream *stream;
 const SherpaOnnxVoiceActivityDetector *vad;
} LifeOSDetector;
void lifeos_detector_destroy(LifeOSDetector *d) {
 if(!d)return;
 if(d->stream)SherpaOnnxDestroyOnlineStream(d->stream);
 if(d->kws)SherpaOnnxDestroyKeywordSpotter(d->kws);
 if(d->vad)SherpaOnnxDestroyVoiceActivityDetector(d->vad);
 memset(d,0,sizeof(*d));free(d);
}
// Integrator resolves ONLY immutable packaged, hash/license-verified model paths.
// No frontend path/URL or authorization flag is accepted by the IPC wrapper.
LifeOSDetector *lifeos_detector_create(const char *encoder,const char *decoder,const char *joiner,const char *tokens,const char *keywords,const char *vad_model) {
 if(!encoder||!decoder||!joiner||!tokens||!keywords||!vad_model)return NULL;
 LifeOSDetector *d=calloc(1,sizeof(*d));if(!d)return NULL;
 SherpaOnnxKeywordSpotterConfig k={0};
 k.feat_config.sample_rate=16000;k.feat_config.feature_dim=80;
 k.model_config.transducer.encoder=encoder;k.model_config.transducer.decoder=decoder;k.model_config.transducer.joiner=joiner;
 k.model_config.tokens=tokens;k.model_config.provider="cpu";k.model_config.num_threads=1;k.model_config.debug=0;
 k.max_active_paths=4;k.num_trailing_blanks=1;k.keywords_score=1.0f;k.keywords_threshold=0.25f;k.keywords_buf=keywords;k.keywords_buf_size=(int32_t)strlen(keywords);
 d->kws=SherpaOnnxCreateKeywordSpotter(&k);if(!d->kws){lifeos_detector_destroy(d);return NULL;}
 d->stream=SherpaOnnxCreateKeywordStream(d->kws);if(!d->stream){lifeos_detector_destroy(d);return NULL;}
 SherpaOnnxVadModelConfig v={0};v.sample_rate=16000;v.num_threads=1;v.provider="cpu";v.debug=0;
 v.silero_vad.model=vad_model;v.silero_vad.threshold=0.5f;v.silero_vad.min_silence_duration=0.8f;v.silero_vad.min_speech_duration=0.1f;v.silero_vad.max_speech_duration=60.0f;v.silero_vad.window_size=512;
 d->vad=SherpaOnnxCreateVoiceActivityDetector(&v,62.0f);if(!d->vad){lifeos_detector_destroy(d);return NULL;}return d;
}
int32_t lifeos_detector_accept(LifeOSDetector *d,const float *pcm,int32_t count,int32_t listening_for_wake) {
 if(!d||!pcm||count<=0||count>8192)return -1;
 for(int i=0;i<count;i++)if(!isfinite(pcm[i])||pcm[i]<-1.0f||pcm[i]>1.0f)return -1;
 int result=0;
 if(listening_for_wake){
  SherpaOnnxOnlineStreamAcceptWaveform(d->stream,16000,pcm,count);
  while(SherpaOnnxIsKeywordStreamReady(d->kws,d->stream))SherpaOnnxDecodeKeywordStream(d->kws,d->stream);
  const SherpaOnnxKeywordResult *r=SherpaOnnxGetKeywordResult(d->kws,d->stream);
  if(r){if(r->keyword&&r->keyword[0]){result|=1;SherpaOnnxResetKeywordStream(d->kws,d->stream);}SherpaOnnxDestroyKeywordResult(r);}
 }
 SherpaOnnxVoiceActivityDetectorAcceptWaveform(d->vad,pcm,count);
 if(SherpaOnnxVoiceActivityDetectorDetected(d->vad))result|=2;
 // Host Segmenter owns the utterance. Do not keep a second completed-audio queue.
 while(!SherpaOnnxVoiceActivityDetectorEmpty(d->vad))SherpaOnnxVoiceActivityDetectorPop(d->vad);
 return result;
}
void lifeos_detector_reset(LifeOSDetector *d){if(!d)return;SherpaOnnxResetKeywordStream(d->kws,d->stream);SherpaOnnxVoiceActivityDetectorReset(d->vad);}
