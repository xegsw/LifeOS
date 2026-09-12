//! Native local calendar; no system clock or timezone mutation.
use super::*;
use std::{ffi::{c_void,CStr,CString},ptr};
#[link(name="CoreFoundation",kind="framework")]
unsafe extern "C" {
 fn CFTimeZoneResetSystem();
 fn CFTimeZoneCopySystem()->*const c_void;
 fn CFTimeZoneGetName(t:*const c_void)->*const c_void;
 fn CFTimeZoneCreateWithName(a:*const c_void,n:*const c_void,abbrev:u8)->*const c_void;
 fn CFStringCreateWithCString(a:*const c_void,s:*const i8,e:u32)->*const c_void;
 fn CFStringGetCString(s:*const c_void,b:*mut i8,len:isize,e:u32)->u8;
 fn CFCalendarCreateWithIdentifier(a:*const c_void,id:*const c_void)->*const c_void;
 fn CFCalendarSetTimeZone(c:*const c_void,t:*const c_void);
 fn CFCalendarGetTimeRangeOfUnit(c:*const c_void,u:usize,at:f64,start:*mut f64,duration:*mut f64)->u8;
 fn CFCalendarDecomposeAbsoluteTime(c:*const c_void,at:f64,desc:*const i8,...)->u8;
 fn CFRelease(v:*const c_void);
}
struct Owned(*const c_void);
impl Owned {fn new(p:*const c_void)->R<Self>{if p.is_null(){Err(error("proactive_clock_unavailable"))}else{Ok(Self(p))}}}
impl Drop for Owned {fn drop(&mut self){unsafe{CFRelease(self.0)}}}
pub(super) struct Civil {pub name:String,pub hour:i32,pub end:i64}
#[cfg(test)]thread_local!{pub(super) static TEST_ZONE:std::cell::RefCell<String>=std::cell::RefCell::new("Asia/Shanghai".into());}
pub(super) fn local(at:i64)->R<Civil>{
 #[cfg(test)] let name=Some(TEST_ZONE.with(|z|z.borrow().clone()));
 #[cfg(not(test))] let name:Option<String>=None;
 in_zone(at,name.as_deref())
}
fn in_zone(at:i64,name:Option<&str>)->R<Civil>{unsafe{
 let tz=if let Some(name)=name{let n=CString::new(name).map_err(|_|error("proactive_clock_unavailable"))?;let n=Owned::new(CFStringCreateWithCString(ptr::null(),n.as_ptr(),0x08000100))?;Owned::new(CFTimeZoneCreateWithName(ptr::null(),n.0,0))?}else{CFTimeZoneResetSystem();Owned::new(CFTimeZoneCopySystem())?};
 let ident=Owned::new(CFStringCreateWithCString(ptr::null(),c"gregorian".as_ptr(),0x08000100))?;let calendar=Owned::new(CFCalendarCreateWithIdentifier(ptr::null(),ident.0))?;CFCalendarSetTimeZone(calendar.0,tz.0);
 let absolute=at as f64/1000.0-978307200.0;let(mut start,mut duration,mut hour)=(0.0,0.0,0i32);
 if CFCalendarGetTimeRangeOfUnit(calendar.0,1<<4,absolute,&mut start,&mut duration)==0||CFCalendarDecomposeAbsoluteTime(calendar.0,absolute,c"H".as_ptr(),&mut hour)==0{return Err(error("proactive_clock_unavailable"))}
 let mut buffer=[0i8;128];if CFStringGetCString(CFTimeZoneGetName(tz.0),buffer.as_mut_ptr(),buffer.len() as isize,0x08000100)==0{return Err(error("proactive_clock_unavailable"))}
 let name=CStr::from_ptr(buffer.as_ptr()).to_str().map_err(|_|error("proactive_clock_unavailable"))?.to_string();let end=((start+duration+978307200.0)*1000.0).round() as i64;
 if !(0..24).contains(&hour)||end<=at{return Err(error("proactive_clock_unavailable"))}Ok(Civil{name,hour,end})
}}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn local_day_handles_dst_without_changing_machine_timezone(){
  let spring=in_zone(1772956800000,Some("America/New_York")).unwrap();
  assert_eq!(spring.name,"America/New_York");assert_eq!(spring.end,1773028800000);
  let shanghai=in_zone(1772956800000,Some("Asia/Shanghai")).unwrap();assert_ne!(spring.end,shanghai.end);
 }
}
