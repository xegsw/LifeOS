//! Audio-only modules. The host owns all business, storage, grants and credentials.
//! No module initialization opens a device or a network connection.
pub mod audio;
pub mod budget;
pub mod gateway;
pub mod mimo;
pub mod session;
mod strict;
pub mod worker;
