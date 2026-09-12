import Foundation
public typealias VoiceHTTPEvent = @convention(c) (UnsafeMutableRawPointer?, Int32, UnsafePointer<UInt8>?, Int32) -> Int32
// Fixed-recipient, one-shot transport. Host supplies an in-memory key via the EXISTING
// CredentialPort. This adapter never loads settings, Keychain, files or environment keys.
final class MiMoHTTP: NSObject, URLSessionDataDelegate, URLSessionTaskDelegate {
    var session: URLSession?
    var task: URLSessionDataTask?
    let mutex = NSRecursiveLock()
    var terminal = false
    var total = 0
    let cap: Int
    let context: UnsafeMutableRawPointer?
    let callback: VoiceHTTPEvent
    init(_ c: UnsafeMutableRawPointer?, _ cb: @escaping VoiceHTTPEvent, _ asr: Bool) { context=c;callback=cb;cap=asr ? 262144 : 12582912;super.init() }
    func start(_ body: UnsafePointer<UInt8>, _ count: Int, _ key: UnsafePointer<UInt8>, _ keyCount: Int, _ asr: Bool) -> Int32 {
        #if !LIFEOS_VOICE_REAL
        return 1 // A cannot POST even if a caller supplies a string resembling a key.
        #else
        guard count > 0 && count <= 4194304, keyCount > 0 && keyCount <= 4096,
              let token = String(bytes: UnsafeBufferPointer(start:key,count:keyCount), encoding:.utf8),
              !token.contains("\r"), !token.contains("\n") else { return 2 }
        mutex.lock(); defer { mutex.unlock() }
        guard task == nil && !terminal else { return 3 }
        let config = URLSessionConfiguration.ephemeral
        config.urlCache=nil; config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.httpCookieStorage=nil;config.httpShouldSetCookies=false;config.urlCredentialStorage=nil
        config.connectionProxyDictionary=[:];config.waitsForConnectivity=false
        config.httpMaximumConnectionsPerHost=1;config.timeoutIntervalForRequest=asr ? 60 : 15
        config.timeoutIntervalForResource=asr ? 60 : 120
        let queue = OperationQueue();queue.maxConcurrentOperationCount=1
        let s=URLSession(configuration:config,delegate:self,delegateQueue:queue);session=s
        var req=URLRequest(url:URL(string:"https://api.xiaomimimo.com/v1/chat/completions")!)
        req.httpMethod="POST";req.setValue("application/json",forHTTPHeaderField:"Content-Type")
        req.setValue("text/event-stream",forHTTPHeaderField:"Accept")
        req.setValue(token,forHTTPHeaderField:"api-key")
        req.httpBody=Data(bytes:body,count:count)
        let t=s.dataTask(with:req);task=t;t.resume();return 0
        #endif
    }
    func emit(_ code:Int32,_ bytes:UnsafePointer<UInt8>?,_ n:Int32)->Int32 {mutex.lock();defer{mutex.unlock()};if terminal{return -1};return callback(context,code,bytes,n)}
    func cancel(){mutex.lock();if terminal{mutex.unlock();return};terminal=true;let t=task;let s=session;task=nil;session=nil;mutex.unlock();t?.cancel();s?.invalidateAndCancel()}
    func resume(){mutex.lock();let t=terminal ? nil : task;mutex.unlock();t?.resume()}
    func urlSession(_ session:URLSession, task:URLSessionTask, willPerformHTTPRedirection response:HTTPURLResponse,newRequest request:URLRequest,completionHandler:@escaping(URLRequest?)->Void){completionHandler(nil);_ = emit(302,nil,0);cancel()}
    func urlSession(_ session:URLSession, task:URLSessionTask,didReceive challenge:URLAuthenticationChallenge,completionHandler:@escaping(URLSession.AuthChallengeDisposition,URLCredential?)->Void){
        // Use system TLS trust only; never accept a custom trust override or HTTP auth retry.
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust {completionHandler(.performDefaultHandling,nil)} else {completionHandler(.cancelAuthenticationChallenge,nil)}
    }
    func urlSession(_ session:URLSession,dataTask:URLSessionDataTask,didReceive response:URLResponse,completionHandler:@escaping(URLSession.ResponseDisposition)->Void){
        guard let http=response as? HTTPURLResponse else {completionHandler(.cancel);cancel();return}
        mutex.lock();let stopped=terminal;mutex.unlock();if stopped{completionHandler(.cancel);return}
        guard http.statusCode==200, (http.value(forHTTPHeaderField:"Content-Type") ?? "").lowercased().hasPrefix("text/event-stream") else {_ = emit(Int32(http.statusCode == 200 ? 415 : http.statusCode),nil,0);completionHandler(.cancel);cancel();return}
        let keep=emit(200,nil,0);completionHandler(keep>=0 ? .allow : .cancel);if keep<0{cancel()}
    }
    func urlSession(_ session:URLSession,dataTask:URLSessionDataTask,didReceive data:Data){
        mutex.lock();if terminal{mutex.unlock();return};total += data.count;let over=total>cap;mutex.unlock()
        if over{_ = emit(-3,nil,0);cancel();return}
        // Callback copies at most this chunk into bounded parser/PCM queues; no disk.
        let disposition=data.withUnsafeBytes{raw in emit(0,raw.bindMemory(to:UInt8.self).baseAddress,Int32(data.count))}
        if disposition<0{cancel()} else if disposition>0{dataTask.suspend()} // explicit backpressure
    }
    func urlSession(_ session:URLSession,task:URLSessionTask,didCompleteWithError error:Error?){
        mutex.lock();if terminal{mutex.unlock();return}
        _ = callback(context,error == nil ? -1 : -2,nil,0)
        terminal=true;self.task=nil;let s=self.session;self.session=nil;mutex.unlock();s?.finishTasksAndInvalidate()
    }
    deinit {cancel()}
}
@_cdecl("lifeos_voice_http_create") public func createHTTP(_ c:UnsafeMutableRawPointer?,_ cb:@escaping VoiceHTTPEvent,_ asr:Int32)->UnsafeMutableRawPointer{Unmanaged.passRetained(MiMoHTTP(c,cb,asr != 0)).toOpaque()}
@_cdecl("lifeos_voice_http_start") public func startHTTP(_ p:UnsafeMutableRawPointer,_ body:UnsafePointer<UInt8>,_ n:Int32,_ key:UnsafePointer<UInt8>,_ kn:Int32,_ asr:Int32)->Int32{Unmanaged<MiMoHTTP>.fromOpaque(p).takeUnretainedValue().start(body,Int(n),key,Int(kn),asr != 0)}
@_cdecl("lifeos_voice_http_cancel") public func cancelHTTP(_ p:UnsafeMutableRawPointer){Unmanaged<MiMoHTTP>.fromOpaque(p).takeUnretainedValue().cancel()}
@_cdecl("lifeos_voice_http_resume") public func resumeHTTP(_ p:UnsafeMutableRawPointer){Unmanaged<MiMoHTTP>.fromOpaque(p).takeUnretainedValue().resume()}
@_cdecl("lifeos_voice_http_destroy") public func destroyHTTP(_ p:UnsafeMutableRawPointer){let h=Unmanaged<MiMoHTTP>.fromOpaque(p);h.takeUnretainedValue().cancel();h.release()}
